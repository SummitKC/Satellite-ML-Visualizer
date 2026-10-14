import { useReentryPrediction } from "../../hooks/useReentryPrediction";
import type { ReentryPrediction, ReentryStatus } from "../../types/satellite";

interface ReentryForecastProps {
  noradId: number;
}

const DAY_MS = 24 * 60 * 60 * 1000;

const NOT_MODELLED_REASON = "Outside what the model covers. It only forecasts low, near-circular orbits.";

const LOW_CONFIDENCE_DISCLAIMERS: Record<Exclude<ReentryStatus, "forecast" | "not_modelled">, string> = {
  controlled:
    "Part of an actively controlled constellation. Its operator decides when it deorbits, so this drag-based estimate may not apply.",
  too_high:
    "This orbit is higher than the model can reliably forecast. It only learned from objects within ~7 months of reentry, so the real lifetime is likely much longer.",
};

// Tiers match the horizon buckets the model is evaluated on (ml/evaluate.py).
function tier(daysLeft: number) {
  if (daysLeft < 7) return { label: "Imminent", className: "imminent" };
  if (daysLeft < 30) return { label: "Weeks", className: "weeks" };
  return { label: "Months", className: "months" };
}

function formatDate(date: Date, withYear = false) {
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    ...(withYear && { year: "numeric" }),
  });
}

function ForecastDetails({ prediction }: { prediction: ReentryPrediction }) {
  if (prediction.status === "not_modelled") {
    return <p className="reentry-note">{NOT_MODELLED_REASON}</p>;
  }
  if (!prediction.predicted_decay_date) return null;

  const disclaimer = prediction.status === "forecast" ? null : LOW_CONFIDENCE_DISCLAIMERS[prediction.status];
  const now = Date.now();
  const decay = new Date(prediction.predicted_decay_date).getTime();
  // The error band was measured on objects the model covers, so for a
  // low-confidence estimate it would overstate the precision; show one date.
  const errorDays = disclaimer ? 0 : prediction.error_days ?? 0;
  const windowStart = new Date(Math.max(now, decay - errorDays * DAY_MS));
  const windowEnd = new Date(decay + errorDays * DAY_MS);
  const daysLeft = (decay - now) / DAY_MS;

  // Predictions count from the object's latest TLE, so a stale one can pass its whole window.
  const passed = windowEnd.getTime() < now;
  const { label, className } = disclaimer
    ? { label: "Low confidence", className: "low-confidence" }
    : tier(Math.max(daysLeft, 0));
  const errorText = errorDays < 10 ? errorDays.toFixed(1) : Math.round(errorDays).toString();

  return (
    <>
      {passed ? (
        <p className="reentry-note">
          Was predicted to reenter around {formatDate(new Date(decay), true)}. It may already have reentered.
        </p>
      ) : (
        <>
          <span className={`reentry-tier ${className}`}>{label}</span>
          <p className="reentry-window">
            {disclaimer
              ? `Around ${formatDate(new Date(decay), true)}`
              : `${formatDate(windowStart)} – ${formatDate(windowEnd, true)}`}
          </p>
          <p className="reentry-countdown">
            {daysLeft < 1 ? "Within a day" : `In ~${Math.round(daysLeft)} days`}
            {!disclaimer && ` (±${errorText} d)`}
          </p>
        </>
      )}
      {disclaimer && <p className="reentry-disclaimer">{disclaimer}</p>}
      {prediction.tle_epoch && (
        <p className="reentry-note">Based on the TLE from {formatDate(new Date(prediction.tle_epoch))}.</p>
      )}
    </>
  );
}

export function ReentryForecast({ noradId }: ReentryForecastProps) {
  const { prediction, loading, error } = useReentryPrediction(noradId);

  return (
    <section className="reentry">
      <h3>Reentry forecast</h3>
      {loading && <p className="reentry-note">Loading forecast...</p>}
      {error && <p className="reentry-note">Forecast unavailable right now.</p>}
      {prediction && <ForecastDetails prediction={prediction} />}
    </section>
  );
}
