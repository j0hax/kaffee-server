import logging
from werkzeug.exceptions import HTTPException
from flask import Blueprint, render_template, current_app, request
from uuid import uuid4
import sqlite3

bp = Blueprint("error_handlers", __name__)


@bp.app_errorhandler(HTTPException)
def http_error(e):
    """HTTP Error Handler"""

    # Log to a certain error ID
    e_id = uuid4()
    msg = f"HTTP {e.code}: {request.method} {request.url} (ID {e_id})"

    if e.code < 500:
        current_app.logger.warn(msg)
    else:
        current_app.logger.exception(e)

    return render_template("errorpages/http.html", e=e, id=e_id), e.code


@bp.app_errorhandler(sqlite3.IntegrityError)
def handle_sql(e):
    """SQLite related errors"""
    # Log to a certain error ID
    e_id = uuid4()
    current_app.logger.exception(e)

    return render_template("errorpages/sql.html", e=e, id=e_id), 409


@bp.app_errorhandler(Exception)
def handle_exception(e):

    # Log to a certain error ID
    e_id = uuid4()
    current_app.logger.exception(e)

    # now you're handling non-HTTP exceptions only
    return render_template("errorpages/generic.html", e=e, id=e_id), 500
