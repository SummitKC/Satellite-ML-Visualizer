"""Backfills historical TLEs for decayed objects from Space-Track.

The live CelesTrak collector only sees the current active catalog, so it can
never observe an object's decay: by the time something reenters it has left
the feed. That leaves SATCAT's ~35k decay dates with no matching orbital
history to learn from. This job closes that gap by pulling each decayed
object's final months of TLEs, which become the training set for the
deorbit model.

Runs for hours under Space-Track's rate cap, so progress is checkpointed
per batch in `backfill_progress` and re-running resumes where it stopped.

    python -m app.jobs.backfill_history --since-year 2015
"""

import argparse
import asyncio
import datetime as dt
import logging
from collections import defaultdict

from app.db import get_connection
from app.schemas import OrbitalParameters
from app.services.spacetrack import SpaceTrackClient
from app.services.tle_fetcher import parse_orbital_parameters
from app.services.tle_history import save_snapshots

logger = logging.getLogger(__name__)

ParsedSnapshot = tuple[str, str, str, str, OrbitalParameters]


def _decayed_targets(since_year: int) -> dict[str, list[int]]:
    """Group decayed objects by decay month, so one query covers one window."""
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT norad_id, decay_date FROM satcat
            WHERE decay_date IS NOT NULL AND decay_date >= ?
            ORDER BY decay_date, norad_id
            """,
            (f"{since_year}-01-01",),
        ).fetchall()
    finally:
        connection.close()

    groups: dict[str, list[int]] = defaultdict(list)
    for norad_id, decay_date in rows:
        groups[decay_date[:7]].append(norad_id)
    return dict(groups)


def _completed_batches() -> set[str]:
    connection = get_connection()
    try:
        return {row[0] for row in connection.execute("SELECT batch_key FROM backfill_progress")}
    finally:
        connection.close()


def _mark_batch(batch_key: str, record_count: int) -> None:
    connection = get_connection()
    try:
        with connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO backfill_progress (batch_key, completed_at, record_count)
                VALUES (?, ?, ?)
                """,
                (batch_key, dt.datetime.now(dt.timezone.utc).isoformat(), record_count),
            )
    finally:
        connection.close()


def _epoch_window(decay_month: str, window_days: int) -> tuple[str, str]:
    """Epoch range covering the run-up to decays in the given YYYY-MM."""
    month_start = dt.date.fromisoformat(f"{decay_month}-01")
    next_month = (month_start.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return (month_start - dt.timedelta(days=window_days)).isoformat(), next_month.isoformat()


def _parse_records(records: list[dict]) -> tuple[list[ParsedSnapshot], int]:
    """Convert gp_history rows into snapshots, dropping unparseable TLEs.

    Two decades of archived TLEs contain some malformed and pre-launch rows;
    one bad line should cost that record, not the whole batch.
    """
    parsed: list[ParsedSnapshot] = []
    skipped = 0

    for record in records:
        line1 = record.get("TLE_LINE1")
        line2 = record.get("TLE_LINE2")
        norad_id = record.get("NORAD_CAT_ID")

        if not (line1 and line2 and norad_id):
            skipped += 1
            continue

        try:
            orbital_parameters = parse_orbital_parameters(line1, line2)
        except Exception:
            skipped += 1
            continue

        parsed.append((norad_id, record.get("OBJECT_NAME") or "", line1, line2, orbital_parameters))

    return parsed, skipped


async def backfill_decayed(
    since_year: int,
    window_days: int,
    batch_size: int,
    max_batches: int | None,
) -> None:
    groups = _decayed_targets(since_year)
    if not groups:
        logger.warning("No decayed objects found since %d; is satcat populated?", since_year)
        return

    batches: list[tuple[str, str, list[int]]] = []
    for month in sorted(groups):
        norad_ids = groups[month]
        for index in range(0, len(norad_ids), batch_size):
            batch_key = f"decayed:{month}:{index // batch_size}"
            batches.append((batch_key, month, norad_ids[index : index + batch_size]))

    completed = _completed_batches()
    pending = [batch for batch in batches if batch[0] not in completed]

    logger.info(
        "Backfill plan: %d objects, %d batches (%d done, %d pending)",
        sum(len(ids) for ids in groups.values()),
        len(batches),
        len(batches) - len(pending),
        len(pending),
    )

    if max_batches is not None:
        pending = pending[:max_batches]
        logger.info("Limiting this run to %d batches", len(pending))

    if not pending:
        logger.info("Nothing to do; backfill is already complete for these targets.")
        return

    async with SpaceTrackClient() as client:
        for position, (batch_key, month, norad_ids) in enumerate(pending, start=1):
            start, end = _epoch_window(month, window_days)
            ids = ",".join(str(norad_id) for norad_id in norad_ids)
            path = (
                f"class/gp_history/NORAD_CAT_ID/{ids}"
                f"/EPOCH/{start}--{end}/format/json"
            )

            records = await client.query(path)
            parsed, skipped = _parse_records(records)

            if parsed:
                save_snapshots(parsed)
            _mark_batch(batch_key, len(parsed))

            logger.info(
                "[%d/%d] %s: %d fetched, %d saved, %d skipped",
                position,
                len(pending),
                batch_key,
                len(records),
                len(parsed),
                skipped,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--since-year",
        type=int,
        default=2015,
        help="Only backfill objects that decayed in or after this year (default: 2015)",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=180,
        help="Days of TLE history to pull before each decay (default: 180)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Objects per Space-Track query (default: 50)",
    )
    parser.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Stop after this many batches; useful for a small first test run",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(
        backfill_decayed(
            since_year=args.since_year,
            window_days=args.window_days,
            batch_size=args.batch_size,
            max_batches=args.max_batches,
        )
    )


if __name__ == "__main__":
    main()
