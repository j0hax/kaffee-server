################################################################################
## __init__.py
################################################################################
## Starten der Flask App:
## $ export FLASK_APP=kaffee_server
## $ export FLASK_ENV=development
## $ flask init-db
## $ flask run
################################################################################

import os

from flask import Flask, render_template, session
from flask_cors import CORS

import locale
from datetime import datetime

from kaffee_server.users import get_users, get_transactions

from werkzeug.middleware.proxy_fix import ProxyFix

locale.setlocale(locale.LC_ALL, "de_DE")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # App is behind one proxy that sets the -For and -Host headers.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "kaffee.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that displays key statistics
    # more can be done in a seperate file later
    @app.route("/")
    def overview():
        return render_template(
            "overview.html", users=get_users(), transactions=get_transactions()
        )

    # register database
    from . import db

    db.init_app(app)

    # register API blueprint
    from . import api

    app.register_blueprint(api.bp)

    # register admin blueprint
    from . import admin

    app.register_blueprint(admin.bp)

    # Add our custom filters
    @app.template_filter("from_cents")
    def from_cents(cents: int) -> float:
        if not cents:
            return 0
        return cents / 100

    @app.template_filter("pretty_currency")
    def pretty_currency(cents: int) -> str:
        return locale.currency(from_cents(cents))

    @app.template_filter("pretty_date")
    def pretty_date(timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%a, %x um %X")

    @app.template_filter("pretty_number")
    def pretty_number(number: float) -> str:
        return locale.format_string("%d", number, grouping=True)

    return app
