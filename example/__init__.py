from flask import Flask
from flask_restful import Api


def create_app():
    app = Flask(__name__)
    api = Api(prefix="/api", app=app)

    from example.apis.config import ConfigApi
    import example.apis.user
    api.add_resource(ConfigApi, '/config')
    api.add_resource(example.apis.user.UserApi, "/user/<name>")

    return app
