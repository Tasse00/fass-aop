from collections import defaultdict
from typing import List, Dict

from fass_aop.aspect import Aspect, ProceedingJoinPoint, AspectConfig, aspect_used_collections
from fass_aop.pointcut import Pointcut, PointcutParser
from fass_aop.utils import import_target

VERSION = "0.1.0"


class Weaver:
    """
    1. 解析所有切面设置
    2. 将同一具体切点的aspect进行排序后织入

        顺序指定方式
        1. Aspect中指定
        2. 配置中指定，会覆盖Aspect中的优先级设置


    伪代码如下 ::
        config = [
            {
                "pointcut_expression": "services.Service.*",
                "aspect": "aspects.log.LogAspect",
                "order": 10
            }
        ]
        pointcut_config = parse_config()
        for pointcut, aspects = pointcut_config.items():
            weave(pointcut, sort(aspects))

    """

    def __init__(self, pointcut_parser: PointcutParser, config_list: List[Dict]):
        self.pointcut_parser = pointcut_parser
        self.config_list = config_list

    def parse_config(self) -> Dict[Pointcut, List[AspectConfig]]:
        """通过配置文件的解析"""

        parsed = defaultdict(list)

        for cfg in self.config_list:
            pointcut_expression = cfg['pointcut']
            aspect_expression = cfg['aspect']
            aspect_args = cfg.get('aspect_args', {})

            pointcut_list = self.pointcut_parser.parse(pointcut_expression)
            aspect = self._get_aspect(aspect_expression, aspect_args)
            try:
                order = cfg['order']
            except KeyError:
                order = aspect.order

            for pt in pointcut_list:

                existed_aspect_idx = [idx for idx, ac in enumerate(parsed[pt]) if ac.aspect == aspect]
                existed_aspect_idx = existed_aspect_idx[0] if len(existed_aspect_idx) > 0 else -1
                if existed_aspect_idx == -1:
                    parsed[pt].append(AspectConfig(aspect=aspect, order=order))
                else:
                    parsed[pt][existed_aspect_idx] = AspectConfig(aspect=aspect, order=order)
        return parsed

    def parse_decorated(self) -> Dict[Pointcut, List[AspectConfig]]:
        """代码中直接装饰的Aspect解析"""
        parsed = defaultdict(list)
        for target_expr, attribute, aspect_config in aspect_used_collections:

            pt = Pointcut(import_target(target_expr), attribute)

            existed_aspect_idx = [idx for idx, ac in enumerate(parsed[pt]) if ac.aspect == aspect_config.aspect]
            existed_aspect_idx = existed_aspect_idx[0] if len(existed_aspect_idx) > 0 else -1
            if existed_aspect_idx == -1:
                parsed[pt].append(aspect_config)
            else:
                parsed[pt][existed_aspect_idx] = aspect_config
        return parsed

    def parse(self) -> Dict[Pointcut, List[AspectConfig]]:
        parsed: Dict[Pointcut, List[AspectConfig]] = defaultdict(list)
        # 解析代码中的配置
        parsed.update(self.parse_decorated())

        # 解析设置中的配置， 覆盖代码配置中同pointcut的同aspect配置参数。
        for pointcut, aspect_config_list in self.parse_config().items():
            for aspect_config in aspect_config_list:
                existed_aspect_config_idx = [idx for idx, eac in enumerate(parsed[pointcut]) if
                                             eac.aspect == aspect_config.aspect]
                existed_aspect_config_idx = existed_aspect_config_idx[0] if len(existed_aspect_config_idx) == 1 else -1
                if existed_aspect_config_idx != -1:
                    parsed[pointcut][existed_aspect_config_idx] = aspect_config
                else:
                    parsed[pointcut].append(aspect_config)

        # 按照order从小到大对各pointcut的aspect进行排序
        for _, aspect_config_list in parsed.items():
            aspect_config_list.sort(key=lambda ac: ac.order)

        return parsed

    def weave(self):
        parsed = self.parse()
        for pointcut, aspect_config_list in parsed.items():
            self._set_proxy(pointcut, [ac.aspect for ac in aspect_config_list])

    @staticmethod
    def _set_proxy(pointcut: Pointcut, aspect_list: List[Aspect]):
        def proxy(*args, **kwargs):
            pjp = ProceedingJoinPoint(pointcut=pointcut,
                                      rest_aspect_list=aspect_list,
                                      args=args,
                                      kwargs=kwargs)
            return pjp.current_aspect.around(pjp)

        proxy.__qualname__ = f'{pointcut.target.__qualname__}.aop_proxy'
        pointcut.set_proxy_method(proxy)

    @staticmethod
    def _get_aspect(aspect_expression: str, aspect_args: Dict) -> Aspect:
        return import_target(aspect_expression)(**aspect_args)


def weaveAll(cfg: List[Dict]):
    Weaver(pointcut_parser=PointcutParser(),
           config_list=cfg).weave()
