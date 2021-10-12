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
from time import strftime

scheduler = APScheduler()


@scheduler.task("cron", day_of_week=6)
def vacuum_database():
    """Optimizes the Database file"""
    with scheduler.app.app_context():
        with get_db() as con:
            con.execute("VACUUM")


@scheduler.task("interval", days=1)
def backup_database():
    """Saves an optimized copy of the database to instance folder"""
    with scheduler.app.app_context():
        backup_dir = current_app.config["BACKUP_DIR"]

        # Ensure the backup folder exists
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(
            backup_dir, strftime("BACKUP-%Y-%m-%d-%H%M%S.sqlite")
        )

        current_app.logger.debug(f"Writing Backup to {backup_file}")

        with get_db() as db:
            db.execute("VACUUM main INTO ?", (backup_file,))

        prune_backups(pattern="BACKUP-*.sqlite")


def prune_backups(pattern="*"):
    """Deduplicate the backup directory"""

    backup_dir = ""

    with scheduler.app.app_context():
        backup_dir = current_app.config["BACKUP_DIR"]

    expr = backup_dir + os.path.sep + pattern

    current_app.logger.info(f"Pruning {expr}")

    all_files = iglob(expr)

    current_app.logger.debug(f"Comparing {len(iglob)} backups to another")

    for i in all_files:
        for j in all_files:
            if i != j and os.path.exists(i) and os.path.exists(j):
                if filecmp.cmp(i, j, shallow=False):
                    os.remove(i)
                    current_app.logger.warning(f"Removed identical backup file {i}!")