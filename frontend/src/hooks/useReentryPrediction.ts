import { useEffect, useState } from "react";
import type { ReentryPrediction } from "../types/satellite";
import { API_BASE_URL } from "../constants/api";

interface UseReentryPredictionResult {
  prediction: ReentryPrediction | null;
  loading: boolean;
  error: string | null;
}

export function useReentryPrediction(noradId: number | null): UseReentryPredictionResult {
  const [prediction, setPrediction] = useState<ReentryPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPrediction(null);
    setError(null);
    if (noradId === null) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    fetch(`${API_BASE_URL}/satellites/${noradId}/reentry`)
      .then((res) => {
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!cancelled) setPrediction(data);
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
  }, [noradId]);

  return { prediction, loading, error };
}
