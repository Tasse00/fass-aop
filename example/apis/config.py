from flask_restful import Resource


class ConfigApi(Resource):
    def get(self):
        return {
            "config": "normal"
        }, 200