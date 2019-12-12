from aop.aspect import Aspect


class StrPrefixAspect(Aspect):

    def __init__(self, prefix: str = "prefix-01"):
        self.prefix = prefix

    def after_result(self, result: str, join_point):
        return self.prefix + result
