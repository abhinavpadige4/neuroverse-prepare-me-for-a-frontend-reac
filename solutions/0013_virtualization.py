import json

# This file contains the React/JavaScript solution for virtualizing 10,000 restaurant items
# using react-window. The content below is the actual code to be used in a React project.

solution_code = r'''
// solutions/0013_virtualization.jsx
// Virtualized list of 10,000 restaurant items using react-window
// npm install react-window

import React, { useMemo, useCallback } from 'react';
import { FixedSizeList as List } from 'react-window';

// --- Data Generation ---
const generateRestaurants = (count) => {
  const cuisines = ['Indian', 'Chinese', 'Italian', 'Mexican', 'Japanese', 'Thai', 'American', 'French'];
  const cities = ['Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad'];
  const names = ['Spice Garden', 'Tasty Bites', 'Foodie Hub', 'Culinary Corner', 'Flavor House', 'Dish Dazzle', 'Meal Masters', 'Bite Bliss'];

  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `${names[i % names.length]} #${i + 1}`,
    cuisine: cuisines[i % cuisines.length],
    city: cities[i % cities.length],
    rating: (3.5 + Math.random() * 1.5).toFixed(1),
    deliveryTime: `${15 + Math.floor(Math.random() * 45)} mins`,
    priceRange: `₹${50 + Math.floor(Math.random() * 450)}`,
  }));
};

// --- Row Component ---
const RestaurantRow = React.memo(({ index, style, restaurant }) => {
  return (
    <div style={{ ...style, display: 'flex', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid #eee' }}>
      <div style={{ width: '40px', fontWeight: 'bold', color: '#666' }}>#{index + 1}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: '14px' }}>{restaurant.name}</div>
        <div style={{ fontSize: '12px', color: '#888' }}>
          {restaurant.cuisine} · {restaurant.city} · ⭐ {restaurant.rating} · {restaurant.deliveryTime} · {restaurant.priceRange}
        </div>
      </div>
    </div>
  );
});

// --- Main Virtualized List Component ---
const VirtualizedRestaurantList = () => {
  const restaurants = useMemo(() => generateRestaurants(10000), []);

  const Row = useCallback(
    ({ index, style }) => (
      <RestaurantRow index={index} style={style} restaurant={restaurants[index]} />
    ),
    [restaurants]
  );

  return (
    <div style={{ height: '100vh', overflow: 'auto' }}>
      <h2 style={{ padding: '16px' }}>🍽️ Restaurants (10,000 items — virtualized)</h2>
      <List
        height={window.innerHeight - 80}
        width={'100%'}
        itemSize={64}
        itemCount={restaurants.length}
        itemData={restaurants}
      >
        {Row}
      </List>
    </div>
  );
};

export default VirtualizedRestaurantList;

// --- Explanation for Interview ---
/*
KEY CONCEPTS:
1. react-window renders only visible items (~15-20) instead of all 10,000 DOM nodes.
2. FixedSizeList requires fixed itemSize; use VariableSizeList for dynamic heights.
3. React.memo on Row prevents unnecessary re-renders of individual rows.
4. useMemo caches the data array; useCallback stabilizes the Row reference.
5. Performance: O(visible) DOM nodes vs O(n) without virtualization.

INTERVIEW TALKING POINTS:
- Why virtualization? 10,000 DOM nodes cause layout/paint jank and memory bloat.
- react-window vs react-virtualized: lighter, simpler API, fixed/variable size lists.
- Swiggy context: restaurant search results, order history, menu items all benefit.
- Trade-offs: no native scroll-to-element, accessibility needs manual handling.
*/
'''

# Metadata for the solution
metadata = {
    "file": "solutions/0013_virtualization.py",
    "topic": "Virtualization with react-window",
    "difficulty": "Medium",
    "interview_relevance": "High — Swiggy handles large restaurant lists",
    "key_concepts": [
        "react-window FixedSizeList",
        "React.memo for row optimization",
        "useMemo for data caching",
        "useCallback for stable references",
        "DOM node reduction from O(n) to O(visible)"
    ],
    "dependencies": ["react", "react-dom", "react-window"],
    "test_commands": [
        "npm install react-window",
        "npm start",
        "Verify only ~20 DOM nodes rendered for 10,000 items"
    ]
}

print(json.dumps({"solution": solution_code, "metadata": metadata}, indent=2))
