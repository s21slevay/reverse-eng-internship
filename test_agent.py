# test_agent.py — test the loop with a scripted fake model. No Ollama required.
from agent import run

script = [
    'not json at all',  # malformed
    '{"action": "tool", "tool": "calculator", "args": {"expression": "17*23"}}',
    '{"action": "tool", "tool": "nonexistent", "args": {}}',  # bad tool name
    '{"action": "final", "answer": "17*23 = 391"}',
]


def make_fake_chat():
    calls = {"i": 0}

    def fake_chat(messages):
        reply = script[calls["i"]]
        calls["i"] += 1
        return reply

    return fake_chat


def test_full_run_handles_everything():
    answer, msgs = run("what is 17*23?", chat_fn=make_fake_chat())
    assert answer == "17*23 = 391"

    user_msgs = [m["content"] for m in msgs if m["role"] == "user"]
    assert any("not valid JSON" in c for c in user_msgs)     # malformed reply was caught
    assert any("TOOL RESULT: 391" in c for c in user_msgs)   # tool actually ran
    assert any("no tool named" in c for c in user_msgs)      # bad tool name handled