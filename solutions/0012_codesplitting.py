import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

// ============================================================
// FALLBACK SPINNER COMPONENT
// Shown while the lazy-loaded chunk is being fetched
// ============================================================
function Spinner() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div
        style={{
          width: 40,
          height: 40,
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #fc8019',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ============================================================
// ERROR BOUNDARY for lazy-loaded chunks
// Catches chunk load failures (e.g., network errors, 404s)
// ============================================================
class ChunkErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Chunk load error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, textAlign: 'center' }}>
          <h2>Failed to load component</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ============================================================
// LAZY-LOADED COMPONENTS
// React.lazy() returns a component that dynamically imports a module.
// The import() function tells the bundler (Webpack/Vite) to create
// a separate chunk for each component.
// ============================================================
const Dashboard = React.lazy(() => import('./Dashboard'));
const Orders = React.lazy(() => import('./Orders'));
const Profile = React.lazy(() => import('./Profile'));
const NotFound = React.lazy(() => import('./NotFound'));

// ============================================================
// STATICALLY IMPORTED COMPONENTS (always loaded)
// These are small enough that splitting them adds no benefit.
// ============================================================
function Navbar() {
  return (
    <nav style={{ display: 'flex', gap: 16, padding: '12px 24px', background: '#fc8019', color: '#fff' }}>
      <Link to="/" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Swiggy</Link>
      <Link to="/dashboard" style={{ color: '#fff', textDecoration: 'none' }}>Dashboard</Link>
      <Link to="/orders" style={{ color: '#fff', textDecoration: 'none' }}>Orders</Link>
      <Link to="/profile" style={{ color: '#fff', textDecoration: 'none' }}>Profile</Link>
    </nav>
  );
}

// ============================================================
// PRELOAD HINTS
// Preload chunks on hover/focus to reduce perceived latency.
// ============================================================
function PreloadLink({ to, children, ...rest }) {
  const handleMouseEnter = () => {
    // Trigger the dynamic import early without rendering
    if (to === '/dashboard') import('./Dashboard');
    if (to === '/orders') import('./Orders');
    if (to === '/profile') import('./Profile');
  };

  return (
    <Link to={to} onMouseEnter={handleMouseEnter} onFocus={handleMouseEnter} {...rest}>
      {children}
    </Link>
  );
}

// ============================================================
// APP COMPONENT
// Suspense wraps lazy components and shows the fallback while loading.
// Each <Route> with a lazy component is wrapped in its own Suspense
// so that one slow chunk doesn't block others.
// ============================================================
function App() {
  return (
    <BrowserRouter>
      <ChunkErrorBoundary>
        <Navbar />
        <main style={{ padding: 24 }}>
          <Routes>
            <Route
              path="/"
              element={
                <Suspense fallback={<Spinner />}>
                  <Dashboard />
                </Suspense>
              }
            />
            <Route
              path="/dashboard"
              element={
                <Suspense fallback={<Spinner />}>
                  <Dashboard />
                </Suspense>
              }
            />
            <Route
              path="/orders"
              element={
                <Suspense fallback={<Spinner />}>
                  <Orders />
                </Suspense>
              }
            />
            <Route
              path="/profile"
              element={
                <Suspense fallback={<Spinner />}>
                  <Profile />
                </Suspense>
              }
            />
            <Route
              path="*"
              element={
                <Suspense fallback={<Spinner />}>
                  <NotFound />
                </Suspense>
              }
            />
          </Routes>
        </main>
      </ChunkErrorBoundary>
    </BrowserRouter>
  );
}

// ============================================================
// ENTRY POINT
// ============================================================
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<React.StrictMode><App /></React.StrictMode>);

// ============================================================
// DASHBOARD COMPONENT (separate file: ./Dashboard.js)
// This file is split into its own chunk by the bundler.
// ============================================================
export default function Dashboard() {
  const [stats, setStats] = React.useState(null);

  React.useEffect(() => {
    fetch('/api/dashboard/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Dashboard stats error:', err));
  }, []);

  if (!stats) return <p>Loading dashboard data...</p>;

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        <div style={{ padding: 16, background: '#f9f9f9', borderRadius: 8 }}>
          <h3>Total Orders</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold' }}>{stats.totalOrders}</p>
        </div>
        <div style={{ padding: 16, background: '#f9f9f9', borderRadius: 8 }}>
          <h3>Revenue</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold' }}>₹{stats.revenue}</p>
        </div>
        <div style={{ padding: 16, background: '#f9f9f9', borderRadius: 8 }}>
          <h3>Active Restaurants</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold' }}>{stats.activeRestaurants}</p>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// ORDERS COMPONENT (separate file: ./Orders.js)
// ============================================================
export default function Orders() {
  const [orders, setOrders] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetch('/api/orders')
      .then(res => res.json())
      .then(data => setOrders(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading orders...</p>;

  return (
    <div>
      <h1>My Orders</h1>
      {orders.length === 0 ? <p>No orders yet.</p> : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {orders.map(order => (
            <li key={order.id} style={{ padding: 12, borderBottom: '1px solid #eee' }}>
              <strong>{order.restaurant}</strong> — ₹{order.total} — {order.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ============================================================
// PROFILE COMPONENT (separate file: ./Profile.js)
// ============================================================
export default function Profile() {
  const [user, setUser] = React.useState(null);

  React.useEffect(() => {
    fetch('/api/user/profile')
      .then(res => res.json())
      .then(data => setUser(data));
  }, []);

  if (!user) return <p>Loading profile...</p>;

  return (
    <div>
      <h1>Profile</h1>
      <p>Name: {user.name}</p>
      <p>Email: {user.email}</p>
      <p>Phone: {user.phone}</p>
    </div>
  );
}

// ============================================================
// NOT FOUND COMPONENT (separate file: ./NotFound.js)
// ============================================================
export default function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: 40 }}>
      <h1>404</h1>
      <p>Page not found.</p>
      <Link to="/">Go Home</Link>
    </div>
  );
}

// ============================================================
// WEBPACK/VITE CONFIG NOTES
// ============================================================
// Webpack (webpack.config.js):
//   module.exports = {
//     output: {
//       filename: 'static/js/[name].[contenthash:8].js',
//       chunkFilename: 'static/js/[name].[contenthash:8].chunk.js',
//     },
//     optimization: {
//       splitChunks: {
//         chunks: 'all',
//         cacheGroups: {
//           vendor: { test: /[\\/]node_modules[\\/]/, name: 'vendor', priority: 10 },
//         },
//       },
//     },
//   };
//
// Vite (vite.config.js):
//   import { defineConfig } from 'vite';
//   import react from '@vitejs/plugin-react';
//   export default defineConfig({
//     plugins: [react()],
//     build: {
//       rollupOptions: {
//         output: {
//           manualChunks: {
//             vendor: ['react', 'react-dom', 'react-router-dom'],
//           },
//         },
//       },
//     },
//   });
//
// KEY INTERVIEW POINTS:
// 1. React.lazy() + Suspense = code splitting with minimal boilerplate.
// 2. Each lazy() call creates a separate chunk; the bundler handles the rest.
// 3. Suspense fallback shows while the chunk is being fetched.
// 4. Error boundaries catch chunk load failures (network, 404, etc.).
// 5. Preload on hover/focus reduces perceived latency.
// 6. Static imports for small components avoid unnecessary chunk overhead.
// 7. Vendor chunks (react, react-dom) are cached across sessions.
// 8. Content hashes in filenames enable long-term caching.
// 9. Route-based splitting is the most common pattern in SPAs.
// 10. For Swiggy: Dashboard, Orders, Profile are heavy pages worth splitting.
