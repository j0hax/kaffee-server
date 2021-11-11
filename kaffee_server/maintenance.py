################################################################################
## maintenance.py
################################################################################
## Führt periodische Wartungen mittels APScheduler aus
################################################################################

import os
from kaffee_server.db import get_db
from flask import current_app
from flask_apscheduler import APScheduler
from glob import iglob
import filecmp
from time import strftime, time

scheduler = APScheduler()


@scheduler.task("cron", day_of_week=6)
def vacuum_database():
    """Optimizes the Database file"""
    with scheduler.app.app_context():
        current_app.logger.info(f"Vacuuming database")
        with get_db() as con:
            con.execute("VACUUM")
        current_app.logger.info(f"Finished vacuuming")


@scheduler.task("interval", days=1)
def backup_database():
    """Saves an optimized copy of the database to instance folder"""
    with scheduler.app.app_context():
        backup_dir = current_app.config.get("BACKUP_DIR")

        # Ensure the backup folder exists
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(
            backup_dir, strftime("BACKUP-%Y-%m-%d-%H%M%S.sqlite")
        )

        current_app.logger.info(f"Backing up to {backup_file}")

        with get_db() as db:
            db.execute("VACUUM main INTO ?", (backup_file,))

        current_app.logger.info(f"Finished backing up")

        prune_backups(pattern="BACKUP-*.sqlite")


def prune_backups(pattern="*"):
    """Deduplicate the backup directory"""

    backup_dir = ""

    with scheduler.app.app_context():
        backup_dir = current_app.config.get("BACKUP_DIR")

    expr = backup_dir + os.path.sep + pattern

    current_app.logger.debug(f"Pruning {expr}")

    all_files = iglob(expr)

    for i in all_files:
        # Remove files older than 1 month
        age = time() - os.path.getctime(i)
        if age > 60 * 60 * 24 * 31:
            current_app.logger.warning(f"Removing old file {i}")
            os.remove(i)
        for j in all_files:
            if i != j and os.path.exists(i) and os.path.exists(j):
                if filecmp.cmp(i, j, shallow=False):
                    current_app.logger.warning(f"Removing identical backup file {i}")
                    os.remove(i)
