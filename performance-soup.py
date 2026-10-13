#!/usr/bin/env python3
# Adapt performance-host.nsl for Primordial Soup (README, Intel i3 table, note 3):
# the clock, Soup's collection classes, and asFloat on float literals (Soup reads 87.0 as a Fraction).
# Usage: performance-soup.py performance-host.nsl PerformanceBench.ns
#   then: primordialsoup CompilerApp.vfuel newspeak/*.ns PerformanceBench.ns Runtime PerformanceBench perf.vfuel
#         primordialsoup perf.vfuel
import re, sys
s = open(sys.argv[1]).read()
s = re.sub(r"^\s*\(\*.*?\*\)\s*", "", s, count=1, flags=re.S)  # Soup wants the class first
s = s.replace("0 millis", "sw elapsedMilliseconds")
s = s.replace("public class Performance usingPlatform: platform = () (",
              "public class Performance usingPlatform: platform = (| sw = platform time Stopwatch new start. Map = platform collections Map. List = platform collections List. |) (")
s = s.replace("platform Dictionary new", "Map new")
s = s.replace("platform OrderedCollection new", "List new")
s = re.sub(r"(-?\d+\.\d+)(?=\.)", r"\1 asFloat", s)
open(sys.argv[2], "w").write(s)
