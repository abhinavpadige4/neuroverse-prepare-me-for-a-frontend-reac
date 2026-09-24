// Optimistic Cart Update — React + TypeScript
// Pattern: update UI immediately, call API, rollback on failure, show toast

import React, { useState, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';

// ---------- Types ----------
interface CartItem {
  id: string;
  name: string;
  price: number;
  qty: number;
}

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

// ---------- Toast Component ----------
const ToastContainer: React.FC<{ toasts: Toast[]; remove: (id: number) => void }> = ({ toasts, remove }) => {
  return createPortal(
    <div style={{ position: 'fixed', top: 16, right: 16, zIndex: 9999 }}>
      {toasts.map(t => (
        <div
          key={t.id}
          onClick={() => remove(t.id)}
          style={{
            padding: '12px 20px',
            margin: '8px 0',
            borderRadius: 8,
            color: '#fff',
            background: t.type === 'success' ? '#22c55e' : '#ef4444',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            animation: 'slideIn 0.3s ease',
          }}
        >
          {t.message}
        </div>
      ))}
    </div>,
    document.body
  );
};

// ---------- Optimistic Cart Hook ----------
function useOptimisticCart() {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const toastId = useRef(0);

  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    const id = ++toastId.current;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToCart = useCallback(
    async (item: Omit<CartItem, 'qty'>) => {
      // 1. Snapshot previous state for rollback
      const prevCart = cart;

      // 2. Optimistic update — add or increment qty immediately
      setCart(prev => {
        const existing = prev.find(i => i.id === item.id);
        if (existing) {
          return prev.map(i => (i.id === item.id ? { ...i, qty: i.qty + 1 } : i));
        }
        return [...prev, { ...item, qty: 1 }];
      });

      showToast(`Added ${item.name} to cart`, 'success');

      // 3. Call API — simulate network
      try {
        await fakeApiAddToCart(item);
      } catch (err) {
        // 4. Rollback on failure
        setCart(prevCart);
        showToast(`Failed to add ${item.name}. Reverted.`, 'error');
      }
    },
    [cart, showToast]
  );

  const removeFromCart = useCallback((id: string) => {
    setCart(prev => prev.filter(i => i.id !== id));
  }, []);

  const total = cart.reduce((sum, i) => sum + i.price * i.qty, 0);

  return { cart, total, addToCart, removeFromCart, toasts, removeToast };
}

// ---------- Simulated API (replace with real fetch) ----------
function fakeApiAddToCart(item: Omit<CartItem, 'qty'>): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 30% failure rate for demo
      if (Math.random() < 0.3) {
        reject(new Error('Server error'));
      } else {
        resolve();
      }
    }, 800);
  });
}

// ---------- Cart UI Component ----------
const Cart: React.FC = () => {
  const { cart, total, addToCart, removeFromCart, toasts, removeToast } = useOptimisticCart();

  const sampleItems = [
    { id: '1', name: 'Paneer Tikka', price: 249 },
    { id: '2', name: 'Butter Chicken', price: 349 },
    { id: '3', name: 'Garlic Naan', price: 49 },
    { id: '4', name: 'Mango Lassi', price: 99 },
  ];

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 600, margin: '40px auto', padding: 20 }}>
      <h1>Swiggy Cart — Optimistic Updates</h1>

      <h2>Add Items</h2>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {sampleItems.map(item => (
          <button
            key={item.id}
            onClick={() => addToCart(item)}
            style={{ padding: '10px 16px', cursor: 'pointer', borderRadius: 6, border: '1px solid #ccc' }}
          >
            {item.name} — ₹{item.price}
          </button>
        ))}
      </div>

      <h2>Cart ({cart.length} items)</h2>
      {cart.length === 0 ? (
        <p style={{ color: '#888' }}>Cart is empty</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #eee' }}>
              <th style={{ textAlign: 'left', padding: 8 }}>Item</th>
              <th style={{ padding: 8 }}>Qty</th>
              <th style={{ padding: 8 }}>Price</th>
              <th style={{ padding: 8 }}></th>
            </tr>
          </thead>
          <tbody>
            {cart.map(item => (
              <tr key={item.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: 8 }}>{item.name}</td>
                <td style={{ padding: 8, textAlign: 'center' }}>{item.qty}</td>
                <td style={{ padding: 8, textAlign: 'center' }}>₹{item.price * item.qty}</td>
                <td style={{ padding: 8, textAlign: 'center' }}>
                  <button onClick={() => removeFromCart(item.id)} style={{ color: 'red', cursor: 'pointer' }}>
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={2} style={{ padding: 8, textAlign: 'right', fontWeight: 'bold' }}>Total:</td>
              <td colSpan={2} style={{ padding: 8, fontWeight: 'bold' }}>₹{total}</td>
            </tr>
          </tfoot>
        </table>
      )}

      <ToastContainer toasts={toasts} remove={removeToast} />
    </div>
  );
};

export default Cart;

// ---------- Key Interview Talking Points ----------
/*
1. WHY OPTIMISTIC?
   - Reduces perceived latency; user sees instant feedback
   - Common in food delivery (Swiggy/Zomato) where cart adds are frequent

2. ROLLBACK STRATEGY
   - Snapshot state before mutation (prevCart)
   - On API failure, restore snapshot
   - Show error toast so user knows the action didn't persist

3. EDGE CASES
   - Rapid double-clicks: each call snapshots independently
   - Concurrent adds: functional setState ensures correct merges
   - Network timeout: consider AbortController for real apps

4. REAL-WORLD (Swiggy)
   - Use Redux Toolkit createAsyncThunk or RTK Query for state management
   - Persist cart to localStorage as backup
   - Retry logic with exponential backoff
   - Conflict resolution if server state differs (e.g., item sold out)
*/
