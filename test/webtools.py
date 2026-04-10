'''
test for web search feature
'''

import os
from dotenv import load_dotenv

load_dotenv()
OLLAMA_API_KEY = os.getenv("OLLAMA_API")
os.environ["OLLAMA_API_KEY"] = OLLAMA_API_KEY

from ollama import chat, web_search, web_fetch
from config.constants import MODEL

MODEL = MODEL
available_tools = {"web_search": web_search, "web_fetch": web_fetch}

def run(query):
    print(f"\nQuery: {query}")
    print("-" * 50)
    messages = [{"role": "user", "content": f"/no_think {query}"}] # udont need /no_think for instruct models

    while True:
        response = chat(
            model=MODEL,
            messages=messages,
            tools=[web_search, web_fetch],
            options={"num_predict": 1024, "think": False, "num_ctx": 4096},
        )

        msg = response.message
        messages.append(msg)

        if msg.tool_calls:
            for call in msg.tool_calls:
                name = call.function.name
                args = call.function.arguments
                print(f"[tool] {name}({args})")
                result = available_tools[name](**args)
                print(f"[result] {str(result)[:300]}...\n")
                messages.append({
                    "role": "tool",
                    "content": str(result)[:3000],
                    "tool_name": name,
                })
        else:
            print(f"Answer:\n{msg.content}")
            break

if __name__ == "__main__":
    run("what is leetcode problem 254? web search and give me the description")