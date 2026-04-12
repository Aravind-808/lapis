from config import DANGEROUS_KEYWORDS
from config import TOOLS
from ollama import web_fetch, web_search

BUILTIN_TOOLS = {
    "web_search": web_search,
    "web_fetch": web_fetch,
}

def is_risky(args):
    return any(kw in str(args).lower() for kw in DANGEROUS_KEYWORDS)


def confirm_risky(name, args):
    print(f"Risky command detected in {name}({args})")
    return input("Allow? (y/n): ").strip().lower() == "y"


def deploy_tool(name, args):
    if name in BUILTIN_TOOLS:
        try:
            result = BUILTIN_TOOLS[name](**args)
            return str(result)[:3000]
        except Exception as e:
            return f"Error using {name}: {str(e)}"
    if name not in TOOLS:
        return f"Error: unknown tool '{name}'"
    if is_risky(args):
        if not confirm_risky(name, args):
            return "User denied this action."
    result = TOOLS[name](**args)
    return result