################################################################################
## settings.py
################################################################################
## Enthält alle wichtigen informationen für Einstellungen
################################################################################

import os, json

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
)

from kaffee_server.admin import login_required


bp = Blueprint("settings", __name__, url_prefix="/settings")


def save_configuration(settings: dict):
    current_app.config.update(settings)
    config_path = os.path.join(current_app.instance_path, "config.json")
    with open(config_path, "w") as f:
        json.dump(obj=settings, fp=f, sort_keys=True, indent=4)
    print(f"Saved config to {config_path}...")


@bp.route("/")
@login_required
def index():
    return render_template(
        "admin/settings.html", admin=g.user, config=current_app.config
    )


@bp.route("/save", methods=["POST"])
@login_required
def change_price():
    price = request.form["price"]
    brand = request.form["brand"]
    bean = request.form["bean"]

    name = request.form["contactname"]
    email = request.form["contactemail"]
    phone = request.form["contactphone"]

    save_configuration(
        {
            "DRINK_PRICE": int(price),
            "BEANINFO": {"brand": brand, "type": bean},
            "CONTACT": {"name": name, "email": email, "phone": phone},
        }
    )
    return redirect(url_for(".index"))
