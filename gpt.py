from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
base_url = os.getenv("NVIDIA_API_BASE_URL")
api_key = os.getenv("NVIDIA_API_KEY")
model = os.getenv("NVIDIA_API_MODEL")

client = OpenAI(
  base_url = base_url,
  api_key = api_key
)

completion = client.chat.completions.create(
  model=model,
  messages=[{"role":"user","content":""}],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")

