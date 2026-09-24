"""
Swiggy Frontend Interview Prep - useReducer Counter
=====================================================
Rewrite the counter component using useReducer with
increment/decrement/reset actions.

Interview Focus:
- Understanding useReducer vs useState for complex state
- Action types and reducer pattern
- Dispatching actions
- Derived state and action creators
"""

# ============================================================
# REACT COMPONENT (JSX) - useReducer Counter
# ============================================================

REACT_CODE = r'''
import React, { useReducer, useCallback } from "react";

// --- Reducer Function ---
// Pure function: (state, action) => newState
function counterReducer(state, action) {
  switch (action.type) {
    case "INCREMENT":
      return { ...state, count: state.count + 1 };
    case "DECREMENT":
      return { ...state, count: state.count - 1 };
    case "RESET":
      return { ...state, count: 0 };
    case "SET_COUNT":
      return { ...state, count: action.payload };
    case "INCREMENT_BY":
      return { ...state, count: state.count + action.payload };
    default:
      return state; // Unknown action, return current state unchanged
  }
}

// --- Initial State ---
const initialState = {
  count: 0,
  history: [], // Track all changes for undo capability
};

// --- Action Creators (optional but clean) ---
const actions = {
  increment: () => ({ type: "INCREMENT" }),
  decrement: () => ({ type: "DECREMENT" }),
  reset: () => ({ type: "RESET" }),
  setCount: (value) => ({ type: "SET_COUNT", payload: value }),
  incrementBy: (amount) => ({ type: "INCREMENT_BY", payload: amount }),
};

// --- Counter Component ---
export default function Counter() {
  const [state, dispatch] = useReducer(counterReducer, initialState);

  // Memoize dispatch handlers to prevent unnecessary re-renders
  const handleIncrement = useCallback(() => dispatch(actions.increment()), []);
  const handleDecrement = useCallback(() => dispatch(actions.decrement()), []);
  const handleReset = useCallback(() => dispatch(actions.reset()), []);
  const handleIncrementBy5 = useCallback(
    () => dispatch(actions.incrementBy(5)),
    []
  );

  return (
    <div className="counter-container">
      <h2>useReducer Counter</h2>
      <p className="count-display">Count: {state.count}</p>

      <div className="button-group">
        <button onClick={handleIncrement} aria-label="Increment">
          +1
        </button>
        <button onClick={handleDecrement} aria-label="Decrement">
          -1
        </button>
        <button onClick={handleIncrementBy5} aria-label="Increment by 5">
          +5
        </button>
        <button onClick={handleReset} aria-label="Reset">
          Reset
        </button>
      </div>

      {/* Derived state example */}
      <p className="derived-info">
        Status: {state.count > 0 ? "Positive" : state.count < 0 ? "Negative" : "Zero"}
      </p>
    </div>
  );
}
'''

# ============================================================
# UNIT TESTS (Jest + React Testing Library)
# ============================================================

TEST_CODE = r'''
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import Counter from "./Counter";

describe("Counter with useReducer", () => {
  test("renders initial count of 0", () => {
    render(<Counter />);
    expect(screen.getByText("Count: 0")).toBeInTheDocument();
  });

  test("increments count on +1 click", () => {
    render(<Counter />);
    fireEvent.click(screen.getByLabelText("Increment"));
    expect(screen.getByText("Count: 1")).toBeInTheDocument();
  });

  test("decrements count on -1 click", () => {
    render(<Counter />);
    fireEvent.click(screen.getByLabelText("Decrement"));
    expect(screen.getByText("Count: -1")).toBeInTheDocument();
  });

  test("resets count to 0", () => {
    render(<Counter />);
    fireEvent.click(screen.getByLabelText("Increment"));
    fireEvent.click(screen.getByLabelText("Increment"));
    fireEvent.click(screen.getByLabelText("Reset"));
    expect(screen.getByText("Count: 0")).toBeInTheDocument();
  });

  test("increments by 5", () => {
    render(<Counter />);
    fireEvent.click(screen.getByLabelText("Increment by 5"));
    expect(screen.getByText("Count: 5")).toBeInTheDocument();
  });

  test("shows correct derived status", () => {
    render(<Counter />);
    expect(screen.getByText("Status: Zero")).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText("Increment"));
    expect(screen.getByText("Status: Positive")).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText("Reset"));
    fireEvent.click(screen.getByLabelText("Decrement"));
    expect(screen.getByText("Status: Negative")).toBeInTheDocument();
  });
});
'''

