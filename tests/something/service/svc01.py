class Service01:
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def raise_exception(self, exec: Exception):
        raise exec