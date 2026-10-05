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

## Day 4 — ELF scavenger hunt (app_dynamic)

1. Entry point: 0x10c0 (readelf -h)
2. Section headers: 31 (readelf -h)
3. String constant: usage line lives in .rodata (strings -t x app_dynamic | grep usage)
4. main: address 0x11a9, size 165 bytes (readelf -s)
5. .text size: 0x18e = 398 bytes (readelf -SW)
6. PIE: yes — "DYN (Position-Independent Executable file)" (readelf -h) and
   "pie executable" (file)
7. Needed libraries: libmathutils.so, libc.so.6 (readelf -d / ldd).
   libmathutils.so is among them, confirmed.
8. checksum: undefined (U) in app_dynamic — nm app_dynamic | grep checksum -> "U checksum".
   Resolved from libmathutils.so at runtime, unlike main which is T (defined, in .text).
9. Symbol count: 33 before stripping, "no symbols" after (nm's literal message on
   app_stripped, not a zero count). Still runs identically after stripping
   (LD_LIBRARY_PATH=. ./app_stripped hello -> checksum=99162322 clamped=1000).
10. Sections after stripping: 29 (down from 31). .symtab and .strtab are gone.
    Every section holding actual code/data (.text, .rodata, .data, .bss, .plt,
    .dynsym, .dynstr, .got) survived untouched — stripping removed only the
    human-readable name table, not the program itself.

## Day 5 


tiny:     file format elf64-x86-64


Disassembly of section .init:

0000000000001000 <_init>:
    1000:	endbr64
    1004:	sub    rsp,0x8
    1008:	mov    rax,QWORD PTR [rip+0x2fd9]        # 3fe8 <__gmon_start__@Base>
    100f:	test   rax,rax
    1012:	je     1016 <_init+0x16>
    1014:	call   rax
    1016:	add    rsp,0x8
    101a:	ret

Disassembly of section .plt:

0000000000001020 <.plt>:
    1020:	push   QWORD PTR [rip+0x2fa2]        # 3fc8 <_GLOBAL_OFFSET_TABLE_+0x8>
    1026:	jmp    QWORD PTR [rip+0x2fa4]        # 3fd0 <_GLOBAL_OFFSET_TABLE_+0x10>
    102c:	nop    DWORD PTR [rax+0x0]

Disassembly of section .plt.got:

0000000000001030 <__cxa_finalize@plt>:
    1030:	endbr64
    1034:	jmp    QWORD PTR [rip+0x2fbe]        # 3ff8 <__cxa_finalize@GLIBC_2.2.5>
    103a:	nop    WORD PTR [rax+rax*1+0x0]

Disassembly of section .text:

0000000000001040 <_start>:
    1040:	endbr64
    1044:	xor    ebp,ebp
    1046:	mov    r9,rdx
    1049:	pop    rsi
    104a:	mov    rdx,rsp
    104d:	and    rsp,0xfffffffffffffff0
    1051:	push   rax
    1052:	push   rsp
    1053:	xor    r8d,r8d
    1056:	xor    ecx,ecx
    1058:	lea    rdi,[rip+0x11c]        # 117b <main>
    105f:	call   QWORD PTR [rip+0x2f73]        # 3fd8 <__libc_start_main@GLIBC_2.34>
    1065:	hlt
    1066:	cs nop WORD PTR [rax+rax*1+0x0]

0000000000001070 <deregister_tm_clones>:
    1070:	lea    rdi,[rip+0x2f99]        # 4010 <__TMC_END__>
    1077:	lea    rax,[rip+0x2f92]        # 4010 <__TMC_END__>
    107e:	cmp    rax,rdi
    1081:	je     1098 <deregister_tm_clones+0x28>
    1083:	mov    rax,QWORD PTR [rip+0x2f56]        # 3fe0 <_ITM_deregisterTMCloneTable@Base>
    108a:	test   rax,rax
    108d:	je     1098 <deregister_tm_clones+0x28>
    108f:	jmp    rax
    1091:	nop    DWORD PTR [rax+0x0]
    1098:	ret
    1099:	nop    DWORD PTR [rax+0x0]

00000000000010a0 <register_tm_clones>:
    10a0:	lea    rdi,[rip+0x2f69]        # 4010 <__TMC_END__>
    10a7:	lea    rsi,[rip+0x2f62]        # 4010 <__TMC_END__>
    10ae:	sub    rsi,rdi
    10b1:	mov    rax,rsi
    10b4:	shr    rsi,0x3f
    10b8:	sar    rax,0x3
    10bc:	add    rsi,rax
    10bf:	sar    rsi,1
    10c2:	je     10d8 <register_tm_clones+0x38>
    10c4:	mov    rax,QWORD PTR [rip+0x2f25]        # 3ff0 <_ITM_registerTMCloneTable@Base>
    10cb:	test   rax,rax
    10ce:	je     10d8 <register_tm_clones+0x38>
    10d0:	jmp    rax
    10d2:	nop    WORD PTR [rax+rax*1+0x0]
    10d8:	ret
    10d9:	nop    DWORD PTR [rax+0x0]

