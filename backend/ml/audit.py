"""Reports whether the history DB is ready to train the deorbit model.

Re-run after each backfill session; the readiness check at the bottom is
what gates `python -m ml.train`.

    python -m ml.audit
"""

import sqlite3

from app.db import get_connection
from ml.config import MIN_DECAYED_OBJECTS, MIN_HISTORY_POINTS_PER_OBJECT

EARTH_RADIUS_KM = 6378.137


def _scalar(connection: sqlite3.Connection, sql: str, params: tuple = ()) -> float:
    return connection.execute(sql, params).fetchone()[0] or 0


def main() -> None:
    connection = get_connection()
    try:
        tle_rows = _scalar(connection, "SELECT COUNT(*) FROM tle_history")
        tle_objects = _scalar(connection, "SELECT COUNT(DISTINCT norad_id) FROM tle_history")
        decayed_total = _scalar(
            connection, "SELECT COUNT(*) FROM satcat WHERE decay_date IS NOT NULL"
        )

        decayed_with_history = _scalar(
            connection,
            """
            SELECT COUNT(*) FROM (
                SELECT t.norad_id FROM tle_history t
                JOIN satcat s USING (norad_id)
                WHERE s.decay_date IS NOT NULL
                GROUP BY t.norad_id
                HAVING COUNT(*) >= ?
            )
            """,
            (MIN_HISTORY_POINTS_PER_OBJECT,),
        )

        controlled = _scalar(
            connection,
            """
            SELECT COUNT(*) FROM (
                SELECT t.norad_id FROM tle_history t
                JOIN satcat s USING (norad_id)
                WHERE s.decay_date IS NOT NULL AND s.object_name LIKE 'STARLINK%'
                GROUP BY t.norad_id
                HAVING COUNT(*) >= ?
            )
            """,
            (MIN_HISTORY_POINTS_PER_OBJECT,),
        )

        non_drag = _scalar(
            connection,
            """
            SELECT COUNT(DISTINCT norad_id) FROM tle_history
            WHERE eccentricity > 0.1
            """,
        )

        negative_bstar = _scalar(connection, "SELECT COUNT(*) FROM tle_history WHERE bstar < 0")

        post_decay = _scalar(
            connection,
            """
            SELECT COUNT(*) FROM tle_history t JOIN satcat s USING (norad_id)
            WHERE s.decay_date IS NOT NULL AND t.epoch > s.decay_date || 'T23:59:59'
            """,
        )

        batches_done = _scalar(connection, "SELECT COUNT(*) FROM backfill_progress")
    finally:
        connection.close()

    print(f"TLE rows:                        {tle_rows:,}")
    print(f"Objects with TLE history:        {tle_objects:,}")
    print(f"Decayed objects in SATCAT:       {decayed_total:,}")
    print(
        f"Decayed objects with >= {MIN_HISTORY_POINTS_PER_OBJECT} TLEs: "
        f"{decayed_with_history:,}  (training positives)"
    )
    print(f"  of which Starlink (controlled): {controlled:,}")
    print(f"Objects with e > 0.1 (non-drag): {non_drag:,}")
    print(f"Rows with negative B*:           {negative_bstar:,}")
    print(f"Rows with epoch after decay:     {post_decay:,}")
    print(f"Backfill batches completed:      {batches_done:,}")

    usable = decayed_with_history - controlled
    ready = usable >= MIN_DECAYED_OBJECTS
    print()
    print(
        f"Ready to train: {'YES' if ready else 'NO'} "
        f"({usable:,} usable decayed objects, need {MIN_DECAYED_OBJECTS:,})"
    )


if __name__ == "__main__":
    main()
