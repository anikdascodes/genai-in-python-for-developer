from dotenv import load_dotenv
import os

from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key = )


response = client.models.generate_content(
    model="gemini-2.0-flash", contents= 'why is sky blue?'
)
print(response.text)