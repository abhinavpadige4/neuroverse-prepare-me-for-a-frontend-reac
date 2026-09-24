# solutions/0007_customhook.py
# React Custom Hook: useFetch
# Performs GET requests and returns data, loading, error states.
# Written in TypeScript for production use.

# --- TypeScript Implementation ---

# import { useState, useEffect, useCallback, useRef } from 'react';

# interface UseFetchState<T> {
#   data: T | null;
#   loading: boolean;
#   error: Error | null;
# }

# interface UseFetchOptions {
#   headers?: Record<string, string>;
#   autoFetch?: boolean;
# }

# interface UseFetchReturn<T> extends UseFetchState<T> {
#   refetch: () => Promise<void>;
# }

# function useFetch<T = unknown>(
#   url: string | null,
#   options: UseFetchOptions = {}
# ): UseFetchReturn<T> {
#   const { headers = {}, autoFetch = true } = options;
#   const [state, setState] = useState<UseFetchState<T>>({
#     data: null,
#     loading: false,
#     error: null,
#   });
#   const abortControllerRef = useRef<AbortController | null>(null);

#   const fetchData = useCallback(async () => {
#     if (!url) return;

#     // Cancel any in-flight request
#     if (abortControllerRef.current) {
#       abortControllerRef.current.abort();
#     }
#     const controller = new AbortController();
#     abortControllerRef.current = controller;

#     setState((prev) => ({ ...prev, loading: true, error: null }));

#     try {
#       const response = await fetch(url, {
#         method: 'GET',
#         headers: {
#           'Content-Type': 'application/json',
#           ...headers,
#         },
#         signal: controller.signal,
#       });

#       if (!response.ok) {
#         throw new Error(`HTTP error! status: ${response.status}`);
#       }

#       const data = (await response.json()) as T;
#       setState({ data, loading: false, error: null });
#     } catch (err: unknown) {
#       if (err instanceof DOMException && err.name === 'AbortError') {
#         return; // Request was cancelled; do not update state
#       }
#       const error =
#         err instanceof Error ? err : new Error('An unknown error occurred');
#       setState({ data: null, loading: false, error });
#     }
#   }, [url, headers]);

#   useEffect(() => {
#     if (autoFetch) {
#       fetchData();
#     }
#     return () => {
#       if (abortControllerRef.current) {
#         abortControllerRef.current.abort();
#       }
#     };
#   }, [fetchData, autoFetch]);

#   return { ...state, refetch: fetchData };
# }

# export default useFetch;


# --- Usage Example (Restaurant List for Swiggy) ---

# import React from 'react';
# import useFetch from './useFetch';

# interface Restaurant {
#   id: number;
#   name: string;
#   cuisines: string[];
#   rating: number;
#   deliveryTime: number;
# }

# function RestaurantList() {
#   const { data, loading, error, refetch } = useFetch<Restaurant[]>(
#     'https://api.swiggy.com/restaurants',
#     { headers: { 'X-Auth-Token': 'swiggy-api-key' } }
#   );

#   if (loading) return <div>Loading restaurants...</div>;
#   if (error) return <div>Error: {error.message}</div>;

#   return (
#     <ul>
#       {data?.map((r) => (
#         <li key={r.id}>
#           {r.name} - {r.cuisines.join(', ')} ({r.rating} stars, {r.deliveryTime} min)
#         </li>
#       ))}
#     </ul>
#   );
# }


# --- Unit Tests (Jest + React Testing Library) ---

# import { renderHook, waitFor, act } from '@testing-library/react';
# import useFetch from './useFetch';

# describe('useFetch', () => {
#   beforeEach(() => {
#     global.fetch = jest.fn();
#   });

#   it('returns data on successful GET', async () => {
#     const mockData = [{ id: 1, name: 'Pizza Hut' }];
#     (global.fetch as jest.Mock).mockResolvedValue({
#       ok: true,
#       json: () => Promise.resolve(mockData),
#     });

#     const { result } = renderHook(() => useFetch('/restaurants'));

#     expect(result.current.loading).toBe(true);

#     await waitFor(() => expect(result.current.loading).toBe(false));
#     expect(result.current.data).toEqual(mockData);
#     expect(result.current.error).toBeNull();
#   });

#   it('returns error on failed GET', async () => {
#     (global.fetch as jest.Mock).mockResolvedValue({
#       ok: false,
#       status: 500,
#     });

#     const { result } = renderHook(() => useFetch('/restaurants'));

#     await waitFor(() => expect(result.current.loading).toBe(false));
#     expect(result.current.error).toBeInstanceOf(Error);
#     expect(result.current.error?.message).toContain('500');
#     expect(result.current.data).toBeNull();
#   });

#   it('handles network errors', async () => {
#     (global.fetch as jest.Mock).mockRejectedValue(new Error('Network failure'));

#     const { result } = renderHook(() => useFetch('/restaurants'));

#     await waitFor(() => expect(result.current.loading).toBe(false));
#     expect(result.current.error?.message).toBe('Network failure');
#   });

#   it('does not fetch when url is null', async () => {
#     const { result } = renderHook(() => useFetch(null));

#     expect(result.current.loading).toBe(false);
#     expect(result.current.data).toBeNull();
#     expect(global.fetch).not.toHaveBeenCalled();
#   });

#   it('refetch re-triggers the request', async () => {
#     (global.fetch as jest.Mock).mockResolvedValue({
#       ok: true,
#       json: () => Promise.resolve([{ id: 1 }]),
#     });

#     const { result } = renderHook(() => useFetch('/restaurants'));

#     await waitFor(() => expect(result.current.loading).toBe(false));
#     expect(global.fetch).toHaveBeenCalledTimes(1);

#     await act(async () => {
#       await result.current.refetch();
#     });
#     expect(global.fetch).toHaveBeenCalledTimes(2);
#   });

#   it('aborts in-flight request on unmount', async () => {
#     let abortSignal: AbortSignal;
#     (global.fetch as jest.Mock).mockImplementation((_url, opts) => {
#       abortSignal = opts.signal;
#       return new Promise(() => {}); // never resolves
#     });

#     const { unmount } = renderHook(() => useFetch('/restaurants'));
#     unmount();

#     expect(abortSignal?.aborted).toBe(true);
#   });
# });


# --- Key Interview Talking Points ---
# 1. AbortController prevents state updates after unmount (avoids memory leaks).
# 2. useCallback on fetchData ensures stable reference for useEffect deps.
# 3. Generic type parameter <T> gives type safety to consumers.
# 4. autoFetch option allows manual control (e.g., fetch on button click).
# 5. refetch exposed for retry-on-error UX patterns.
# 6. Headers passed via options support auth tokens (Swiggy API pattern).
# 7. Error normalization: DOMException AbortError is silently ignored.
# 8. State shape {data, loading, error} is idiomatic and predictable.
# 9. Works with React 18 StrictMode (double-mount in dev handled by abort).
# 10. Can be extended with caching (SWR/React Query pattern) if needed.
