# LLM-assisted Ghidra analysis

Results of running the prompts in `prompts.md` with Claude Code + GhidraMCP. Each run
records the program, function, prompt and version used, so every answer can be traced
back to the exact prompt that produced it. New runs are appended as new sections.

## Run index

| Date | Program | Function | Prompt + version | Modifier | Section |
|---|---|---|---|---|---|
| 2026-10-19 | app_stripped | FUN_001011a9 | Prompt 1 v1.0 (function summary) | Uncertainty modifier v1.0 | [Prompt 1](#prompt-1--function-summary-v10) |
| 2026-10-19 | app_stripped | FUN_001011a9 | Prompt 2 v1.0 (signature recovery) | Uncertainty modifier v1.0 | [Prompt 2](#prompt-2--signature-recovery-v10) |
| 2026-10-19 | app_stripped | FUN_001011a9 | Prompt 3 v1.0 (variable naming) | Uncertainty modifier v1.0 | [Prompt 3](#prompt-3--variable-naming-v10) |
| 2026-10-19 | app_stripped | `{START}` = first command-line argument (argv[1]) | Prompt 4 v1.0 (data flow) | Uncertainty modifier v1.0 | [Prompt 4](#prompt-4--data-flow-v10) |
| 2026-10-19 | libmathutils.so | clamp (001010f9) | Prompt 1 v1.0 (function summary) | Uncertainty modifier v1.0 | [Prompt 1](#prompt-1--function-summary-v10--libmathutilsso-clamp) |
| 2026-10-19 | libmathutils.so | clamp (001010f9) | Prompt 2 v1.0 (signature recovery) | Uncertainty modifier v1.0 | [Prompt 2](#prompt-2--signature-recovery-v10--libmathutilsso-clamp) |
| 2026-10-19 | libmathutils.so | clamp (001010f9) | Prompt 3 v1.0 (variable naming) | Uncertainty modifier v1.0 | [Prompt 3](#prompt-3--variable-naming-v10--libmathutilsso-clamp) |
| 2026-10-19 | libmathutils.so | checksum (00101129) | Prompt 1 v1.0 (function summary) | Uncertainty modifier v1.0 | [Prompt 1](#prompt-1--function-summary-v10--libmathutilsso-checksum) |
| 2026-10-19 | libmathutils.so | checksum (00101129) | Prompt 2 v1.0 (signature recovery) | Uncertainty modifier v1.0 | [Prompt 2](#prompt-2--signature-recovery-v10--libmathutilsso-checksum) |
| 2026-10-19 | libmathutils.so | checksum (00101129) | Prompt 3 v1.0 (variable naming) | Uncertainty modifier v1.0 | [Prompt 3](#prompt-3--variable-naming-v10--libmathutilsso-checksum) |

Run conditions (all runs):
- Shared rules + uncertainty modifier from `prompts.md` were applied.
- Only GhidraMCP tools were used (decompile, listing, cross-references, symbols).
- Prompts were answered in order, and earlier answers were not revised after later prompts.

---

## Prompt 1 — Function summary (v1.0)

Program: `app_stripped` · Function: `FUN_001011a9` · Modifier: uncertainty v1.0

### Purpose
FUN_001011a9 is the program's `main`: `entry` passes its address to `__libc_start_main`.
With fewer than 2 arguments it prints a usage line and returns 1. Otherwise it passes
`argv[1]` and its length to the imported `checksum`, passes the result with constants
0 and 1000 to the imported `clamp`, prints both values and returns 0. Why the program
does this is UNKNOWN.

### Inputs
| Parameter | Meaning | Evidence (address or source) | Confidence |
|---|---|---|---|
| param_1 (EDI, 32-bit int) | argc (argument count) | Saved `MOV [RBP-0x14],EDI` at 001011b5 and compared with 1 at 001011bc. It is argc because the function's address goes in RDI to `__libc_start_main` (`LEA RDI,[0x1011a9]` at 001010d8, `CALL [00103fd8]` at 001010df, and 00103fd8 holds 00105000 = `<EXTERNAL> __libc_start_main`) | medium |
| param_2 (RSI, 64-bit pointer) | argv (pointer to an array of string pointers) | Saved at 001011b8. `[argv+0]` is printed with `%s` (001011c2 to 001011db). `[argv+8]` is passed to `strlen` (001011e7 to 001011f5) | high |
| Contents of argv[1] | UNKNOWN (whatever the user types on the command line) | Only the dereference is visible (001011ef). No value is fixed in the binary | UNKNOWN |
| RDX (envp) | Not used | No instruction in 001011a9 to 0010124d reads RDX before writing it | high |

### Outputs
| Output (return value, written memory, printed text, exit code) | Meaning | Evidence | Confidence |
|---|---|---|---|
| Return value EAX = 1 | Usage path: argc ≤ 1 | `MOV EAX,0x1` at 001011e0, `JMP 0010124c` at 001011e5 | high |
| Return value EAX = 0 | Normal path: a checksum was printed | `MOV EAX,0x0` at 00101247 | high |
| Exit code | The return value becomes the process exit status | Inferred from the return to `__libc_start_main` (001010df), whose code is not in this binary | medium |
| Printed text: `"usage: %s <string>\n"` with argv[0] | Usage message | Format string at 00102004 loaded at 001011cc, `printf` call at 001011db | high |
| Printed text: `"checksum=%u clamped=%d\n"` | First value: `checksum`'s return, printed unsigned. Second value: `clamp`'s return, printed signed | Format string at 00102018 loaded at 00101233. ESI ← [RBP-0x8] (checksum) at 0010122e/00101231, EDX ← [RBP-0x4] (clamped) at 0010122b. `printf` call at 00101242 | high |
| Written memory | Only its own stack frame: [RBP-0x14], [RBP-0x20], [RBP-0x8], [RBP-0x4] | 001011b5, 001011b8, 00101211, 00101228. No other stores in the listing | high |

### Claims
| # | Claim | Evidence (address or source) | Confidence |
|---|---|---|---|
| 1 | FUN_001011a9 is `main` | `LEA RDI,[0x1011a9]` at 001010d8, then `CALL qword ptr [0x00103fd8]` at 001010df. 00103fd8 holds 00105000 (`<EXTERNAL> __libc_start_main`) | medium |
| 2 | The usage branch runs when argc ≤ 1 | `CMP dword ptr [RBP-0x14],0x1` at 001011bc, `JG 0x001011e7` at 001011c0 | high |
| 3 | The usage message prints argv[0] | `MOV RAX,[RAX]` at 001011c6 → RSI at 001011c9, `printf` at 001011db | high |
| 4 | Returns 1 after printing the usage message | `MOV EAX,0x1` at 001011e0 | high |
| 5 | argc ≥ 2 is the only input check. argv[1] is not checked for NULL, length or content | The only comparison in 001011a9 to 0010124d is at 001011bc | high |
| 6 | `strlen` is called on argv[1] | `ADD RAX,0x8; MOV RAX,[RAX]` at 001011eb/001011ef, `CALL 0x00101090` at 001011f5. The name comes from the imported symbol `<EXTERNAL> strlen` at 00101090 | high |
| 7 | The 64-bit `strlen` result is cut to 32 bits before being passed on | `MOV EDX,EAX` at 001011fa, `MOV ESI,EDX` at 00101207 (the decompiler shows `sVar3 & 0xffffffff`) | high |
| 8 | `checksum` is called with (argv[1], 32-bit length) | RDI ← argv[1] at 00101209, ESI ← length at 00101207, `CALL 0x001010b0` at 0010120c. The name comes from the imported symbol `<EXTERNAL> checksum` at 001010b0 | high |
| 9 | `checksum` returns a 32-bit value that is stored and later printed with `%u` | `MOV [RBP-0x8],EAX` at 00101211, format string at 00102018 | high |
| 10 | The checksum algorithm and its range of values | UNKNOWN. `checksum` is external (001010b0 → 00105028 `<EXTERNAL>`), and its body is not in this binary | UNKNOWN |
| 11 | `clamp` is called with (checksum, 0, 1000) | EDI ← [RBP-0x8] at 00101214/00101221, `MOV ESI,0x0` at 0010121c, `MOV EDX,0x3e8` at 00101217, `CALL 0x00101080` at 00101223. The name comes from the imported symbol `<EXTERNAL> clamp` at 00101080 | high |
| 12 | Whether 0 and 1000 are the lower and upper bounds, and what `clamp` returns for out-of-range input | UNKNOWN. `clamp` is external (00101080 → 00105010 `<EXTERNAL>`). Only the argument values are visible, not how they are used | UNKNOWN |
| 13 | What the constant 1000 means or what units it is in | UNKNOWN. It is only the immediate `0x3e8` at 00101217 | UNKNOWN |
| 14 | `clamp`'s 32-bit result is stored and printed with `%d` | `MOV [RBP-0x4],EAX` at 00101228, `MOV EDX,[RBP-0x4]` at 0010122b, `printf` at 00101242 | high |
| 15 | The return values of both `printf` calls are ignored | EAX is overwritten right after each call (001011e0, 00101247) | high |
| 16 | The return value is a 32-bit int (0 or 1), not `bool` as Ghidra shows | Written with full-width `MOV EAX,imm32` at 001011e0 and 00101247 | medium |
| 17 | Returns 0 on the checksum path | `MOV EAX,0x0` at 00101247 | high |

### What would settle it
- **argv[1] contents (Inputs):** runtime traces or documentation showing how the program is actually run.
- **Claim 10, checksum algorithm and range:** decompile `checksum` in the shared library that exports it. First confirm which library `app_stripped` loads (its DT_NEEDED entries). `libmathutils.so` in this Ghidra project is a likely candidate, but this was not checked.
- **Claim 12, clamp semantics:** decompile `clamp` in that same library, or test it with values below 0, between 0 and 1000, and above 1000.
- **Claim 13, meaning of 1000:** source code, a header or documentation. The binary contains only the number.
- **Purpose ("why"):** source code or design documentation. The binary shows what the function does, not why.

---

## Prompt 2 — Signature recovery (v1.0)

Program: `app_stripped` · Function: `FUN_001011a9` · Modifier: uncertainty v1.0

Call-site note: FUN_001011a9 has no direct `CALL` anywhere in the binary. Its only code
reference is `LEA RDI,[0x1011a9]` at 001010d8 in `entry`, which passes its address to
`__libc_start_main` (`CALL qword ptr [0x00103fd8]` at 001010df). The real call happens
inside `__libc_start_main`, which is external, so this run uses the `entry` setup
(001010c0 to 001010df) as the call site.

### Proposed signature
```c
int FUN_001011a9(int argc, char **argv);
```

### Parameters
| Position | Register | Width (bits) | Proposed type | Evidence: instruction(s) and address(es) | Confidence |
|---|---|---|---|---|---|
| 1 | EDI | 32 | `int` (signed) | `MOV dword ptr [RBP-0x14],EDI` at 001011b5 stores only 32 bits. `CMP dword ptr [RBP-0x14],0x1` at 001011bc, then the signed jump `JG` at 001011c0 | high |
| 2 | RSI | 64 | `char **` | `MOV qword ptr [RBP-0x20],RSI` at 001011b8. It is dereferenced as an array of 8-byte pointers at offsets +0 (001011c6) and +8 (001011eb/001011ef). Element [0] is passed as the `%s` argument (001011c9, format at 00102004) and element [1] as `strlen`'s argument (001011f2/001011f5) | medium |
| 3 | RDX | — | not a parameter (unused) | RDX is never read before being written in 001011a9 to 0010124d. Its first use is the write `MOV EDX,EAX` at 001011fa | high |
| Call-site values | RSI / RDX into `__libc_start_main` | 64 | argc / argv for libc | At `entry`: `POP RSI` at 001010c9 (argc from the initial stack) and `MOV RDX,RSP` at 001010ca (argv pointer) set up `__libc_start_main`'s arguments. How libc forwards them into EDI/RSI for FUN_001011a9 is not in this binary: UNKNOWN | UNKNOWN |

### Return value
| Register | Width | Proposed type | Evidence: instruction and address | Confidence |
|---|---|---|---|---|
| EAX | 32 | `int` | `MOV EAX,0x1` at 001011e0 (usage path) and `MOV EAX,0x0` at 00101247 (normal path), both full 32-bit writes, then `LEAVE; RET` at 0010124c/0010124d | high (width), medium (`int` vs another 32-bit integer type) |

### Disagreements with Ghidra
- **Return type:** the decompiler shows `bool` (`return param_1 < 2;`). The listing writes the full 32-bit EAX with immediates 1 and 0 (001011e0, 00101247), which fits a 32-bit `int` that happens to hold 0 or 1. The function database entry (`functions list`) also has a different signature, `undefined FUN_001011a9(void)`, which has not been updated.
- **param_2 type:** Ghidra shows `undefined8 *`. The proposed type is `char **`, because both elements used are passed where a string is expected (a `%s` argument at 001011db and `strlen` at 001011f5).
- **param_1 type:** no disagreement (`int`).

### What would settle it
- **Call-site values (how libc forwards argc/argv):** the source or disassembly of the `__libc_start_main` that is actually loaded, or a debugger breakpoint at 001011a9 to inspect EDI/RSI.
- **`int` vs another 32-bit return type:** source code or a header. The binary shows only width and values.

---

## Prompt 3 — Variable naming (v1.0)

Program: `app_stripped` · Function: `FUN_001011a9` · Modifier: uncertainty v1.0 ·
Nothing was renamed in Ghidra.

Variables come from `functions list_variables` at 001011a9. Stack locals map to frame
slots as follows: local_1c = [RBP-0x14], local_28 = [RBP-0x20], local_10 = [RBP-0x8],
local_c = [RBP-0x4].

| Current name | Proposed name | Evidence: how it is used, with address(es) | Confidence |
|---|---|---|---|
| param_1 | `argc` | Arrives in EDI and is stored at 001011b5. It is compared with 1 (001011bc), and when it is ≤ 1 the code never reads `param_2[1]` (001011c0 skips 001011e7 to 00101242). It acts as a count that guards the array index. The name `argc` also relies on Prompt 1 claim 1 (address passed to `__libc_start_main` at 001010d8) | medium |
| param_2 | `argv` | Arrives in RSI and is stored at 001011b8. It is indexed as an array of pointers at +0 (001011c6) and +8 (001011ef). Element 0 is printed into the `"usage: %s <string>"` slot (00102004, 001011db) | medium |
| local_1c | none (compiler temporary: stack copy of param_1) | Written once from EDI at 001011b5 and read once at 001011bc. Holds the same value as param_1 | high |
| local_28 | none (compiler temporary: stack copy of param_2) | Written once from RSI at 001011b8 and read at 001011c2, 001011e7 and 001011fc. Holds the same value as param_2 | high |
| sVar3 | `input_len` | `strlen` return value (call at 001011f5, import symbol `<EXTERNAL> strlen` at 00101090) for argv[1]. It is cut to 32 bits (001011fa) and passed as `checksum`'s 2nd argument (00101207) | high |
| uVar1 / local_10 | `checksum_value` | EAX from the call to the imported `checksum` (0010120c) is stored at [RBP-0x8] (00101211). It is passed as `clamp`'s first argument (00101214/00101221) and printed into the `checksum=%u` slot (0010122e/00101231, format at 00102018). uVar1 is the decompiler's register value; local_10 is its stack slot | high |
| uVar2 / local_c | `clamped_value` | EAX from the call to the imported `clamp` (00101223) is stored at [RBP-0x4] (00101228) and printed into the `clamped=%d` slot (0010122b, format at 00102018). uVar2 is the decompiler's register value; local_c is its stack slot | high |

Notes:
- The names `checksum_value` and `clamped_value` describe where each value comes from
  (which import returned it) and how it is labelled when printed. They do not claim
  anything about the algorithm, which is UNKNOWN (Prompt 1 claims 10 and 12).

### What would settle it
- **`argc` / `argv` (medium):** a debugger break at 001011a9 showing that EDI equals the number of command-line words and RSI points to them, or the source code.

---

## Prompt 4 — Data flow (v1.0)

Program: `app_stripped` · `{START}` = the program's first command-line argument (the
string the user types after the program name, i.e. argv[1]) · Modifier: uncertainty v1.0

### Trace
| Step | Address | Instruction or call | Where the value is (register / stack slot / memory) | What happens to it |
|---|---|---|---|---|
| 1 | (before 001010c0) | Process start (kernel) | Initial process stack: argc at [RSP], argv[] array at [RSP+8] | The string and the argv[] array are set up before any code in this binary runs. This layout comes from the System V ABI, not from the binary itself |
| 2 | 001010c9 | `POP RSI` | RSI = argc | Removes argc from the stack, so RSP now points at argv[0] |
| 3 | 001010ca | `MOV RDX,RSP` | RDX = pointer to argv[]; argv[1] is at [RDX+8] | The argv array pointer is prepared as `__libc_start_main`'s 3rd argument |
| 4 | 001010d8 | `LEA RDI,[0x1011a9]` | RDI = address of FUN_001011a9 | Passes main's address (Prompt 1 claim 1). This does not carry argv[1] itself |
| 5 | 001010df | `CALL qword ptr [0x00103fd8]` → 00105000 `<EXTERNAL> __libc_start_main` | RDX (argv[]) goes into libc | UNKNOWN: what libc does with argv before calling main is not in this binary |
| 6 | 001011a9 | Function entry (called from inside libc) | RSI = argv[] pointer (by System V convention for main's 2nd argument) | argv[1] arrives indirectly, as `RSI+8` |
| 7 | 001011b8 | `MOV qword ptr [RBP-0x20],RSI` | Stack slot [RBP-0x20] = argv[] | Spilled to the stack |
| 8 | 001011bc / 001011c0 | `CMP dword ptr [RBP-0x14],0x1` / `JG 0x001011e7` | — | Gate: argv[1] is only read when argc > 1. On the usage path (001011c2 to 001011e5) only argv[0] is read, never argv[1] |
| 9 | 001011e7 / 001011eb / 001011ef | `MOV RAX,[RBP-0x20]` / `ADD RAX,0x8` / `MOV RAX,[RAX]` | RAX = argv[1] (char * to the string) | First direct load of the argv[1] pointer |
| 10 | 001011f2 | `MOV RDI,RAX` | RDI = argv[1] | Becomes the 1st argument to `strlen` |
| 11 | 001011f5 | `CALL 0x00101090` → `JMP [00103fc0]` (00101094) → 00105018 `<EXTERNAL> strlen` | In: RDI = argv[1]. Out: RAX = length | The string's length is computed (standard `strlen` behavior, inferred from the import name; the body is external) |
| 12 | 001011fa | `MOV EDX,EAX` | EDX = length (low 32 bits only) | Derived value: the length is cut to 32 bits |
| 13 | 001011fc / 00101200 / 00101204 | `MOV RAX,[RBP-0x20]` / `ADD RAX,0x8` / `MOV RAX,[RAX]` | RAX = argv[1] again | The pointer is reloaded from the argv[] array, not from a saved copy |
| 14 | 00101207 / 00101209 | `MOV ESI,EDX` / `MOV RDI,RAX` | RDI = argv[1], ESI = 32-bit length | Both become arguments to `checksum` |
| 15 | 0010120c | `CALL 0x001010b0` → `JMP [00103fd0]` (001010b4) → 00105028 `<EXTERNAL> checksum` | In: RDI = argv[1], ESI = length. Out: EAX = 32-bit result | UNKNOWN: how `checksum` reads the string, whether it modifies it, and whether it keeps the pointer. The body is external |
| 16 | 00101211 | `MOV dword ptr [RBP-0x8],EAX` | Stack slot [RBP-0x8] = checksum result (derived from argv[1]) | Spilled to the stack |
| 17 | 00101214 / 00101221 | `MOV EAX,[RBP-0x8]` / `MOV EDI,EAX` | EDI = checksum result. ESI = 0 (0010121c), EDX = 0x3e8 (00101217) | Becomes `clamp`'s 1st argument |
| 18 | 00101223 | `CALL 0x00101080` → `JMP [00103fb8]` (00101084) → 00105010 `<EXTERNAL> clamp` | In: EDI = checksum result, ESI = 0, EDX = 1000. Out: EAX = 32-bit result | UNKNOWN: how the result relates to the input. The body is external |
| 19 | 00101228 | `MOV dword ptr [RBP-0x4],EAX` | Stack slot [RBP-0x4] = clamp result (derived from argv[1]) | Spilled to the stack |
| 20 | 0010122b / 0010122e / 00101231 | `MOV EDX,[RBP-0x4]` / `MOV EAX,[RBP-0x8]` / `MOV ESI,EAX` | EDX = clamp result, ESI = checksum result | Both derived values become `printf` arguments |
| 21 | 00101233 / 0010123a | `LEA RAX,[0x102018]` / `MOV RDI,RAX` | RDI = `"checksum=%u clamped=%d\n"` | Format string |
| 22 | 00101242 | `CALL 0x001010a0` → `JMP [00103fc8]` (001010a4) → 00105020 `<EXTERNAL> printf` | In: ESI (`%u`), EDX (`%d`) | Both derived values are printed. The argv[1] string itself is never printed |
| 23 | 00101247 | `MOV EAX,0x0` | EAX = 0 | The return value is a constant, not derived from argv[1] |

### Boundary crossings
| Call address | Stub → target | Value in (register) | Result out (register) |
|---|---|---|---|
| 001010df | `CALL [00103fd8]` → 00105000 `<EXTERNAL> __libc_start_main` | RDX = argv[] array (argv[1] at +8) | Does not return here (`HLT` at 001010e5). Calls FUN_001011a9 with RSI = argv[] (by convention; UNKNOWN from the binary) |
| 001011f5 | 00101090 → `JMP [00103fc0]` → 00105018 `<EXTERNAL> strlen` | RDI = argv[1] | RAX = length (only EAX is used afterwards, 001011fa) |
| 0010120c | 001010b0 → `JMP [00103fd0]` → 00105028 `<EXTERNAL> checksum` | RDI = argv[1], ESI = 32-bit length | EAX = checksum result |
| 00101223 | 00101080 → `JMP [00103fb8]` → 00105010 `<EXTERNAL> clamp` | EDI = checksum result (derived), ESI = 0, EDX = 1000 | EAX = clamp result |
| 00101242 | 001010a0 → `JMP [00103fc8]` → 00105020 `<EXTERNAL> printf` | ESI = checksum result, EDX = clamp result (both derived) | EAX = ignored (overwritten at 00101247) |

### Final destination
- **Printed:** two values derived from argv[1] are printed by `printf` at 00101242 using
  `"checksum=%u clamped=%d\n"` (00102018): the `checksum` result as unsigned decimal and
  the `clamp` result as signed decimal. Where `printf` output ends up (stdout) comes
  from libc behavior, not from this binary.
- **Not printed:** the argv[1] string itself is never printed. The usage path prints
  argv[0], not argv[1].
- **Not returned:** the return value is a constant (0 at 00101247, 1 at 001011e0) and does not depend on argv[1].
- **Not stored globally:** argv[1] and the values derived from it are only kept in
  registers and in the stack slots [RBP-0x20] (argv[] pointer), [RBP-0x8] and [RBP-0x4].
  No global or heap writes appear in 001011a9 to 0010124d.
- **UNKNOWN:** whether `checksum` (or `clamp`, which only receives a derived integer)
  stores the pointer or a copy of the string anywhere inside the external library.

### What would settle it
- **Step 5 / first boundary crossing (libc → main):** a debugger breakpoint at 001011a9 to confirm RSI+8 points to the typed string, or the source of the libc that is actually loaded.
- **Step 15 (what `checksum` does with the string):** decompile `checksum` in the library that exports it (confirm via app_stripped's DT_NEEDED; `libmathutils.so` is a candidate, not yet checked).
- **Step 18 (how clamp's output relates to its input):** decompile `clamp` in that library, or run it with known inputs.
- **Final destination, UNKNOWN line:** the same decompilation of `checksum`, checking it for stores to global or heap memory.

---

## Prompt 1 — Function summary (v1.0) · libmathutils.so `clamp`

Program: `libmathutils.so` · Function: `clamp` (001010f9) · Modifier: uncertainty v1.0

### Purpose
`clamp` takes three signed 32-bit integers and returns one of them. It returns the 2nd
if the 1st is less than the 2nd. Otherwise it returns the 3rd if the 1st is greater
than the 3rd. Otherwise it returns the 1st. In effect, it limits the 1st argument to
the inclusive range [2nd, 3rd]. Why the library provides it, and what the values
represent, is UNKNOWN.

### Inputs
| Parameter | Meaning | Evidence (address or source) | Confidence |
|---|---|---|---|
| param_1 (EDI, 32-bit) | The value to be limited. It is returned unchanged when it lies within [param_2, param_3] | Stored `MOV [RBP-0x4],EDI` at 00101101. Compared with param_2 at 0010110d and with param_3 at 0010111a. Returned at 00101124 | high |
| param_2 (ESI, 32-bit) | Lower limit: returned when param_1 < param_2 | Stored at 00101104. `CMP EAX,[RBP-0x8]` at 0010110d. When `JGE` at 00101110 is not taken, `MOV EAX,[RBP-0x8]` at 00101112 returns it | high |
| param_3 (EDX, 32-bit) | Upper limit: returned when param_1 > param_3 (and param_1 ≥ param_2) | Stored at 00101107. `CMP EAX,[RBP-0xc]` at 0010111a. When `JLE` at 0010111d is not taken, `MOV EAX,[RBP-0xc]` at 0010111f returns it | high |
| What the values mean, and their units | UNKNOWN | The function only compares and moves integers. Nothing in it names or scales them | UNKNOWN |
| Whether callers always pass param_2 ≤ param_3 | UNKNOWN | No caller exists inside this library (claim 13). The function itself does not check it (claim 9) | UNKNOWN |
| RCX, R8, R9 and stack arguments | Not used | No instruction from 001010f9 to 00101128 reads them | high |

### Outputs
| Output (return value, written memory, printed text, exit code) | Meaning | Evidence | Confidence |
|---|---|---|---|
| Return value EAX (32-bit) | One of the three inputs, chosen as described in Purpose | `MOV EAX,[RBP-0x8]` at 00101112, `MOV EAX,[RBP-0xc]` at 0010111f and `MOV EAX,[RBP-0x4]` at 00101124 all lead to `POP RBP; RET` at 00101127/00101128 | high |
| Written memory | Only the function's own frame slots [RBP-0x4], [RBP-0x8] and [RBP-0xc]. These lie below RSP (red zone, because there is no `SUB RSP`) | 00101101, 00101104, 00101107. The listing has no other stores | high |
| Printed text | None | The function makes no `CALL` | high |
| Exit code | None. This is a library function that returns to its caller | `RET` at 00101128 | high |

### Claims
| # | Claim | Evidence (address or source) | Confidence |
|---|---|---|---|
| 1 | The name `clamp` comes from an exported dynamic symbol | The .dynsym entry at 00100390 has st_name 0x55, which points to "clamp" at 00100415 in .dynstr. Its st_info 0x12 means GLOBAL FUNC, st_shndx 0x0a, st_value 0x10f9 and st_size 0x30. The Ghidra symbol source is IMPORTED | high |
| 2 | The function occupies 48 bytes (001010f9 to 00101128) and has one exit | st_size 0x30 (claim 1). The only `RET` is at 00101128 | high |
| 3 | All three arguments are 32-bit | Stored as dwords from EDI, ESI and EDX at 00101101, 00101104 and 00101107 | high |
| 4 | The comparisons are signed | `JGE` at 00101110 and `JLE` at 0010111d (signed conditions, not `JAE`/`JBE`) | high |
| 5 | If param_1 < param_2, it returns param_2 | 0010110a to 00101115: `CMP`, then `JGE` not taken, then `MOV EAX,[RBP-0x8]`, then `JMP 00101127` | high |
| 6 | Otherwise, if param_1 > param_3, it returns param_3 | 00101117 to 00101122: `CMP`, then `JLE` not taken, then `MOV EAX,[RBP-0xc]` | high |
| 7 | Otherwise it returns param_1 | `MOV EAX,[RBP-0x4]` at 00101124 | high |
| 8 | Both limits are inclusive: param_1 == param_2 or param_1 == param_3 returns param_1 | `JGE` (00101110) and `JLE` (0010111d) are both taken on equality | high |
| 9 | The function does not check that param_2 ≤ param_3. The lower limit is tested first, so with an inverted range the result depends on the order of the tests. For example, (5, 10, 0) returns 10 and (20, 10, 0) returns 0 | The only comparisons are at 0010110d and 0010111a, in that order | high |
| 10 | No calls, no global or heap memory access, no side effects | The listing from 001010f9 to 00101128 has no `CALL` and only accesses memory relative to RBP | high |
| 11 | No arithmetic is done on the values, so overflow cannot occur | Only `MOV`, `CMP` and jumps operate on the values (0010110a to 00101124) | high |
| 12 | The library was built with Intel CET indirect-branch tracking (`-fcf-protection`) | `ENDBR64` at 001010f9 | medium |
| 13 | Nothing in libmathutils.so calls `clamp` | The only references are 0010201c (.eh_frame_hdr "Initial Location") and 00102090 (.eh_frame FDE PcBegin), both unwind metadata, plus the external entry point | high |
| 14 | The code is unoptimized (-O0 style): arguments are spilled to the stack and reloaded before each comparison | 00101101 to 00101107 spill, then reloads at 0010110a, 00101117 and 00101124 | medium |
| 15 | The values callers pass in practice | UNKNOWN. They come from outside this binary | UNKNOWN |
| 16 | The intended meaning of the limits (e.g. what range 0 to 1000 represents for a caller) | UNKNOWN. This library has no constants, strings or callers for `clamp` | UNKNOWN |

Cross-reference note: this run answers app_stripped Prompt 1, claim 12 ("whether 0 and
1000 are the lower and upper bounds"), assuming app_stripped's `clamp` resolves to this
library (see Prompt 2 below). As the run rules require, that earlier answer is left
unchanged.

### What would settle it
- **Meaning and units of the values (Inputs, claim 16):** source code, a header or documentation for libmathutils.so.
- **Whether callers guarantee param_2 ≤ param_3 (Inputs):** analysis of every program that links against libmathutils.so, or the library's API documentation.
- **Values passed in practice (claim 15):** the callers' disassembly (one is app_stripped at 00101223; see Prompt 2) or a runtime trace with a breakpoint at 001010f9.

---

## Prompt 2 — Signature recovery (v1.0) · libmathutils.so `clamp`

Program: `libmathutils.so` · Function: `clamp` (001010f9) · Modifier: uncertainty v1.0

Call-site note: libmathutils.so contains no call to `clamp` (Prompt 1 claim 13). The
call site used here is in `app_stripped`, which is in the same Ghidra project. Its first
DT_NEEDED entry (.dynamic at 00103da0: tag 1, value 0x84) points to .dynstr offset 0x84 =
"libmathutils.so" at 0010054c. Its call at 00101223 goes through the stub 00101080 to
`<EXTERNAL> clamp`. This connects the two by name. Which file the dynamic loader actually
resolves at run time is UNKNOWN.

### Proposed signature
```c
int clamp(int param_1, int param_2, int param_3);
```

### Parameters
| Position | Register | Width (bits) | Proposed type | Evidence: instruction(s) and address(es) | Confidence |
|---|---|---|---|---|---|
| 1 | EDI | 32 | `int` (signed) | Callee: `MOV [RBP-0x4],EDI` at 00101101, then signed `JGE`/`JLE` at 00101110 and 0010111d. Call site: `MOV EDI,EAX` at app_stripped 00101221 (a 32-bit move) | high |
| 2 | ESI | 32 | `int` (signed) | Callee: `MOV [RBP-0x8],ESI` at 00101104, then the signed comparison at 0010110d/00101110. Call site: `MOV ESI,0x0` at app_stripped 0010121c | high |
| 3 | EDX | 32 | `int` (signed) | Callee: `MOV [RBP-0xc],EDX` at 00101107, then the signed comparison at 0010111a/0010111d. Call site: `MOV EDX,0x3e8` at app_stripped 00101217 | high |
| — | RCX, R8, R9 | — | not parameters | Never read in 001010f9 to 00101128. The call site does not set them before 00101223 (00101211 to 00101221) | high |
| Call-site resolution | — | — | — | Whether app_stripped's call at 00101223 really reaches 001010f9 at run time: UNKNOWN (depends on the loader search path) | UNKNOWN |

Signedness note: at the call site the 1st argument is `checksum`'s return value, which
app_stripped prints with `%u` (unsigned; format at 00102018). `clamp` compares it as
signed (`JGE` at 00101110), so a checksum of 0x80000000 or more is treated as negative
and returns param_2 (0 at that call site). This mismatch is visible in the two binaries.
Whether checksum can actually return such a value is a question for `checksum`, outside
this prompt's scope.

### Return value
| Register | Width | Proposed type | Evidence: instruction and address | Confidence |
|---|---|---|---|---|
| EAX | 32 | `int` | Callee: 32-bit loads `MOV EAX,[RBP-…]` at 00101112, 0010111f and 00101124, then `RET` at 00101128. The value is always one of the `int` parameters. Call site: `MOV [RBP-0x4],EAX` at app_stripped 00101228 (32-bit store), later printed with `%d` (signed) | high |

### Disagreements with Ghidra
- **Function database signature:** `functions list` shows `undefined clamp(void)`. The
  proposed signature has three `int` parameters and an `int` return, based on the
  register uses at 00101101 to 00101107 and 00101112 to 00101124.
- **Decompiler signature:** none. The decompiler's `int clamp(int param_1,int param_2,int param_3)`
  matches the proposal.

### What would settle it
- **Call-site resolution:** a debugger breakpoint at app_stripped 00101223, stepping
  through the PLT to confirm it lands at libmathutils.so + 0x10f9, or `ldd`/loader logs on
  the target system.

---

## Prompt 3 — Variable naming (v1.0) · libmathutils.so `clamp`

Program: `libmathutils.so` · Function: `clamp` (001010f9) · Modifier: uncertainty v1.0 ·
Nothing was renamed in Ghidra.

Variables come from `functions list_variables` at 001010f9. Stack locals map to frame
slots as follows: local_c = [RBP-0x4], local_10 = [RBP-0x8], local_14 = [RBP-0xc].

| Current name | Proposed name | Evidence: how it is used, with address(es) | Confidence |
|---|---|---|---|
| param_1 | `value` | Arrives in EDI (00101101). It is the left operand of both comparisons (0010110a/0010110d and 00101117/0010111a) and is returned unchanged when neither limit applies (00101124) | high |
| param_2 | `lower_bound` | Arrives in ESI (00101104). It is returned exactly when `value` is less than it (0010110d, `JGE` not taken at 00101110, `MOV EAX,[RBP-0x8]` at 00101112). Note: the code does not enforce lower_bound ≤ upper_bound (Prompt 1 claim 9) | high |
| param_3 | `upper_bound` | Arrives in EDX (00101107). It is returned exactly when `value` is greater than it, after the lower test passed (0010111a, `JLE` not taken at 0010111d, `MOV EAX,[RBP-0xc]` at 0010111f) | high |
| local_c | none (compiler temporary: stack copy of param_1) | Written once from EDI at 00101101, read at 0010110a, 00101117 and 00101124. Holds the same value as param_1 | high |
| local_10 | none (compiler temporary: stack copy of param_2) | Written once from ESI at 00101104, read at 0010110d and 00101112. Holds the same value as param_2 | high |
| local_14 | none (compiler temporary: stack copy of param_3) | Written once from EDX at 00101107, read at 0010111a and 0010111f. Holds the same value as param_3 | high |

Notes:
- `lower_bound` / `upper_bound` describe how each argument is used (which one is
  returned in which case). They do not say what the range means to a caller, which is
  still UNKNOWN (Prompt 1 claim 16).

### What would settle it
- None: no cell in this prompt is UNKNOWN.

---

## Prompt 1 — Function summary (v1.0) · libmathutils.so `checksum`

Program: `libmathutils.so` · Function: `checksum` (00101129) · Modifier: uncertainty v1.0

Provenance note: this run was done on 2026-10-19 in a separate session, before the
`clamp` run above. Its output was not saved to this file at the time. It is added here
as the session produced it (only the layout was matched to the other sections), without
re-running and without revising earlier answers.

### Purpose
`checksum` computes a 32-bit polynomial rolling hash over a byte buffer. It starts at 0
and, for each of `param_2` bytes, updates the accumulator as
`acc = acc*31 + (unsigned char)buf[i]`. It returns the final accumulator.

### Inputs
| Parameter | Meaning | Evidence (address or source) | Confidence |
|---|---|---|---|
| param_1 (RDI) | Base pointer to a byte buffer, used as the base for per-byte loads | `MOV [RBP-0x18],RDI` at 00101131. `MOV RAX,[RBP-0x18]` / `ADD RAX,RDX` / `MOVZX EAX,byte ptr [RAX]` at 0010115a to 00101161 | high |
| param_2 (ESI) | Number of bytes to process. Signed loop upper bound | `MOV [RBP-0x1c],ESI` at 00101135. `CMP EAX,[RBP-0x1c]` / `JL` at 00101173 to 00101176 | high |

### Outputs
| Output (return value, written memory, printed text, exit code) | Meaning | Evidence | Confidence |
|---|---|---|---|
| Return value EAX | The accumulated 32-bit hash of the buffer | `MOV EAX,[RBP-0x8]` at 00101178, then `RET` at 0010117c | high |

### Claims
| # | Claim | Evidence (address or source) | Confidence |
|---|---|---|---|
| 1 | The accumulator is initialized to 0 | `MOV dword ptr [RBP-0x8],0x0` at 00101138 | high |
| 2 | The loop counter is initialized to 0 | `MOV dword ptr [RBP-0x4],0x0` at 0010113f | high |
| 3 | Each iteration multiplies the accumulator by 31 (`acc<<5 - acc`) | `SHL EAX,0x5` at 0010114d, then `SUB EAX,EDX` at 00101150 (= `acc*0x1f`) | high |
| 4 | Each byte is loaded as an unsigned 8-bit value | `MOVZX EAX,byte ptr [RAX]` at 00101161, then `MOVZX EAX,AL` at 00101164 | high |
| 5 | New accumulator = byte + acc*31 | `ADD EAX,ECX` at 00101167, `MOV [RBP-0x8],EAX` at 00101169 | high |
| 6 | The counter increments by 1 per iteration | `ADD dword ptr [RBP-0x4],0x1` at 0010116c | high |
| 7 | The loop runs while `i < param_2`, using a signed comparison | `CMP EAX,[RBP-0x1c]` at 00101173, `JL 0x00101148` at 00101176 | high |
| 8 | If `param_2 <= 0`, the body never executes and it returns 0 | The condition is checked first via `JMP 0x00101170` at 00101146. `JL` is signed | high |

Cross-reference note: this run bears on app_stripped Prompt 1 claim 10 (the checksum
algorithm) and Prompt 4 step 15 (what `checksum` does with the string), assuming
app_stripped's `checksum` resolves to this library. As the run rules require, those
earlier answers are left unchanged.

Verification note (from the run): each claim was checked against the listing
(00101129 to 0010117c) and the decompilation. The `SHL 5` / `SUB` pair confirms the
`*0x1f` (×31) multiplier shown in Ghidra's pseudocode, and the signed `JL` confirms
`int` rather than an unsigned length.

### What would settle it
- None: no cell in this prompt is UNKNOWN.

---

## Prompt 2 — Signature recovery (v1.0) · libmathutils.so `checksum`

Program: `libmathutils.so` · Function: `checksum` (00101129) · Modifier: uncertainty v1.0

Call-site note: libmathutils.so contains no call to `checksum`. `checksum` is an exported
symbol with no internal `CALL` cross-references. The references at 00102024
(INDIRECTION) and 001020b0 (DATA) are export/dynamic-symbol table entries. The
signature below therefore rests only on the prologue and body.

### Proposed signature
```c
int checksum(const unsigned char *buf, int len);
```

### Parameters
| Position | Register | Width (bits) | Proposed type | Evidence: instruction(s) and address(es) | Confidence |
|---|---|---|---|---|---|
| 1 | RDI | 64 | `const unsigned char *` (pointer to bytes, read-only here) | Stored as a full 64-bit value via `MOV qword ptr [RBP-0x18],RDI` at 00101131. Dereferenced as a byte address at `MOVZX EAX,byte ptr [RAX]` 00101161 after `ADD RAX,RDX` 0010115e. It is only read, never written, hence `const` | high |
| 2 | ESI | 32 | `int` (signed count/length) | Stored as a 32-bit value via `MOV dword ptr [RBP-0x1c],ESI` at 00101135. Used only as the loop bound, with a signed `JL` at 00101176, hence signed `int` | high |

### Return value
| Register | Width | Proposed type | Evidence: instruction and address | Confidence |
|---|---|---|---|---|
| EAX | 32 | `int` | `MOV EAX,[RBP-0x8]` at 00101178 loads the 32-bit accumulator into EAX before `RET` at 0010117c | high |

### Disagreements with Ghidra
- Ghidra's prototype is `int checksum(long param_1, int param_2)`. The proposal types
  `param_1` as `const unsigned char *`, not `long`. At 0010115e to 00101161 it is used
  as a base address that is dereferenced byte by byte (`MOVZX EAX,byte ptr [RAX]`),
  which is pointer use, not integer arithmetic. Ghidra defaults the register to `long`
  because nothing inside the function constrains the pointed-to type. The byte load is
  the evidence for `unsigned char *`.
- The element type (`unsigned char`) is supported by the byte-width load. Whether a
  caller treats the buffer as signed bytes cannot be determined from this binary.

### What would settle it
- **Caller-side element type:** the callers' disassembly and types. One candidate is
  app_stripped's call at 0010120c, which passes argv[1] (see app_stripped Prompt 1
  claim 8).

---

## Prompt 3 — Variable naming (v1.0) · libmathutils.so `checksum`

Program: `libmathutils.so` · Function: `checksum` (00101129) · Modifier: uncertainty v1.0

| Current name | Proposed name | Evidence: how it is used, with address(es) | Confidence |
|---|---|---|---|
| param_1 | `buf` | Base address for byte loads: `MOV RAX,[RBP-0x18]` 0010115a, `ADD RAX,RDX` 0010115e, `MOVZX EAX,byte ptr [RAX]` 00101161 | high |
| param_2 | `len` | Its only use is as the loop upper bound: `CMP EAX,[RBP-0x1c]` 00101173, `JL` 00101176. It governs how many bytes are read | high |
| local_10 ([RBP-0x8]) | `hash` (or `acc`) | Initialized to 0 at 00101138. Updated to `byte + acc*31` at 0010114d to 00101169. Returned at 00101178. It is the running checksum accumulator | high |
| local_c ([RBP-0x4]) | `i` | Initialized to 0 at 0010113f. Sign-extended and added to `buf` as the byte index at 00101157 to 0010115e. Incremented at 0010116c. It is the loop induction variable | high |

Notes:
- No variable here is a meaningless compiler temporary. All four have clear roles from
  their uses at the cited addresses.
- `EDX`/`ECX`/`AL` in the loop body are unnamed scratch registers that hold intermediate
  values of the `acc*31 + byte` expression. They are not named locals, so no names are
  proposed for them.

### What would settle it
- None: no cell in this prompt is UNKNOWN.
