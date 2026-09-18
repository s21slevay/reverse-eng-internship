# agent.py — a tiny tool-using agent around your local model.
import json, requests
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
MODEL = "phi4"
SYSTEM = """You can use tools. Available tools:
 calculator: evaluates an arithmetic expression. args: {"expression": "<string>"}
 read_file: returns the first ~2000 characters of a file. args: {"path": "<string>"} (relative to the project directory)
 list_dir: lists the contents of a directory. args: {"path": "<string>"} (relative to the project directory)
 Reply with EXACTLY one JSON object and nothing else, in one of these two forms:
 {"action": "tool", "tool": "<tool name>", "args": {...}}
 {"action": "final", "answer": "<your answer to the user>"}
 After a tool runs, you will receive its result as a message starting with TOOL RESULT.
 """
def chat(messages):
    r = requests.post("http://localhost:11434/api/chat", json={"model": MODEL, "messages": messages, "stream": False, "format": "json"})
    return r.json()["message"]["content"]

def calculator(args):
    # A restricted eval: no builtins available to the expression.
    # (Real systems never eval model output like this — fine for a local toy,
    # and worth remembering when you see agents given real shells later.)
    return str(eval(args["expression"], {"__builtins__": {}}, {}))

def _resolve_safe_path(path):
    """Resolve a path and confirm it's inside PROJECT_ROOT. Raises ValueError if not."""
    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if not full_path.startswith(PROJECT_ROOT):
        raise ValueError(f"Path '{path}' is outside the allowed project directory.")
    return full_path


def read_file(args):
    try:
        full_path = _resolve_safe_path(args["path"])
        with open(full_path, "r") as f:
            content = f.read(2000)
        return content
    except ValueError as e:
        return f"ERROR: {e}"
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        return f"ERROR: {e}"


def list_dir(args):
    try:
        full_path = _resolve_safe_path(args["path"])
        entries = os.listdir(full_path)
        return json.dumps(entries)
    except ValueError as e:
        return f"ERROR: {e}"
    except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
        return f"ERROR: {e}"

TOOLS = {"calculator": calculator, "read_file": read_file, "list_dir": list_dir}

def run(user_question, chat_fn=chat, max_steps=5):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_question}]
    for _ in range(max_steps):
        reply = chat_fn(messages)
        messages.append({"role": "assistant", "content": reply})

        try:
            action = json.loads(reply)
        except json.JSONDecodeError:
            messages.append({"role": "user", "content": "Your reply was not valid JSON. Follow the format exactly."})
            continue

        if action["action"] == "final":
            return (action["answer"], messages)

        if action["action"] == "tool":
            tool_name = action["tool"]
            if tool_name in TOOLS:
                result = TOOLS[tool_name](action["args"])
                messages.append({"role": "user", "content": f"TOOL RESULT: {result}"})
            else:
                messages.append({"role": "user", "content": f"ERROR: no tool named {tool_name}"})
            continue

        messages.append({"role": "user", "content": "Please respond with either a 'tool' action or a 'final' action, as instructed."})

    return "(gave up after max_steps)", messages

if __name__ == "__main__":
    answer, history = run("List the files in the current directory, then read attention.py and tell me what the softmax function does.")
    print(answer)
    print("\n--- Full conversation ---")
    for msg in history:
        print(f"[{msg['role']}]: {msg['content'][:200]}\n")  # truncate for readability

    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    full_text = "\n".join(m["content"] for m in history)
    print(f"\nTotal history token count: {len(enc.encode(full_text))}")