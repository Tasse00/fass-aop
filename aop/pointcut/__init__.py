from dataclasses import dataclass


@dataclass
class Pointcut:
    # 切点表达式
    # eg.
    #   server.apis.v1.*.get|post
    #   server.apis.v*.get|post
    # 语法:
    #   "*" 通配符，"_"开头的属性不在匹配范围内
    #   "|" 或，区分两个表达式
    # 语法解释优先级
    #   "get|p*", 优先处理"|",将表达式分割为子表达式.切点匹配时子表达式之间为或关系。

    expr: str
    aspect_name: str  # 切面名称
    order: int  # 切点中切面排序
