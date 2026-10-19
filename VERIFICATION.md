# VERIFICATION.md — How to check an LLM's claims about a binary

A procedure for checking what an LLM (or any analyst) says about a binary before
trusting it. The deliverable of LLM-assisted analysis is the verified claim, not the
summary.

Every claim gets sorted into one of three kinds, and each kind has its own check.

| Kind | What it is | How to check it |
|---|---|---|
| READ | Stated directly in the binary: an instruction, a constant, a string, a symbol | Look at the cited address in Ghidra |
| INFERRED | A conclusion about behavior, drawn from what's read | Run the binary with inputs that would expose it if wrong |
| INVENTED | A claim that nothing in the binary could confirm or refute | Recognize it, and replace it with UNKNOWN |

---

## 1. READ claims: confirm in Ghidra

A READ claim points at something concrete: "`SHL EAX,0x5` at 0010114d", "the constant
`0x3e8`", "the string at 00102004", "`clamp` is an exported symbol".

**Procedure**
1. Open the right program. Claims about a library function need the library, not the
   executable that calls it.
2. Press `G` (Go To), type the cited address, and press Enter.
3. Check the instruction: same mnemonic, same operands, same registers.
4. Check any constant: convert it (`0x3e8` = 1000; `0x1f` = 31; `0x3e000000` as a float =
   0.125). Confirm it's the operand the claim says it is.
