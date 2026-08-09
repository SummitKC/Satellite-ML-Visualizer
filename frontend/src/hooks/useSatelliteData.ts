import { useEffect, useState } from "react";
import type { Satellite } from "../types/satellite";
import { mockSatellites } from "../mocks/mockSatellites";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

// TODO: flip back to false once the backend /satellites endpoint is running.
const USE_MOCK_DATA = false;

interface UseSatelliteDataResult {
  satellites: Satellite[];
  loading: boolean;
  error: string | null;
}

export function useSatelliteData(): UseSatelliteDataResult {
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (USE_MOCK_DATA) {
      setSatellites(mockSatellites);
      setLoading(false);
      return;
    }

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
