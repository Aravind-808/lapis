import json
import re

def extract_tool_calls(text):
    calls = []

    if not text:
        return calls

    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    content = match.group(1) if match else text

    content = re.sub(
        r'"""(.*?)"""',
        lambda m: json.dumps(m.group(1)),
        content,
        flags=re.DOTALL
    )

    content = content.replace("\\\"", "'")
    content = re.sub(r'\\+"', '"', content)

    try:
        data = json.loads(content)
        if isinstance(data, dict) and "name" in data and "arguments" in data:
            return [(data["name"], data["arguments"])]
        elif isinstance(data, list):
            for obj in data:
                if isinstance(obj, dict) and "name" in obj and "arguments" in obj:
                    calls.append((obj["name"], obj["arguments"]))
            if calls:
                return calls
    except:
        pass

    decoder = json.JSONDecoder()
    idx = 0

    while idx < len(content):
        try:
            obj, end = decoder.raw_decode(content[idx:])
            idx += end

            if isinstance(obj, dict) and "name" in obj and "arguments" in obj:
                calls.append((obj["name"], obj["arguments"]))

        except json.JSONDecodeError:
            idx += 1

    return calls