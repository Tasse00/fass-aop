from tests.something.aspects.log import Log01, Log02


class ServiceDecorated:

    def __init__(self, name: str):
        self.name = name

    @Log02.use()
    @Log01.use()
    def get_name(self) -> str:
        return self.name

    @Log02.use(order=2)
    @Log01.use(order=1)
    def raise_exception(self, exec: Exception):
        raise exec

    @Log01.use()
    def get_name_decorated_log1(self) -> str:
        return self.name
