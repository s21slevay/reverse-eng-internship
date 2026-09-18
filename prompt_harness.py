# prompt_harness.py — measure prompt reliability instead of guessing.
import json, requests

MODEL = "phi4"  # whatever you ran in Week 2


def chat_once(system, user, force_json=False):
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if force_json:
        payload["format"] = "json"  # Ollama's JSON mode: constrains output to valid JSON
    r = requests.post("http://localhost:11434/api/chat", json=payload)
    return r.json()["message"]["content"]


def json_validity_rate(system, user, n=10, force_json=False):
    """Run the same prompt n times; return the fraction of replies that json.loads cleanly."""
    successes = 0 
    # TODO 1: call chat_once n times
    for _ in range(n):
        reply = chat_once(system, user, force_json=force_json)
        # TODO 2: for each reply, try json.loads(reply); count successes (try/except)
        try: 
            json.loads(reply)
            successes += 1
        except json.JSONDecodeError: 
            pass
    # TODO 3: return successes / n
    return successes / n

if __name__ == "__main__":
    USER = "What is the capital of France?"
    SYSTEM_A = "Answer the user's question."
    SYSTEM_B = (
        'Reply with EXACTLY one JSON object and nothing else, in this form: '
        '{"answer": "", "confidence": "low|medium|high"}'
    )

    # A) SYSTEM_A, force_json=False (baseline)
    print("Condition A (no json mode, the general baseline):")
    print(f"  {json_validity_rate(SYSTEM_A, USER, n=10, force_json=False):.0%}\n")

    # B) SYSTEM_B, force_json=False (strict instructions alone)
    print("Condition B (instructions but JSON mode off):")
    print(f"  {json_validity_rate(SYSTEM_B, USER, n=10, force_json=False):.0%}\n")

    # C) SYSTEM_B, force_json=True (instructions + JSON mode)
    print("Condition C (explicit instructions and JSON mode on):")
    print(f"  {json_validity_rate(SYSTEM_B, USER, n=10, force_json=True):.0%}\n")
    