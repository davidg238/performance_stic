# Copyright 2011 Google Inc. All Rights Reserved.
# Copyright 1996 John Maloney and Mario Wolczko
# Distributed under the GNU General Public License v2 or later (this file
# derives, via deltablue.toit in this directory, from the GNU Smalltalk /
# V8 / Dart lineage of the benchmark — see deltablue.toit for the full
# notice).
#
# A Python implementation of the DeltaBlue incremental constraint solver
# benchmark (Freeman-Benson & Maloney, CACM January 1990).
#
# Authored for the stic cross-VM benchmark family as a direct translation
# of deltablue.toit (this directory); runs on CPython and CircuitPython.
# chain_test uses the SOM-lineage shape the nsl/tuvm column runs
# (n variables, n-1 equality constraints, n verified plan executions) so
# all columns do identical work.  Output format matches the nsl
# deltablue.ns node: "deltablue: <ms>" per run of
# (chain_test(50) + projection_test(50)), then "verified: <bool>" and
# "done".  The workload self-verifies: any wrong plan raises.

import time


class Strength:
    def __init__(self, value, name):
        self.value = value
        self.name = name

    def next_weaker(self):
        return WEAKER_TABLE[self.value]


REQUIRED = Strength(0, "required")
STRONG_PREFERRED = Strength(1, "strongPreferred")
PREFERRED = Strength(2, "preferred")
STRONG_DEFAULT = Strength(3, "strongDefault")
NORMAL = Strength(4, "normal")
WEAK_DEFAULT = Strength(5, "weakDefault")
WEAKEST = Strength(6, "weakest")

WEAKER_TABLE = [WEAKEST, WEAK_DEFAULT, NORMAL, STRONG_DEFAULT, PREFERRED, STRONG_PREFERRED]


def stronger(s1, s2):
    return s1.value < s2.value


def weaker(s1, s2):
    return s1.value > s2.value


def weakest_of(s1, s2):
    return s1 if weaker(s1, s2) else s2


# Directions.
NONE = 1
FORWARD = 2
BACKWARD = 0

planner = None


class Constraint:
    def __init__(self, strength):
        self.strength = strength

    def add_constraint(self):
        self.add_to_graph()
        planner.incremental_add(self)

    def satisfy(self, mark):
        self.choose_method(mark)
        if not self.is_satisfied():
            if self.strength is REQUIRED:
                raise Exception("Could not satisfy a required constraint!")
            return None
        self.mark_inputs(mark)
        out = self.output()
        overridden = out.determined_by
        if overridden is not None:
            overridden.mark_unsatisfied()
        out.determined_by = self
        if not planner.add_propagate(self, mark):
            raise Exception("Cycle encountered")
        out.mark = mark
        return overridden

    def destroy_constraint(self):
        if self.is_satisfied():
            planner.incremental_remove(self)
        self.remove_from_graph()

    def is_input(self):
        return False


class UnaryConstraint(Constraint):
    def __init__(self, strength, my_output):
        Constraint.__init__(self, strength)
        self.my_output = my_output
        self.satisfied = False
        self.add_constraint()

    def add_to_graph(self):
        self.my_output.add_constraint(self)
        self.satisfied = False

    def choose_method(self, mark):
        self.satisfied = (self.my_output.mark != mark
                          and stronger(self.strength, self.my_output.walk_strength))

    def is_satisfied(self):
        return self.satisfied

    def mark_inputs(self, mark):
        pass  # No inputs.

    def output(self):
        return self.my_output

    def recalculate(self):
        self.my_output.walk_strength = self.strength
        self.my_output.stay = not self.is_input()
        if self.my_output.stay:
            self.execute()  # Stay optimization.

    def mark_unsatisfied(self):
        self.satisfied = False

    def inputs_known(self, mark):
        return True

    def remove_from_graph(self):
        self.my_output.remove_constraint(self)
        self.satisfied = False


class StayConstraint(UnaryConstraint):
    def execute(self):
        pass  # Stay constraints do nothing.


class EditConstraint(UnaryConstraint):
    def is_input(self):
        return True

    def execute(self):
        pass  # Edit constraints do nothing.


