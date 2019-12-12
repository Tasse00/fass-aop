import logging

from aop.aspect import Aspect
from aop.joinpoint.proceeding import ProceedingJoinPoint


class Logger(Aspect):

    def __init__(self, logger_name: str = "aop.logger"):
        self.logger = logging.getLogger(logger_name)
        self.depth = 0

    def around(self, pjp: ProceedingJoinPoint):
        tag = "INVOKING"
        self.logger.info(f"[{tag:^12}]:{' ' * self.depth}{pjp.join_point.get_name()} with {pjp.get_params()}")
        self.depth += 1

        ret = pjp.proceed()

        tag = "INVOKED"
        self.depth -= 1
        self.logger.info(f"[{tag:^12}]:{' ' * self.depth}{pjp.join_point.get_name()} ret `{ret}`")

        return ret