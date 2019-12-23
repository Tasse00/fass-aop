import functools
from typing import List, Tuple

from aop.aspect import Aspect, LazyAspect


class JoinPoint:

    def __init__(self, obj: object, point: str):
        self.obj = obj
        self.point = point
        self.target = getattr(obj, point)
        self._ordered_aspects: List[Tuple[int, Aspect]] = []

        self.set_join_point()

    def set_join_point(self):
        """将自身替换到目标连接点，JoinPoint实例化时会自动进行该操作。"""

        # 实例调用时 __call__无法获取实例的self属性
        # setattr(self.obj, self.point, MethodType(self, self.obj))

        @functools.wraps(self.target)
        def join_point_proxy(*args, **kwargs):
            from aop.joinpoint.proceeding import ProceedingJoinPoint
            ordered_aspects = self.get_ordered_aspects()
            pjp = ProceedingJoinPoint(self, ordered_aspects, 0, args, kwargs)

            if pjp.has_aspects():
                return pjp.curr_aspect.around(pjp)
            else:
                return self.invoke_method(*args, **kwargs)

        setattr(self.obj, self.point, join_point_proxy)

    def unset_join_point(self):
        """使目标连接点恢复到原方法。"""
        setattr(self.obj, self.point, self.target)

    def add_aspect(self, aspect: Aspect, order: int):

        if isinstance(aspect, LazyAspect):

            # lazy aspect 可能同时存在多个实例，需要通过内部的lazy_aspect_name进行区分
            if aspect.lazy_aspect_name not in [a.lazy_aspect_name for _, a in self._ordered_aspects if
                                               isinstance(a, LazyAspect)]:
                self._ordered_aspects.append((order, aspect))
        else:
            # @TIPS 如果存在 "moduleA" 及 "moduleA.moduleB"，且moduleA中导入了moduleB
            #       那么当处于这两个module已经被加载的状态下时，去添加pointcut: 'moduleA.moduleB.XXX' 会导致其多次添加aspect
            #       因为match moduleA时因为其内有属性moduleB，所以可以被推导到切点位置。match moduleA.moduleB 时又会再次match到
            #       该join point并再次add_aspect.

            if aspect not in [a for _, a in self._ordered_aspects]:
                self._ordered_aspects.append((order, aspect))
                self._ordered_aspects.sort(key=lambda e: e[0])

    def get_ordered_aspects(self) -> List[Aspect]:
        return [a for o, a in self._ordered_aspects]

    def invoke_method(self, *args, **kwargs):
        return self.target(*args, **kwargs)

    def get_name(self):
        """获取连接点的描述名"""
        return self.obj.__module__ + "." + self.obj.__name__ + "." + self.point

    def lazy_load_aspect(self, aspect_name: str, aspect: Aspect):
        """懒加载aspect实例"""
        for idx, ordered_aspect in enumerate(self._ordered_aspects):
            order, existed_aspect = ordered_aspect
            if isinstance(existed_aspect, LazyAspect) and existed_aspect.lazy_aspect_name == aspect_name:
                self._ordered_aspects[idx] = (order, aspect)
                break

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.get_name())
