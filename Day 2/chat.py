from dotenv import load_dotenv
import os
from together import Together

# Load environment variables from .env
load_dotenv()

# Get the API key
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize the Together client with API key
client = Together(api_key=api_key)

# Run your completion
response = client.chat.completions.create(
    model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    messages=[
        {"role": "user", "content": "what is life"}
    ]
)

# Print the result
print(response.choices[0].message.content)
