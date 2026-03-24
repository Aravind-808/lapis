from config import DANGEROUS_KEYWORDS
from tools import TOOLS

def is_risky(args):
    return any(kw in str(args).lower() for kw in DANGEROUS_KEYWORDS)


def confirm_risky(name, args):
    print(f"Risky command detected in {name}({args})")
    return input("Allow? (y/n): ").strip().lower() == "y"


def deploy_tool(name, args):
    if name not in TOOLS:
        return f"Error: unknown tool '{name}'"
    if is_risky(args):
        if not confirm_risky(name, args):
            return "User denied this action."
    result = TOOLS[name](**args)
    print(f"→ {result}\n")
    return result