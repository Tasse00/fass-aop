import collections
import time
from aop import Aspect
from aop.joinpoint.proceeding import ProceedingJoinPoint


class SimpleProfiler(Aspect):
    """若目标抛出异常则不计入统计范围内"""

    def __init__(self):
        self.counter = collections.OrderedDict()  # {joinpoint: [count, average_cost]}

    def around(self, pjp: ProceedingJoinPoint):
        item = self.counter.setdefault(pjp.join_point.get_name(), [0.0, 0.0])  # [count, cost]

        start_at = time.time()

        ret = pjp.proceed()

        cost = time.time() - start_at
        item[1] = (item[0] * item[1] + cost) / (item[0] + 1)
        item[0] += 1
        return ret

    def console_report(self):
        """控制台打印执行次数、耗时统计"""
        print(self.format_console_report())

    def format_console_report(self) -> str:
        name_len = max(len(k) for k in self.counter.keys())
        total = ""
        fmt = '{k:%d}|{c:10}|{v:10}\n' % name_len
        total += '\n' + fmt.format(k="Fun", c="Count", v="AveCost")
        for k, v in self.counter.items():
            total += fmt.format(k=k, c=v[0], v=v[1])
        return total
