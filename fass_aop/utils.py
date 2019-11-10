import importlib


def import_target(target_expression: str):
    """依据expression获取对象"""
    components = target_expression.split('.')

    for idx in range(len(components)):
        package_path = ".".join(components[:len(components)-idx])

        try:
            mod = importlib.import_module(package_path)
        except ModuleNotFoundError:
            continue
        else:

            rest_components = components[len(components)-idx:]
            obj = mod
            for com in rest_components:
                obj = getattr(obj, com)
            return obj
    raise ValueError(f'"{target_expression}" is invalid expression!')
    # obj = __import__(import_path)
    # for com in components[1:]:
    #     try:
    #         ori = import_path
    #         import_path += "." + com
    #         __import__(import_path, fromlist=[ori])
    #         print(obj, com)
    #         obj = getattr(obj, com)
    #     except ImportError:
    #         obj = getattr(obj, com)
    # return obj
