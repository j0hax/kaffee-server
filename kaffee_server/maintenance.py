################################################################################
## maintenance.py
################################################################################
## Führt periodische Wartungen mittels APScheduler aus
################################################################################

import os
from typing import Iterator
from kaffee_server.db import get_db
from flask import current_app
from flask_apscheduler import APScheduler
from glob import iglob
import filecmp
from time import strftime, time
from itertools import combinations
from multiprocessing import Pool

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
def auto_backup():
    with scheduler.app.app_context():
        backup_database()


def backup_database():
    """Saves an optimized copy of the database to instance folder"""

    backup_dir = current_app.config.get("BACKUP_DIR")

    # Ensure the backup folder exists
    os.makedirs(backup_dir, exist_ok=True)

    backup_file = os.path.join(backup_dir, strftime("BACKUP-%Y-%m-%d-%H%M%S.sqlite"))

    current_app.logger.info(f"Backing up to {backup_file}")

    with get_db() as db:
        db.execute("VACUUM main INTO ?", (backup_file,))

    current_app.logger.info(f"Finished backing up")

    prune_backups()


def list_backups() -> Iterator:
    """Lists Backup files"""
    backup_dir = current_app.config.get("BACKUP_DIR")
    expr = backup_dir + os.path.sep + "BACKUP-*.sqlite"
    return iglob(expr)


def remove_if_old(path: str):
    """Remove files older than 1 year"""
    month = 60 * 60 * 24 * 31
    age = time() - os.path.getctime(path)
    if age > month:
        name = os.path.basename(path)
        current_app.logger.warning(f"Removing old file {name}")
        os.remove(path)


def remove_duplicate(path1: str, path2: str):
    """Compares and removes duplicates"""
    if path1 != path2:
        if filecmp.cmp(path1, path2, shallow=False):
            name = os.path.basename(path2)
            current_app.logger.warning(f"Removing identical backup file {name}")
            os.remove(path2)


def prune_backups():
    """Prune unneeded files from the backup directory"""

    with Pool() as p:
        # Remove very old files first
        p.map(remove_if_old, list_backups())

        # Remove identical backup files
        p.starmap(remove_duplicate, combinations(list_backups(), 2))
