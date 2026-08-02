import type { Satellite } from "../types/satellite";

const MOCK_SATELLITE_COUNT = 25;

/**
 * Deterministic fake satellites for exercising SatelliteField/InfoPanel without
 * a running backend. TLE lines are placeholders, not physically valid.
 */
export const mockSatellites: Satellite[] = Array.from(
  { length: MOCK_SATELLITE_COUNT },
  (_, i) => ({
    norad_id: 10000 + i,
    name: `TESTSAT-${i + 1}`,
    tle_line1: `1 ${10000 + i}U 26001A   26001.00000000  .00000000  00000-0  00000-0 0  0000`,
    tle_line2: `2 ${10000 + i} ${(i * 7) % 180}.0000 000.0000 0001000 000.0000 000.0000 14.50000000000000`,
    orbital_parameters: {
      semi_major_axis_km: 6771 + i * 50,
      inclination_deg: (i * 7) % 180,
      eccentricity: 0.0001 * i,
      raan_deg: (i * 15) % 360,
    },
    cluster_id: i % 5,
  }),
);