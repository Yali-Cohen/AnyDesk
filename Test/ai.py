from google import genai
import os
import json
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

session_goal = "Open youtube only"
memory = ""

client = genai.Client(api_key=os.getenv("API_KEY"))


def ask_gemini():
    path = os.path.dirname(__file__)
    prompt_path = os.path.join(path, "prompt.txt")

    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    prompt = prompt_template.replace("{session_goal}", session_goal)
    prompt = prompt.replace("{memory_summary}", memory)

    image = Image.open(os.path.join(path, "test.png"))

    response = client.models.generate_content(
        model="gemini-2.5-flash",   
        contents=[prompt, image]
    )

    return response.text


print(ask_gemini())