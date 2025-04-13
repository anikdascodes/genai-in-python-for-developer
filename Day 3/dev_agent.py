import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os
import subprocess 


load_dotenv()
client = OpenAI()
PROJECT_DIR = "ai_generated_project" 
# Create the project directory if it doesn't exist
os.makedirs(PROJECT_DIR, exist_ok=True)
print(f"🤖 Project files will be managed in: ./{PROJECT_DIR}/")

# --- Tool Functions ---

def create_directory(path: str) -> str:
    """Creates a directory (including parent directories) if it doesn't exist."""
    full_path = os.path.join(PROJECT_DIR, path)
    print(f"🔨 Tool Called: create_directory, Path: {full_path}")
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Successfully created directory: {full_path}"
    except Exception as e:
        return f"Error creating directory {full_path}: {e}"

def create_file(path: str, content: str = "") -> str:
    """Creates a new file with specified content. Overwrites if exists."""
    full_path = os.path.join(PROJECT_DIR, path)
    print(f"🔨 Tool Called: create_file, Path: {full_path}")
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"Successfully created/overwritten file: {full_path}"
    except Exception as e:
        return f"Error creating file {full_path}: {e}"

def write_to_file(path: str, content: str) -> str:
    """Writes (overwrites) content to an existing file."""
    
    return create_file(path, content)

def read_file(path: str) -> str:
    """Reads the content of a file."""
    full_path = os.path.join(PROJECT_DIR, path)
    print(f"🔨 Tool Called: read_file, Path: {full_path}")
    try:
        with open(full_path, 'r') as f:
            content = f.read()
            # Add truncation for potentially large files to fit context
            max_len = 2000
            if len(content) > max_len:
                return content[:max_len] + "\n... [File truncated]"
            return content
    except FileNotFoundError:
        return f"Error: File not found at {full_path}"
    except Exception as e:
        return f"Error reading file {full_path}: {e}"

def list_directory(path: str = ".") -> str:
    """Lists the contents of a directory within the project."""
    full_path = os.path.join(PROJECT_DIR, path)
    print(f"🔨 Tool Called: list_directory, Path: {full_path}")
    try:
        entries = os.listdir(full_path)
        if not entries:
            return f"Directory is empty: {full_path}"
        # Add indication if entry is a file or directory
        output = f"Contents of {full_path}:\n"
        for entry in entries:
            entry_path = os.path.join(full_path, entry)
            is_dir = os.path.isdir(entry_path)
            output += f"- {entry} {'(Directory)' if is_dir else '(File)'}\n"
        return output

    except FileNotFoundError:
        return f"Error: Directory not found at {full_path}"
    except Exception as e:
        return f"Error listing directory {full_path}: {e}"


def run_command(command: str) -> str:
    """Runs a shell command within the project directory."""
    print(f"🔨 Tool Called: run_command, Command: {command}")
    # SECURITY WARNING: Running arbitrary commands can be dangerous.
    # In a real-world scenario, implement strict sandboxing or command validation.
    try:
        # Execute the command within the defined PROJECT_DIR
        result = subprocess.run(
            command,
            shell=True,         # Be cautious with shell=True
            cwd=PROJECT_DIR,    # Run command in the project directory
            capture_output=True,
            text=True,
            check=False         # Don't raise exception on non-zero exit code
        )
        output = f"Exit Code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        # Limit output length for context window
        max_len = 1000
        if len(output) > max_len:
             output = output[:max_len] + "\n... [Output truncated]"
        return output

    except Exception as e:
        return f"Error running command '{command}': {e}"

# --- Available Tools Dictionary ---

available_tools = {
    "create_directory": {
        "fn": create_directory,
        "description": "Creates a new directory at the specified path relative to the project root. Use POSIX-style paths (e.g., 'src/components').",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    },
    "create_file": {
        "fn": create_file,
        "description": "Creates a new file at the specified path relative to the project root with the given content. Overwrites if the file already exists. Creates parent directories if needed. Use POSIX-style paths.",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}
    },
     "write_to_file": { # Alias for create_file for clarity in LLM's reasoning
        "fn": write_to_file,
        "description": "Writes (or overwrites) content to a file at the specified path relative to the project root. Creates parent directories if needed. Use POSIX-style paths.",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}
    },
    "read_file": {
        "fn": read_file,
        "description": "Reads the content of a file at the specified path relative to the project root. Returns the content or an error if the file doesn't exist. Use POSIX-style paths.",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    },
    "list_directory": {
        "fn": list_directory,
        "description": "Lists the files and subdirectories within a specified directory path relative to the project root. Use '.' for the root directory. Use POSIX-style paths.",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}, "required": ["path"]}
    },
    "run_command": {
        "fn": run_command,
        "description": "Executes a shell command (like 'npm install', 'pip install', 'python app.py', 'npm run build') within the project's root directory. Returns the command's output (stdout/stderr) and exit code.",
        "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
    }
}

