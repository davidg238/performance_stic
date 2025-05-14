// Copyright (c) 2023, 2025 Ekorau LLC

import system

ITER_10K := 10000
ITER_100K := 100000
ITER_300K := 300000
ITER_1000K := 1000000

class SimpleHanoi:

  hanoi:
    runtime := Duration.of:
      move 16 --from 1 --to 2 --pile 3
    return runtime.in-ms / 1000.0

  move number-disks /int --from source /int --to dest/int --pile temp /int:
    if number-disks == 1: return
    move number-disks - 1 --from source --to temp --pile dest
    move number-disks - 1 --from temp --to dest --pile source


class SpeedTester:

  run:
    results := List 9
    tester := SpeedTester
    simple-hanoi := SimpleHanoi
    results[0] = tester.alloc-speed-test
    results[1] = tester.array-write-speed-test
    results[2] = tester.dictionary-write-speed-test
    results[3] = tester.float-math-speed-test
    results[4] = tester.integer-math-speed-test
    results[5] = tester.ordered-collection-iterate-speed-test
    results[6] = tester.ordered-collection-write-speed-test
    results[7] = tester.string-compare-speed-test
    results[8] = simple-hanoi.hanoi
    return results

  alloc-speed-test:

    runtime := Duration.of:
      ITER_100K.repeat :
        a := List 10 --initial=0
        b := List 10 --initial=0
        c := List 10 --initial=0
        d := List 10 --initial=0
        e := List 10 --initial=0
        f := List 10 --initial=0
        g := List 10 --initial=0
        h := List 10 --initial=0
        i := List 10 --initial=0
        j := List 10 --initial=0
    return runtime.in-ms / 1000.0

  array-write-speed-test:
    junk := SimpleHanoi
    array := List 10
    runtime := Duration.of:
      ITER_1000K.repeat:
        array.size.repeat:
          array[it] = junk
    return runtime.in-ms / 1000.0

  dictionary-write-speed-test:
    junk := SimpleHanoi
    keys := ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

    runtime := Duration.of:
      ITER_10K.repeat :
        dict := {:}
        keys.do:
          dict[it] = junk
    return runtime.in-ms / 1000.0

  float-math-speed-test:
    a := 87.0
    b := 53.0
    c := -87.0
    d := 42461.0
    e := 5.0
    runtime := Duration.of:
      ITER_300K.repeat :
        10.repeat:
          e = (e * a + b) * c + d
    return runtime.in-ms / 1000.0

  float-math-speed-test-inlined:
    e := 5.0
    runtime := Duration.of:
      ITER_300K.repeat :
        10.repeat:
          e = (e * 87.0 + 53.0) * -87.0 + 42461.0
    return runtime.in-ms / 1000.0

  integer-math-speed-test:
    a := 87
    b := 53
    c := -87
    d := 42461
    e := 5
    runtime := Duration.of:
      ITER_300K.repeat :
        10.repeat:
          e = (e * a + b) * c + d
    return runtime.in-ms / 1000.0


  ordered-collection-iterate-speed-test:
    junk := SimpleHanoi
    oc := List 20 --initial=junk
    runtime := Duration.of:
      ITER_100K.repeat :
        10.repeat:
          oc.do: it
    return runtime.in-ms / 1000.0

  ordered-collection-iterate-unrolled-speed-test:
    junk := SimpleHanoi
    oc := List 20 --initial=junk
    runtime := Duration.of:
      ITER_100K.repeat :
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
        oc.do: it
    return runtime.in-ms / 1000.0

  ordered-collection-write-speed-test:
    junk := SimpleHanoi
    runtime := Duration.of:
      ITER_100K.repeat :
        oc := []
        10.repeat:
          oc.add junk
    return runtime.in-ms / 1000.0


  ordered-collection-unrolled-write-speed-test:
    junk := SimpleHanoi
    runtime := Duration.of:
      ITER_100K.repeat :
        oc := []
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
        oc.add junk
    return runtime.in-ms / 1000.0

  ordered-collection-open-write-speed-test:
    junk := SimpleHanoi
    runtime := Duration.of:
      ITER_100K.repeat :
        oc := []
        10.repeat:
          oc.add junk
    return runtime.in-ms / 1000.0

  string-compare-speed-test:
    s1 := "this is a test of a string compare of two long strings"
    s2 := "this is a test of a string compare of two long strings"
    runtime := Duration.of :
      ITER_100K.repeat :
        10.repeat:
          s1 == s2
    return runtime.in-ms / 1000.0


main:

  print "Starting STIC benchmark..."
  stats := system.process-stats --gc
  print "Full GC count $stats[9]"
  tester := SpeedTester
  one := tester.run
  stats = system.process-stats --gc
  print "Full GC count $stats[9]"
  tester = SpeedTester
  two := tester.run
  stats = system.process-stats --gc
  print "Full GC count $stats[9]"
  tester = SpeedTester
  three := tester.run

  results := List 9
  for i := 0; i < 9; i++:
    results[i] = (one[i] + two[i] + three[i]) / 3.0

  print "STIC benchmark for Toit $system.app-sdk-version ---------------------------"
  print "   (smaller numbers are better)"
  print "alloc               $(%.2f results[0])"
  print "array write         $(%.2f results[1])"
  print "dictionary write    $(%.2f results[2])"
  print "float math          $(%.2f results[3])"
  print "integer math        $(%.2f results[4])"
  print "collection iterate  $(%.2f results[5])"
  print "collection write    $(%.2f results[6])"
  print "string compare      $(%.2f results[7])"
  print "hanoi               $(%.2f results[8])"
  print "-------------------------------------------"
