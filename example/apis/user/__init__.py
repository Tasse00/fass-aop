from flask_restful import Resource

from example.services.foo import Foo


class UserApi(Resource):

    def get(self, name):
        return {"name": Foo().pipe(name)}, 200
