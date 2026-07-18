# Copyright 2006-2008 the V8 project authors. All rights reserved.
# Redistributed under the V8 project's BSD-style license (see richards.toit
# in this directory for the full notice).
#
# This is a Python implementation of the Richards benchmark from:
#
#    http://www.cl.cam.ac.uk/~mr10/Bench.html
#
# The benchmark was originally implemented in BCPL by Martin Richards.
#
# Authored for the stic cross-VM benchmark family as a direct translation
# of richards.toit (this directory); runs on CPython and CircuitPython.
# Output format matches the nsl/tuvm richards.nsl node: "richards: <ms>" per
# run, then "verified: <bool>" and "done".  The nsl column runs the
# SOM-lineage port of the same benchmark; the two schedule identical work,
# verified by the canonical counts (23246 / 9297).

import time

# How many times a packet is queued and a task held in a correct run.
COUNT = 10000
EXPECTED_QUEUE_COUNT = 23246
EXPECTED_HOLD_COUNT = 9297

ID_IDLE = 0
ID_WORKER = 1
ID_HANDLER_A = 2
ID_HANDLER_B = 3
ID_DEVICE_A = 4
ID_DEVICE_B = 5
NUMBER_OF_IDS = 6

KIND_DEVICE = 0
KIND_WORK = 1

DATA_SIZE = 4

STATE_RUNNING = 0
STATE_RUNNABLE = 1
STATE_SUSPENDED = 2
STATE_HELD = 4
STATE_SUSPENDED_RUNNABLE = STATE_SUSPENDED | STATE_RUNNABLE
STATE_NOT_HELD = ~STATE_HELD


class Scheduler:
    def __init__(self):
        self.queue_count = 0
        self.hold_count = 0
        self.blocks = [None] * NUMBER_OF_IDS
        self.list = None
        self.current_tcb = None
        self.current_id = None

    def add_idle_task(self, ident, priority, queue, count):
        self.add_running_task(ident, priority, queue, IdleTask(self, 1, count))

    def add_worker_task(self, ident, priority, queue):
        self.add_task(ident, priority, queue, WorkerTask(self, ID_HANDLER_A, 0))

    def add_handler_task(self, ident, priority, queue):
        self.add_task(ident, priority, queue, HandlerTask(self))

    def add_device_task(self, ident, priority, queue):
        self.add_task(ident, priority, queue, DeviceTask(self))

    def add_running_task(self, ident, priority, queue, task):
        self.add_task(ident, priority, queue, task)
        self.current_tcb.set_running()

    def add_task(self, ident, priority, queue, task):
        self.current_tcb = TaskControlBlock(self.list, ident, priority, queue, task)
        self.list = self.current_tcb
        self.blocks[ident] = self.current_tcb

    def schedule(self):
        self.current_tcb = self.list
        while self.current_tcb is not None:
            tcb = self.current_tcb
            if tcb.is_held_or_suspended():
                self.current_tcb = tcb.link
            else:
                self.current_id = tcb.ident
                self.current_tcb = tcb.run()

    def hold_current(self):
        self.hold_count += 1
        self.current_tcb.mark_as_held()
        return self.current_tcb.link

    def suspend_current(self):
        self.current_tcb.mark_as_suspended()
        return self.current_tcb

    def release(self, ident):
        tcb = self.blocks[ident]
        if tcb is None:
            return tcb
        tcb.mark_as_not_held()
        if tcb.priority > self.current_tcb.priority:
            return tcb
        return self.current_tcb

    def queue(self, packet):
        t = self.blocks[packet.ident]
        if t is None:
            return t
        self.queue_count += 1
        packet.link = None
        packet.ident = self.current_id
        return t.check_priority_add(self.current_tcb, packet)


class TaskControlBlock:
    def __init__(self, link, ident, priority, queue, task):
        self.link = link
        self.ident = ident
        self.priority = priority
        self.queue = queue
        self.task = task
        self.state = STATE_SUSPENDED_RUNNABLE if queue is not None else STATE_SUSPENDED

    def set_running(self):
        self.state = STATE_RUNNING

    def mark_as_not_held(self):
        self.state &= STATE_NOT_HELD

    def mark_as_held(self):
        self.state |= STATE_HELD

    def is_held_or_suspended(self):
        return (self.state & STATE_HELD) != 0 or self.state == STATE_SUSPENDED

    def mark_as_suspended(self):
        self.state |= STATE_SUSPENDED

    def mark_as_runnable(self):
        self.state |= STATE_RUNNABLE

    def run(self):
        packet = None
        if self.state == STATE_SUSPENDED_RUNNABLE:
            packet = self.queue
            self.queue = packet.link
            self.state = STATE_RUNNABLE if self.queue is not None else STATE_RUNNING
        return self.task.run(packet)

    def check_priority_add(self, task, packet):
        if self.queue is None:
            self.queue = packet
            self.mark_as_runnable()
            if self.priority > task.priority:
                return self
        else:
            self.queue = packet.add_to(self.queue)
        return task