00000000000010e0 <__do_global_dtors_aux>:
    10e0:	endbr64
    10e4:	cmp    BYTE PTR [rip+0x2f25],0x0        # 4010 <__TMC_END__>
    10eb:	jne    1118 <__do_global_dtors_aux+0x38>
    10ed:	push   rbp
    10ee:	cmp    QWORD PTR [rip+0x2f02],0x0        # 3ff8 <__cxa_finalize@GLIBC_2.2.5>
    10f6:	mov    rbp,rsp
    10f9:	je     1107 <__do_global_dtors_aux+0x27>
    10fb:	mov    rdi,QWORD PTR [rip+0x2f06]        # 4008 <__dso_handle>
    1102:	call   1030 <__cxa_finalize@plt>
    1107:	call   1070 <deregister_tm_clones>
    110c:	mov    BYTE PTR [rip+0x2efd],0x1        # 4010 <__TMC_END__>
    1113:	pop    rbp
    1114:	ret
    1115:	nop    DWORD PTR [rax]
    1118:	ret
    1119:	nop    DWORD PTR [rax+0x0]

0000000000001120 <frame_dummy>:
    1120:	endbr64
    1124:	jmp    10a0 <register_tm_clones>

0000000000001129 <add3>:
    1129:	endbr64
    112d:	push   rbp
    112e:	mov    rbp,rsp
    1131:	mov    DWORD PTR [rbp-0x4],edi
    1134:	mov    DWORD PTR [rbp-0x8],esi
    1137:	mov    DWORD PTR [rbp-0xc],edx
    113a:	mov    edx,DWORD PTR [rbp-0x4]
    113d:	mov    eax,DWORD PTR [rbp-0x8]
    1140:	add    edx,eax
    1142:	mov    eax,DWORD PTR [rbp-0xc]
    1145:	add    eax,edx
    1147:	pop    rbp
    1148:	ret

0000000000001149 <sum_to>:
    1149:	endbr64
    114d:	push   rbp
    114e:	mov    rbp,rsp
    1151:	mov    DWORD PTR [rbp-0x14],edi
    1154:	mov    DWORD PTR [rbp-0x8],0x0
    115b:	mov    DWORD PTR [rbp-0x4],0x1
    1162:	jmp    116e <sum_to+0x25>
    1164:	mov    eax,DWORD PTR [rbp-0x4]
    1167:	add    DWORD PTR [rbp-0x8],eax
    116a:	add    DWORD PTR [rbp-0x4],0x1
    116e:	mov    eax,DWORD PTR [rbp-0x4]
    1171:	cmp    eax,DWORD PTR [rbp-0x14]
    1174:	jle    1164 <sum_to+0x1b>
    1176:	mov    eax,DWORD PTR [rbp-0x8]
    1179:	pop    rbp
    117a:	ret

000000000000117b <main>:
    117b:	endbr64
    117f:	push   rbp
    1180:	mov    rbp,rsp
    1183:	push   rbx
    1184:	mov    edx,0x3
    1189:	mov    esi,0x2
    118e:	mov    edi,0x1
    1193:	call   1129 <add3>
    1198:	mov    ebx,eax
    119a:	mov    edi,0xa
    119f:	call   1149 <sum_to>
    11a4:	add    eax,ebx
    11a6:	mov    rbx,QWORD PTR [rbp-0x8]
    11aa:	leave
    11ab:	ret

Disassembly of section .fini:

00000000000011ac <_fini>:
    11ac:	endbr64
    11b0:	sub    rsp,0x8
    11b4:	add    rsp,0x8
    11b8:	ret

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

## Week 6 — stripping experiment

nm libmathutils_stripped.so    -> no symbols
nm -D libmathutils_stripped.so -> T checksum @ 0x1129, T clamp @ 0x10f9
                                  (plus weak toolchain hooks: _ITM_*, __cxa_finalize, __gmon_start__)
nm -D app_stripped             -> U checksum, U clamp, U printf, U strlen, U __libc_start_main

strip removes .symtab/.strtab but cannot remove .dynsym: the loader needs those names
at runtime. The library exports checksum and clamp by name (T); the executable imports
them by name (U). That's why app_stripped lost main's name -- a local symbol that lived
only in .symtab -- but Ghidra still labeled checksum, clamp, printf, and strlen.

__libc_start_main is the runtime-resolved function entry calls with main's address,
which explains the indirect CALL QWORD PTR seen in Route B.

Takeaway: a dynamically linked binary always leaks the names of the library functions it
calls, however thoroughly it's stripped -- free information about what it does.
## Week 6 — Cross-library data-flow map (input: argv[1] = "hello")

