import os, json, time
from openai import OpenAI
from datetime import datetime
from fb_api import get_posts_by_range, create_campaign, boost_posts

API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
PAGE_ID = os.getenv("FB_PAGE_ID")

client = OpenAI(api_key=API_KEY)

def create_thread() -> str:
    thread = client.beta.threads.create()
    return thread.id

def post_user_message(thread_id: str, content: str):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

def call_GetPosts(args: dict) -> str:
    try:
        since = datetime.fromisoformat(args["since"])
        until = datetime.fromisoformat(args["until"])
        posts = get_posts_by_range(PAGE_ID, since, until)
        if not posts:
            return f"No posts found from {args['since']} to {args['until']}."
        # Convert the posts array to a JSON string
        return json.dumps(posts)
    except Exception as e:
        return f"Error in GetPosts: {e}"

def call_CreateCampaign(args: dict) -> str:
    try:
        name = args["name"]
        objective = args["objective"]
        budget = float(args["budget"])
        daily_cents = int(budget * 100)
        res = create_campaign(name, objective, daily_cents)
        return f"Campaign '{name}' created with ID: {res['campaign_id']}."
    except Exception as e:
        return f"Error in CreateCampaign: {e}"

def call_BoostPosts(args: dict) -> str:
    try:
        campaign_id = args["campaign_id"]
        post_ids = args["post_ids"]
        opt_goal = args["optimization_goal"]
        bid_cents = int(float(args["bid_amount"]) * 100)
        geos = [g.strip().upper() for g in args["geo_locations"]]
        res = boost_posts(campaign_id, post_ids, opt_goal, bid_cents, geos)
        return (
            f"Boosted {len(post_ids)} posts under ad set {res['ad_set_id']}. "
                f"Ad IDs: {res['ad_ids']}"
            )
    except Exception as e:
        return f"Error in BoostPosts: {e}"

def run_turn(thread_id: str, user_input: str):
    """ Generator: yields assistant output (streamed). """
    # 1) post user
    post_user_message(thread_id, user_input)

    current_date = datetime.now().strftime('%B %d, %Y')
    additional_instructions = f"Today's date is {current_date}. You can use it to understand which year, month or day user is referring to when asking questions."

    # 2) first run (sync) to detect function_call
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
        additional_instructions=additional_instructions,
        stream=False
    )
    
    # Wait for the run to complete
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        
        if run.status == "requires_action" and run.required_action:
            # Handle function calling
            tools_to_call = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool in tools_to_call:
                name = tool.function.name
                args = json.loads(tool.function.arguments or "{}")
                # dispatch
                if name == "GetPosts":
                    result = call_GetPosts(args)
                elif name == "CreateCampaign":
                    result = call_CreateCampaign(args)
                elif name == "BoostPosts":
                    result = call_BoostPosts(args)
                else:
                    result = f"Error: unknown function '{name}'"
                
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": result
                })
            
            # Submit outputs
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
    
    # Get messages, focusing on the newest assistant message
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc"
    )
    
    latest_message = next((m for m in messages.data if m.role == "assistant"), None)
    
    if latest_message:
        # Since we're not streaming, yield the entire content at once
        content_text = ""
        for content_item in latest_message.content:
            if content_item.type == "text":
                content_text += content_item.text.value
        
        yield content_text
