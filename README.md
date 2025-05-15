# STIC Smalltalk benchmark

A translation to Toit, of a Smalltalk benchmark written by the Smalltalk Industry Council (STIC) in the late 90's.  
It is only published for comparison to the original Smalltalk benchmark and to enable results to be reproduced.  
See also the [original post](https://ekorau.com/some-numbers/).

### Update 2025-05-14

The Toit code has had minor updates since the original post.  
A comparison of several language implementations on an embedded target.

STIC benchmark

| Test | Toit | uLisp  | CircuitPython |
| :-- | --: | --: | --: |
| alloc | 16.0 | 21.6 | 11.4 |
| array write | 19.4 | 98.1 | 63.3 |
| dictionary write | 5.7 | 1.4 | 0.9 |
| float math | 41.1 | 124.3 | 20.9 |
| integer math | 9.4 | 122.5 | 14.4 |
| collection iterate | 12.7 | 42.5 | 29.2 |
| collection write | 9.5 | 6.7 | 15.4 |
| string compare | 1.5 | 12.5 | 2.9 |
| hanoi @ blocks:  8 | 0.0000 | 0.01 | 0.01 |
| 16 | 0.2 | 3.2 | 1.4 |
|   20 | 3.0 | 54.2 | 21.6 |
|  21 | ut | ut | 43.1 |
|  22 | ut | ut | se |
| 24 | 49.2 | 924.1 | se |

Notes:  

1) ut: un-tested,  se: stack exhausted
2) Hardware:
   - Espressif ESP32 DevKitc V4 WROOM-32E  
3) Software:  
    - Toit v2.0.0-alpha.180
    - uLisp v4.7
    - Adafruit CircuitPython 9.2.7
    
On an i3-12100 desktop machine, using Zig v0.14.0

| Test                 | Toit   | Zig     |
| :------------------- | -----: | ------: |
| alloc                | 0.0473 | 2.7775  |
| array write          | 0.1373 | 0.0155  |
| dictionary write     | 0.0217 | 0.0250  |
| float math           | 0.0950 | 0.0140  |
| integer math         | 0.0743 | 0.0085  |
| collection iterate   | 0.1407 | 0.0310  |
| collection write     | 0.0440 | 0.0017  |
| string compare       | 0.0100 | 0.0130  |
| hanoi @ blocks: 16   | 0.0010 | 0.0003  |
| 20                   | ut     | ut |
| 21                   | ut     | ut |
| 22                   | ut     | ut |
| 24                   | 0.3933 | 0.0671  |

 