./layout
sizeof(struct telemetry) = 24
offset of id    = 0
offset of count = 4
offset of flag  = 8
offset of value = 16
count before bump = 10
count after bump  = 11
root@f23d837666a6:/work/c-basics# 


## Day 3 — target/ checksum

Scheme: for each byte, acc = acc * 31 + byte (running multiply-and-add accumulator).

./app_simple hello -> checksum=99162322 clamped=1000

## Day 3 — static vs. dynamic linking

| Binary | Size (bytes) | ldd result |
|---|---|---|
| app_static | 785,432 | not a dynamic executable — libmathutils's code (and much of libc) is baked directly in, nothing to resolve at runtime |
| app_dynamic | 16,064 | libmathutils.so => not found (until LD_LIBRARY_PATH=. set, then resolved to ./libmathutils.so); libc.so.6 resolved from system path |

app_static is ~49x larger than app_dynamic (785,432 vs 16,064 bytes). That gap is the
size of libmathutils's compiled code plus a statically-linked copy of the C runtime
library (libc), all baked directly into the executable at build time. app_dynamic, by
contrast, only stores a reference — the name libmathutils.so — with the actual checksum
and clamp code left entirely outside the binary, to be located and loaded fresh at
every launch.

The build succeeded for app_dynamic because -L. only tells the *linker* where to find
the library at build time, so it can confirm the library exists and read its symbol
table to link correctly against. It writes nothing about that -L. path into the binary
itself. At runtime, a separate program — the dynamic loader — is what actually locates
and loads libmathutils.so, and it only searches a fixed set of standard system
directories by default; the current directory isn't one of them. That's why app_dynamic
failed with "cannot open shared object file" until LD_LIBRARY_PATH=. explicitly told the
loader to also search here.

Once LD_LIBRARY_PATH was set, app_dynamic produced identical output to app_static and
app_simple (checksum=99162322 clamped=1000), confirming both builds run the exact same
logic — they differ only in *when* and *how* that logic gets attached to the running
program, and the size difference is the direct, visible cost of that choice.

## Week 6 — moved Ghidra work to Windows

Mac's Ghidra 12.1.4 install had no native decompiler for mac_arm_64 in the official
release. Built it locally with ./gradlew buildNatives (succeeded), but the app then
hung indefinitely on project load afterward, even in a fresh project -- confirmed via
ps aux showing near-zero CPU time over several minutes, ruling out "just slow."
Possible Gatekeeper/quarantine interaction with the newly-built unsigned natives,
not fully diagnosed.

Decision: moved all Ghidra work to a Windows desktop, where the official release
ships a working native decompiler out of the box. Cloned the repo via git, installed
Temurin 21 and Ghidra 12.1.4, imported app_dynamic and libmathutils.so -- Decompiler
panel worked immediately, no native-build step needed. Mac continues to be used for
everything else (Docker, Python, Claude Code, write-ups); Windows is Ghidra-only.
Repo (GitHub) is the sync point between the two machines.