# -*- coding: utf-8 -*-

################################################################################
## __init__.py
################################################################################
## Starten der Flask App:
## $ export FLASK_APP=kaffee_server
## $ export FLASK_ENV=development
## $ flask init-db
## $ flask run
################################################################################

import logging
import os, json

from flask import Flask, render_template, request
from flask_cors import CORS
import locale
from datetime import datetime
from platform import system
from time import time
from kaffee_server.users import get_users

from werkzeug.middleware.proxy_fix import ProxyFix

locale.setlocale(locale.LC_ALL, "de_DE")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # App is behind one proxy that sets the -For and -Host headers.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    CORS(app)
    app.config.from_mapping(
        SCHEDULER_API_ENABLED=True,
        SECRET_KEY=os.urandom(32),
        DATABASE=os.path.join(app.instance_path, "kaffee.sqlite"),
        BACKUP_DIR=os.path.join(app.instance_path, "backups"),
        DRINK_PRICE=40,
        MOTD="Willkommen!",
        BEANINFO={"brand": "Tchibo", "type": "Espresso, Mailänder Art"},
        CONTACT={
            "name": "Johannes Arnold",
            "email": "johannes.arnold@stud.uni-hannover.de",
            "phone": "",
        },
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_file("config.json", json.load, silent=True)

    # Set up the logger
    logfile = os.path.join(app.instance_path, "server.log")
    filelogger = logging.FileHandler(logfile, encoding="utf-8")
    # Allow for overriding the default level
    pref_level = os.environ.get("LOGLEVEL", logging.INFO)
    app.logger.addHandler(filelogger)
    app.logger.setLevel(pref_level)

    # Initialize the database
    from . import db

    db.init_app(app)

    # a simple page that displays key statistics
    # more can be done in a seperate file later
    @app.route("/")
    def overview():
        return render_template("overview.html", users=get_users())

    # register API blueprint
    from . import api, admin, settings, error_handlers

    app.register_blueprint(api.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(error_handlers.bp)

    # Add our custom filters
    @app.template_filter("from_cents")
    def from_cents(cents: int) -> float:
        """ Formats an amount of cents into full currency """
        if not cents:
            return 0
        return cents / 100

    @app.template_filter("pretty_currency")
    def pretty_currency(cents: int) -> str:
        """ Formats an amount of cents as a localized String """
        return locale.currency(from_cents(cents))

    @app.template_filter("pretty_date")
    def pretty_date(timestamp: float) -> str:
        """ Formats a UNIX Timestamp as a localized string """
        return datetime.fromtimestamp(timestamp).strftime("%A, %x")

    @app.template_filter("pretty_number")
    def pretty_number(number: float) -> str:
        """ Formats a number with localized seperators """
        return locale.format_string("%d", number, grouping=True)

    @app.before_request
    def log_request():
        """Log requests"""
        app.logger.debug(
            f"{request.remote_addr} -> {request.method} {request.full_path}"
        )

    @app.after_request
    def set_header(request):
        """Add custom headers to each request"""
        request.headers["Server"] = f"Kaffee-Server/{0.1} ({system()})"
        request.date = time()
        request.headers["X-Powered-By"] = "Coffee, black."
        return request

    return app
