"""
Optimistic Cart Implementation for Swiggy Frontend Interview Prep

Pattern: Update local state immediately, roll back on API failure, show toast.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum


class ToastType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"


@dataclass
class CartItem:
    id: str
    name: str
    price: float
    quantity: int = 1


@dataclass
class Toast:
    message: str
    type: ToastType
    visible: bool = True


@dataclass
class CartState:
    items: list = field(default_factory=list)
    loading: bool = False
    toasts: list = field(default_factory=list)


class OptimisticCart:
    """Python simulation of the optimistic cart pattern."""

    def __init__(self, api_client=None):
        self.state = CartState()
        self._api = api_client or self._default_api
        self._toast_timeout = 3000

    def _default_api(self, item: CartItem) -> bool:
        return True

    def add_to_cart(self, item: CartItem) -> CartState:
        """Optimistically add item, rollback on failure."""
        previous_items = list(self.state.items)

        # 1. Optimistic update
        existing = next((i for i in self.state.items if i.id == item.id), None)
        if existing:
            existing.quantity += item.quantity
        else:
            self.state.items.append(item)

        # 2. Attempt API call
        try:
            success = self._api(item)
            if not success:
                raise Exception("API returned failure")
        except Exception as e:
            # 3. Rollback
            self.state.items = previous_items
            self._show_toast(f"Failed to add {item.name}: {e}", ToastType.ERROR)
            return self.state

        # 4. Success toast
        self._show_toast(f"{item.name} added to cart!", ToastType.SUCCESS)
        return self.state

    def _show_toast(self, message: str, toast_type: ToastType):
        self.state.toasts.append(Toast(message=message, type=toast_type))

    def dismiss_toast(self, index: int):
        if 0 <= index < len(self.state.toasts):
            self.state.toasts[index].visible = False


# ============================================================
# React Implementation (JavaScript) - Full Component Code
# ============================================================

REACT_IMPLEMENTATION = r'''// OptimisticCart.jsx
import React, { useState, useCallback, useRef } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// API service
const api = {
  addToCart: async (item) => {
    const res = await fetch("/api/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    });
    if (!res.ok) throw new Error("Failed to add item");
    return res.json();
  },
};

export default function OptimisticCart({ items }) {
  const [cart, setCart] = useState([]);
  const [pendingIds, setPendingIds] = useState(new Set());
  const abortRef = useRef(new AbortController());

  const addToCart = useCallback(async (item) => {
    // 1. Save previous state for rollback
    const previousCart = [...cart];

    // 2. Optimistic update - update UI immediately
    setCart((prev) => {
      const existing = prev.find((i) => i.id === item.id);
      if (existing) {
        return prev.map((i) =>
          i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      return [...prev, { ...item, quantity: 1 }];
    });

    // 3. Mark as pending
    setPendingIds((prev) => new Set(prev).add(item.id));

    try {
      // 4. Call API
      await api.addToCart(item);

      // 5. Success toast
      toast.success(`${item.name} added to cart!`, {
        position: "top-right",
        autoClose: 3000,
      });
    } catch (error) {
      // 6. Rollback on failure
      setCart(previousCart);

      // 7. Error toast
      toast.error(`Failed to add ${item.name}. Please try again.`, {
        position: "top-right",
        autoClose: 4000,
      });
    } finally {
      // 8. Clear pending state
      setPendingIds((prev) => {
        const next = new Set(prev);
        next.delete(item.id);
        return next;
      });
    }
  }, [cart]);

  return (
    <div className="cart-container">
      <ToastContainer />
      <h2>Cart ({cart.reduce((s, i) => s + i.quantity, 0)} items)</h2>
      <ul>
        {cart.map((item) => (
          <li key={item.id} className={pendingIds.has(item.id) ? "pending" : ""}>
            {item.name} x{item.quantity} - Rs.{item.price * item.quantity}
          </li>
        ))}
      </ul>
      <div className="menu">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => addToCart(item)}
            disabled={pendingIds.has(item.id)}
          >
            Add {item.name} (Rs.{item.price})
          </button>
        ))}
      </div>
    </div>
  );
}
'''


# ============================================================
# Tests
# ============================================================

def test_optimistic_add_success():
    cart = OptimisticCart()
    item = CartItem(id="1", name="Biryani", price=299.0)
    state = cart.add_to_cart(item)
    assert len(state.items) == 1
    assert state.items[0].name == "Biryani"
    assert state.items[0].quantity == 1
    assert len(state.toasts) == 1
    assert state.toasts[0].type == ToastType.SUCCESS
    print("PASS: test_optimistic_add_success")


def test_optimistic_add_rollback():
    def failing_api(item):
        raise Exception("Network error")

    cart = OptimisticCart(api_client=failing_api)
    item = CartItem(id="2", name="Pizza", price=199.0)
    state = cart.add_to_cart(item)
    assert len(state.items) == 0, "Should have rolled back"
    assert len(state.toasts) == 1
    assert state.toasts[0].type == ToastType.ERROR
    print("PASS: test_optimistic_add_rollback")


def test_optimistic_increment_quantity():
    cart = OptimisticCart()
    item = CartItem(id="3", name="Dosa", price=99.0)
    cart.add_to_cart(item)
    cart.add_to_cart(item)
    assert len(cart.state.items) == 1
    assert cart.state.items[0].quantity == 2
    print("PASS: test_optimistic_increment_quantity")


def test_rollback_preserves_previous_state():
    def failing_api(item):
        raise Exception("Server down")

    cart = OptimisticCart(api_client=failing_api)
    good_item = CartItem(id="4", name="Samosa", price=49.0)
    cart.add_to_cart(good_item)
    assert len(cart.state.items) == 1

    bad_item = CartItem(id="5", name="Cake", price=499.0)
    cart.add_to_cart(bad_item)
    assert len(cart.state.items) == 1
    assert cart.state.items[0].name == "Samosa"
    print("PASS: test_rollback_preserves_previous_state")


def test_toast_dismiss():
    cart = OptimisticCart()
    item = CartItem(id="6", name="Chai", price=20.0)
    cart.add_to_cart(item)
    assert cart.state.toasts[0].visible is True
    cart.dismiss_toast(0)
    assert cart.state.toasts[0].visible is False
    print("PASS: test_toast_dismiss")


if __name__ == "__main__":
    test_optimistic_add_success()
    test_optimistic_add_rollback()
    test_optimistic_increment_quantity()
    test_rollback_preserves_previous_state()
    test_toast_dismiss()
    print("\nAll tests passed!")
    print("\n--- React Implementation ---")
    print(REACT_IMPLEMENTATION)