5. Check strings and symbols: Window → Defined Strings, or the Symbol Tree, and confirm
   the name, address, and where it comes from (exported symbol vs. Ghidra's guess).
6. For a structural claim ("called only from main"), use right-click → Show References to.
7. When possible, confirm with a second tool in the container: `objdump -d -M intel`,
   `nm -D`, `readelf`, or `strings -t x`. Two tools agreeing is stronger than one.

**Result:** CONFIRMED (address and instruction match), WRONG ADDRESS (the instruction
exists but somewhere else), or NOT FOUND (no such instruction). NOT FOUND means the
evidence was fabricated, which triggers the stop rule (section 5).

**Examples from this project**
- "×31 is computed as `SHL 5` then `SUB`": confirmed at 0010114d–00101150 in libmathutils.so.
- "the bound is `0x3ff`": confirmed as the immediate passed to validate_reading.

---

## 2. INFERRED claims: a behavioral test

An INFERRED claim is about what the program *does*: "the upper bound is inclusive",
"the value is rounded to nearest", "long inputs give clamped=0". Reading can make it
likely; running the binary settles it.

**Procedure**
1. Write the claim as a prediction with a concrete input and expected output, *before*
   running anything.
2. Choose inputs that **discriminate**: inputs where the claim and its most plausible
   alternative give different results. Testing 500 doesn't tell inclusive from
   exclusive; testing exactly 1023 and 1024 does.
3. Run it in the container (`LD_LIBRARY_PATH=.` for dynamically linked targets).
4. Compare exit code and output to the prediction.
5. Encode it as a check in `verify.py`, so it becomes a permanent regression test.

**Examples from this project**
- `temp 404` → `...1f 1b` (51): proved the `+0.5` rounds to nearest, not truncation.
- `temp 1023` accepted, `temp 1024` rejected: proved the upper bound is inclusive.
- `temp abc` accepted as 0: found an input-validation gap that reading the code missed.
- `reverseengineering` → `clamped=0`: confirmed the signed/unsigned mismatch, and refuted
  the LLM's "most long strings hit 1000" in the same run.

---

## 3. INVENTED claims: recognize and replace

An INVENTED claim sounds informed but has no evidence behind it: intent, units,
purpose, the meaning of a constant, the author's reasons.

**The test:** ask, *what bytes in the binary would be different if this claim were
false?* If the answer is "none", the claim is invented.

| Claim | Bytes that would change if false? | Verdict |
|---|---|---|
| "The upper bound is 1023" | The `0x3ff` immediate | READ |
| "0 to 1023 is a 10-bit ADC reading" | None; the same code could clamp anything | INVENTED |
| "0.125 converts raw counts to degrees" | None; the binary contains only the number | INVENTED |
| "The XOR is there to hide data from casual inspection" | None; the binary shows *that* it XORs, not *why* | INVENTED |
| "The variable was named `acc` in the source" | None; stripped names leave no trace | INVENTED |

**What to write instead**
> UNKNOWN: not determinable from the binary. Would be settled by: [documentation /
> source code / the hardware / the program that reads this output].

An interpretation can still be worth recording, but label it as one:
> Interpretation (unverified): consistent with a 10-bit ADC; nothing in the binary
> confirms it.

---

## 4. Boundary-case checklist for behavioral tests

For every input the program takes, try each row that applies.

| Case | Example inputs | What it catches |
|---|---|---|
| Zero | `0` | Off-by-one at a lower bound, division by zero, empty loops |
| Negative | `-1`, `-2147483648` | Signed vs. unsigned handling, sentinel collisions (is -1 also an error code?) |
| Empty string | `""` | Missing length checks, zero-length loops |
| Max value | `2147483647`, `4294967295`, `99999999999` | Overflow, wraparound, atoi behavior past int range |
| Off-by-one at each limit | `lo-1`, `lo`, `hi`, `hi+1` (e.g. -1, 0, 1023, 1024) | Inclusive vs. exclusive bounds |
| Malformed | `abc`, `12abc`, ` 5`, `+5`, `0x10`, `1.5` | Parser leniency: atoi stops at the first non-digit and returns 0 for none |
| Too few / too many args | (none), extra args | Argument-count checks, ignored extras |
| Long input | A label longer than any buffer (e.g. 100 characters) | Truncation, buffer over-read or overflow, length mismatches |

**A case worth testing next on sensor_stripped:** `encode_record` limits its XOR loop to
the buffer size (64), but returns snprintf's full length. `main` then prints that many
bytes from a 64-byte buffer. A 100-character label should report more bytes than the
buffer holds. That's an INFERRED claim with a clear prediction, so test it before
believing it.

---

## 5. Stop rule: when to reject an answer and go manual

Discard the **whole** LLM answer, not just the bad line, and analyze by hand when any of
these happen:

1. **Fabricated evidence.** A cited address doesn't contain the cited instruction
   (NOT FOUND in section 1). If one citation is invented, none of them can be trusted.
2. **A high-confidence claim fails verification.** Being wrong at "low" is acceptable;
   being wrong at "high" means the confidence labels carry no information.
3. **Two or more claims in one answer fail.**
4. **Internal contradiction.** The answer argues against itself, as in Week 7 Day 1,
   where the wraparound reasoning refuted "most long strings hit 1000".
5. **READ claims with no citations**, or claims based only on what a function's name
   suggests.
6. **Claims about code that wasn't analyzed**, such as describing an external function's
   behavior without opening the library that contains it.

After stopping: note what failed in the log, check whether the prompt allowed it (and
revise `prompts.md` if so, with a version bump), and redo the analysis manually.

---

## Recording a verification

Add one row per claim to the log:

| # | Claim | Kind | Check performed | Result | Confidence the model gave |
|---|---|---|---|---|---|
| 1 | ×31 via SHL/SUB | READ | Go to 0010114d | CONFIRMED | high |
| 2 | Upper bound inclusive | INFERRED | verify.py "upper bound inclusive" | PASS | high |
| 3 | 0–1023 is a 10-bit ADC | INVENTED | Byte test: no bytes would change | Replaced with UNKNOWN | medium |

---

## 6. Worked examples: five claims from the Day 2 sweep

Claims taken from `LLM-assisted_ghidra.md` (all runs: prompts v1.0 + uncertainty modifier
v1.0). Two READ, two INFERRED, one INVENTED. One fails.

| # | Claim (source in Day 2 results) | Category | Verification performed | Verdict |
|---|---|---|---|---|
| 1 | "Each iteration multiplies the accumulator by 31 (`acc<<5 - acc`)": `SHL EAX,0x5` at 0010114d, `SUB EAX,EDX` at 00101150 (checksum, Prompt 1, claim 3, high) | READ | Ghidra, libmathutils.so: `G` → 0010114d. Bytes `c1 e0 05` = `SHL EAX,0x5`; 00101150 bytes `29 d0` = `SUB EAX,EDX`. No `IMUL` anywhere in 00101129–0010117c | **PASS** |
| 2 | "The comparisons are signed": `JGE` at 00101110, `JLE` at 0010111d (clamp, Prompt 1, claim 4, high) | READ | Ghidra, libmathutils.so: `G` → 00101110, bytes `7d 05` = `JGE`; `G` → 0010111d, bytes `7e 05` = `JLE`. Both are signed conditions (unsigned would be `JAE`/`JBE`) | **PASS** |
| 3 | checksum computes `acc = acc*31 + (unsigned char)buf[i]`, kept to 32 bits (checksum, Prompt 1, purpose and claims 3–5, high) | INFERRED | `verify.py` check "checksum formula": runs `app_stripped hello` and compares the printed checksum to a Python implementation of the claimed formula (99162322) | **PASS** |
| 4 | "A checksum of 0x80000000 or more is treated as negative and returns param_2 (0 at that call site)" (clamp, Prompt 2, signedness note) | INFERRED | `verify.py` check "signed/unsigned wraparound": `app_stripped reverseengineering` must print a checksum ≥ 2^31 with `clamped=0`. Discriminating input: a checksum above 2^31, where signed and unsigned comparison disagree | **PASS** (checksum=4046928625, clamped=0) |
| 5 | checksum's return type is `int` (checksum, Prompt 2, return value, **high**) | INVENTED | Byte test: inside checksum, the result is only loaded and returned (`MOV EAX,[RBP-0x8]` at 00101178, `RET` at 0010117c). Nothing in checksum's bytes would differ if it returned `unsigned int`. The only evidence about signedness is outside this binary, and it points the other way: app_stripped prints the value with `%u` (format at 00102018), and test 4 shows it printed as 4046928625. Source: `unsigned int` | **FAIL** |

### Notes on each

**1 and 2 (READ).** Both confirmed at the exact cited addresses, with matching bytes.
These are the easiest claims to check and the least informative: they restate the
listing. Their value is that they ground the inferred claims built on them.

**3 and 4 (INFERRED).** Both now live in `verify.py` as permanent tests. Claim 4 needed a
discriminating input: short strings like `abc` give the same `clamped=1000` whether clamp
compares signed or unsigned, so they can't tell the two apart. Only a checksum above 2^31
separates them.

**5 (INVENTED, stated at high confidence).** This is the failure. The model reported a
width it could read (32 bits) plus a signedness it could not, and rated the whole claim
high. It also had the contrary evidence available: in the clamp run it used app_stripped's
`%u` to reason about signedness, but never connected that back to checksum's return type.
What it should have written instead:
> Return: 32-bit value in EAX (high). Signedness: UNKNOWN from libmathutils.so; the caller
> in app_stripped prints it with `%u`, which suggests unsigned.

Under the stop rule (section 5, trigger 2), a high-confidence claim failing means that
answer's confidence labels can't be trusted, so the checksum Prompt 2 run should be redone
by hand.

**Bonus INVENTED claim, right by coincidence.** The same run typed the first parameter
`const unsigned char *` (high), reasoning that the buffer is only read. The source does say
`const`, but the byte test fails: a non-`const` parameter that is never written compiles to
the same bytes. Being right here was luck, not evidence. It should read: "pointer to
unsigned bytes, read-only in this function; `const` qualifier not determinable."
