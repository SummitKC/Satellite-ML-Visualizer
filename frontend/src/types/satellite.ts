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

export interface SatelliteListResponse {
  satellites: Satellite[];
  total: number;
}
