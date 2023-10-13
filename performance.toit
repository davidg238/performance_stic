// Copyright (c) 2023, Ekorau LLC


class SimpleHanoi:

  hanoi:
    runtime := Duration.of:
      move 22 --from 1 --to 2 --pile 3
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
      100000.repeat :
        a := List 10
        b := List 10
        c := List 10
        d := List 10
        e := List 10
        f := List 10
        g := List 10
        h := List 10
        i := List 10
        j := List 10
    return runtime.in-ms / 1000.0

  array-write-speed-test:
    junk := SimpleHanoi
    array := List 10
    runtime := Duration.of:
      1000000.repeat :
        array[0] = junk
        array[1] = junk
        array[2] = junk
        array[3] = junk
        array[4] = junk
        array[5] = junk
        array[6] = junk
        array[7] = junk
        array[8] = junk
        array[9] = junk
    return runtime.in-ms / 1000.0

  dictionary-write-speed-test:
    junk := SimpleHanoi
    key0 := "a"
    key1 := "b"
    key2 := "c"
    key3 := "d"
    key4 := "e"
    key5 := "f"
    key6 := "g"
    key7 := "h"
    key8 := "i"
    key9 := "j"

    runtime := Duration.of:
      10000.repeat :
        dict := {:}
        dict[key0] = junk
        dict[key1] = junk
        dict[key2] = junk
        dict[key3] = junk
        dict[key4] = junk
        dict[key5] = junk
        dict[key6] = junk
        dict[key7] = junk
        dict[key8] = junk
        dict[key9] = junk
    return runtime.in-ms / 1000.0

  float-math-speed-test:
    a := 87.0
    b := 53.0
    c := -87.0
    d := 42461.0
    e := 5.0
    runtime := Duration.of:
      300000.repeat :
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
    return runtime.in-ms / 1000.0

  integer-math-speed-test:
    a := 87
    b := 53
    c := -87
    d := 42461
    e := 5
    runtime := Duration.of:
      300000.repeat :
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
        e = (e * a + b) * c + d
    return runtime.in-ms / 1000.0

  ordered-collection-iterate-speed-test:
    junk := SimpleHanoi
    oc := List 20 junk
    runtime := Duration.of:
      100000.repeat :
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
        oc.do : it
    return runtime.in-ms / 1000.0

  ordered-collection-write-speed-test:
    junk := SimpleHanoi
    runtime := Duration.of:
      100000.repeat :
        oc := List 20
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

  string-compare-speed-test:
    runtime := Duration.of :
      100000.repeat :
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
        "this is a test of a string compare of two long strings" == "this is a test of a string compare of two long strings"
    return runtime.in-ms / 1000.0


main:

  stats := process-stats --gc
  print "Full GC count $stats[9]"
  tester := SpeedTester
  one := tester.run
  stats = process-stats --gc
  print "Full GC count $stats[9]"
  tester = SpeedTester
  two := tester.run
  stats = process-stats --gc
  print "Full GC count $stats[9]"
  tester = SpeedTester
  three := tester.run

  results := List 9
  for i := 0; i < 9; i++:
    results[i] = (one[i] + two[i] + three[i]) / 3.0
  
  print "STIC benchmark ---------------------------"
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