from kaffee_server import create_app

if __name__ == "__main__":
    import bjoern

    app = create_app()

    bjoern.run(app, "0.0.0.0", 5000)