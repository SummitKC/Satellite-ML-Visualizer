from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    celestrak_tle_url: str = (
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
    )
    satcat_url: str = "https://celestrak.org/pub/satcat.csv"
    satcat_fallback_path: str = "data/satcat.csv"
    cors_origins: str = "http://localhost:5173"
    cluster_count: int = 5
    tle_refresh_interval_seconds: int = 2 * 60 * 60
    satcat_refresh_interval_seconds: int = 24 * 60 * 60
    db_path: str = "data/satellite_history.sqlite3"
    reentry_model_path: str = "ml/artifacts/gbm.joblib"

    spacetrack_identity: str = ""
    spacetrack_password: str = ""
    # Space-Track's published caps are 30/minute and 300/hour; staying under
    # them leaves headroom for retries, and exceeding them risks suspension.
    spacetrack_requests_per_minute: int = 20
    spacetrack_requests_per_hour: int = 250

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
