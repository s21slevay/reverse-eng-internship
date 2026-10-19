# prompts.md — Structured prompts for LLM-assisted reverse engineering

Reusable prompts for Claude Code + GhidraMCP. Replace `{PROGRAM}`, `{FUNCTION}`, and
`{START}` before use. Every prompt fixes the output format so answers can be checked
line by line against the binary, the same lesson as Week 4's JSON-validity experiment
(0% -> 90% -> 100% as structure and constraints were added).

This is a living document, like LOG.md. When a prompt produces a bad answer, fix the
prompt here, bump its version, and record what changed and why in the revision log
below. Git keeps every earlier version (`git log -p prompts.md`), so any result in
LOG.md can be traced back to the exact prompt that produced it. When logging a result,
note the prompt and version used, e.g. "Prompt 1 v1.0 + modifier v1.0".

## Revision log

| Date | Prompt | Version | Change | Why (evidence that prompted it) |
|---|---|---|---|---|
| 2026-10-13 | All | 1.0 | Initial set: summary, signature, naming, data flow, uncertainty modifier | Week 7 Day 2 |

## Shared rules (paste at the top of every prompt)

```
Use only the GhidraMCP tools to inspect {PROGRAM}. Base every claim on what the tools
return: the decompilation, the listing, cross-references, strings, or symbols. Do not
rely on what a function's name suggests unless you cite where the name comes from
(e.g. an exported symbol). Cite instruction addresses as 8-digit hex (e.g. 001011a9).

Confidence levels, used wherever a confidence column appears:
- high: directly visible in the listing or decompilation at the cited address
- medium: inferred from strong indirect evidence (e.g. a format string, a register width)
- low: plausible but weakly supported
```

---

## 1. Function summary (v1.0)

```
Analyze {FUNCTION} in {PROGRAM}. Return exactly these four sections and nothing else.

### Purpose
One or two sentences.

### Inputs
| Parameter | Meaning | Evidence (address or source) | Confidence |
|---|---|---|---|

### Outputs
| Output (return value, written memory, printed text, exit code) | Meaning | Evidence | Confidence |
|---|---|---|---|

### Claims
| # | Claim | Evidence (address or source) | Confidence |
|---|---|---|---|

Example row for Claims:
| 1 | Returns -1 when the value is out of range | MOV EAX,0xffffffff at 00101115 | high |
```

## 2. Signature recovery (v1.0)

```
Recover the signature of {FUNCTION} in {PROGRAM} using the System V x86-64 calling
convention. Examine both the function's prologue and at least one call site (find call
sites with cross-references). Return exactly:

### Proposed signature
A single C prototype line.

### Parameters
| Position | Register | Width (bits) | Proposed type | Evidence: instruction(s) and address(es) | Confidence |
|---|---|---|---|---|---|

### Return value
| Register | Width | Proposed type | Evidence: instruction and address | Confidence |
|---|---|---|---|---|

### Disagreements with Ghidra
List any place where your proposed type differs from Ghidra's guess, and why.
Write "None" if there are none.
```

## 3. Variable naming (v1.0)

```
Propose meaningful names for every parameter and local variable in {FUNCTION} in
{PROGRAM}. Do not rename anything in Ghidra; only propose. Return exactly:

| Current name | Proposed name | Evidence: how it is used, with address(es) | Confidence |
|---|---|---|---|

Rules:
- Every proposed name must be justified by how the variable is used (what writes it,
  what reads it, what it is passed to), not by what would be conventional.
- If a variable is a compiler temporary with no clear meaning, say so instead of
  inventing a name.
- Prefer names a colleague could verify from the cited addresses.
```

## 4. Data flow (v1.0)

```
Trace {START} through {PROGRAM}, from where it first enters to every place it is
used or output, including across library calls. Return exactly:

### Trace
| Step | Address | Instruction or call | Where the value is (register / stack slot / memory) | What happens to it |
|---|---|---|---|---|

### Boundary crossings
For each call into another function or library: the call address, the stub or target,
which register carries the value in, and which register carries the result out.

### Final destination
Where the value (or anything derived from it) ends up: printed, returned, stored.
```

## 5. Uncertainty modifier (v1.0)

Append this block to any prompt above.

```
Calibration rule: if something cannot be determined from the binary itself, write
UNKNOWN in that cell rather than guessing. This includes intent, units, the meaning of
constants, what an external caller passes in, and anything only documentation or source
code would settle. For every UNKNOWN, add one line under a final "### What would settle
it" section naming the evidence that would resolve it. An honest UNKNOWN is better than
a confident guess.
```

---

## Experiment: does asking for calibration produce it?

**Setup.** Run prompt 1 (function summary) twice on the same function, once without and
once with the uncertainty modifier. Use a function with a known answer key so every claim
can be scored: `main` (FUN_00101229) in sensor_stripped, or `encode_record` in
libsensorlog.so, both fully analyzed and behaviorally verified in Week 6.

**Prediction (write this before running anything):**
- Without the modifier, the model will ...
- With the modifier, the model will ...
- The claims most likely to be marked UNKNOWN (or wrongly stated as fact) are ...
- How I'll measure it: ...

**Results:**

| | Without modifier | With modifier |
|---|---|---|
| Total claims | | |
| Claims marked high confidence | | |
| Claims marked UNKNOWN | | |
| Wrong claims (checked against Week 6 evidence) | | |
| Wrong claims stated at high confidence | | |

**Interpretation:** did asking for calibration change what the model claimed, only how it
labeled its claims, or neither?
