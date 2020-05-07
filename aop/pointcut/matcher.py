import re
import sys
import warnings
from types import ModuleType, MethodType, FunctionType
from typing import List, Dict

from aop.aspect.store import AspectStore
from aop.joinpoint import JoinPoint
from aop.joinpoint.store import JoinPointStore
from aop.pointcut import Pointcut

POINT_CUT_TYPES = (MethodType, FunctionType)
POINT_CUT_PATH_TYPES = (object,)


class PointcutMatcher:

    def __init__(self, join_point_store: JoinPointStore, aspect_store: AspectStore):
        self.join_point_store = join_point_store
        self.aspect_store = aspect_store
        self.pointcut_list: List[Pointcut] = []
        self._module_executed_hooker: Dict[str, List[Pointcut]] = {}

    def add_pointcut(self, expr: str, aspect_name: str, order: int = 16):
        """添加一个切点规则"""
        pc = Pointcut(expr, aspect_name, order)
        self.pointcut_list.append(pc)

        # 将已导入的module立即匹配
        for module in sys.modules.values():
            self.match_pointcut(module, pc)

    def rematch_imported_modules(self):
        """将已经导入的modules重新匹配切点规则"""
        for module in sys.modules.values():
            for pc in self.pointcut_list:
                self.match_pointcut(module, pc)
            # self.on_module_executed(module)

    def clear_pointcuts(self):
        """清除全部切点规则"""
        self.pointcut_list = []

    @staticmethod
    def is_com_matched(com: str, expr: str):
        for expr_com in expr.split(','):
            condition_result = False
            for sub_expr in expr_com.split("|"):
                if sub_expr.startswith('^'):
                    if not re.fullmatch(sub_expr[1:].replace("*", ".*"), com):
                        condition_result = True
                        break
                else:
                    if re.fullmatch(sub_expr.replace("*", ".*"), com):
                        condition_result = True
                        break
            if not condition_result:
                return False
        return True

    def match_pointcut(self, module: ModuleType, pointcut: Pointcut):
        """module对单独一个切点进行检查、匹配"""
        # 排除不可控情况，使得程序可以继续运行下去
        # TODO
        # case 1:
        #   coverage run -m pytest 情况下出现module值为下述tuple
        #   (<coverage.debug.DebugOutputFile object at 0x7f10ad7eb1c0>, False)
        #
        if not isinstance(module, ModuleType):
            warnings.warn("invalid module: %s"%module)
            return

        # "server.api.v*.*.get|post" -> ['server', 'api', 'v*', '*', 'get|post']
        expr_com_list = pointcut.expr.split(".")

        # "server.api.v1.user" -> ['server', 'api', 'v1', 'user']
        module_com_lis = module.__name__.split(".")

        if len(module_com_lis) >= len(expr_com_list):
            return

        # validate module name
        if not all(self.is_com_matched(mod_com, expr_com) for mod_com, expr_com in zip(module_com_lis, expr_com_list)):
            return  # 当前module不满足当前切点

        # ["*", "get|post"]
        expr_com_list = expr_com_list[len(module_com_lis):]

        # 递归寻找module内部符合剩余切点表达式的method、function

        def _match(rest_expr_com_list: List[str], obj: object) -> List[JoinPoint]:
            if len(rest_expr_com_list) == 1:
                # 当前表达式指定了目标切点
                return [
                    self.join_point_store.new_join_point(obj, attr)
                    for attr in dir(obj)
                    if self.is_com_matched(attr, rest_expr_com_list[0]) and isinstance(getattr(obj, attr),
                                                                                       POINT_CUT_TYPES)
                ]
            else:
                curr_com_expr, next_rest_expr_com_list = rest_expr_com_list[0], rest_expr_com_list[1:]

                # 尚未达到切点
                return sum([
                    _match(next_rest_expr_com_list, getattr(obj, attr))
                    for attr in dir(obj)
                    if self.is_com_matched(attr, curr_com_expr) and not attr.startswith("__") and isinstance(
                        getattr(obj, attr),
                        POINT_CUT_PATH_TYPES)
                ], [])

        join_point_list = _match(expr_com_list, module)

        # 为切点注册aspect
        for join_point in join_point_list:
            join_point.add_aspect(self.aspect_store.get_aspect(pointcut.aspect_name), pointcut.order)

    def match_advance_set_pointcuts(self, module: ModuleType):
        """module对全部切点进行检查、匹配"""
        for pc in self.pointcut_list:
            self.match_pointcut(module, pc)
    #
    # def on_module_executed(self, module: ModuleType):
    #     self._module_executed_hooker.setdefault(module.__name__, list())
    #     for pc in self._module_executed_hooker[module.__name__]:
    #         self.match_pointcut(module, pc)

    # def register_on_module_executed(self, module: str, point_cut: Pointcut):
    #     print("module", module, point_cut)
    #     self._module_executed_hooker.setdefault(module, list())
    #     self._module_executed_hooker[module].append(point_cut)
