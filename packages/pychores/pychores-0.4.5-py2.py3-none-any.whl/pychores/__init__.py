"""
A flask app to help you manage your recurent tasks

I tried to use flak, sqlalchemy and pytest as cleanly as possible
This app is also a test about publishing a package using flit
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from ._version import version
from .configmodule import Config
from .model import DeferedSession

jwt = JWTManager()

__version__ = version


def respond_success(title, content):
    response_object = {
        "status": "success",
        title: content,
    }
    return jsonify(response_object)


def create_app(environment):
    app = Flask(__name__, static_folder="app", static_url_path="/chores")
    app.config.from_object(Config.get_config(environment))
    jwt.init_app(app)
    app.db_session = DeferedSession.get_session_local(
        app.config["SQLALCHEMY_DATABASE_URI"]
    )

    CORS(app, resources={r"/*": {"origins": "*"}})

    # sanity check route
    @app.route("/infos", methods=["GET"])
    def api_version():
        return respond_success("version", __version__)

    from .routes import auth, chores, tasks

    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(chores.bp)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return app.send_static_file("index.html")

    return app
