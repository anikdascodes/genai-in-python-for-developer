import json
from dotenv import load_dotenv
from openai import OpenAI

# Load your .env file (make sure it contains OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Mock function to simulate a tool
def get_weather(city: str):
    print("🔧 Tool Called: get_weather →", city)
    return "31 degree Celsius"

# Define available tools
available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as input and returns the current weather for the city"
    }
}

# System prompt to guide the assistant's behavior
system_prompt = """
You are a helpful assistant who resolves user queries using tools.
You work in four steps: plan, action, observe, and output.

For a given user query and available tools:
- First, plan what the user wants
- Then choose the relevant tool
- Then take action by calling the tool
- Then observe the result and finally output the answer

Rules:
- Follow the JSON format strictly.
- Only perform one step at a time and wait for the next input.

Output JSON Format:
{
    "step": "string",
    "content": "string",
    "function": "The name of the function if the step is action",
    "input": "The input parameter for the function"
}

Available Tools:
- get_weather: Takes a city name and returns the current weather

Example:
User Query: What is the weather of New York?
Step-by-step output should look like this:
{"step": "plan", "content": "User is asking for weather in New York"}
{"step": "plan", "content": "I will call get_weather for this"}
{"step": "action", "function": "get_weather", "input": "New York"}
{"step": "observe", "output": "12 degree Celsius"}
{"step": "output", "content": "The weather in New York is 12 degree Celsius"}
"""

# Messages list to simulate chat history
messages = [
    {"role": "system", "content": system_prompt}
]

# Take user input
user_query = input("> ")
messages.append({"role": "user", "content": user_query})

# Loop through the steps
while True:
    # Get assistant's next step as JSON
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=messages
    )

    # Parse assistant response
    parsed_output = json.loads(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

    # Handle each step
    step = parsed_output.get("step")

    if step == "plan":
        print("🧠:", parsed_output.get("content"))
        continue

    elif step == "action":
        tool_name = parsed_output.get("function")
        tool_input = parsed_output.get("input")

        # Check if the tool exists and call it
        if tool_name in available_tools:
            tool_function = available_tools[tool_name]["fn"]
            output = tool_function(tool_input)

            # Send observation to assistant
            observation = {"step": "observe", "output": output}
            messages.append({"role": "assistant", "content": json.dumps(observation)})
        continue

    elif step == "observe":
        print("👀 Observation:", parsed_output.get("output"))
        continue

    elif step == "output":
        print("🤖:", parsed_output.get("content"))
        break
