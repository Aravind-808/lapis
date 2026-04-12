import os
from config import OLLAMA_API_KEY
os.environ["OLLAMA_API_KEY"] = OLLAMA_API_KEY

import ollama
from ollama import web_fetch, web_search
from config import MODEL, SYSPROMPT, DANGEROUS_KEYWORDS
from config import TOOLS
from utilities import deploy_tool, extract_tool_calls

import threading
import itertools
import time
from rich.console import Console
from rich.markdown import Markdown

console = Console()
CTX_LIMIT = 15000

SPINNER_PHRASES = [
    "cooking up a response...",
    "thinking hard...",
    "giving you the best answer...",
    "on it...",
    "brewing something good...",
    "connecting the dots...",
    "working my magic...",
    "almost there...",
]

SPINNER_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

def run_spinner(stop_event):
    phrase_cycle = itertools.cycle(SPINNER_PHRASES)
    char_cycle = itertools.cycle(SPINNER_CHARS)
    phrase = next(phrase_cycle)
    phrase_timer = time.time()
    while not stop_event.is_set():
        if time.time() - phrase_timer > 3:
            phrase = next(phrase_cycle)
            phrase_timer = time.time()
        char = next(char_cycle)
        line = f"{char} {phrase}"
        print(f"\r{line:<50}", end="", flush=True)  
        time.sleep(0.1)
    print("\r" + " " * 50 + "\r", end="", flush=True)


def chat_with_spinner(messages, tools, options, keep_alive):
    result = [None]
    error = [None]
    def target():
        try:
            result[0] = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=tools,
                options=options,
                keep_alive=keep_alive,
            )
        except Exception as e:
            error[0] = e

    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=run_spinner, args=(stop_event,), daemon=True)
    spinner_thread.start()

    t = threading.Thread(target=target)
    t.start()
    t.join()

    stop_event.set()
    spinner_thread.join()

    if error[0]:
        raise error[0]
    return result[0]


def run_agent(task: str):

    messages = [
        {"role": "system", "content": SYSPROMPT},
        {"role": "user", "content": f"/no_think {task}"}
    ]

    while True:
        response = chat_with_spinner(
            messages=messages,
            tools=list(TOOLS.values()) + [web_search, web_fetch],
            options={"num_predict": 2048, "think": False, "num_ctx": 4096},
            keep_alive="2m",
        )

        msg = response.message
        messages.append(msg)

        if msg.tool_calls:
            for call in msg.tool_calls:
                name = call.function.name
                args = call.function.arguments
                args_str = str(args).lower()
                is_risky = any(kw in args_str for kw in DANGEROUS_KEYWORDS)
                console.print(f"[dim]⚙ {name}({args})[/dim]")
                if is_risky:
                    print("Risky command detected — confirm required")
                    confirm = input("   Allow? (y/n): ").strip().lower()
                    if confirm != "y":
                        messages.append({"role": "tool", "content": "User denied this action."})
                        continue
                result = deploy_tool(name, args)
                messages.append({"role": "tool", "content": result})

        else:
            calls = extract_tool_calls(msg.content or "")
            if calls:
                for name, args in calls:
                    console.print(f"[dim]⚙ [FAKE] {name}({args})[/dim]")
                    args_str = str(args).lower()
                    is_risky = any(kw in args_str for kw in DANGEROUS_KEYWORDS)
                    if is_risky:
                        print("Risky command detected — confirm required")
                        confirm = input("   Allow? (y/n): ").strip().lower()
                        if confirm != "y":
                            messages.append({"role": "tool", "content": "User denied this action."})
                            continue
                    result = deploy_tool(name, args)
                    messages.append({"role": "tool", "content": result})
                continue
            console.print(Markdown(msg.content))
            break

    ollama.chat(model=MODEL, messages=[], keep_alive=0)


def run_agent_multiturn() -> None:
    messages = [
        {"role": "system", "content": SYSPROMPT},
    ]

    total_in = 0
    total_out = 0

    print("what we doin?? type 'exit' to quit, 'clear' to reset conversation, 'usage' to see token count.\n")

    while True:
        try:
            task = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not task:
            continue
        if task.lower() in ("exit", "quit", "q"):
            print("bye")
            break
        if task.lower() == "clear":
            messages = [{"role": "system", "content": SYSPROMPT}]
            total_in = 0
            total_out = 0
            print("Conversation cleared.\n")
            continue
        if task.lower() == "usage":
            print(f"Tokens so far: {total_in} in / {total_out} out\n")
            continue

        messages.append({"role": "user", "content": f"/no_think {task}"})

        while True:
            response = chat_with_spinner(
                messages=messages,
                tools=list(TOOLS.values()) + [web_search, web_fetch],
                options={"num_predict": 2048, "think": False, "num_ctx": 15000},
                keep_alive="10m",
            )

            msg = response.message
            total_in = response.prompt_eval_count or total_in
            total_out += response.eval_count or 0
            messages.append(msg)

            if total_in >= CTX_LIMIT:
                print("Context limit reached. Type 'clear' to start a new session.\n")
                break

            if msg.tool_calls:
                for call in msg.tool_calls:
                    console.print(f"[dim]⚙ {call.function.name}({call.function.arguments})[/dim]")
                    result = deploy_tool(call.function.name, call.function.arguments)
                    messages.append({"role": "tool", "content": result})
                continue

            fake_calls = extract_tool_calls(msg.content or "")
            if fake_calls:
                for name, args in fake_calls:
                    console.print(f"[dim]⚙ [FAKE] {name}({args})[/dim]")
                    result = deploy_tool(name, args)
                    messages.append({"role": "tool", "content": result})
                continue

            console.print(Markdown(msg.content))
            print()
            break

    ollama.chat(model=MODEL, messages=[], keep_alive=0)
    print(f"Total tokens: {total_in} in / {total_out} out")