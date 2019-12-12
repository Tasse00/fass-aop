from typing import Dict

# from fass_aop import JoinPointStore
from aop.aspect import Aspect, LazyAspect
from aop.signals import SIG_ASPECT_ADDED, notifier
from aop.utils import import_target


class AspectStore:

    def __init__(self):
        self.aspects: Dict[str, Aspect] = {}

    def add_aspect(self, name: str, aspect: Aspect):
        self.aspects[name] = aspect
        notifier.trigger(SIG_ASPECT_ADDED, name, aspect)

    def new_aspect_from_config(self, name: str, aspect_cls_expr: str, args=None, kwargs=None):
        aspect_cls = import_target(aspect_cls_expr)
        args = args or []
        kwargs = kwargs or {}
        aspect = aspect_cls(*args, **kwargs)
        self.add_aspect(name, aspect)

    def get_aspect(self, name: str) -> Aspect:
        return self.aspects.get(name, LazyAspect(name))

    def clear(self):
        self.aspects = []