# ============================================================
# INTERVIEW EXPLANATION
# ============================================================

EXPLANATION = """
WHY useReducer OVER useState?
=============================
1. Complex state logic: When state transitions depend on previous state
   in multiple ways, a reducer centralizes that logic.

2. Predictability: Reducers are pure functions — easy to test in isolation.

3. Debugging: DevTools show every action dispatched, making time-travel
   debugging straightforward.

4. Scalability: As actions grow, the reducer pattern scales better than
   multiple setState calls scattered across components.

KEY INTERVIEW POINTS:
=====================
- Reducer is a PURE function: no side effects, no mutation.
- Always return a NEW state object (spread operator).
- The default case in switch prevents silent bugs from typos.
- Action creators keep dispatch calls clean and typed.
- useCallback on handlers prevents child re-renders.
- initialState can be a function for lazy initialization.

WHEN TO USE EACH:
=================
- useState: Simple, independent state (count, boolean, string)
- useReducer: Complex state with multiple sub-values, transitions,
  or when logic would be duplicated across multiple setState calls

SWIGGY CONTEXT:
===============
In a food delivery app, useReducer shines for:
- Cart state (add/remove/update quantity/clear)
- Order status tracking (placed -> confirmed -> out_for_delivery -> delivered)
- Filter state with multiple interacting filters
"""

# ============================================================
# REDUCER UNIT TEST (Pure function test)
# ============================================================

REDUCER_TEST = r'''
import { counterReducer, initialState } from "./Counter";

describe("counterReducer", () => {
  test("INCREMENT increases count by 1", () => {
    const result = counterReducer(initialState, { type: "INCREMENT" });
    expect(result.count).toBe(1);
  });

  test("DECREMENT decreases count by 1", () => {
    const result = counterReducer(initialState, { type: "DECREMENT" });
    expect(result.count).toBe(-1);
  });

  test("RESET sets count to 0", () => {
    const state = { count: 42, history: [] };
    const result = counterReducer(state, { type: "RESET" });
    expect(result.count).toBe(0);
  });

  test("INCREMENT_BY adds payload to count", () => {
    const result = counterReducer(initialState, { type: "INCREMENT_BY", payload: 10 });
    expect(result.count).toBe(10);
  });

  test("SET_COUNT sets exact value", () => {
    const result = counterReducer(initialState, { type: "SET_COUNT", payload: 99 });
    expect(result.count).toBe(99);
  });

  test("unknown action returns current state unchanged", () => {
    const state = { count: 5, history: [] };
    const result = counterReducer(state, { type: "UNKNOWN" });
    expect(result).toBe(state); // Same reference
  });

  test("does not mutate original state", () => {
    const state = { count: 3, history: [] };
    const result = counterReducer(state, { type: "INCREMENT" });
    expect(state.count).toBe(3); // Original unchanged
    expect(result.count).toBe(4);
    expect(result).not.toBe(state); // Different reference
  });
});
'''

# ============================================================
# COMPLETE FILE OUTPUT
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SWIGGY INTERVIEW PREP: useReducer Counter")
    print("=" * 60)
    print()
    print("--- REACT COMPONENT ---")
    print(REACT_CODE)
    print()
    print("--- COMPONENT TESTS ---")
    print(TEST_CODE)
    print()
    print("--- REDUCER UNIT TESTS ---")
    print(REDUCER_TEST)
    print()
    print("--- INTERVIEW NOTES ---")
    print(EXPLANATION)
