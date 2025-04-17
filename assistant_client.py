import os, json, time
from openai import OpenAI
from datetime import datetime
from fb_api import get_posts_by_range, create_campaign, boost_posts
from logger import info, error, debug, warning

API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
PAGE_ID = os.getenv("FB_PAGE_ID")

info(f"Starting assistant client with ASSISTANT_ID: {ASSISTANT_ID}, PAGE_ID: {PAGE_ID}")
client = OpenAI(api_key=API_KEY)

def create_thread() -> str:
    debug("Creating new thread")
    try:
        thread = client.beta.threads.create()
        info(f"Created new thread with ID: {thread.id}")
        return thread.id
    except Exception as e:
        error(f"Error creating thread: {e}")
        raise

def post_user_message(thread_id: str, content: str):
    debug(f"Posting user message to thread {thread_id}")
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        info(f"Posted user message ID: {message.id} to thread {thread_id}")
        return message
    except Exception as e:
        error(f"Error posting user message to thread {thread_id}: {e}")
        raise

def call_GetPosts(args: dict) -> str:
    info(f"Tool call: GetPosts with args: {args}")
    try:
        since = datetime.fromisoformat(args["since"])
        until = datetime.fromisoformat(args["until"])
        debug(f"Fetching posts from {since} to {until}")
        posts = get_posts_by_range(PAGE_ID, since, until)
        if not posts:
            warning(f"No posts found from {args['since']} to {args['until']}")
            return f"No posts found from {args['since']} to {args['until']}."
        # Convert the posts array to a JSON string
        info(f"Found {len(posts)} posts between {args['since']} and {args['until']}")
        return json.dumps(posts)
    except Exception as e:
        error(f"Error in GetPosts: {e}")
        return f"Error in GetPosts: {e}"

def call_CreateCampaign(args: dict) -> str:
    info(f"Tool call: CreateCampaign with args: {args}")
    try:
        name = args["name"]
        objective = args["objective"]
        budget = float(args["budget"])
        daily_cents = int(budget * 100)
        debug(f"Creating campaign '{name}' with objective '{objective}' and daily budget {budget} USD")
        res = create_campaign(name, objective, daily_cents)
        info(f"Campaign created: {res}")
        return f"Campaign '{name}' created with ID: {res['campaign_id']}."
    except Exception as e:
        error(f"Error in CreateCampaign: {e}")
        return f"Error in CreateCampaign: {e}"

def call_BoostPosts(args: dict) -> str:
    info(f"Tool call: BoostPosts with args: {args}")
    try:
        campaign_id = args["campaign_id"]
        post_ids = args["post_ids"]
        opt_goal = args["optimization_goal"]
        bid_cents = int(float(args["bid_amount"]) * 100)
        geos = [g.strip().upper() for g in args["geo_locations"]]
        
        debug(f"Boosting posts {post_ids} under campaign {campaign_id} with goal {opt_goal}")
        res = boost_posts(campaign_id, post_ids, opt_goal, bid_cents, geos)
        info(f"Posts boosted: {res}")
        return (
            f"Boosted {len(post_ids)} posts under ad set {res['ad_set_id']}. "
                f"Ad IDs: {res['ad_ids']}"
            )
    except Exception as e:
        error(f"Error in BoostPosts: {e}")
        return f"Error in BoostPosts: {e}"

def run_turn(thread_id: str, user_input: str):
    """ Generator: yields assistant output (streamed). """
    info(f"Starting new conversation turn for thread {thread_id}")
    debug(f"User input: {user_input}")
    
    # 1) post user message
    try:
        post_user_message(thread_id, user_input)
    except Exception as e:
        error(f"Failed to post user message: {e}")
        yield f"Error: Failed to send your message. {str(e)}"
        return

    current_date = datetime.now().strftime('%B %d, %Y')
    additional_instructions = f"Today's date is {current_date}. You can use it to understand which year, month or day user is referring to when asking questions."
    debug(f"Using additional instructions: {additional_instructions}")

    # 2) first run (sync) to detect function_call
    try:
        info(f"Creating run for thread {thread_id}")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            additional_instructions=additional_instructions,
            stream=False
        )
        
        debug(f"Run created with ID: {run.id}, status: {run.status}")
        
        # Wait for the run to complete
        run_start_time = time.time()
        while run.status not in ["completed", "failed", "cancelled", "expired"]:
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            # Log status changes and duration
            run_duration = time.time() - run_start_time
            debug(f"Run {run.id} status: {run.status}, duration: {run_duration:.2f}s")
            
            if run.status == "requires_action" and run.required_action:
                # Handle function calling
                tools_to_call = run.required_action.submit_tool_outputs.tool_calls
                info(f"Run requires action: {len(tools_to_call)} tool call(s)")
                
                tool_outputs = []
                
                for tool in tools_to_call:
                    name = tool.function.name
                    args = json.loads(tool.function.arguments or "{}")
                    debug(f"Tool call: {name} with args: {args}")
                    
                    # dispatch
                    tool_start_time = time.time()
                    try:
                        if name == "GetPosts":
                            result = call_GetPosts(args)
                        elif name == "CreateCampaign":
                            result = call_CreateCampaign(args)
                        elif name == "BoostPosts":
                            result = call_BoostPosts(args)
                        else:
                            error(f"Unknown function '{name}'")
                            result = f"Error: unknown function '{name}'"
                    except Exception as e:
                        error(f"Exception during tool call {name}: {e}")
                        result = f"Error during {name}: {str(e)}"
                    
                    tool_duration = time.time() - tool_start_time
                    debug(f"Tool call {name} completed in {tool_duration:.2f}s")
                    
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": result
                    })
                
                # Submit outputs
                debug(f"Submitting {len(tool_outputs)} tool outputs")
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
        
        # Log final run status
        run_total_duration = time.time() - run_start_time
        if run.status == "completed":
            info(f"Run {run.id} completed successfully in {run_total_duration:.2f}s")
        else:
            warning(f"Run {run.id} ended with status {run.status} after {run_total_duration:.2f}s")
            if hasattr(run, 'last_error'):
                error(f"Run error: {run.last_error}")
    
        # Get messages, focusing on the newest assistant message
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc"
        )
        
        latest_message = next((m for m in messages.data if m.role == "assistant"), None)
        
        if latest_message:
            info(f"Retrieved assistant message {latest_message.id}")
            # Since we're not streaming, yield the entire content at once
            content_text = ""
            for content_item in latest_message.content:
                if content_item.type == "text":
                    content_text += content_item.text.value
            
            debug(f"Assistant response: {content_text[:100]}..." if len(content_text) > 100 else content_text)
            yield content_text
        else:
            warning("No assistant message found after run completion")
            yield "I couldn't generate a response. Please try again."
            
    except Exception as e:
        error(f"Error during run_turn: {e}")
        yield f"I encountered an error: {str(e)}"
