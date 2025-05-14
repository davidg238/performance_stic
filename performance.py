import time
import gc

ITER_10K = 10000
ITER_100K = 100000
ITER_300K = 300000
ITER_1000K = 1000000


class SimpleHanoi:

    def hanoi(self):
        start = time.monotonic()
        self.move(16, 1, 2, 3)
        end = time.monotonic()
        return end - start

    def move(self, number_disks, source, dest, temp):
        if number_disks == 1:
            return
        self.move(number_disks - 1, source, temp, dest)
        self.move(number_disks - 1, temp, dest, source)


class SpeedTester:

    def run(self):
        results = [0] * 9
        simple_hanoi = SimpleHanoi()
        results[0] = self.alloc_speed_test()
        results[1] = self.array_write_speed_test()
        results[2] = self.dictionary_write_speed_test()
        results[3] = self.float_math_speed_test()
        results[4] = self.integer_math_speed_test()
        results[5] = self.ordered_collection_iterate_speed_test()
        results[6] = self.ordered_collection_write_speed_test()
        results[7] = self.string_compare_speed_test()
        results[8] = simple_hanoi.hanoi()
        return results

    def alloc_speed_test(self):
        start = time.monotonic()
        for _ in range(ITER_100K):
            a = [0] * 10
            b = [0] * 10
            c = [0] * 10
            d = [0] * 10
            e = [0] * 10
            f = [0] * 10
            g = [0] * 10
            h = [0] * 10
            i = [0] * 10
            j = [0] * 10
        return time.monotonic() - start

    def array_write_speed_test(self):
        array = [None] * 10
        junk = SimpleHanoi()
        start = time.monotonic()
        for _ in range(ITER_1000K):
            for i in range(10):
                array[i] = junk
        return time.monotonic() - start
    

    def array_write_unrolled_speed_test(self):
        array = [None] * 10
        junk = SimpleHanoi()
        start = time.monotonic()
        for _ in range(ITER_1000K):
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
        return time.monotonic() - start

    def dictionary_write_speed_test(self):
        junk = SimpleHanoi()
        keys = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        start = time.monotonic()
        for _ in range(ITER_10K):
            d = {}
            for key in keys:
                d[key] = junk
        return time.monotonic() - start

    def float_math_speed_test(self):
        a = 87.0
        b = 53.0
        c = -87.0
        d = 42461.0
        e = 5.0
        start = time.monotonic()
        for _ in range(ITER_300K):
            for _ in range(10):
                e = (e * a + b) * c + d
        return time.monotonic() - start

    def integer_math_speed_test(self):
        a = 87
        b = 53
        c = -87
        d = 42461
        e = 5
        start = time.monotonic()
        for _ in range(ITER_300K):
            for _ in range(10):
                e = (e * a + b) * c + d
        return time.monotonic() - start

    def ordered_collection_iterate_speed_test(self):
        junk = SimpleHanoi()
        oc = [junk] * 20
        start = time.monotonic()
        for _ in range(ITER_100K):
            for _ in range(10):
                for item in oc:
                    pass
        return time.monotonic() - start

    def ordered_collection_write_speed_test(self):
        junk = SimpleHanoi()
        start = time.monotonic()
        for _ in range(ITER_100K):
            oc = []
            for _ in range(10):
                oc.append(junk)
        return time.monotonic() - start

    def string_compare_speed_test(self):
        s1 = "this is a test of a string compare of two long strings"
        s2 = "this is a test of a string compare of two long strings"
        start = time.monotonic()
        for _ in range(ITER_100K):
            for _ in range(10):
                _ = (s1 == s2)
        return time.monotonic() - start


def main():
    print("Starting STIC benchmark...")
    gc.collect()
    print("... test run 1")
    tester = SpeedTester()
    one = tester.run()
    gc.collect()

    print("... test run 2")
    tester = SpeedTester()
    two = tester.run()
    gc.collect()

    print("... test run 3")
    tester = SpeedTester()
    three = tester.run()

    results = [(one[i] + two[i] + three[i]) / 3.0 for i in range(9)]

    print("STIC benchmark ---------------------------")
    print("   (smaller numbers are better)")
    print("alloc               %.2f" % results[0])
    print("array write         %.2f" % results[1])
    print("dictionary write    %.2f" % results[2])
    print("float math          %.2f" % results[3])
    print("integer math        %.2f" % results[4])
    print("collection iterate  %.2f" % results[5])
    print("collection write    %.2f" % results[6])
    print("string compare      %.2f" % results[7])
    print("hanoi               %.2f" % results[8])
    print("-------------------------------------------")


main()