class IdleTask:
    def __init__(self, scheduler, v1, count):
        self.scheduler = scheduler
        self.v1 = v1
        self.count = count

    def run(self, packet):
        self.count -= 1
        if self.count == 0:
            return self.scheduler.hold_current()
        if self.v1 & 1 == 0:
            self.v1 >>= 1
            return self.scheduler.release(ID_DEVICE_A)
        self.v1 = (self.v1 >> 1) ^ 0xD008
        return self.scheduler.release(ID_DEVICE_B)


class DeviceTask:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.v1 = None

    def run(self, packet):
        if packet is None:
            if self.v1 is None:
                return self.scheduler.suspend_current()
            v = self.v1
            self.v1 = None
            return self.scheduler.queue(v)
        self.v1 = packet
        return self.scheduler.hold_current()


class WorkerTask:
    def __init__(self, scheduler, v1, v2):
        self.scheduler = scheduler
        self.v1 = v1
        self.v2 = v2

    def run(self, packet):
        if packet is None:
            return self.scheduler.suspend_current()
        self.v1 = ID_HANDLER_B if self.v1 == ID_HANDLER_A else ID_HANDLER_A
        packet.ident = self.v1
        packet.a1 = 0
        for i in range(DATA_SIZE):
            self.v2 += 1
            if self.v2 > 26:
                self.v2 = 1
            packet.a2[i] = self.v2
        return self.scheduler.queue(packet)


class HandlerTask:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.v1 = None
        self.v2 = None

    def run(self, packet):
        if packet is not None:
            if packet.kind == KIND_WORK:
                self.v1 = packet.add_to(self.v1)
            else:
                self.v2 = packet.add_to(self.v2)
        if self.v1 is not None:
            count = self.v1.a1
            if count < DATA_SIZE:
                if self.v2 is not None:
                    v = self.v2
                    self.v2 = self.v2.link
                    v.a1 = self.v1.a2[count]
                    self.v1.a1 = count + 1
                    return self.scheduler.queue(v)
            else:
                v = self.v1
                self.v1 = self.v1.link
                return self.scheduler.queue(v)
        return self.scheduler.suspend_current()


class Packet:
    def __init__(self, link, ident, kind):
        self.link = link
        self.ident = ident
        self.kind = kind
        self.a1 = 0
        self.a2 = [0] * DATA_SIZE

    def add_to(self, queue):
        self.link = None
        if queue is None:
            return self
        nxt = queue
        while nxt.link is not None:
            nxt = nxt.link
        nxt.link = self
        return queue


def run_richards():
    scheduler = Scheduler()
    scheduler.add_idle_task(ID_IDLE, 0, None, COUNT)

    queue = Packet(None, ID_WORKER, KIND_WORK)
    queue = Packet(queue, ID_WORKER, KIND_WORK)
    scheduler.add_worker_task(ID_WORKER, 1000, queue)

    queue = Packet(None, ID_DEVICE_A, KIND_DEVICE)
    queue = Packet(queue, ID_DEVICE_A, KIND_DEVICE)
    queue = Packet(queue, ID_DEVICE_A, KIND_DEVICE)
    scheduler.add_handler_task(ID_HANDLER_A, 2000, queue)

    queue = Packet(None, ID_DEVICE_B, KIND_DEVICE)
    queue = Packet(queue, ID_DEVICE_B, KIND_DEVICE)
    queue = Packet(queue, ID_DEVICE_B, KIND_DEVICE)
    scheduler.add_handler_task(ID_HANDLER_B, 3000, queue)

    scheduler.add_device_task(ID_DEVICE_A, 4000, None)
    scheduler.add_device_task(ID_DEVICE_B, 5000, None)

    scheduler.schedule()
    return scheduler


def main():
    ok = True
    for _ in range(3):
        start = time.monotonic()
        s = run_richards()
        elapsed = time.monotonic() - start
        if s.queue_count != EXPECTED_QUEUE_COUNT:
            ok = False
        if s.hold_count != EXPECTED_HOLD_COUNT:
            ok = False
        print("richards: %d" % int(elapsed * 1000))
    print("verified: %s" % ("true" if ok else "false"))
    print("done")


main()
