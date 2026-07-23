import { useEffect, useState } from "react";
import type { Satellite } from "../types/satellite";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

interface UseSatelliteDataResult {
  satellites: Satellite[];
  loading: boolean;
  error: string | null;
}

/**
 * Fetches the satellite list (with orbital parameters + cluster IDs) from the backend.
 *
 * TODO (Step 4): once the backend /satellites endpoint returns real data, this hook
 * should be enough as-is - verify the shape matches `Satellite` in ../types/satellite.ts.
 */
export function useSatelliteData(): UseSatelliteDataResult {
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetch(`${API_BASE_URL}/satellites`)
      .then((res) => {
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!cancelled) setSatellites(data.satellites ?? []);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { satellites, loading, error };
}
