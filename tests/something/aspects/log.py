from typing import List, Any

from fass_aop import Aspect, ProceedingJoinPoint

run_log: List[str] = []


class Log01(Aspect):

    def __init__(self, name: str=""):
        self.name = name

    def log(self, msg: str):
        msg = f'{self.name}@{self.__class__.__name__} {msg}'
        run_log.append(msg)

    def before(self):
        self.log('before')

    def after_result(self, result: Any):
        self.log('after_result')
        return result

    def after_exception(self, e: Exception):
        self.log('after_exception')

    def after(self):
        self.log('after')

    def around(self, pjp: ProceedingJoinPoint):
        self.log('around start')
        result = pjp.proceed()
        self.log('around end')
        return result


class Log02(Log01):
    pass


def reset_run_log():
    run_log.clear()

def get_run_log():
    return run_log