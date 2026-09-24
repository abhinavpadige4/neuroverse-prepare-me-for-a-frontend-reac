"""
Event Loop Prediction: setTimeout / Promise / queueMicrotask

This module demonstrates the JavaScript event loop execution order
by predicting the output of a mixed async snippet and explaining why.

Swiggy Interview Prep — Frontend React (Day 1 of 4)
"""

# ──────────────────────────────────────────────────────────────────────
# THE SNIPPET (JavaScript)
# ──────────────────────────────────────────────────────────────────────

SNIPPET = """\
console.log('1: script start');

setTimeout(() => {
  console.log('2: setTimeout callback');
}, 0);

Promise.resolve().then(() => {
  console.log('3: promise .then');
});

queueMicrotask(() => {
  console.log('4: queueMicrotask');
});

async function asyncFn() {
  console.log('5: async function body');
}
asyncFn();

console.log('6: script end');
"""

# ──────────────────────────────────────────────────────────────────────
# PREDICTED OUTPUT
# ──────────────────────────────────────────────────────────────────────

PREDICTED_OUTPUT = [
    "1: script start",
    "5: async function body",
    "6: script end",
    "4: queueMicrotask",
    "3: promise .then",
    "2: setTimeout callback",
]

# ──────────────────────────────────────────────────────────────────────
# EXPLANATION
# ──────────────────────────────────────────────────────────────────────

EXPLANATION = """\
JavaScript Event Loop Execution Order
======================================

The JavaScript runtime uses a single-threaded event loop with three
key queues:

1. CALL STACK — synchronous code executes here first.
2. MICROTASK QUEUE — Promises (.then/.catch/finally), queueMicrotask,
   MutationObserver. Drained COMPLETELY after each synchronous task.
3. MACROTASK QUEUE — setTimeout, setInterval, I/O, UI events.
   Only ONE macrotask runs per loop iteration.

Step-by-step walkthrough of the snippet:

  1. '1: script start' — synchronous, runs immediately.

  2. setTimeout(fn, 0) — schedules fn in the MACROTASK queue.
     Even with 0ms delay, it waits for the current synchronous code
     AND all microtasks to finish.

  3. Promise.resolve().then(fn) — schedules fn in the MICROTASK queue.
     Promise callbacks are microtasks.

  4. queueMicrotask(fn) — schedules fn in the MICROTASK queue.
     This is the explicit microtask API (same priority as Promise).

  5. asyncFn() — the body of an async function runs synchronously
     up to the first await. Since there is no await, the entire body
     executes synchronously. '5: async function body' prints now.

  6. '6: script end' — synchronous, runs immediately.

  --- Synchronous code is done. Event loop drains microtask queue ---

  7. queueMicrotask callback runs: '4: queueMicrotask'
     (queued before the Promise .then, so it runs first)

  8. Promise .then callback runs: '3: promise .then'

  --- Microtask queue is empty. Event loop picks next macrotask ---

  9. setTimeout callback runs: '2: setTimeout callback'

Key takeaways for the interview:

  • setTimeout(fn, 0) does NOT mean 'run immediately'. It means
    'run after the current call stack and all microtasks finish'.

  • Microtasks ALWAYS run before macrotasks.

  • Within the microtask queue, order is FIFO (first-in-first-out).

  • An async function body runs synchronously until the first await.

  • Promise.resolve().then() is a microtask, not a macrotask.

  • queueMicrotask is the lowest-level microtask scheduling API.

Common interview follow-ups:

  Q: What if setTimeout had a delay of 100ms?
  A: Same order — setTimeout is still a macrotask. The delay only
     affects WHEN it becomes eligible, not its queue type.

  Q: What if we add another setTimeout after the first one?
  A: Both go to the macrotask queue in order. After microtasks drain,
     the first setTimeout runs, then the event loop checks if the
     second is eligible, and runs it.

  Q: What about process.nextTick in Node.js?
  A: process.nextTick has HIGHER priority than Promises. It runs
     before Promise microtasks in Node.js (but not in browsers).

  Q: How does this relate to React?
  A: React 18 uses microtasks (via MessageChannel or setTimeout) for
     scheduling updates. Understanding the event loop helps you debug
     why state updates appear 'batched' or why effects fire in a
     certain order.
"""

# ──────────────────────────────────────────────────────────────────────
# VERIFICATION FUNCTION
# ──────────────────────────────────────────────────────────────────────

def verify_output(actual_output: list[str]) -> bool:
    """Compare actual browser output with predicted output."""
    return actual_output == PREDICTED_OUTPUT


def print_full_solution() -> None:
    """Print the complete solution for study."""
    print("=" * 60)
    print("EVENT LOOP PREDICTION — JavaScript Async Execution")
    print("=" * 60)
    print()
    print("--- JavaScript Snippet ---")
    print(SNIPPET)
    print()
    print("--- Predicted Output ---")
    for i, line in enumerate(PREDICTED_OUTPUT, 1):
        print(f"  {i}. {line}")
    print()
    print("--- Explanation ---")
    print(EXPLANATION)


# ──────────────────────────────────────────────────────────────────────
# ADDITIONAL PRACTICE SNIPPETS
# ──────────────────────────────────────────────────────────────────────

PRACTICE_1 = """\
// Practice 1: Nested microtasks
Promise.resolve().then(() => {
  console.log('A');
  Promise.resolve().then(() => console.log('B'));
});
console.log('C');
// Output: C, A, B
// 'C' is sync. 'A' is microtask. 'B' is a microtask queued
// during microtask execution — it runs after 'A' but before
// any macrotask.
"""

PRACTICE_2 = """\
// Practice 2: setTimeout inside Promise
Promise.resolve().then(() => {
  setTimeout(() => console.log('A'), 0);
  console.log('B');
});
setTimeout(() => console.log('C'), 0);
// Output: B, C, A
// 'B' is a microtask (runs first).
// 'C' is a macrotask queued before 'A'.
// 'A' is a macrotask queued during microtask execution,
// so it runs after 'C'.
"""

PRACTICE_3 = """\
// Practice 3: async/await ordering
async function f1() {
  console.log('1');
  await Promise.resolve();
  console.log('2');
}
async function f2() {
  console.log('3');
  await Promise.resolve();
  console.log('4');
}
f1();
f2();
console.log('5');
// Output: 1, 3, 5, 2, 4
// '1' and '3' run synchronously (before first await).
// '5' runs synchronously.
// '2' and '4' are microtasks queued in order.
"""

PRACTICE_SNIPPETS = [PRACTICE_1, PRACTICE_2, PRACTICE_3]


if __name__ == "__main__":
    print_full_solution()
    print()
    print("=" * 60)
    print("ADDITIONAL PRACTICE SNIPPETS")
    print("=" * 60)
    for i, snippet in enumerate(PRACTICE_SNIPPETS, 1):
        print(f"\n--- Practice {i} ---")
        print(snippet)
