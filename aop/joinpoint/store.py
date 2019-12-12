from typing import List

from aop.joinpoint import JoinPoint


class JoinPointStore:

    def __init__(self):
        self._join_points: List[JoinPoint] = []

    def new_join_point(self, obj: object, point: str):
        for jp in self._join_points:
            if jp.obj == obj and jp.point == point:
                return jp
        else:
            jp = JoinPoint(obj, point)
            self._join_points.append(jp)
            return jp

    def clear(self):
        """清除所有的join points，并将连接点恢复为原功能"""
        for join_point in self._join_points:
            join_point.unset_join_point()
        self._join_points = []

    def get_join_points(self) -> List[JoinPoint]:
        return self._join_points