# --- System Prompt ---

# Dynamically generate tool descriptions for the prompt
tool_descriptions = "\n".join([
    f"- {name}: {tool['description']} | Input JSON Schema: {json.dumps(tool['input_schema'])}"
    for name, tool in available_tools.items()
])

system_prompt = f"""
You are a specialized AI Assistant agent focused on coding and full-stack project development.
Your goal is to help the user create, modify, and manage web development projects step-by-step directly through terminal interaction.
You operate entirely within the './{PROJECT_DIR}/' directory. All file paths you generate or use MUST be relative to this directory and use POSIX-style separators (/).

Workflow:
1.  **Understand:** Analyze the user's request.
2.  **Plan:** Break down the request into small, sequential steps. For complex requests or follow-ups, PLAN to use 'list_directory' and 'read_file' first to understand the current project state before proposing changes. Output each planning step individually.
3.  **Action:** For steps requiring interaction with the file system or command line, select the appropriate tool from the list below and specify the required input parameters in JSON format. Output the action step.
4.  **Observe:** Wait for the result of the action (which will be provided in the next message).
5.  **Output/Continue:** Based on the observation, either provide the final output/confirmation to the user or continue with the next planning/action step if the task is not complete.

Rules:
- Follow the Output JSON Format STRICTLY.
- Perform ONE step (plan, action, or output) at a time. Wait for the next message before proceeding.
- ALWAYS use relative paths based on the './{PROJECT_DIR}/' root. Example: 'src/index.js', 'requirements.txt'.
- When writing code, provide the complete code content for the file in the 'content' field of the 'create_file' or 'write_to_file' action.
- Before modifying existing files in follow-up requests, ALWAYS plan to use 'read_file' to get the current content first.
- If a command fails (non-zero exit code in observation), inform the user and ask how to proceed.

Output JSON Format:
{{
    "step": "plan | action | output",
    "content": "Description of the plan, the final response to the user, or reasoning for the action.",
    "function": "(Optional) The name of the function tool to call if step is 'action'.",
    "input": "(Optional) A JSON object containing the required parameters for the function if step is 'action'."
}}

Available Tools:
{tool_descriptions}

Example Interaction:

User Query: Create a simple python flask app with a single route.
Assistant: {{ "step": "plan", "content": "Okay, I will create a simple Flask application. First, I need a main Python file." }}
Assistant: {{ "step": "plan", "content": "I will create a file named 'app.py' in the root directory." }}
Assistant: {{ "step": "action", "content": "Creating the main application file.", "function": "create_file", "input": {{ "path": "app.py", "content": "from flask import Flask\\n\\napp = Flask(__name__)\\n\\n@app.route('/')\\ndef hello_world():\\n    return 'Hello, World!'\\n\\nif __name__ == '__main__':\\n    app.run(debug=True)" }} }}
User (System): {{ "step": "observe", "output": "Successfully created/overwritten file: ai_generated_project/app.py" }}
Assistant: {{ "step": "plan", "content": "Now, I need to create a requirements.txt file for Flask." }}
Assistant: {{ "step": "action", "content": "Creating requirements.txt.", "function": "create_file", "input": {{ "path": "requirements.txt", "content": "Flask" }} }}
User (System): {{ "step": "observe", "output": "Successfully created/overwritten file: ai_generated_project/requirements.txt" }}
Assistant: {{ "step": "plan", "content": "Next, I should install the dependencies using pip." }}
Assistant: {{ "step": "action", "content": "Running pip install.", "function": "run_command", "input": {{ "command": "pip install -r requirements.txt" }} }}
User (System): {{ "step": "observe", "output": "Exit Code: 0\\nSTDOUT:\\nCollecting Flask..." }}
Assistant: {{ "step": "output", "content": "Flask project setup is complete. You have 'app.py' and 'requirements.txt'. Dependencies have been installed. You can run it using 'python app.py' within the '{PROJECT_DIR}' directory." }}

"""

# --- Main Interaction Loop ---

messages = [
    { "role": "system", "content": system_prompt }
]

print("🤖 Agent Ready. How can I help you build today?")

