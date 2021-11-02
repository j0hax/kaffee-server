################################################################################
## settings.py
################################################################################
## Enthält alle wichtigen informationen für Einstellungen
################################################################################

import os, json

from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
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
    price = request.form.get("price")
    brand = request.form.get("brand")
    bean = request.form.get("bean")

    name = request.form.get("contactname")
    email = request.form.get("contactemail")
    phone = request.form.get("contactphone")

    save_configuration(
        {
            "DRINK_PRICE": int(price),
            "BEANINFO": {"brand": brand, "type": bean},
            "CONTACT": {"name": name, "email": email, "phone": phone},
        }
    )
    return redirect(url_for(".index"))
