from dataclasses import dataclass


@dataclass
class Pointcut:
    # 切点表达式
    # eg.
    #   server.apis.v1.*.get|post
    #   server.apis.v*.get|post
    #   server.apis.^vs*.get|post
    #   server.apis.*Api,^x.get|post
    # 语法:
    #   "*" 通配符，"_"开头的属性不在匹配范围内
    #   "|" 或，区分两个表达式
    #   "^" 不符合后续表达逻辑其后可紧跟常量表达式或通配表达式
    #   "," 连接多个条件,且每个条件都需要通过
    # 语法解释优先级
    #   valid = isMeetRule(attrName)
    #
    #   1) 依据','切分条件(Condition)，attrName需要满足全部条件．
    #   2) 每个条件按照'|'切分为子条件,满足任一子条件即可
    #   3) 执行'*','^'对应的匹配规则
    #
    #   举例说明:
    #       "get|p*,^*st"
    #   转化判断逻辑表达式子: [ attr.match(get) | attr.match("p*") ] and [ not attr.match("*st") ]
    #   输入: [get, post, put]
    #   输出: [True, False, True]


    expr: str
    aspect_name: str  # 切面名称
    order: int  # 切点中切面排序
