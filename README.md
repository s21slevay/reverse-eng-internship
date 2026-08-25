# AI-Assisted Reverse Engineering Internship

An 8-week, self-paced internship building toward LLM-assisted reverse engineering of unknown
Linux binaries — connecting a large language model to Ghidra via the Model Context Protocol
(MCP) to accelerate binary analysis. This repo tracks my work as I go.

**Status:** In progress (Week 3 of 8)

## What's in here

### Environment & engineering hygiene (Week 1)
- Reproducible Python environment managed with [`uv`](https://docs.astral.sh/uv/)
- A version-controlled Docker-based Linux lab (`lab/Dockerfile`) with `gcc`, `gdb`, `binutils`,
  `file`, and `xxd` — built once, launched anywhere, identically
- Git/GitHub workflow with a real commit history

### LLM internals, from the math up (Weeks 2–3)
- `tokenizer_explore.py` — hands-on exploration of subword tokenization using `tiktoken`
- `attention.py` — scaled dot-product attention implemented from scratch in NumPy: stable
  softmax, QKV projections, `√dk` scaling (empirically verified against its theoretical
  variance justification), causal masking, and a batched (einsum-based) variant
- `multihead.py` — multi-head attention: splitting Q/K/V into parallel subspaces, attending
  independently, concatenating, and re-projecting
- `positional_encoding.py` — sinusoidal positional encoding, verified to break attention's
  permutation invariance as intended
- Local open-weights model (`phi4` via Ollama) run and compared against a frontier model
  (Claude) on reasoning and up-to-date-knowledge tasks
- All core implementations covered by `pytest`

## Setup

```bash
uv sync
uv run pytest -v
```

## What's coming

Weeks 4–8 move into agentic development with Claude Code, C/ELF/x86-64 fundamentals, Ghidra-based
static and dynamic analysis, and finally wiring an LLM into Ghidra via MCP to analyze a
previously-unseen binary — the capstone project.test
