// Copyright (c) 2025 Ekorau LLC

const std = @import("std");
const builtin = @import("builtin");

const Allocator = std.mem.Allocator;

const ITER_10K = 10_000;
const ITER_100K = 100_000;
const ITER_300K = 300_000;
const ITER_1000K = 1_000_000;

// Calculates elapsed time in seconds (as f64) from nanoseconds (u64).
fn timeElapsed(start: u64, end: u64) f64 {
    const elapsed = end - start;
    // Convert the u64 nanoseconds to f64 seconds.
    // Using @floatFromInt might be more explicit for the compiler.
    return @as(f64, @floatFromInt(elapsed)) / 1_000_000_000.0;
}

const SpeedTester = struct {
    allocator: *std.heap.GeneralPurposeAllocator(.{}),

    // Runs all benchmark tests and returns an array of results in seconds.
    pub fn run(self: *SpeedTester) ![9]f64 {
        var results: [9]f64 = undefined;
        results[0] = try self.allocSpeedTest();
        results[1] = try self.arrayWriteSpeedTest();
        results[2] = try self.dictWriteSpeedTest();
        results[3] = try SpeedTester.floatMathSpeedTest();
        results[4] = try SpeedTester.intMathSpeedTest();
        results[5] = try self.collectionIterateSpeedTest();
        results[6] = try self.collectionWriteSpeedTest();
        results[7] = try SpeedTester.stringCompareSpeedTest();
        results[8] = try hanoiBenchmark();
        return results;
    }

    // Tests the speed of memory allocation.
    pub fn allocSpeedTest(self: *SpeedTester) !f64 {
        var timer = try std.time.Timer.start();
        // Allocate and immediately free small chunks of memory repeatedly.
        for (0..ITER_100K) |_| {
            // Allocate 10 bytes. The memory is intentionally leaked here
            // for the benchmark, relying on the GPA to manage it.
            // In real code, you'd free this.
            // _ = try self.allocator.allocator().alloc(u8, 10);
            // If you wanted to test alloc+free:
            const mem = try self.allocator.allocator().alloc(u8, 10);
            self.allocator.allocator().free(mem);
        }
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of writing to elements of a fixed-size array.
    pub fn arrayWriteSpeedTest(self: *SpeedTester) !f64 {
        // Initialize the array elements to null.
        var array: [10]?*SpeedTester = [_]?*SpeedTester{null} ** 10;
        const junk = self; // Pointer to self to write into the array.
        var timer = try std.time.Timer.start();
        for (0..ITER_1000K) |_| {
            // Iterate over a mutable slice of the array (&array) to get pointers.
            for (&array) |*item| {
                item.* = junk; // Assign the pointer to each element.
            }
        }
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of writing to and removing from a hash map.
    pub fn dictWriteSpeedTest(self: *SpeedTester) !f64 {
        var dict = std.StringHashMap(?*SpeedTester).init(self.allocator.allocator());
        defer dict.deinit(); // Ensure dictionary memory is freed.

        const keys = [_][]const u8{ "a", "b", "c", "d", "e", "f", "g", "h", "i", "j" };
        const junk = self; // Pointer to self to store as value.

        var timer = try std.time.Timer.start();
        for (0..ITER_10K) |_| {
            // Add all keys to the dictionary.
            for (keys) |key| {
                _ = try dict.put(key, junk);
            }
            // Remove all keys from the dictionary.
            var it = dict.iterator();
            while (it.next()) |entry| {
                // Use remove entry for potentially better efficiency
                if (dict.fetchRemove(entry.key_ptr.*)) |_| {}
            }
        }
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of basic floating-point arithmetic.
    pub fn floatMathSpeedTest() !f64 {
        const a: f64 = 87.0;
        const b: f64 = 53.0;
        const c: f64 = -87.0;
        const d: f64 = 42461.0;
        var e: f64 = 5.0; // Variable to accumulate results.

        var timer = try std.time.Timer.start();
        for (0..ITER_300K) |_| {
            for (0..10) |_| {
                // Perform a series of floating-point operations.
                e = (e * a + b) * c + d;
            }
        }
        // Prevent the compiler from optimizing away the calculation by using 'e'.
        // This write ensures 'e' is potentially used.
        if (e == 0) {}
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of basic integer arithmetic.
    pub fn intMathSpeedTest() !f64 {
        const a: i32 = 87;
        const b: i32 = 53;
        const c: i32 = -87;
        const d: i32 = 42461;
        var e: i32 = 5; // Variable to accumulate results.

        var timer = try std.time.Timer.start();
        for (0..ITER_300K) |_| {
            for (0..10) |_| {
                // Perform a series of integer operations.
                e = (e * a + b) * c + d;
            }
        }
        // Prevent the compiler from optimizing away the calculation by using 'e'.
        if (e == 0) {}
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of iterating over elements in a fixed-size array.
    pub fn collectionIterateSpeedTest(self: *SpeedTester) !f64 {
        // Initialize the array elements to null.
        var oc: [20]?*SpeedTester = [_]?*SpeedTester{null} ** 20;
        const junk = self;
        // Populate the array first. Iterate over a mutable slice (&oc).
        for (&oc) |*item| {
            item.* = junk;
        }

        var timer = try std.time.Timer.start();
        for (0..ITER_100K) |_| {
            for (0..10) |_| {
                // Iterate over the array (by value is fine here).
                for (oc) |item| {
                    // Ensure the item is used to prevent optimization.
                    _ = item;
                }
            }
        }
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of creating and writing to a fixed-size array repeatedly.
    pub fn collectionWriteSpeedTest(self: *SpeedTester) !f64 {
        const junk = self;
        var timer = try std.time.Timer.start();
        for (0..ITER_100K) |_| {
            // Create and initialize the array inside the loop.
            var oc: [10]?*SpeedTester = [_]?*SpeedTester{null} ** 10;
            // Iterate over a mutable slice (&oc) to write elements.
            for (&oc) |*item| {
                item.* = junk;
            }
        }
        return timeElapsed(0, timer.read());
    }

    // Tests the speed of comparing two identical strings.
    pub fn stringCompareSpeedTest() !f64 {
        // Use string literals (comptime known).
        const s1 = "this is a test of a string compare of two long strings";
        const s2 = "this is a test of a string compare of two long strings";
        const result: bool = false; // Variable to store result.

        var timer = try std.time.Timer.start();
        for (0..ITER_100K) |_| {
            for (0..10) |_| {
                // Perform string comparison.
                _ = std.mem.eql(u8, s1, s2); // Use std.mem.eql for clarity
            }
        }
        // Prevent optimization by potentially using the result.
        if (!result) {}
        return timeElapsed(0, timer.read());
    }
};

// Recursive function to solve the Tower of Hanoi puzzle.
fn hanoi(n: u32, from: u32, to: u32, via: u32) void {
    if (n == 0) return;
    hanoi(n - 1, from, via, to);
    // In a real scenario, you might "move" the disk here.
    // std.debug.print("Move disk {} from {} to {}\n", .{ n, from, to });
    hanoi(n - 1, via, to, from);
}

// Benchmarks the Tower of Hanoi solution.
fn hanoiBenchmark() !f64 {
    var timer = try std.time.Timer.start();
    // Run Hanoi for a reasonably complex case (2^22 - 1 moves).
    hanoi(16, 1, 2, 3);
    return timeElapsed(0, timer.read());
}

// Main entry point for the benchmark program.
pub fn main() !void {
    // Initialize a general-purpose allocator.
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    // Ensure the allocator is deinitialized at the end of main.
    defer _ = gpa.deinit();
    var tester = SpeedTester{ .allocator = &gpa };

    // Run the benchmark suite three times to get an average.
    const one = try tester.run();
    const two = try tester.run();
    const three = try tester.run();

    // Calculate the average time for each test.
    var avg: [9]f64 = undefined;
    for (&avg, 0..) |*item, i| {
        item.* = (one[i] + two[i] + three[i]) / 3.0;
    }

    // Print the results to standard output.
    const stdout = std.io.getStdOut().writer();
    const version = builtin.zig_version;
    try stdout.print("STIC benchmark for Zig v{}.{}.{} ---------------------------\n", .{version.major, version.minor, version.patch});
    // Using {d:.N} format specifier for floating point numbers with N decimal places.
    try stdout.print("alloc              {d:.4}\n", .{avg[0]});
    try stdout.print("array write        {d:.4}\n", .{avg[1]});
    try stdout.print("dictionary write   {d:.4}\n", .{avg[2]});
    try stdout.print("float math         {d:.4}\n", .{avg[3]});
    try stdout.print("integer math       {d:.4}\n", .{avg[4]});
    try stdout.print("collection iterate {d:.4}\n", .{avg[5]});
    try stdout.print("collection write   {d:.4}\n", .{avg[6]});
    try stdout.print("string compare     {d:.4}\n", .{avg[7]});
    try stdout.print("hanoi              {d:.4}\n", .{avg[8]});
    try stdout.print("-------------------------------------------\n", .{});
}