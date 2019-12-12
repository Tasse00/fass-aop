from typing import List, Tuple, Dict

from aop.aspect import Aspect
from aop.joinpoint import JoinPoint


class ProceedingJoinPoint:

    def __init__(self, join_point: JoinPoint, aspects: List[Aspect], aspect_idx: int, args, kwargs):
        self.join_point = join_point
        self._aspects = aspects
        self._aspect_idx = aspect_idx
        self._args = args
        self._kwargs = kwargs

    def has_aspects(self) -> bool:
        return len(self._aspects) > 0

    @property
    def curr_aspect(self) -> Aspect:
        return self._aspects[self._aspect_idx]

    def get_params(self) -> Tuple[List, Dict]:
        """获取方法运行时参数"""
        return self._args, self._kwargs

    def proceed(self, *args, **kwargs):
        """执行切入点自身，参数默认为原始参数"""
        ori_args, ori_kwargs = self.get_params()

        # 是否由切面制定了args, kwargs，若没有则使用运行时默认参数
        args = args or ori_args
        kwargs = kwargs or ori_kwargs

        self.curr_aspect.before(self.join_point)

        try:
            if self._aspect_idx + 1 < len(self._aspects):
                next_pjp = ProceedingJoinPoint(join_point=self.join_point,
                                               aspects=self._aspects,
                                               aspect_idx=self._aspect_idx + 1,
                                               args=args,
                                               kwargs=kwargs)
                result = next_pjp.curr_aspect.around(next_pjp)
            else:
                result = self.join_point.invoke_method(*args, **kwargs)
        except Exception as e:
            self.curr_aspect.after(self.join_point)
            self.curr_aspect.after_exception(e, self.join_point)
            raise e
        else:
            self.curr_aspect.after(self.join_point)
            return self.curr_aspect.after_result(result, self.join_point)
