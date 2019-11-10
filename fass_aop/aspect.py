from dataclasses import dataclass
from typing import Any, Tuple, List, Dict

from fass_aop.pointcut import Pointcut


class Aspect:
    """
    Around[Before -> Method -> After -> AfterResult]
    """
    order = 16

    def before(self):
        pass

    def after_result(self, result: Any):
        return result

    def after_exception(self, e: Exception):
        pass

    def after(self):
        pass

    def around(self, pjp: 'ProceedingJoinPoint'):
        return pjp.proceed()

    @classmethod
    def use(cls, order=None, aspect_args: Dict={}):
        order = cls.order if order is None else order

        def wrapper(func):
            target_expression, attribute = f'{func.__module__}.{func.__qualname__}'.rsplit('.', 1)
            ac = AspectConfig(aspect=cls(**aspect_args), order=order)

            # 头部插入确保不指定order时
            # Aspect的执行顺序如同配置装饰器的顺序
            #
            # @Aspect01
            # @Aspect02
            # def foo():
            #   pass
            #
            # @Aspect01 -> @Aspect02 -> foo -> @Aspect02 -> @Aspect01
            aspect_used_collections.insert(0, (target_expression, attribute, ac))
            return func

        return wrapper


@dataclass
class AspectConfig:
    aspect: Aspect
    order: int

    def __hash__(self):
        return hash(id(self.aspect))


# 收集在代码中设置的切面
# [(target_expr, attr, aspect_config),]
aspect_used_collections: List[Tuple[str, str, AspectConfig]] = []


class ProceedingJoinPoint:
    """JoinPoint执行时的运行对象"""

    def __init__(self, pointcut: Pointcut, rest_aspect_list: List[Aspect], args, kwargs):
        self._pointcut = pointcut
        self._rest_aspect_list = rest_aspect_list[1:]
        self._aspect = rest_aspect_list[0] if len(rest_aspect_list) != 0 else None
        self._args = args
        self._kwargs = kwargs

    @property
    def current_aspect(self):
        return self._aspect

    def proceed(self, args=None, kwargs=None) -> Any:
        """
        执行切入点自身，参数默认为原始参数
        """
        args = args or self._args
        kwargs = kwargs or self._kwargs

        lower_aspect_pjp = ProceedingJoinPoint(pointcut=self._pointcut,
                                               rest_aspect_list=self._rest_aspect_list,
                                               args=args,
                                               kwargs=kwargs)
        self._aspect.before()
        try:
            if lower_aspect_pjp.current_aspect:
                result = lower_aspect_pjp.current_aspect.around(lower_aspect_pjp)
            else:
                result = self._pointcut.method(*args, **kwargs)
        except Exception as e:
            self._aspect.after()
            self._aspect.after_exception(e)
            raise e
        else:
            self._aspect.after()
            return self._aspect.after_result(result)

    def get_args(self) -> Tuple[List[Any], Dict[str, Any]]:
        return self._args, self._kwargs
