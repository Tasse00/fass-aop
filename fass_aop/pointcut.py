import importlib.util
import logging
import os
import re
import types
from pathlib import Path
from typing import List, Callable, Any

logger = logging.getLogger('FAss')


class Pointcut:
    def __init__(self, target: Any, attribute: str):
        self.target = target
        self.attribute = attribute
        self.method = getattr(target, self.attribute)
        global_pointcut_collections.add(self)

    def set_proxy_method(self, proxy: Callable):
        setattr(self.target, self.attribute, proxy)

    def unset_proxy_method(self):
        setattr(self.target, self.attribute, self.method)

    @property
    def identifier(self) -> str:
        return f'{self.target.__qualname__}.{self.attribute}'

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    @staticmethod
    def unset_proxy_all():
        global global_pointcut_collections
        for pt in global_pointcut_collections:
            pt.unset_proxy_method()
        global_pointcut_collections = set()


global_pointcut_collections = set()


class PointcutParser:

    def parse(self, expression: str) -> List[Pointcut]:
        """
        :param expression: 切点匹配规则，支持按.分割的正则表达式匹配
        :return:
        """

        components = expression.split('.')
        first_expr, rest_regs = components[0], components[1:]

        mod = globals().get(first_expr, None) or importlib.import_module(first_expr)

        return self._parse_reg(mod, first_expr, rest_regs[0], rest_regs[1:])

    def _parse_reg(self, target, prev: str, curr_reg: str, rest_regs: List[str]) -> List[Pointcut]:

        if isinstance(target, types.ModuleType) and Path(target.__file__).name == '__init__.py':
            matched_submodules = [os.path.splitext(item.name)[0] for item in Path(target.__file__).parent.iterdir() if
                                  not str(item.name).startswith('_') and re.match(curr_reg,
                                                                                  str(item.name).replace('.py', ''))]

            for sm in matched_submodules:
                try:
                    # 检查是否已经加载
                    getattr(target, sm)
                except AttributeError:
                    try:
                        importlib.import_module(".".join([prev, sm]))
                    except ModuleNotFoundError:
                        pass

        # 获取匹配的属性
        matched_attrs = [attr for attr in dir(target) if not attr.startswith("_") and re.match(curr_reg, attr)]

        pointcuts = []
        for attr in matched_attrs:

            val = getattr(target, attr)

            if isinstance(val, type) or isinstance(val, types.ModuleType):
                # class/module type. go iter
                curr_package_path = ".".join([prev, attr])

                if len(rest_regs) == 0:
                    # logger.info(f"endpoint {curr_package_path} is not Function/Method. Ignore it.")
                    continue

                # logger.info(f"parser step in {curr_package_path}")
                pointcuts.extend(self._parse_reg(val, curr_package_path, rest_regs[0], rest_regs[1:]))

            elif isinstance(val, types.FunctionType) or isinstance(val, types.MethodType):
                # function
                curr_package_path = ".".join([prev, attr])
                if len(rest_regs) == 0:
                    # logger.info(f"parsed pointcut {curr_package_path}")
                    pointcuts.append(Pointcut(target, attr))
                else:
                    # logger.info(f"parser step in {curr_package_path}")
                    pointcuts.extend(self._parse_reg(val, curr_package_path, rest_regs[0], rest_regs[1:]))
            else:
                # logger.info(f" route {curr_package_path} is not Function/Method")
                pass
        return pointcuts
