export interface OrbitalParameters {
  semi_major_axis_km: number;
  inclination_deg: number;
  eccentricity: number;
  raan_deg: number;
}

export interface Satellite {
  norad_id: number;
  name: string;
  tle_line1: string;
  tle_line2: string;
  orbital_parameters: OrbitalParameters;
  cluster_id: number | null;
}

export type ReentryStatus = "forecast" | "controlled" | "too_high" | "not_modelled";

// Every status but "not_modelled" carries the model's estimate; "controlled"
// and "too_high" are outside what it was trained on, so they need a caveat.
export interface ReentryPrediction {
  norad_id: number;
  status: ReentryStatus;
  tle_epoch: string | null;
  predicted_decay_date: string | null;
  error_days: number | null;
}

export interface SatelliteListResponse {
  satellites: Satellite[];
  total: number;
}
