#!/usr/bin/env python3
"""verify.py - turn a claim about a binary into a test that passes or fails."""
import re
import subprocess
import sys

# Run this script from the folder holding BOTH sensor_stripped and
# libsensorlog.so (your blind/ folder) - the loader looks in "." for the .so.
BINARY = "./sensor_stripped"
ENV = {"LD_LIBRARY_PATH": "."}  # the Week 5 loader lesson, in code


def run(args, binary=BINARY, env=ENV):
    """Run the binary with args; return (exit_code, stdout)."""
    try:
        result = subprocess.run([binary] + [str(a) for a in args],
                                capture_output=True, text=True, env=env, timeout=10)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    except OSError as e:  # missing file, no execute permission, wrong architecture
        return None, f"COULD NOT RUN: {e}"
    return result.returncode, result.stdout.strip()


def check(name, args, predicate, claim, binary=BINARY, env=ENV):
    """Run one claim. predicate(exit_code, stdout) -> True if the claim holds."""
    code, out = run(args, binary, env)
    try:
        ok = bool(predicate(code, out))
    except Exception as e:  # a predicate that crashes counts as a failure, not a pass
        ok = False
        out = f"{out}  [predicate error: {e}]"
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: {claim}")
    print(f"        input: {binary} {' '.join(str(a) for a in args)}")
    print(f"        exit:  {code}")
    print(f"        out:   {out}")
    return ok


def decode(out):
    """Undo encode_record: parse the hex bytes after 'encoded N bytes:' and XOR with 0x2a."""
    hex_part = out.split(":", 1)[1]
    return bytes(int(h, 16) ^ 0x2A for h in hex_part.split()).decode("ascii", "replace")


def reported_values(out):
    """Parse 'checksum=X clamped=Y' from app_stripped's output."""
    m = re.search(r"checksum=(\d+) clamped=(-?\d+)", out)
    return int(m.group(1)), int(m.group(2))


def reference_checksum(s):
    """The LLM's claimed algorithm: acc = acc*31 + byte, kept to 32 bits."""
    acc = 0
    for b in s.encode():
        acc = (acc * 31 + b) & 0xFFFFFFFF
    return acc


results = []

# Each check below encodes ONE claim from the Week 6 analysis of sensor_stripped.
# Exit codes, from main: 0 = success, 1 = usage, 2 = out of range.
results.append(check("upper bound inclusive", ["t", 1023],
    lambda c, o: c == 0 and decode(o) == "t:128",
    "1023 is accepted (and scales to 128)"))

results.append(check("just past upper bound", ["t", 1024],
    lambda c, o: c == 2 and "out of range" in o,
    "1024 is rejected with 'out of range'"))

results.append(check("lower bound inclusive", ["t", 0],
    lambda c, o: c == 0 and decode(o) == "t:0",
    "0 is accepted"))

results.append(check("negative rejected", ["t", -1],
    lambda c, o: c == 2 and "out of range" in o,
    "-1 is rejected"))

results.append(check("non-numeric passes", ["t", "abc"],
    lambda c, o: c == 0 and decode(o) == "t:0",
    "atoi('abc')==0, which PASSES validation"))

results.append(check("missing args", ["t"],
    lambda c, o: c == 1 and o.startswith("usage:"),
    "too few args prints usage, exit 1"))

# Two claims the LLM made in Day 2 (prompt sweep on app_stripped / libmathutils.so).
# These target app_stripped, so they use its folder and loader path.
APP = "../target/app_stripped"
APP_ENV = {"LD_LIBRARY_PATH": "../target"}

results.append(check("checksum formula", ["hello"],
    lambda c, o: c == 0 and reported_values(o)[0] == reference_checksum("hello"),
    "checksum computes acc = acc*31 + byte (Day 2, checksum Prompt 1, claims 3-5)",
    binary=APP, env=APP_ENV))

results.append(check("signed/unsigned wraparound", ["reverseengineering"],
    lambda c, o: (c == 0
                  and reported_values(o)[0] >= 2**31
                  and reported_values(o)[1] == 0),
    "a checksum >= 0x80000000 reads as negative in clamp, so clamped=0 "
    "(Day 2, clamp Prompt 2, signedness note)",
    binary=APP, env=APP_ENV))

print(f"\n{sum(results)}/{len(results)} claims verified")
sys.exit(0 if all(results) else 1)
