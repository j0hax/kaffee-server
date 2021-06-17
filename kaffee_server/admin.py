################################################################################
## admin.py
################################################################################
## Behandelt Authentifizierung (login) und die Übersicht von Administratorn
################################################################################

import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_file
)
from werkzeug.security import check_password_hash, generate_password_hash

from kaffee_server.db import get_db
from kaffee_server.users import (
    get_users,
    merge_users,
    get_transactions,
    insert_transaction,
    delete_user,
)

import time
import csv
import tempfile

bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("admin.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/")
@login_required
def index():
    return render_template(
        "admin/admin.html", users=get_users(), transactions=get_transactions()
    )


@bp.route("/save/password", methods=["POST"])
@login_required
def save_admin_password():
    password = request.form["password"]
    hashed = generate_password_hash(password)
    username = session.get("user_id")

    with get_db() as con:
        con.cursor().execute(
            "UPDATE admins SET password = ? WHERE username = ?",
            (hashed, username),
        )
        flash("Passwort geändert.")

    return redirect(url_for(".index"))


@bp.route("/save/transaction", methods=["POST"])
@login_required
def save_transaction():
    data = {
        "user": 0,
        "amount": -(int(request.form["amount"]) * 100),
        "description": f"[ADMIN/{request.form['user']}] {request.form['description']}",
        "timestamp": time.time(),
    }
    print(data)
    insert_transaction(data)

    return redirect(url_for(".index"))


@bp.route("/save/user", methods=["POST"])
@login_required
def save_table():
    user_id = request.form["id"]
    user_name = request.form["name"]

    if request.form["action"] == "delete":
        delete_user(user_id)
        flash("Deleted user " + user_name)
        return redirect(url_for("admin"))

    # Assume we are getting one row
    user = [
        {
            "id": user_id,
            "name": user_name,
            "lastUpdate": time.time(),
            "transponder": request.form["transponder_code"],
        }
    ]

    merge_users(user)

    # Check if a deposit was made
    if "payment" in request.form:
        # TODO: ensure there are no float innaccuracies
        payment = round(float(request.form["payment"]) * 100)
        if payment > 0:
            db = get_db()
            c = db.cursor()
            c.execute(
                "INSERT INTO transactions (user, amount, description) VALUES (?,?,?)",
                (user[0]["id"], payment, "Einzahlung durch Adminbereich"),
            )
            db.commit()

    flash("Updated user " + request.form["name"])

    return redirect(url_for(".index"))


@bp.route("/dump/users")
def dump_users():
    """Downloads a CSV of user data"""
    outfile = tempfile.NamedTemporaryFile(mode="w")
    users = get_users()

    dict_writer = csv.DictWriter(outfile, users[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(users)
    outfile.flush()

    return send_file(outfile.name, as_attachment=True, attachment_filename="users.csv")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["username"]
            return redirect(url_for(".index"))

        flash(error)

    return render_template("admin/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute("SELECT * FROM admins WHERE username = ?", (user_id,))
            .fetchone()
        )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".index"))
