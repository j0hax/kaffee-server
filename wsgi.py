import json
from kaffee_server import create_app

if __name__ == "__main__":
    import bjoern

    app = create_app()

    app.config.from_file("config.json", json.load, silent=True)

    bjoern.run(app, "0.0.0.0", 5000)