class BinaryConstraint(Constraint):
    def __init__(self, strength, v1, v2):
        Constraint.__init__(self, strength)
        self.v1 = v1
        self.v2 = v2
        self.direction = NONE
        self.add_constraint()

    def choose_method(self, mark):
        if self.v1.mark == mark:
            self.direction = (FORWARD if self.v2.mark != mark
                              and stronger(self.strength, self.v2.walk_strength)
                              else NONE)
        elif self.v2.mark == mark:
            self.direction = (BACKWARD if self.v1.mark != mark
                              and stronger(self.strength, self.v1.walk_strength)
                              else NONE)
        elif weaker(self.v1.walk_strength, self.v2.walk_strength):
            self.direction = (BACKWARD if stronger(self.strength, self.v1.walk_strength)
                              else NONE)
        else:
            self.direction = (FORWARD if stronger(self.strength, self.v2.walk_strength)
                              else BACKWARD)

    def add_to_graph(self):
        self.v1.add_constraint(self)
        self.v2.add_constraint(self)
        self.direction = NONE

    def is_satisfied(self):
        return self.direction != NONE

    def mark_inputs(self, mark):
        self.input().mark = mark

    def input(self):
        return self.v1 if self.direction == FORWARD else self.v2

    def output(self):
        return self.v2 if self.direction == FORWARD else self.v1

    def recalculate(self):
        ihs = self.input()
        out = self.output()
        out.walk_strength = weakest_of(self.strength, ihs.walk_strength)
        out.stay = ihs.stay
        if out.stay:
            self.execute()

    def mark_unsatisfied(self):
        self.direction = NONE

    def inputs_known(self, mark):
        i = self.input()
        return i.mark == mark or i.stay or i.determined_by is not None

    def remove_from_graph(self):
        self.v1.remove_constraint(self)
        self.v2.remove_constraint(self)
        self.direction = NONE


class ScaleConstraint(BinaryConstraint):
    def __init__(self, strength, v1, v2, scale, offset):
        # scale/offset must be set before add_constraint (called by the
        # superclass constructor) reaches our add_to_graph.
        self.scale = scale
        self.offset = offset
        BinaryConstraint.__init__(self, strength, v1, v2)

    def add_to_graph(self):
        BinaryConstraint.add_to_graph(self)
        self.scale.add_constraint(self)
        self.offset.add_constraint(self)

    def remove_from_graph(self):
        BinaryConstraint.remove_from_graph(self)
        self.scale.remove_constraint(self)
        self.offset.remove_constraint(self)

    def mark_inputs(self, mark):
        BinaryConstraint.mark_inputs(self, mark)
        self.scale.mark = mark
        self.offset.mark = mark

    def execute(self):
        if self.direction == FORWARD:
            self.v2.value = self.v1.value * self.scale.value + self.offset.value
        else:
            self.v1.value = (self.v2.value - self.offset.value) // self.scale.value

    def recalculate(self):
        ihs = self.input()
        out = self.output()
        out.walk_strength = weakest_of(self.strength, ihs.walk_strength)
        out.stay = ihs.stay and self.scale.stay and self.offset.stay
        if out.stay:
            self.execute()


class EqualityConstraint(BinaryConstraint):
    def execute(self):
        self.output().value = self.input().value


class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.determined_by = None
        self.mark = 0
        self.walk_strength = WEAKEST
        self.stay = True
        self.constraints = []

    def add_constraint(self, c):
        self.constraints.append(c)

    def remove_constraint(self, c):
        self.constraints = [x for x in self.constraints if x is not c]
        if self.determined_by is c:
            self.determined_by = None


