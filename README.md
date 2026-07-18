# STIC Smalltalk benchmark

A translation to Toit, of a Smalltalk benchmark written by the Smalltalk Industry Council (STIC) in the late 90's.  
It is only published for comparison to the original Smalltalk benchmark and to enable results to be reproduced.  
See also the [original post](https://ekorau.com/some-numbers/).

## Platform: Espressif ESP32, 240 MHz, 520 KB RAM, 4 MB Flash

STIC benchmark

| Test | Toit | uLisp  | CircuitPython | tuvm/nsl |
| --: | --: | --: | --: | --: |
| alloc | 16.0 | 21.6 | 11.4 | 24.1 |
| array write | 19.4 | 98.1 | 63.3 | 138.9 |
| dictionary write | 5.7 | 1.4 | 0.9 | 43.3 |
| float math | 41.1 | 124.3 | 20.9 | 35.1 |
| integer math | 9.4 | 122.5 | 14.4 | 15.3 |
| collection iterate | 12.7 | 42.5 | 29.2 | 532.6 |
| collection write | 9.5 | 6.7 | 15.4 | 97.0 |
| string compare | 1.5 | 12.5 | 2.9 | 5.2 |
| hanoi @ blocks:  8 | 0.0000 | 0.01 | 0.01 | 0.003 |
| 16 | 0.2 | 3.2 | 1.4 | 0.7 |
|   20 | 3.0 | 54.2 | 21.6 | 12.0 |
|  21 | ut | ut | 43.1 | 24.0 |
|  22 | ut | ut | se | ut |
| 24 | 49.2 | 924.1 | se | 191.7 |

Notes:  

1. Smaller numbers are better
2. ut: un-tested,  se: stack exhausted
3. Software:
   - Toit v2.0.0-alpha.180
   - uLisp v4.7
   - Adafruit CircuitPython 9.2.7
   - nsl-tuvm is experimental software, running on Zephyr 4.2.0, with 96 KB VM heap

### tuvm native-AOT — the OEOM lever

The `tuvm/nsl` Hanoi rows above are the **interpreter**. Because tuvm's object model
(OEOM) makes every call a `send` and every method just a `Binding → Closure`, "native vs
interpreted" is **one field** on the closure — so a hot method can be replaced by
hand-written C *dropped straight into the vtable*, with **callers, interpreter, and
`.oimg` image format all unchanged** (no JIT, no recompile, no format break). Same board,
same binary, A/B:

| Hanoi n | interpreted (`tuvm/nsl`) | native-in-vtable | speedup |
| --: | --: | --: | --: |
| 16 | 0.7 s   | 0.0067 s | **~116×** |
| 20 | 12.0 s  | 0.103 s  | **~119×** |

~11.75 µs/move → ~0.10 µs/move; native is linear and allocation-free (no GC). This is the
*fully-inlined* AOT **ceiling** (the recursion collapses to raw C), so it sits ~10× past
Toit's compiled column on this workload — a real bytecode→native compiler preserving
send/GC semantics would land between the interpreter and this bound. The point is the
**lever, not the number**: OEOM's single dispatch choke point lets you ship the
interpreter, learn from months of fleet usage which one selector is actually hot, then
push a surgical bespoke-AOT patch for exactly that method. Method + caveats:
`~/workspace/tuvm/docs/design/2026-07-17-oeom-native-substitution-hanoi-spike-design.md`.

## Platform: Intel i3-12100, 3.3GHz, 16GB RAM, Ubuntu 24.04

| Test                 | Toit   | Zig     |
| -------------------: | -----: | ------: |
| alloc                | 0.0473 | 2.7775  |
| array write          | 0.1373 | 0.0155  |
| dictionary write     | 0.0217 | 0.0250  |
| float math           | 0.0950 | 0.0140  |
| integer math         | 0.0743 | 0.0085  |
| collection iterate   | 0.1407 | 0.0310  |
| collection write     | 0.0440 | 0.0017  |
| string compare       | 0.0100 | 0.0130  |
| hanoi @ blocks: 8   |  0.00000000 | 0.00000147  |
| 16                   | 0.0010     | 0.0003 |
| 20                   | ut     | ut |
| 21                   | ut     | ut |
| 22                   | ut     | ut |
| 24                   | 0.3933 | 0.0671  |

Notes:

1. Zig v0.14.0

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
| hanoi | 4.7 | 0.9 | 12.6 | 12.9 | 7.9 | 8.2 | 1.8 | 1.0 | 4.0 |

Notes:

1. Each test was run three times.
2. The Java alloc value (846.8) was extrapolated from 1000 iterations, rather than the 100,000 used in other images.
3. ObjectConnect provided commentary regarding Smalltalk/MT performance metrics.
