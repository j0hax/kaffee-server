################################################################################
## maintenance.py
################################################################################
## Führt periodische Wartungen mittels APScheduler aus
################################################################################

import os
from datetime import datetime
from kaffee_server.db import get_db
from kaffee_server import logger
from flask import current_app
from flask_apscheduler import APScheduler

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
        # Ensure the backup folder in the instance folder exists
        dir = current_app.instance_path + "/backups"
        os.makedirs(dir, exist_ok=True)

        filename = f"{dir}/backup-{datetime.now()}.sqlite"

        with get_db() as db:
            db.execute("VACUUM main INTO ?", (filename,))