class Planner:
    def __init__(self):
        self.current_mark = 0

    def incremental_add(self, c):
        mark = self.new_mark()
        overridden = c.satisfy(mark)
        while overridden is not None:
            overridden = overridden.satisfy(mark)

    def incremental_remove(self, c):
        out = c.output()
        c.mark_unsatisfied()
        c.remove_from_graph()
        unsatisfied = self.remove_propagate_from(out)
        strength = REQUIRED
        while True:
            for u in unsatisfied:
                if u.strength is strength:
                    self.incremental_add(u)
            strength = strength.next_weaker()
            if strength is WEAKEST:
                break

    def new_mark(self):
        self.current_mark += 1
        return self.current_mark

    def make_plan(self, sources):
        mark = self.new_mark()
        plan = Plan()
        todo = sources
        while todo:
            c = todo.pop()
            if c.output().mark != mark and c.inputs_known(mark):
                plan.add_constraint(c)
                c.output().mark = mark
                self.add_constraints_consuming_to(c.output(), todo)
        return plan

    def extract_plan_from_constraints(self, constraints):
        sources = []
        for c in constraints:
            if c.is_input() and c.is_satisfied():
                sources.append(c)
        return self.make_plan(sources)

    def add_propagate(self, c, mark):
        todo = [c]
        while todo:
            d = todo.pop()
            if d.output().mark == mark:
                self.incremental_remove(c)
                return False
            d.recalculate()
            self.add_constraints_consuming_to(d.output(), todo)
        return True

    def remove_propagate_from(self, out):
        out.determined_by = None
        out.walk_strength = WEAKEST
        out.stay = True
        unsatisfied = []
        todo = [out]
        while todo:
            v = todo.pop()
            for c in v.constraints:
                if not c.is_satisfied():
                    unsatisfied.append(c)
            determining = v.determined_by
            for c in v.constraints:
                if c is not determining and c.is_satisfied():
                    c.recalculate()
                    todo.append(c.output())
        return unsatisfied

    def add_constraints_consuming_to(self, v, coll):
        determining = v.determined_by
        for c in v.constraints:
            if c is not determining and c.is_satisfied():
                coll.append(c)


class Plan:
    def __init__(self):
        self.list = []

    def add_constraint(self, c):
        self.list.append(c)

    def execute(self):
        for c in self.list:
            c.execute()


def chain_test(n):
    # SOM-lineage shape: n variables, n-1 equality constraints.
    global planner
    planner = Planner()
    prev = None
    first = None
    last = None
    for i in range(1, n + 1):
        v = Variable("v%d" % i, 0)
        if prev is not None:
            EqualityConstraint(REQUIRED, prev, v)
        if i == 1:
            first = v
        if i == n:
            last = v
        prev = v
    StayConstraint(STRONG_DEFAULT, last)
    edit = EditConstraint(PREFERRED, first)
    plan = planner.extract_plan_from_constraints([edit])
    for i in range(1, n + 1):
        first.value = i
        plan.execute()
        if last.value != i:
            raise Exception("Chain test failed: %d != %d" % (last.value, i))
    edit.destroy_constraint()


def projection_test(n):
    global planner
    planner = Planner()
    scale = Variable("scale", 10)
    offset = Variable("offset", 1000)
    src = None
    dst = None
    dests = []
    for i in range(n):
        src = Variable("src%d" % i, i)
        dst = Variable("dst%d" % i, i)
        dests.append(dst)
        StayConstraint(NORMAL, src)
        ScaleConstraint(REQUIRED, src, dst, scale, offset)
    change(src, 17)
    if dst.value != 1170:
        raise Exception("Projection 1 failed")
    change(dst, 1050)
    if src.value != 5:
        raise Exception("Projection 2 failed")
    change(scale, 5)
    for i in range(n - 1):
        if dests[i].value != i * 5 + 1000:
            raise Exception("Projection 3 failed")
    change(offset, 2000)
    for i in range(n - 1):
        if dests[i].value != i * 5 + 2000:
            raise Exception("Projection 4 failed")


def change(v, new_value):
    edit = EditConstraint(PREFERRED, v)
    plan = planner.extract_plan_from_constraints([edit])
    for _ in range(10):
        v.value = new_value
        plan.execute()
    edit.destroy_constraint()


def main():
    ok = True
    for _ in range(3):
        try:
            start = time.monotonic()
            chain_test(50)
            projection_test(50)
            elapsed = time.monotonic() - start
            print("deltablue: %d" % int(elapsed * 1000))
        except Exception as e:
            ok = False
            print("deltablue: FAILED (%s)" % e)
    print("verified: %s" % ("true" if ok else "false"))
    print("done")


main()
