import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# ────────────────────────────────────────
# TOOL DEFINITIONS
# ────────────────────────────────────────

def get_weather(city: str):
    print("🔨 Tool Called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong while fetching the weather."

def run_command(command: str):
    print("🔨 Tool Called: run_command", command)
    result = os.system(command)
    return f"Command executed with result code: {result}"

def web_search(query: str):
    print("🔨 Tool Called: web_search", query)
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        abstract = data.get("Abstract", "")
        related_topics = data.get("RelatedTopics", [])
        if abstract:
            return f"📄 Abstract: {abstract}"
        elif related_topics:
            return f"🔗 Related: {related_topics[0].get('Text', 'No result')}"
        else:
            return "❓ No relevant results found."
    return "Something went wrong while searching the web."

# ────────────────────────────────────────
# AVAILABLE TOOLS DICTIONARY
# ────────────────────────────────────────

available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as input and returns the current weather for that city."
    },
    "run_command": {
        "fn": run_command,
        "description": "Takes a command string and executes it in the system shell."
    },
    "web_search": {
        "fn": web_search,
        "description": "Takes a search query and returns a short summary using DuckDuckGo."
    }
}

# ────────────────────────────────────────
# SYSTEM PROMPT FOR THE AGENT
# ────────────────────────────────────────

system_prompt = """
You are a helpful AI Assistant specialized in resolving user queries.
You work in a four-stage cycle: start, plan, action, observe.

For each user query, follow this cycle:

1. Plan the steps needed to resolve the query.
2. Select the relevant tool from the available tools.
3. Perform an action by calling the tool.
4. Wait for the observation and use it to form your final answer.

Rules:
- Follow the Output JSON Format strictly.
- Only perform ONE step at a time and wait for the next input.
- Carefully analyze the user query before taking action.

Output JSON Format:
{
    "step": "string",                  # One of: plan, action, observe, output
    "content": "string",              # Explanation of what you're doing (for plan/output)
    "function": "function_name",      # Only for step=action
    "input": "function input param"   # Only for step=action
}

Available Tools:
- get_weather: Takes a city name as input and returns the current weather for that city.
- run_command: Takes a command string and executes it in the system shell.
- web_search: Takes a search query and returns a short summary using DuckDuckGo.

Example:
User Query: What is the weather of New York?
Output: { "step": "plan", "content": "The user is interested in the weather in New York." }
Output: { "step": "plan", "content": "From the available tools I should call get_weather." }
Output: { "step": "action", "function": "get_weather", "input": "New York" }
Output: { "step": "observe", "output": "12°C, Sunny" }
Output: { "step": "output", "content": "The weather in New York is 12°C and sunny." }
"""

# ────────────────────────────────────────
# CONVERSATION LOOP
# ────────────────────────────────────────

messages = [{ "role": "system", "content": system_prompt }]

while True:
    user_query = input("\n> ")
    messages.append({ "role": "user", "content": user_query })

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({ "role": "assistant", "content": json.dumps(parsed_output) })

        step = parsed_output.get("step")

        if step == "plan":
            print(f"🧠 PLAN: {parsed_output.get('content')}")
            continue

        elif step == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            tool = available_tools.get(tool_name)
            if tool:
                result = tool["fn"](tool_input)
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({ "step": "observe", "output": result })
                })
                continue

        elif step == "output":
            print(f"🤖 FINAL OUTPUT: {parsed_output.get('content')}")
            break
