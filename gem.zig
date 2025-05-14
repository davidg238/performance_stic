const std = @import("std");
const Allocator = std.mem.Allocator;

// Your existing timeElapsed function (it's good)
fn timeElapsed(start: u64, end: u64) f64 {
    const elapsed = end - start;
    return @as(f64, elapsed) / 1_000_000_000.0;
}

const SpeedTester = struct {
    allocator: *std.heap.GeneralPurposeAllocator(.{}),

    pub fn run(self: *SpeedTester) ![9]f64 {
        var results: [9]f64 = undefined;
        results[0] = try self.allocSpeedTest();
        results[1] = try self.arrayWriteSpeedTest(); // Assuming this and others will be implemented
        results[2] = try self.dictWriteSpeedTest();
        results[3] = try self.floatMathSpeedTest();
        results[4] = try self.intMathSpeedTest();
        results[5] = try self.collectionIterateSpeedTest();
        results[6] = try self.collectionWriteSpeedTest();
        results[7] = try self.stringCompareSpeedTest();
        results[8] = try hanoiBenchmark();
        return results;
    }

    // Corrected allocSpeedTest
    pub fn allocSpeedTest(self: *SpeedTester) !f64 {
        var timer = try std.time.Timer.start();
        for (0..100_000) |_| {
            // Ensure allocations are freed if they are not meant to accumulate,
            // though for a pure allocation speed test, this might be intended.
            // For this example, we assume the goal is to measure allocation overhead.
            var ptr = try self.allocator.allocator().alloc(u8, 10);
            // If you want to measure alloc+free, you'd free here:
            // self.allocator.allocator().free(ptr);
            // For now, sticking to the original logic of just alloc.
            _ = ptr; // to silence unused variable if not freed.
        }
        const elapsed_nanos = timer.read(); // Store the u64 result in an intermediate variable
        return @as(f64, elapsed_nanos) / 1_000_000_000.0; // Now cast the variable
    }

    // Placeholder for other methods - they would need similar fixes if they use the problematic pattern
    // For example:
    pub fn arrayWriteSpeedTest(self: *SpeedTester) !f64 {
        // To be implemented. If it uses a timer like allocSpeedTest:
        var timer = try std.time.Timer.start();
        // ... array write operations ...
        const elapsed_nanos = timer.read();
        return @as(f64, elapsed_nanos) / 1_000_000_000.0;
        // Alternatively, and perhaps cleaner:
        // return timeElapsed(0, timer.read());
    }
    pub fn dictWriteSpeedTest(self: *SpeedTester) !f64 {
        std.debug.print("dictWriteSpeedTest not implemented\n", .{});
        return 0.0; // Placeholder
    }
    pub fn floatMathSpeedTest(self: *SpeedTester) !f64 {
        std.debug.print("floatMathSpeedTest not implemented\n", .{});
        return 0.0; // Placeholder
    }
    pub fn intMathSpeedTest(self: *SpeedTester) !f64 {
        std.debug.print("intMathSpeedTest not implemented\n", .{});
        return 0.0; // Placeholder
    }
    pub fn collectionIterateSpeedTest(self: *SpeedTester) !f64 {
        std.debug.print("collectionIterateSpeedTest not implemented\n", .{});
        return 0.0; // Placeholder
    }
    pub fn collectionWriteSpeedTest(self: *SpeedTester) !f64 {
        std.debug.print("collectionWriteSpeedTest not implemented\n", .{});
        return 0.0; // Placeholder
    }
    pub fn stringCompareSpeedTest(self: *SpeedTester) !f64 {
        std.debug.print("stringCompareSpeedTest not implemented\n", .{});
        return 0.0; // Placeholder
    }
};

// Example Hanoi (no changes needed here, it uses timeElapsed correctly)
fn hanoi(n: u32, from: u32, to: u32, via: u32) void {
    if (n == 0) return;
    hanoi(n - 1, from, via, to);
    // Simulating some work - in a real benchmark, this might be a print or volatile write
    // For the purpose of the benchmark, the recursive calls are the work.
    hanoi(n - 1, via, to, from);
}

fn hanoiBenchmark() !f64 {
    var timer = try std.time.Timer.start(); // Changed to var for consistency, though const is fine if not reassigned
    hanoi(22, 1, 2, 3);
    return timeElapsed(0, timer.read()); // This correctly uses your timeElapsed function
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit(); // Good practice to deinit the allocator

    var tester = SpeedTester{ .allocator = &gpa };

    const one = try tester.run();
    const two = try tester.run();
    const three = try tester.run();

    var avg: [9]f64 = undefined;
    for (avg, 0..) |_, i| {
        avg[i] = (one[i] + two[i] + three[i]) / 3.0;
    }

    const stdout = std.io.getStdOut().writer();
    try stdout.print("STIC benchmark ---------------------------\n", .{});
    try stdout.print("alloc                 {d:.2}\n", .{avg[0]});
    try stdout.print("array write           {d:.2}\n", .{avg[1]});
    try stdout.print("dictionary write      {d:.2}\n", .{avg[2]});
    try stdout.print("float math            {d:.2}\n", .{avg[3]});
    try stdout.print("integer math          {d:.2}\n", .{avg[4]});
    try stdout.print("collection iterate    {d:.2}\n", .{avg[5]});
    try stdout.print("collection write      {d:.2}\n", .{avg[6]});
    try stdout.print("string compare        {d:.2}\n", .{avg[7]});
    try stdout.print("hanoi                 {d:.2}\n", .{avg[8]});
    try stdout.print("-------------------------------------------\n", .{});
}

