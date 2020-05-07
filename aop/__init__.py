from types import MethodType

from aop.aspect import Aspect
from aop.aspect.store import AspectStore
from aop.joinpoint.store import JoinPointStore
from aop.pointcut import Pointcut
from aop.pointcut.matcher import PointcutMatcher
from aop.signals import notifier, SIG_ASPECT_ADDED, SIG_MODULE_LOADED
from aop.utils import import_target

join_point_store = JoinPointStore()
aspect_store = AspectStore()
point_cut_matcher = PointcutMatcher(join_point_store, aspect_store)


@notifier.on(SIG_ASPECT_ADDED)
def _on_aspect_added_jps_lazy_load_aspect(aspect_name, added_aspect):
    for jp in join_point_store.get_join_points():
        jp.lazy_load_aspect(aspect_name, added_aspect)


@notifier.on(SIG_MODULE_LOADED)
def _on_module_loaded(module):
    point_cut_matcher.match_advance_set_pointcuts(module)


def use_aspect(aspect_name: str, order: int = 16):
    """decorator usage"""

    # @TIPS use_aspect执行时必须确保aop已经install，否则无法确保生效
    #       aop包默认导入时install()

    def register(f):
        """register join point"""
        # 当前文件没有 exec_module 完成，无法通过f.__module__导入
        # 通过on_module_executed事件，在当前module, exec_module完成后再进行属性匹配
        # pc = Pointcut(expr=f'{f.__module__}.{f.__qualname__}', aspect_name=aspect_name, order=order)
        # logger.debug("register '%s' on module '%s' executed" % (pc, f.__module__))

        # use_aspect 使用时机可能比aop.install更早，所以无法通过import hook的方式完成切面织入。
        point_cut_matcher.add_pointcut(f'{f.__module__}.{f.__qualname__}', aspect_name, order)
        return f

    return register


def install():
    """
    1. 包装meta_path中的importer
    2. 确保切面已经按照matcher中存在的pointcut织入到已经加载的module中
    """
    import sys
    for finder in sys.meta_path:

        if hasattr(finder, "find_spec"):

            finder.ori_find_spec = finder.find_spec

            def wrap_find_spec(cls, fullname, path=None, target=None):

                spec = cls.ori_find_spec(fullname, path, target)
                if spec:
                    loader = spec.loader
                    if hasattr(loader, 'exec_module'):
                        ori_exec_module = loader.exec_module
                        def aop_exec_module(module):
                            ret = ori_exec_module(module)
                            # 装饰器方式引入的切点
                            notifier.trigger(SIG_MODULE_LOADED, module)
                            # point_cut_matcher.on_module_executed(module)
                            # point_cut_matcher.match_advance_set_pointcuts(module)
                            return ret

                        loader.exec_module = aop_exec_module
                    else:
                        pass
                        # # TODO
                        # # loader.load_module 是read only属性，所以暂时略过
                        # ori_load_module = loader.load_module
                        # def aop_load_module(fullname):
                        #     module = ori_load_module(fullname)
                        #     # 装饰器方式引入的切点
                        #
                        #     notifier.trigger(SIG_MODULE_LOADED, module)
                        #     # point_cut_matcher.on_module_executed(module)
                        #     # point_cut_matcher.match_advance_set_pointcuts(module)
                        #     return ret
                        # loader.load_module = aop_load_module
                return spec

            # 保持cls变量的传入，避免使用外部的finder，与循环变量同名致函数内部用错
            finder.find_spec = MethodType(wrap_find_spec, finder)
        else:

            finder.ori_find_module = finder.find_module

            def wrap_find_module(cls, fullname, path=None):
                loader = cls.ori_find_module(fullname, path)
                if loader:
                    if hasattr(loader, "exec_module"):
                        ori_exec_module = loader.exec_module

                        def aop_exec_module(module):
                            ret = ori_exec_module(module)
                            notifier.trigger(SIG_MODULE_LOADED, module)
                            # point_cut_matcher.on_module_executed(module)
                            # point_cut_matcher.match_advance_set_pointcuts(module)
                            return ret

                        loader.exec_module = aop_exec_module
                    else:
                        # TODO
                        # AttributeError: '_SixMetaPathImporter' object has no attribute 'exec_module'
                        pass

                return loader

            # 保持cls变量的传入，避免使用外部的finder，与循环变量同名致函数内部用错
            finder.find_module = MethodType(wrap_find_module, finder)

    point_cut_matcher.rematch_imported_modules()


def uninstall():
    """
    1. 恢复meta_path中的importer
    2. 清除join point，并恢复所有目标的原方法
    pointcut配置将不会清除
    """
    import sys
    for finder in sys.meta_path:
        if hasattr(finder, 'ori_find_spec'):
            setattr(finder, 'find_spec', finder.ori_find_spec)
            delattr(finder, 'ori_find_spec')
    join_point_store.clear()


def from_config(config: dict):
    """
    数据格式参照

    aspects:
      prefix:
        class: example.aspects.prefix.StrPrefixAspect
        args: ["prefix-01"]
      logger:
        class: example.aspects.logger.Logger
        kwargs:
          logger_name: logger-01
      profiler:
        class: aop.aspect.collection.profiler.SimpleProfiler
    pointcuts:
      logger:
        - example.apis.*.*Api.get
      prefix:
        - pointcut: example.services.foo.Foo.pipe
          order: 20
      profiler:
        - pointcut: example.apis.*.*Api.get
          order: 1
        - pointcut: example.services.foo.Foo.pipe
          order: 1
    """

    aspects = config['aspects']
    for name, setting in aspects.items():
        aspect_store.new_aspect_from_config(name, setting['class'], setting.get('args'), setting.get('kwargs'))

    pointcuts = config['pointcuts']
    for aspect_name, point_cut_conf_list in pointcuts.items():
        for point_cut_conf in point_cut_conf_list:
            if isinstance(point_cut_conf, str):
                point_cut_matcher.add_pointcut(point_cut_conf, aspect_name)
            else:
                point_cut_matcher.add_pointcut(point_cut_conf['pointcut'], aspect_name,
                                               int(point_cut_conf.get('order', 16)))


install()