while True:
    user_query = input('> ')
    if user_query.lower() in ['exit', 'quit']:
        break

    messages.append({ "role": "user", "content": user_query })

    while True: # Inner loop for plan/action/observe steps
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Or gpt-3.5-turbo if preferred
                response_format={"type": "json_object"},
                messages=messages
            )

            raw_response_content = response.choices[0].message.content
            # Append the raw assistant response for context
            messages.append({"role": "assistant", "content": raw_response_content})

            # Attempt to parse the JSON
            try:
                parsed_output = json.loads(raw_response_content)
            except json.JSONDecodeError:
                print(f"🚨 Error: LLM returned invalid JSON: {raw_response_content}")
                # Ask LLM to fix or just break and ask user again
                messages.append({"role": "user", "content": "Your previous response was not valid JSON. Please provide the response in the correct JSON format."})
                continue # Ask LLM again


            step = parsed_output.get("step")
            content = parsed_output.get("content", "")

            print(f" M: Step: {step}, Content: {content}") # Debugging print

            if step == "plan":
                print(f"🧠 Planning: {content}")
                # Append a system message indicating the plan was acknowledged (optional, might help LLM track)
                # messages.append({"role": "system", "content": f"Plan acknowledged: {content}"})
                continue # Let the LLM generate the next step

            elif step == "action":
                tool_name = parsed_output.get("function")
                tool_input_dict = parsed_output.get("input") # Expecting a dictionary

                print(f"🎬 Action: Calling {tool_name} with input: {tool_input_dict}")

                if not tool_name or not isinstance(tool_input_dict, dict):
                     print(f"🚨 Error: Invalid action format from LLM. Missing function name or input is not a JSON object.")
                     # Provide feedback to LLM
                     messages.append({"role": "user", "content": f"Invalid action format provided. Ensure 'function' is specified and 'input' is a JSON object matching the tool schema. Tool: {tool_name}, Input: {tool_input_dict}"})
                     continue


                if tool_name in available_tools:
                    tool_config = available_tools[tool_name]
                    tool_function = tool_config["fn"]
                    schema = tool_config["input_schema"]

                    # Basic input validation (can be expanded)
                    required_params = schema.get("required", [])
                    missing_params = [p for p in required_params if p not in tool_input_dict]

                    if missing_params:
                        print(f"🚨 Error: Missing required parameters for {tool_name}: {missing_params}")
                        observation_content = f"Error: Missing required parameters for {tool_name}: {missing_params}. Required: {required_params}"

                    else:
                         # Extract arguments based on function signature (more robust than just passing dict)
                        # This part assumes tool function args match keys in input_dict
                        # For more complex cases, inspect function signature
                        try:
                           # We pass the dict directly, Python function should unpack it or handle **kwargs
                           # Or better: Inspect signature and pass args explicitly
                           # func_sig = inspect.signature(tool_function)
                           # args_to_pass = {k: tool_input_dict[k] for k in func_sig.parameters if k in tool_input_dict}
                           # observation_content = tool_function(**args_to_pass)

                           # Simpler approach: pass the dictionary if the function expects keyword arguments
                           # This relies on functions being defined like: def my_tool(path=None, content=None):
                           # Or more simply, just passing positional args if schema matches order (less robust)

                           # Let's try passing the dictionary as keyword arguments
                           observation_content = tool_function(**tool_input_dict)

                        except TypeError as e:
                             print(f"🚨 Error: Input mismatch for {tool_name}. Input: {tool_input_dict}, Error: {e}")
                             observation_content = f"Error calling {tool_name}: Input mismatch or invalid argument. Provided input: {tool_input_dict}. Error: {e}"
                        except Exception as e:
                            print(f"🚨 Error executing tool {tool_name}: {e}")
                            observation_content = f"Error during execution of {tool_name}: {e}"

                    # Add the observation result back into the message history for the LLM
                    observation_message = {
                        "step": "observe",
                        "tool_name": tool_name,
                        "input": tool_input_dict,
                        "output": observation_content
                    }
                    # Use role: user for observations, as if the system/user is providing the tool result
                    # OR use role: tool (if using newer OpenAI models/APIs that support it)
                    # Let's stick to the example's pattern for now using 'assistant' role for simplicity,
                    # though 'tool' or 'user' might be semantically better.
                    messages.append({ "role": "assistant", "content": json.dumps(observation_message) })
                    print(f"👀 Observation: {observation_content}") # Show observation to user
                    continue # Let the LLM process the observation

                else:
                    print(f"🚨 Error: Tool '{tool_name}' not found.")
                    # Provide feedback to LLM
                    messages.append({"role": "user", "content": f"Error: The tool '{tool_name}' you specified is not available. Please choose from the available tools."})
                    continue

            elif step == "output":
                print(f"🤖 Agent: {content}")
                break # Exit the inner loop, wait for next user input

            else:
                print(f"🚨 Error: Unknown step type '{step}' received from LLM.")
                # Provide feedback to LLM
                messages.append({"role": "user", "content": f"Error: Unknown step type '{step}'. Please use 'plan', 'action', or 'output'."})
                # Decide whether to break or continue
                break # Safer to break and get new user input

        except Exception as e:
            print(f"🚨 An unexpected error occurred: {e}")
            # You might want to log the error and the messages list for debugging
            print("Messages so far:", json.dumps(messages, indent=2))
            break # Exit inner loop on critical error

print("🤖 Agent session finished.")