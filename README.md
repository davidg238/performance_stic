# STIC Smalltalk benchmark

A translation to Toit, of a Smalltalk benchmark written by the Smalltalk Industry Council (STIC) in the late 90's.  
It is only published for comparison to the original Smalltalk benchmark and to enable results to be reproduced.  
See also the [original post](https://ekorau.com/some-numbers/).

## Platform: Espressif ESP32, 240 MHz, 520 KB RAM, 4 MB Flash

STIC benchmark

| Test | Toit | uLisp  | CircuitPython | rete/nsl (2026-10-12) |
| --: | --: | --: | --: | --: |
| alloc | 16.0 | 21.6 | 11.4 | 25.2⁵ |
| array write | 19.4 | 98.1 | 63.3 | 21.8 |
| dictionary write | 5.7 | 1.4 | 0.9 | 6.4 |
| float math | 41.1 | 124.3 | 20.9 | 38.9⁴ |
| integer math | 9.4 | 122.5 | 14.4 | 2.8 |
| collection iterate | 12.7 | 42.5 | 29.2 | 17.3 |
| collection write | 9.5 | 6.7 | 15.4 | 14.5 |
| string compare | 1.5 | 12.5 | 2.9 | 2.5 |
| hanoi @ blocks:  8 | 0.0000 | 0.01 | 0.01 | 0.002 |
| 16 | 0.2 | 3.2 | 1.4 | ut |
|   20 | 3.0 | 54.2 | 21.6 | ut |
|  21 | ut | ut | 43.1 | ut |
|  22 | ut | ut | se | ut |
| 24 | 49.2 | 924.1 | se | ut |

Notes:  

1. Smaller numbers are better
2. ut: un-tested,  se: stack exhausted
3. Software:
   - Toit v2.0.0-alpha.180
   - uLisp v4.7
   - Adafruit CircuitPython 9.2.7
   - rete/nsl is experimental software: rete master `38a5500` (2026-10-12), Zephyr 4.2.0, Model B, 96 KB VM
     heap, no WiFi, on an ESP32-D0WDQ6 rev 1.0 (WROOM-32). Three runs, identical to the millisecond. Hanoi
     above 8 was not part of this run.
4. Float math runs with a 2 KB (128-cell) boxed-float slab: the image leaves ~3 KB of libc heap, so a larger
   slab does not fit.
5. Alloc is slower than the previous day's run on the same board (19.3 s) and is not yet explained; on the
   ESP32-C6 the same row got faster over the same changes (below).

### native-AOT — the OEOM lever (2026-07)

A July 2026 spike on the same board, with the VM then called tuvm (now rete). Because its object model
(OEOM) makes every call a `send` and every method just a `Binding → Closure`, "native vs
interpreted" is **one field** on the closure — so a hot method can be replaced by
hand-written C *dropped straight into the vtable*, with **callers, interpreter, and
`.oimg` image format all unchanged** (no JIT, no recompile, no format break). Same board,
same binary, A/B:

| Hanoi n | Toit | uLisp | CircuitPython | rete interpreted | rete native-in-vtable | native speedup |
| --: | --: | --: | --: | --: | --: | --: |
| 16 | 0.2 | 3.2 | 1.4 | 0.7 | 0.0067 | **~116×** |
| 20 | 3.0 | 54.2 | 21.6 | 12.0 | 0.103 | **~119×** |

~11.75 µs/move → ~0.10 µs/move; native is linear and allocation-free (no GC). This is the
*fully-inlined* AOT **ceiling** (the recursion collapses to raw C), so it sits ~10× past
Toit's compiled column on this workload — a real bytecode→native compiler preserving
send/GC semantics would land between the interpreter and this bound. The point is the
**lever, not the number**: OEOM's single dispatch choke point lets you ship the
interpreter, profile real workloads to find the genuinely hot methods, then push a
surgical bespoke-AOT patch for just those. Method + caveats: rete's design record
`docs/design/2026-07-17-oeom-native-substitution-hanoi-spike-design.md`.

## Platform: Espressif ESP32-C6, RISC-V, 160 MHz, 512 KB RAM, 8 MB Flash

STIC, plus Richards and DeltaBlue from this repo, on one board (ESP32-C6 devkit) in one session, 2026-10-12.

| Test | Toit | MicroPython | rete/nsl |
| --: | --: | --: | --: |
| alloc | 28.0 | 13.2 | 10.9 |
| array write | 25.9 | 41.5 | 18.0 |
| dictionary write | 5.5 | 1.0 | 5.3 |
| float math | 78.7 | 49.0 | 23.3 |
| integer math | 13.8 | 17.6 | 3.6 |
| collection iterate | 17.1 | 35.3 | 10.9 |
| collection write | 12.1 | 6.4 | 11.8 |
| string compare | 1.9 | 4.0 | 2.2 |
| Richards (ms per run) | 1,178 | 7,471 | 5,080 |
| DeltaBlue (ms per run) | 77 | 326–359 | 336 |

Notes:

1. Smaller numbers are better; seconds unless marked. All three VMs print `verified: true` for Richards and DeltaBlue.
2. Software:
   - Toit v2.0.0-alpha.194, the benchmark installed as a boot container on the `firmware-esp32c6` envelope.
     Mean of three in-process runs.
   - MicroPython v1.29.0 (`ESP32_GENERIC_C6-20260824`), the `.py` sources here with `time.monotonic()` replaced by
     `time.ticks_ms()/1000`. Mean of three in-process runs.
   - rete/nsl: rete `e2fa47e` (2026-10-12), Zephyr 4.2.0, Model B, 128 KB VM heap, no radio, the interpreter's
     hot path in SRAM. STIC once per boot, three boots, identical to the millisecond; Richards and DeltaBlue three
     runs in one boot.
3. The send-heavy, object-heavy pair is where Toit's compiled code leads: about 4.3× on Richards and 4.4× on
   DeltaBlue. rete/nsl is ahead of MicroPython on Richards and level on DeltaBlue.

## Are We Fast Yet: rete/nsl against Primordial Soup (host)

The [Are We Fast Yet](https://github.com/smarr/are-we-fast-yet) suite (Marr, Daloze, Mössenböck, DLS 2016), ported
from its SOMns sources to nsl as `awfy.nsl` in this repo (MIT; the notice is in the file), against
[Primordial Soup](https://github.com/newspeaklanguage/primordialsoup), the Newspeak VM, running the same `awfy.nsl`
(nsl is a subset of Newspeak). Four mechanical substitutions make it compile on Soup: the clock read, float literals
computed once with `asFloat` (Soup reads `1.5` as an exact Fraction), Json's substring read, and `==`/`notNil` added
to a copy of Soup's kernel. Both are interpreters, on an Intel i7-6700 at 3.4 GHz, gcc 16.2.1, 2026-10-12.

| Benchmark | Primordial Soup (ms) | rete/nsl (ms) | nsl ÷ Soup |
| --: | --: | --: | --: |
| List | 89 | 238 | 2.67 |
| Storage | 237 | 391 | 1.65 |
| Towers | 158 | 217 | 1.37 |
| Json | 160 | 212 | 1.32 |
| DeltaBlue | 84 | 106 | 1.26 |
| Permute | 237 | 288 | 1.22 |
| Queens | 257 | 262 | 1.02 |
| Sieve | 179 | 166 | 0.93 |
| NBody | 2574 | 2331 | 0.91 |
| Richards | 334 | 244 | 0.73 |
| Mandelbrot | 1574 | 1024 | 0.65 |
| Bounce | 313 | 184 | 0.59 |
| CD | 322 | 120 | 0.37 |
| **geomean** | | | **1.01** |

Notes:

1. Median of three runs each, sequential. rete `13d5e6e`, Primordial Soup `9ac43be` (ReleaseHost).
2. Inner iteration counts are scaled to host size (Bounce 300, List 100, Permute 200, Storage 200, Richards 5,
   Queens 200, Sieve 300, Towers 60, NBody 250000, DeltaBlue 2000, Json 20, Mandelbrot 500, CD 10). Havlak is not
   ported.
3. `awfy.nsl` here is rete master's copy (2026-10-12): it differs from the run's only in visibility markers
   (`private`/`public`), which nsl began enforcing the same day.
4. Soup's lead is in the allocation-heavy rows (List, Storage).

## Platform: Intel i3-12100, 3.3GHz, 16GB RAM, Ubuntu 24.04

| Test                 | Toit   | Zig     | rete/nsl |
| -------------------: | -----: | ------: | -------: |
| alloc                | 0.0473 | 2.7775  | 0.0807 |
| array write          | 0.1373 | 0.0155  | 0.1570 |
| dictionary write     | 0.0217 | 0.0250  | 0.0370 |
| float math           | 0.0950 | 0.0140  | 0.0983 |
| integer math         | 0.0743 | 0.0085  | 0.0283 |
| collection iterate   | 0.1407 | 0.0310  | 0.0977 |
| collection write     | 0.0440 | 0.0017  | 0.0860 |
| string compare       | 0.0100 | 0.0130  | 0.0127 |
| hanoi @ blocks: 8   |  0.00000000 | 0.00000147  | 0.0000 |
| 16                   | 0.0010     | 0.0003 | 0.0027 |
| 20                   | ut     | ut | ut |
| 21                   | ut     | ut | ut |
| 22                   | ut     | ut | ut |
| 24                   | 0.3933 | 0.0671  | 0.6760 |

Notes:

1. Zig v0.14.0
2. rete/nsl: rete master `5e1d6d45` (2026-10-12), host image VM (`oevm_img`, posix backend) built `gcc -O2`, no
   profiler; mean of three runs. It times in whole milliseconds, so hanoi 8 reads 0.

## Platform: 166MMX Pentium, 40MB RAM, Windows/95 OSR2

Reproduced from the [original results](https://ekorau.com/some_numbers/Performance.html).

| Test | Smalltalk Express 2.0.4 | Visual Smalltalk 3.0.1 | Squeak 1.20 | Squeak 1.30 | Squeak 1.30J | Dolphin/98 rel1 | VAST 4.02 | Smalltalk MT 1.5b3 | Java 1.2b2 |
| --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| alloc | 3.9 | 1.1 | 3.0 | 3.1 | 3.9 | 1.9 | 2.5 | 15.7 | 846.8 |
| arrayWrite | 8.4 | 2.4 | 11.9 | 11.8 | 9.9 | 9.1 | 4.7 | 1.7 | 0.5 |
| dictionaryWrite | 5.9 | 0.5 | 3.6 | 3.8 | 3.4 | 1.6 | 0.5 | 1.0 | 6.7 |
| floatMath | 20.7 | 7.1 | 19.3 | 20.5 | 24.5 | 14.1 | 17.8 | 66.8 | 2.6 |
| integerMath | 20.5 | 0.9 | 7.1 | 7.0 | 5.9 | 2.3 | 1.8 | 1.0 | 3.2 |
| collectionIterate | 21.8 | 5.9 | 42.1 | 42.2 | 34.7 | 24.5 | 4.0 | 3.2 | 61.6 |
| collectionWrite | 3.5 | 1.0 | 6.3 | 6.4 | 5.4 | 4.0 | 2.0 | 2.9 | 4.1 |
| stringCompare | 2.3 | 0.9 | 301.2 | 241.4 | 215.7 | 0.6 | 1.2 | 3.6 | 0.9 |
| hanoi @ blocks: 22 | 4.7 | 0.9 | 12.6 | 12.9 | 7.9 | 8.2 | 1.8 | 1.0 | 4.0 |

Notes:

1. Each test was run three times.
2. The Java alloc value (846.8) was extrapolated from 1000 iterations, rather than the 100,000 used in other images.
3. ObjectConnect provided commentary regarding Smalltalk/MT performance metrics.
