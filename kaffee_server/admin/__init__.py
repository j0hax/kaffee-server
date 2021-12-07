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
    send_file,
    current_app,
    escape,
)
from werkzeug.security import check_password_hash, generate_password_hash

from kaffee_server.db import get_db, close_db
from kaffee_server.users import (
    get_users,
    merge_users,
    get_transactions,
    insert_transaction,
    delete_user,
    sum_transactions,
    undo_transaction,
)

import time
import csv
import tempfile
import gzip
import os

bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("admin.login", next=request.path))

        return view(**kwargs)

    return wrapped_view


@bp.route("/")
def index():
    return redirect(url_for(".users"))


@bp.route("/users")
@login_required
def users():
    return render_template("admin/users.html", admin=g.user, users=get_users())


@bp.route("/transactions")
@login_required
def transactions():
    return render_template(
        "admin/transactions.html",
        admin=g.user,
        balance=sum_transactions(),
        transactions=get_transactions(limit=100),
    )


@bp.route("/backups")
@login_required
def backups():
    return render_template("admin/backups.html", admin=g.user)


@bp.route("/account")
@login_required
def admin_account():
    return render_template("admin/account.html", admin=g.user)


@bp.route("/save/password", methods=["POST"])
@login_required
def save_admin_password():
    """ Change the admin password """
    current_app.logger.warning("Changing administrator password")
    password = request.form.get("password")
    hashed = generate_password_hash(password)
    username = session.get("user_id")

    with get_db() as con:
        con.cursor().execute(
            "UPDATE admins SET password = ? WHERE username = ?",
            (hashed, username),
        )
        flash("Passwort geändert.")

    return redirect(url_for(".account"))


@bp.route("/save/transaction", methods=["POST"])
@login_required
def save_transaction():
    data = {
        "user": 0,
        "amount": -(int(request.form.get("amount")) * 100),
        "description": f"[{request.form.get('user')}] {request.form.get('description')}",
        "timestamp": time.time(),
    }
    insert_transaction(data)

    return redirect(url_for(".transactions"))


@bp.route("/save/user", methods=["POST"])
@login_required
def save_table():
    user_id = request.form.get("id")
    user_name = request.form.get("name")
    action = request.form.get("action")

    if action == "delete":
        delete_user(user_id)
        flash("Deleted user " + user_name)
        return redirect(url_for(".users"))

    if action == "undo":
        undo_transaction(user_id)
        flash(f"Letzte Transaktion von {user_name} gelöscht.")
        return redirect(url_for(".users"))

    # Assume we are getting one row
    user = [
        {
            "id": user_id,
            "name": user_name,
            "lastUpdate": time.time(),
            "transponder": request.form.get("transponder_code"),
        }
    ]

    merge_users(user)

    # Check if a deposit was made
    if "payment" in request.form:
        # TODO: ensure there are no float innaccuracies
        payment = round(float(request.form.get("payment")) * 100)
        with get_db() as db:
            db.execute(
                "INSERT INTO transactions (user, amount, description) VALUES (?,?,?)",
                (user[0]["id"], payment, "Transaktion durch Adminbereich"),
            )

    flash("Updated user " + request.form.get("name"))

    return redirect(url_for(".users"))


@bp.route("/dump/users")
def dump_users():
    """Downloads a CSV of user data"""
    current_app.logger.info("User data dump requested")
    outfile = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8")
    users = get_users()

    dict_writer = csv.DictWriter(outfile, users[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(users)
    outfile.flush()

    return send_file(outfile.name, as_attachment=True, attachment_filename="users.csv")


@bp.route("/dump/database")
def dump_db():
    """Downloads a compressed dump of the database"""
    current_app.logger.info("Database dump requested")
    db = get_db()
    with gzip.open(tempfile.NamedTemporaryFile().name, "wb") as f:
        for line in db.iterdump():
            f.write(f"{line}\n".encode())

        f.flush()

        return send_file(
            f.name, as_attachment=True, attachment_filename="database.sql.gz"
        )


@bp.route("/dump/restore", methods=["GET", "POST"])
def restore_db():
    """Restores a compressed dump of the database"""
    if request.method == "POST":
        current_app.logger.warning("Attempting to restore from dump")

        # check if the post request has the file part
        if "file" not in request.files:
            flash("Keine Datei!")
            return redirect(url_for(request.url))

        # Rename the old Database
        close_db()
        db_name = current_app.config.get("DATABASE")
        os.rename(db_name, db_name + ".old")

        # Read the file into the database
        file = request.files["file"]

        data = gzip.decompress(file.read()).decode()

        with get_db() as con:
            # BUG: https://github.com/python/cpython/pull/9621#issuecomment-867623231
            con.execute("CREATE TABLE sqlite_sequence(name varchar(255), seq int);")
            con.executescript(data)

        flash("Daten erfolgreich wiederhergestellt")
        return redirect("/")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        next_url = request.form.get("next")
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
            current_app.logger.info(f"{username} logged in")
            session.clear()
            session["user_id"] = user["username"]
            if next_url:
                return redirect(escape(next_url))
            return redirect(url_for(".admin"))

        current_app.logger.warn(f"{error} ({username}:{password})")
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
    if g.user:
        username = g.user["username"]
        current_app.logger.info(f"Logging out {username}")
    session.clear()
    return redirect("/")