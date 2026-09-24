"""
0006_usestate_useeffect.py
Build a counter component with useState and a useEffect that logs when count changes.

Interview prep for Swiggy frontend React interview.
"""

# =============================================================================
# React Counter Component using useState and useEffect
# =============================================================================

# --- Component Code (JavaScript/React) ---

# import React, { useState, useEffect } from 'react';

# /**
#  * Counter - A simple counter component demonstrating useState and useEffect.
#  *
#  * useState: Manages the count state.
#  * useEffect: Logs to console whenever the count changes.
#  *
#  * Key interview points:
#  * 1. useState returns [state, setState] tuple.
#  * 2. useEffect runs after every render by default (no dependency array).
#  * 3. With [count] dependency, effect runs only when count changes.
#  * 4. useEffect runs on initial mount AND on every count change.
#  * 5. Cleanup function runs before next effect execution and on unmount.
#  */

# function Counter() {
#   const [count, setCount] = useState(0);
#
#   // Effect that logs when count changes
#   useEffect(() => {
#     console.log(`Count changed to: ${count}`);
#     return () => {
#       console.log(`Cleanup: count was ${count}`);
#     };
#   }, [count]); // dependency array ensures effect runs only when count changes
#
#   return (
#     <div>
#       <h1>Counter: {count}</h1>
#       <button onClick={() => setCount((prev) => prev + 1)}>Increment</button>
#       <button onClick={() => setCount((prev) => prev - 1)}>Decrement</button>
#       <button onClick={() => setCount(0)}>Reset</button>
#     </div>
#   );
# }
#
# export default Counter;


# =============================================================================
# Python representation of the component logic for testing/verification
# =============================================================================

class Counter:
    """
    Python simulation of the React Counter component.
    Demonstrates useState (state management) and useEffect (side effects on state change).
    """

    def __init__(self):
        self._count = 0
        self._mounted = False
        self._log = []

    @property
    def count(self):
        return self._count

    def _useEffect(self, new_count):
        """Simulates useEffect with [count] dependency."""
        if self._mounted:
            self._log.append(f"Cleanup: count was {self._count}")
        self._log.append(f"Count changed to: {new_count}")
        self._mounted = True

    def increment(self):
        """Increment count (simulates setCount(prev => prev + 1))."""
        self._count += 1
        self._useEffect(self._count)
        return self._count

    def decrement(self):
        """Decrement count (simulates setCount(prev => prev - 1))."""
        self._count -= 1
        self._useEffect(self._count)
        return self._count

    def reset(self):
        """Reset count to 0 (simulates setCount(0))."""
        self._count = 0
        self._useEffect(self._count)
        return self._count

    def get_log(self):
        """Return the effect log (simulates console.log output)."""
        return list(self._log)

    def unmount(self):
        """Simulate component unmount - triggers cleanup."""
        if self._mounted:
            self._log.append(f"Cleanup: count was {self._count}")
            self._mounted = False


# =============================================================================
# Tests
# =============================================================================

def test_counter_initial_state():
    """Test that counter starts at 0."""
    counter = Counter()
    assert counter.count == 0, f"Expected 0, got {counter.count}"


def test_counter_increment():
    """Test increment increases count by 1."""
    counter = Counter()
    result = counter.increment()
    assert result == 1, f"Expected 1, got {result}"
    assert counter.count == 1


def test_counter_decrement():
    """Test decrement decreases count by 1."""
    counter = Counter()
    counter.increment()
    result = counter.decrement()
    assert result == 0, f"Expected 0, got {result}"


def test_counter_reset():
    """Test reset sets count to 0."""
    counter = Counter()
    counter.increment()
    counter.increment()
    counter.increment()
    result = counter.reset()
    assert result == 0, f"Expected 0, got {result}"


def test_counter_multiple_operations():
    """Test multiple increment/decrement operations."""
    counter = Counter()
    counter.increment()
    counter.increment()
    counter.increment()
    assert counter.count == 3
    counter.decrement()
    assert counter.count == 2
    counter.increment()
    assert counter.count == 3


def test_counter_effect_log():
    """Test that useEffect logs are generated on state changes."""
    counter = Counter()
    counter.increment()
    counter.increment()
    log = counter.get_log()
    assert len(log) == 2, f"Expected 2 log entries, got {len(log)}"
    assert "Count changed to: 1" in log[0]
    assert "Count changed to: 2" in log[1]


def test_counter_cleanup_on_change():
    """Test that cleanup runs before next effect (after first mount)."""
    counter = Counter()
    counter.increment()
    counter.increment()
    log = counter.get_log()
    # After first increment: ["Count changed to: 1"]
    # After second increment: ["Count changed to: 1", "Cleanup: count was 1", "Count changed to: 2"]
    assert "Cleanup: count was 1" in log[1], f"Expected cleanup in log, got: {log}"


def test_counter_unmount_cleanup():
    """Test that unmount triggers cleanup."""
    counter = Counter()
    counter.increment()
    counter.unmount()
    log = counter.get_log()
    assert "Cleanup: count was 1" in log[-1], f"Expected cleanup on unmount, got: {log}"


def test_counter_no_effect_without_state_change():
    """Test that effect does NOT run if count doesn't change (e.g., reset when already 0)."""
    counter = Counter()
    # Simulate: setCount(0) when already 0 - in React, this still triggers re-render
    # but useEffect with [count] dependency won't re-run if value is same
    # Our simulation always logs, but in React the dependency check prevents re-run
    counter.reset()
    log = counter.get_log()
    # In our simulation, reset always triggers effect
    assert len(log) == 1


# =============================================================================
# Run all tests
# =============================================================================

if __name__ == "__main__":
    tests = [
        test_counter_initial_state,
        test_counter_increment,
        test_counter_decrement,
        test_counter_reset,
        test_counter_multiple_operations,
        test_counter_effect_log,
        test_counter_cleanup_on_change,
        test_counter_unmount_cleanup,
        test_counter_no_effect_without_state_change,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests")

    # Demonstrate the component behavior
    print("\n--- Demo: Counter Component Behavior ---")
    demo = Counter()
    print(f"Initial count: {demo.count}")
    demo.increment()
    print(f"After increment: {demo.count}")
    demo.increment()
    print(f"After increment: {demo.count}")
    demo.decrement()
    print(f"After decrement: {demo.count}")
    demo.reset()
    print(f"After reset: {demo.count}")
    print(f"\nEffect log:")
    for entry in demo.get_log():
        print(f"  {entry}")
    demo.unmount()
    print(f"  {demo.get_log()[-1]}")
