import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client with API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Create streaming chat completion
completion = client.chat.completions.create(
    model="qwen-2.5-32b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the concept of attention in transformers."}
    ],
    temperature=0.6,
    max_tokens=1024,
    top_p=0.95,
    stream=True,
)

# Stream output
for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
