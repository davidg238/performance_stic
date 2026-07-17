# STIC Smalltalk benchmark

A translation to Toit, of a Smalltalk benchmark written by the Smalltalk Industry Council (STIC) in the late 90's.  
It is only published for comparison to the original Smalltalk benchmark and to enable results to be reproduced.  
See also the [original post](https://ekorau.com/some-numbers/).

### Update 2025-05-14

The Toit code has had minor updates since the original post.  
A comparison of several language implementations on an embedded target.

STIC benchmark

| Test | Toit | uLisp  | CircuitPython | tuvm/nsl † |
| --: | --: | --: | --: | --: |
| alloc | 16.0 | 21.6 | 11.4 | 24.1 |
| array write | 19.4 | 98.1 | 63.3 | 138.9 |
| dictionary write | 5.7 | 1.4 | 0.9 | 43.3 |
| float math | 41.1 | 124.3 | 20.9 | 35.1 |
| integer math | 9.4 | 122.5 | 14.4 | 15.3 |
| collection iterate | 12.7 | 42.5 | 29.2 | 532.6 |
| collection write | 9.5 | 6.7 | 15.4 | 97.0 |
| string compare | 1.5 | 12.5 | 2.9 | 5.2 |
| hanoi @ blocks:  8 | 0.0000 | 0.01 | 0.01 | 0.004 |
| 16 | 0.2 | 3.2 | 1.4 | ut |
|   20 | 3.0 | 54.2 | 21.6 | ut |
|  21 | ut | ut | 43.1 | ut |
|  22 | ut | ut | se | ut |
| 24 | 49.2 | 924.1 | se | ut |

Notes:  

1) ut: un-tested,  se: stack exhausted
2) Hardware:
   - Espressif ESP32 DevKitc V4 WROOM-32E  
3) Software:  
    - Toit v2.0.0-alpha.180
    - uLisp v4.7
    - Adafruit CircuitPython 9.2.7

† tuvm/nsl column (2026-07-16, preliminary — not yet a peer of the other
columns): a **single run**, not a mean of 3; on **Zephyr 4.2.0**, not
ESP-IDF/FreeRTOS; on an ESP32-D0WDQ6 devkit **rev v1.0**, not the WROOM-32E
above; 96 KB VM heap. Port: `performance.ns` (nsl), semantics and counts from
`performance.toit`. Measurement provenance and caveats:
`~/workspace/tuvm/zephyr/docs/results.md` (E4; VM-side trial branches exist
that halve collection iterate — E6 — but are unmerged and not quoted here).
    
## Program-shaped benchmarks: Richards and DeltaBlue

The STIC rows above are single-mechanism spin loops. Richards (the classic
OS-task-dispatcher simulation, Martin Richards / V8 lineage) and DeltaBlue
(the incremental constraint solver, Freeman-Benson & Maloney) are the
complementary *program-shaped* pair: polymorphic dispatch, linked structures,
branchy control flow, no single hot loop — and both **self-verify** (Richards
by its canonical scheduling counts 23246/9297; DeltaBlue by checking every
plan execution).

Files, one per language, all printing the same format
(`richards: <ms>` / `deltablue: <ms>` per run, 3 runs, then
`verified: <bool>`):

- `richards.toit`, `deltablue.toit` — adapted from the Toit repo's ports
  (classes verbatim; timed harness added).
- `richards.py`, `deltablue.py` — direct translations of the same, for
  CircuitPython (also run on CPython).
- nsl: `~/workspace/nsl-tests/00_perf/richards.ns` and `deltablue.ns`
  (SOM-lineage bodies, same timed harness).

Workload definitions: Richards = one canonical run (idle count 10000).
DeltaBlue = `chain_test(50)` + `projection_test(50)`, SOM shape (50
variables / 49 equality constraints, 50 verified plan executions; the
Toit/Python chain tests were matched to this shape so all columns do
identical work). n=50 rather than the canonical 100 because n=100's live
constraint graph overruns the tuvm column's 96 KB device heap.

| Benchmark (seconds/run) | Toit | CircuitPython | tuvm/nsl † |
| --: | --: | --: | --: |
| richards | tbr | tbr | 17.6 |
| deltablue | tbr | tbr | 1.16 |

tbr: to be run. The tuvm/nsl figures are means of 3 same-binary runs
(richards 17.549/17.658/17.677 s at 96 KB VM heap; deltablue
1.160/1.164/1.159 s at 112 KB — DeltaBlue's constraint graph needs the
larger arena, see tuvm's results ledger). Same hardware/software caveats
as the † footnote above.

On an i3-12100 desktop machine, using Zig v0.14.0

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

 