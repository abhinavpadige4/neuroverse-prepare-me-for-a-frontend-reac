"""
Infinite Scroll for Swiggy-style Restaurant List
=================================================
Component hierarchy, API calls, and state updates for paginated fetch + scroll detection.
"""

# ─── COMPONENT HIERARCHY ─────────────────────────────────────────────────────
# App
# └── RestaurantList (container: owns pagination state, scroll detection)
#     ├── RestaurantItem (presentational: renders a single restaurant card)
#     ├── LoadingSpinner (presentational: shown while fetching next page)
#     └── EndOfList (presentational: shown when no more pages)

# ─── STATE SHAPE ─────────────────────────────────────────────────────────────
# {
#   restaurants: Restaurant[],   // accumulated results across pages
#   page: number,               // current page (1-indexed)
#   hasMore: boolean,           // whether server returned a full page
#   loading: boolean,           // true while fetching
#   error: string | null        // error message if fetch fails
# }

# ─── API CONTRACT ────────────────────────────────────────────────────────────
# GET /api/restaurants?page={n}&limit=20
# Response: { data: Restaurant[], hasMore: boolean }

# ─── FULL REACT IMPLEMENTATION ───────────────────────────────────────────────

REACT_CODE = r'''
import React, { useState, useEffect, useCallback, useRef } from "react";

// ─── TYPES ───────────────────────────────────────────────────────────────────
interface Restaurant {
  id: number;
  name: string;
  cuisines: string[];
  rating: number;
  deliveryTime: number;
  image: string;
}

interface ApiResponse {
  data: Restaurant[];
  hasMore: boolean;
}

// ─── API LAYER ───────────────────────────────────────────────────────────────
const API_BASE = "/api/restaurants";
const PAGE_SIZE = 20;

async function fetchRestaurants(page: number): Promise<ApiResponse> {
  const url = `${API_BASE}?page=${page}&limit=${PAGE_SIZE}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ─── PRESENTATIONAL COMPONENTS ───────────────────────────────────────────────
function LoadingSpinner() {
  return (
    <div style={{ textAlign: "center", padding: 24, color: "#666" }}>
      <span style={{ fontSize: 18 }}>Loading more restaurants...</span>
    </div>
  );
}

function EndOfList() {
  return (
    <div style={{ textAlign: "center", padding: 24, color: "#999" }}>
      You have reached the end. No more restaurants to show.
    </div>
  );
}

function RestaurantItem({ restaurant }: { restaurant: Restaurant }) {
  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        padding: 16,
        borderBottom: "1px solid #eee",
        alignItems: "center",
      }}
    >
      <img
        src={restaurant.image}
        alt={restaurant.name}
        style={{ width: 80, height: 80, borderRadius: 8, objectFit: "cover" }}
      />
      <div style={{ flex: 1 }}>
        <h3 style={{ margin: "0 0 4px" }}>{restaurant.name}</h3>
        <p style={{ margin: "0 0 4px", color: "#666" }}>
          {restaurant.cuisines.join(", ")}
        </p>
        <p style={{ margin: 0, color: "#4caf50", fontWeight: 600 }}>
          ★ {restaurant.rating} · {restaurant.deliveryTime} min
        </p>
      </div>
    </div>
  );
}

// ─── CONTAINER COMPONENT ─────────────────────────────────────────────────────
function RestaurantList() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Ref to track if component is still mounted (prevents state update after unmount)
  const isMounted = useRef(true);

  // Ref to the scroll container
  const scrollRef = useRef<HTMLDivElement>(null);

  // ─── FETCH NEXT PAGE ───────────────────────────────────────────────────────
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return; // guard against duplicate calls

    setLoading(true);
    setError(null);

    try {
      const response = await fetchRestaurants(page);
      if (!isMounted.current) return;

      setRestaurants((prev) => [...prev, ...response.data]);
      setHasMore(response.hasMore);
      setPage((prev) => prev + 1);
    } catch (err) {
      if (!isMounted.current) return;
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      if (isMounted.current) setLoading(false);
    }
  }, [page, loading, hasMore]);

  // ─── INITIAL LOAD ──────────────────────────────────────────────────────────
  useEffect(() => {
    loadMore();
    return () => {
      isMounted.current = false;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ─── SCROLL DETECTION ──────────────────────────────────────────────────────
  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;

    // Trigger when user is within 200px of the bottom
    const threshold = 200;
    const nearBottom =
      el.scrollTop + el.clientHeight >= el.scrollHeight - threshold;

    if (nearBottom) {
      loadMore();
    }
  }, [loadMore]);

  // ─── RENDER ────────────────────────────────────────────────────────────────
  return (
    <div
      ref={scrollRef}
      onScroll={handleScroll}
      style={{
        height: "100vh",
        overflowY: "auto",
        border: "1px solid #ddd",
        borderRadius: 8,
      }}
    >
      <h2 style={{ padding: "16px 16px 0" }}>Restaurants Near You</h2>

      {restaurants.map((r) => (
        <RestaurantItem key={r.id} restaurant={r} />
      ))}

      {loading && <LoadingSpinner />}
      {!hasMore && !loading && <EndOfList />}

      {error && (
        <div style={{ padding: 16, color: "#e53935", textAlign: "center" }}>
          <p>Failed to load: {error}</p>
          <button onClick={loadMore} style={{ padding: "8px 16px" }}>
            Retry
          </button>
        </div>
      )}
    </div>
  );
}

export default RestaurantList;
'''

