from werkzeug.exceptions import HTTPException
from flask import Blueprint, render_template, current_app

bp = Blueprint("error_handlers", __name__)

# TODO: sqlite3.IntegrityError


@bp.app_errorhandler(Exception)
def handle_exception(e):
    """Generic Error Handler"""
    current_app.logger.exception(e)
    if isinstance(e, HTTPException):
        return render_template("errorpages/http.html", e=e), e.code

    # now you're handling non-HTTP exceptions only
    return render_template("errorpages/generic.html", e=e), 500
