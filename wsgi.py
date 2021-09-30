import json
from kaffee_server import create_app
from kaffee_server.maintenance import scheduler

if __name__ == "__main__":
    import bjoern

    app = create_app()

    app.config.from_file("config.json", json.load, silent=True)

    # Run scheduled maintenance only in production
    from kaffee_server.maintenance import scheduler

    scheduler.init_app(app)
    scheduler.start()

    bjoern.run(app, "0.0.0.0", 5000)
