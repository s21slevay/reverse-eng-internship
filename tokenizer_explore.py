# tokenizer_explore.py — watch text get chopped into tokens.
# This uses one common tokenizer for illustration; every model has its own,
# but the *idea* (text -> pieces -> integer IDs) is universal.

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

texts = [
    "Reverse engineering",
    "reverseengineering",  # no space — watch it split differently
    "aerodynamics",
    "antidisestablishmentarianism",  # rare word — splits into many pieces
    "printf(\"hello\\n\");",  # code tokenizes too
    "Maryland Engineering",
    "ClarkSchool Engineering Aerospace 2026",
    "Lamar Jackson 8", #testing out some numbers as well
    "supercalifragilisticexpialidocious",  # a very long, unusual word
    "🚀",  # a single emoji
    "mov eax, ebx\nadd eax, 4\njmp label",  # a line of assembly
]

for t in texts:
    ids = enc.encode(t)
    pieces = [enc.decode([i]) for i in ids]  # turn each id back into its text piece
    print(f"\n{t!r}")
    print(f"  {len(ids)} tokens -> {ids}")
    print(f"  pieces -> {pieces}")