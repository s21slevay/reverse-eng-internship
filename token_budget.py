# token_budget.py — counting tokens across realistic-sized inputs to build
# intuition for what a "context window" actually costs.
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


# 1. A short question — the kind of thing you'd type in a single chat turn
short_question = "How do I fix an off-by-one error in this loop?"

# 2. A long pasted file — paste in something real: a chunk of your own code.
#    Read a real file from your project so this reflects an actual realistic size.
with open("attention.py") as f:
    long_file = f.read()

# 3. A 20-message conversation history — simulate one, since you don't have
#    20 real chat turns sitting in a variable. Roughly realistic message lengths.
conversation_history = "\n".join([
    f"User: message {i} — some realistic back-and-forth about a coding problem, "
    f"with enough detail to be a normal chat turn rather than a one-liner."
    if i % 2 == 0 else
    f"Assistant: response {i} — explaining the fix, showing a code snippet, "
    f"and asking a clarifying follow-up question."
    for i in range(20)
])

print(f"Short question: {count_tokens(short_question)} tokens")
print(f"Long pasted file (attention.py): {count_tokens(long_file)} tokens")
print(f"20-message conversation history: {count_tokens(conversation_history)} tokens")