# ─── KEY DESIGN DECISIONS ────────────────────────────────────────────────────
DESIGN_NOTES = """
1. SCROLL THRESHOLD (200px): Fires before the user hits the absolute bottom,
   giving a seamless feel. Tune based on item height.

2. DUPLICATE-CALL GUARD: `loading` and `hasMore` flags prevent multiple
   concurrent fetches when the user scrolls rapidly.

3. ACCUMULATIVE STATE: `setRestaurants(prev => [...prev, ...new])` appends
   rather than replaces, preserving previously loaded items.

4. UNMOUNT SAFETY: `isMounted` ref prevents setState warnings if the user
   navigates away mid-fetch.

5. PAGE vs OFFSET: Using page numbers keeps the API simple. For Swiggy-scale
   data, cursor-based pagination (nextCursor) is more robust against
   insertions/deletions between pages.

6. INTERSECTION OBSERVER ALTERNATIVE: For production, replace onScroll with
   IntersectionObserver on a sentinel div at the bottom — more performant
   because it avoids scroll-event throttling.

   const observer = new IntersectionObserver(
     (entries) => { if (entries[0].isIntersecting) loadMore(); },
     { root: scrollRef.current, rootMargin: "200px" }
   );
   observer.observe(sentinelRef.current);

7. ERROR RETRY: The retry button re-invokes loadMore with the same page
   number (page is only incremented on success), so the user can recover
   from transient network failures.

8. SWIGGY-SPECIFIC CONSIDERATIONS:
   - Debounce scroll events if using onScroll (not needed with IO).
   - Cancel in-flight requests on unmount using AbortController.
   - Show skeleton loaders for initial page instead of spinner.
   - Cache restaurant data in a SWR/React Query layer for instant re-entry.
"""

# ─── MOCK DATA GENERATOR (for local testing) ─────────────────────────────────
MOCK_SERVER = r'''
// mock-server.js — run with: node mock-server.js
const http = require("http");

const TOTAL = 500;
const PAGE_SIZE = 20;

function generate(page) {
  const start = (page - 1) * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, TOTAL);
  const data = [];
  for (let i = start; i < end; i++) {
    data.push({
      id: i + 1,
      name: `Restaurant #${i + 1}`,
      cuisines: ["North Indian", "Biryani", "South Indian", "Chinese"][i % 4],
      rating: (3.5 + Math.random() * 1.5).toFixed(1),
      deliveryTime: 20 + Math.floor(Math.random() * 40),
      image: `https://picsum.photos/seed/${i}/200/200`,
    });
  }
  return { data, hasMore: end < TOTAL };
}

http
  .createServer((req, res) => {
    const url = new URL(req.url, "http://localhost:3001");
    if (url.pathname === "/api/restaurants") {
      const page = parseInt(url.searchParams.get("page") || "1");
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(generate(page)));
    } else {
      res.writeHead(404);
      res.end();
    }
  })
  .listen(3001, () => console.log("Mock API on :3001"));
'''

# ─── SUMMARY ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("INFINITE SCROLL — Swiggy Restaurant List")
    print("=" * 60)
    print()
    print("COMPONENT HIERARCHY:")
    print("  App")
    print("  └── RestaurantList (container)")
    print("      ├── RestaurantItem (presentational)")
    print("      ├── LoadingSpinner (presentational)")
    print("      └── EndOfList (presentational)")
    print()
    print("STATE:")
    print("  restaurants: Restaurant[]")
    print("  page: number")
    print("  hasMore: boolean")
    print("  loading: boolean")
    print("  error: string | null")
    print()
    print("API: GET /api/restaurants?page={n}&limit=20")
    print("Response: { data: Restaurant[], hasMore: boolean }")
    print()
    print("FULL REACT CODE:")
    print(REACT_CODE)
    print()
    print("DESIGN NOTES:")
    print(DESIGN_NOTES)
    print()
    print("MOCK SERVER:")
    print(MOCK_SERVER)
