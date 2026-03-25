import ollama
from constants import MODEL, SYSPROMPT, DANGEROUS_KEYWORDS
from parser import extract_tool_calls
from toolconfig import TOOLS
from utils import deploy_tool

CTX_LIMIT = 7500
def run_agent(task: str):

    messages = [
        {"role": "system", "content": SYSPROMPT},
        {"role": "user", "content":f"/no_think {task}" }
    ]

    while True:
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=list(TOOLS.values()),
            options={"num_predict": 2048, "think":False, "num_ctx": 4096},
            keep_alive="2m",  # unload after 2 mins of inactivity
        )

        msg = response.message
        # print(f"DEBUG tool_calls: {msg.tool_calls}")
        # print(f"DEBUG content: {msg.content}")
        # print(f"DEBUG stop_reason: {response.done_reason}")
        messages.append(msg)

        if msg.tool_calls:
            for call in msg.tool_calls:
                name = call.function.name
                args = call.function.arguments

                # safety check
                args_str = str(args).lower()
                is_risky = any(kw in args_str for kw in DANGEROUS_KEYWORDS)

                print(f"Tool: {name}({args})")

                if is_risky:
                    print("Risky command detected — confirm required")
                    confirm = input("   Allow? (y/n): ").strip().lower()
                    if confirm != "y":
                        messages.append({"role": "tool", "content": "User denied this action."})
                        continue

                result = TOOLS[name](**args)
                print(f"{result}\n")
                messages.append({"role": "tool", "content": result})

        else:
            calls = extract_tool_calls(msg.content or "")

            if calls:
                for name, args in calls:
                    print(f"[FAKE TOOL CALL] {name}({args})")

                    # safety check (same as above)
                    args_str = str(args).lower()
                    is_risky = any(kw in args_str for kw in DANGEROUS_KEYWORDS)

                    if is_risky:
                        print("Risky command detected — confirm required")
                        confirm = input("   Allow? (y/n): ").strip().lower()
                        if confirm != "y":
                            messages.append({"role": "tool", "content": "User denied this action."})
                            continue

                    result = TOOLS[name](**args)
                    print(f"{result}\n")

                    messages.append({
                        "role": "tool",
                        "content": result
                    })

                continue 
            print(f"Done: {msg.content}")
            break

    # unload model from VRAM when done
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
            response = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=list(TOOLS.values()),
                options={"num_predict": 2048, "think": False, "num_ctx": 8192},
                keep_alive="10m",
            )

            msg = response.message
            total_in = response.prompt_eval_count
            total_out += response.eval_count

            # print(f"DEBUG tool_calls : {msg.tool_calls}")
            # print(f"DEBUG stop_reason: {response.done_reason}")
            messages.append(msg)

            if response.prompt_eval_count >= CTX_LIMIT:
                print("Context limit reached. Type 'clear' to start a new session.\n")
                break

            if msg.tool_calls:
                for call in msg.tool_calls:
                    result = deploy_tool(call.function.name, call.function.arguments)
                    messages.append({"role": "tool", "content": result})
                continue

            fake_calls = extract_tool_calls(msg.content or "")
            if fake_calls:
                for name, args in fake_calls:
                    print(f"[FAKE TOOL CALL] {name}({args})")
                    result = deploy_tool(name, args)
                    messages.append({"role": "tool", "content": result})
                continue

            print(f"agent: {msg.content}\n")
            break

    ollama.chat(model=MODEL, messages=[], keep_alive=0)
    print(f"Total tokens: {total_in} in / {total_out} out")


# if __name__ == "__main__":
#     run_agent_cli()