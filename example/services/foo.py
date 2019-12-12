from aop import use_aspect


class Foo:

    @use_aspect("logger")
    def pipe(self, input):
        return input