```
app_dynamic (executable)                            libmathutils.so (shared library)
------------------------                            --------------------------------
main @ 001011a9
  argc: EDI -> local_1c   (001011b5)
  argv: RSI -> local_28   (001011b8)
      |
      | argv[1] = [argv + 0x8]          (001011e7..ef)
      v
  RDI = argv[1]; CALL strlen            (001011f5)
      | RAX -> EDX, truncated to 32 bits (001011fa)
      v
  ESI = length   (32-bit)               (00101207)
  RDI = argv[1]  (64-bit pointer)       (00101209)
  CALL checksum                         (0010120c)
      |
      v
  checksum stub, .plt.sec @ 001010b0
    ENDBR64
    JMP [00103fd0] --- GOT slot, filled by loader --->  checksum @ 00101129
                                                        RDI -> local_20, ESI -> local_24
                                                        acc = acc*32 - acc + byte
      <---------------- RET, EAX = sum -----------------+
  sum -> local_10                       (00101211)
      |
      v
  EDI = sum, ESI = 0, EDX = 0x3e8       (00101214..21)
  CALL clamp -> stub -> GOT ----------------------->  clamp @ 001010f9
                                                        EDI, ESI, EDX -> locals
                                                        three plain branches
      <---------------- RET, EAX = clamped -------------+
  clamped -> local_c                    (00101228)
      |
      v
  RDI = "checksum=%u clamped=%d\n" (00102018)
  ESI = sum, EDX = clamped
  CALL printf                           (00101242)
      -> stdout: checksum=99162322 clamped=1000
```

### Walkthrough

1. main @ 001011a9 receives argc in EDI and argv in RSI (System V arguments 1 and 2),
   spilling them to local_1c (001011b5) and local_28 (001011b8).
2. argc is compared to 1 at 001011bc; JG at 001011c0 skips the usage branch.
3. argv[1] is computed at 001011e7..ef as [argv + 0x8]: index 1 times the 8-byte
   pointer size.
4. RDI = argv[1] at 001011f2; CALL strlen at 001011f5. The length returns in RAX, and
   MOV EDX,EAX at 001011fa keeps only the low 32 bits. This is the `& 0xffffffff` that
   appears in the decompilation.
5. argv[1] is reloaded at 001011fc..204 (an -O0 artifact). ESI = length at 00101207,
   RDI = argv[1] at 00101209: the pointer in the 64-bit register, the length in the
   32-bit one.
6. CALL at 0010120c lands in the .plt.sec stub at 001010b0: ENDBR64, then
   JMP qword ptr [00103fd0] at 001010b4. Encoding check: `ff 25 16 2f 00 00` is a
   RIP-relative jump; next instruction 001010ba + 0x2f16 = 00103fd0, the GOT slot.
   That slot is empty on disk (Ghidra's EXTERNAL placeholder at 00105028 shows only
   `??` bytes), and the loader fills it with checksum's real address at runtime. This
   is why app_dynamic failed without LD_LIBRARY_PATH in Week 5.
7. The real checksum runs in libmathutils.so @ 00101129, a different file
   (matches nm -D's 0x1129).
   a. Arguments arrive exactly where main placed them: RDI -> local_20 at 00101131,
      ESI -> local_24 at 00101135.
   b. The *31 is compiled as SHL EAX,5 then SUB EAX,EDX at 0010114d..50
      (acc*32 - acc). There is no multiply instruction; the decompiler reconstructed
      0x1f from the shift-and-subtract pattern.
   c. Each byte is read with MOVZX (zero-extended, so unsigned) at 00101161, and the
      loop condition uses JL (signed) at 00101176, matching unsigned char data and
      int n. The result is placed in EAX at 00101178.
8. The checksum returns in EAX and is saved to local_10 at 00101211.
9. clamp's arguments are set at 00101214..21: EDI = sum, ESI = 0, EDX = 0x3e8 (1000).
   CALL at 00101223 goes through clamp's own stub and GOT slot.
   a. The real clamp is in libmathutils.so @ 001010f9 (matches nm -D's 0x10f9).
      Arguments arrive in EDI, ESI, EDX at 00101101..07. The code is three plain
      branches (JGE at 00101110, JLE at 0010111d) with one shared RET at 00101128,
      a direct translation of the source. The decompiler's single compound condition
      was its own restructuring.
   b. The result returns in EAX and is saved to local_c at 00101228.
10. printf's arguments: RDI = format string at 00102018 (loaded 00101233..3a),
    ESI = sum (0010122e..31), EDX = clamped (0010122b). EAX = 0 at 0010123d tells
    the variadic printf that no vector registers carry arguments. CALL printf at
    00101242 prints "checksum=99162322 clamped=1000".
11. main returns 0 (MOV EAX,0 at 00101247; LEAVE/RET at 0010124c..4d). The usage
    branch returns 1 (MOV EAX,1 at 001011e0). The decompiler merged these two returns
    into `return param_1 < 2`; the assembly keeps them separate.

**Verification:** both library addresses were confirmed by two independent tools,
nm -D in the container and the Symbol Tree in Ghidra.
## Week 6 — static vs. dynamic

| | app_dynamic | app_static |
|---|---|---|
| File size | 16,064 bytes | 785,432 bytes |
| Functions in Symbol Tree | ~10 | ~300 |
| Finding main | Immediate (named; one string XREF) | Hard; buried among libc internals, needed help |
| checksum/clamp | <EXTERNAL> stubs, real code in libmathutils.so | [confirm: real functions inside the binary] |

Dynamic is easier: the import boundary names every library call, so the program's own
logic stands out. Static better represents a real unknown sample: it has no .dynsym
imports to leak, so a stripped static binary loses even its libc function names.
