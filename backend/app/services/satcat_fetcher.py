"""Fetches and stores the Celestrak satellite catalog (SATCAT).

Unlike the TLE feed, this changes slowly (object metadata, decay dates), so
it runs on its own slower cadence (see periodic_satcat_refresh_loop) rather
than every TLE refresh. Decay dates here are the ground-truth labels for
training a deorbit model.
"""

import asyncio
import csv
import datetime as dt
import io
import logging
from pathlib import Path

import httpx

from app.config import get_settings
from app.db import get_connection
from app.schemas import SatCatEntry

logger = logging.getLogger(__name__)


def _parse_date(value: str) -> dt.date | None:
    return dt.date.fromisoformat(value) if value else None


def _parse_float(value: str) -> float | None:
    return float(value) if value else None


async def _download_satcat_text() -> str:
    settings = get_settings()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(settings.satcat_url)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            logger.warning(
                "CelesTrak request throttled (likely on cooldown) for %s.",
                e.request.url,
            )
        else:
            logger.error(
                "Error response %s while requesting %s.",
                e.response.status_code,
                e.request.url,
            )
        raise
    except httpx.RequestError as e:
        logger.error("An error occurred while requesting %s.", e.request.url)
        raise

    return response.text


async def fetch_satcat() -> list[SatCatEntry]:
    """Fetch and parse SATCAT from Celestrak, falling back to the local CSV on error."""
    settings = get_settings()

    try:
        text = await _download_satcat_text()
    except httpx.HTTPError:
        fallback = Path(settings.satcat_fallback_path)
        if not fallback.is_file():
            logger.error("No local SATCAT fallback at %s", fallback)
            raise
        logger.warning("Using local SATCAT fallback %s", fallback)
        text = fallback.read_text(encoding="utf-8")

    return _parse_satcat(text)


def _parse_satcat(text: str) -> list[SatCatEntry]:
    entries = []
    for row in csv.DictReader(io.StringIO(text)):
        norad_id = row.get("NORAD_CAT_ID")
        if not norad_id:
            continue

        entries.append(
            SatCatEntry(
                norad_id=int(norad_id),
                object_name=row.get("OBJECT_NAME", "").strip(),
                object_type=row.get("OBJECT_TYPE") or None,
                owner=row.get("OWNER") or None,
                launch_date=_parse_date(row.get("LAUNCH_DATE", "")),
                decay_date=_parse_date(row.get("DECAY_DATE", "")),
                rcs_m2=_parse_float(row.get("RCS", "")),
            )
        )

    return entries


def save_satcat(entries: list[SatCatEntry]) -> None:
    """Upsert SATCAT entries, overwriting stale metadata for the same object."""
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    connection = get_connection()
    try:
        with connection:
            connection.executemany(
                """
                INSERT INTO satcat (
                    norad_id, object_name, object_type, owner,
                    launch_date, decay_date, rcs_m2, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(norad_id) DO UPDATE SET
                    object_name = excluded.object_name,
                    object_type = excluded.object_type,
                    owner = excluded.owner,
                    launch_date = excluded.launch_date,
                    decay_date = excluded.decay_date,
                    rcs_m2 = excluded.rcs_m2,
                    updated_at = excluded.updated_at
                """,
                [
                    (
                        entry.norad_id,
                        entry.object_name,
                        entry.object_type,
                        entry.owner,
                        entry.launch_date.isoformat() if entry.launch_date else None,
                        entry.decay_date.isoformat() if entry.decay_date else None,
                        entry.rcs_m2,
                        now,
                    )
                    for entry in entries
                ],
            )
    finally:
        connection.close()

    logger.info("Refreshed SATCAT: %d entries", len(entries))


async def refresh_satcat() -> None:
    """Fetch the latest SATCAT and replace the stored metadata."""
    save_satcat(await fetch_satcat())


async def periodic_satcat_refresh_loop() -> None:
    """Refresh SATCAT on a timer, retrying quickly on failure."""
    settings = get_settings()
    while True:
        try:
            await refresh_satcat()
            await asyncio.sleep(settings.satcat_refresh_interval_seconds)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to refresh SATCAT; retrying in 300s")
            await asyncio.sleep(300)
