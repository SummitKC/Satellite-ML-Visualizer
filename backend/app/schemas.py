from pydantic import BaseModel


class OrbitalParameters(BaseModel):
    semi_major_axis_km: float
    inclination_deg: float
    eccentricity: float
    raan_deg: float


class Satellite(BaseModel):
    norad_id: int
    name: str
    tle_line1: str
    tle_line2: str
    orbital_parameters: OrbitalParameters
    cluster_id: int | None = None


class SatelliteListResponse(BaseModel):
    satellites: list[Satellite]
    total: int
