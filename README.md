# STIC Smalltalk benchmark

A translation to Toit, of a Smalltalk benchmark written by the Smalltalk Industry Council (STIC) in the late 90's.  
It is only published for comparison to the original Smalltalk benchmark and to enable results to be reproduced.  
See also the [original post](https://ekorau.com/some-numbers/).

### Update 2025-05-15

The code has been updated a little since the original post, to remove some potential optimizations (remove some un-rolled loops).
A trivial comparison of several language implmentations on an embedded target.

STIC benchmark

| Test | Toit | uLisp  | CircuitPython |
| --: | -- | -- | -- |
| alloc | 14.0 | 21.6 | 11.4 |
| array write | 11.6 | 98.1 | 63.3 |
| dictionary write | 5.8 | 1.4 | 0.9 |
| float math | 41.1 | 124.3 | 20.9 |
| integer math | 9.4 | 122.5 | 14.4 |
| collection iterate | 12.7 | 42.5 | 29.2 |
| collection write | 7.9 | 6.7 | 15.4 |
| string compare | 1.4 | 12.5 | 2.9 |
| hanoi @ blocks:  08 | 0.0000 | 0.01 | 0.01 |
| 16 | 0.2 | 3.2 | 1.4 |
|   20 | 3.0 | 54.2 | 21.6 |
|  21 | ut | ut | 43.1 |
|  22 | ut | ut | stack exhausted |
| 24 | 49.2 | 924.1 | stack exhausted |

Notes:  

1) ut: un-tested
2) Hardware:
   - Espressif ESP32 DevKitc V4 WROOM-32E  
3) Software:  
    - Toit v2.0.0-alpha.180
    - uLisp v4.7
    - Adafruit CircuitPython 9.2.7
    - Zig untested
 