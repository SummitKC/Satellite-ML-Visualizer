import datetime as dt

from pydantic import BaseModel


class OrbitalParameters(BaseModel):
    semi_major_axis_km: float
    inclination_deg: float
    eccentricity: float
    raan_deg: float
    bstar: float
    mean_motion_rev_per_day: float
    epoch: dt.datetime


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


class SatCatEntry(BaseModel):
    norad_id: int
    object_name: str
    object_type: str | None = None
    owner: str | None = None
    launch_date: dt.date | None = None
    decay_date: dt.date | None = None
    rcs_m2: float | None = None
