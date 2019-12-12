from typing import Any


# from fass_aop.joinpoint.proceeding import ProceedingJoinPoint


class Aspect:

    def before(self, join_point):
        pass

    def after_result(self, result: Any, join_point):
        return result

    def after_exception(self, e: Exception, join_point):
        pass

    def after(self, join_point):
        pass

    # 此处引入ProceedingJoinPoint会导致循环引用
    # def around(self, pjp: ProceedingJoinPoint):
    def around(self, pjp):
        return pjp.proceed()


class LazyAspect(Aspect):
    """
    当aspect尚未被装载入store时，JoinPoint.add_aspect所需的aspect实例由LazyAspect代替占位。
    AspectStore.add_aspect时会依托于join_point_store进行所有join_point对lazy_aspect替换
    """

    def __init__(self, lazy_aspect_name: str):
        self.lazy_aspect_name = lazy_aspect_name

    def _err(self):
        return RuntimeError("lazy aspect '%s' not loaded!" % self.lazy_aspect_name)

    def before(self, join_point):
        raise self._err()

    def after_result(self, result: Any, join_point):
        raise self._err()

    def after(self, join_point):
        raise self._err()

    def after_exception(self, e: Exception, join_point):
        raise self._err()

    def around(self, pjp):
        raise self._err()

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.lazy_aspect_name)
