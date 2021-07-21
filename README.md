# AOP
> 2.1.0
>
最大限度的无侵入

- 不会改变项目中module的加载顺
- 通过配置织入切面

## 使用

```python
# app.py
if __name__ == "__main__":
    import aop
    aop.from_config({
        "aspects": {
            "profiler": {
                "class": "aop.aspect.collection.profiler.SimpleProfiler"
            }
        },
        "pointcuts": {
            "profiler": [
                 "example.apis.*.*Api.get"
            ]
        }
    })
```

## 配置语法

以yml格式举例

```yaml

# 定义切面实例
aspects:
  # key为自定义的切面实例名称
  prefix:
    class: example.aspects.prefix.StrPrefixAspect
    args: ["prefix-01"] # args与kwargs为切面实例化时的参数
  logger:
    class: example.aspects.logger.Logger
    kwargs:
      logger_name: werkzerg
  profiler:
    class: aop.aspect.collection.profiler.SimpleProfiler

# 定义切点织入切面
pointcuts:
  # key表示使用的切面名称 value为切点及织入配置的定义
  logger:
    - example.apis.*.*Api.get # str, 直接代表切点配置
  prefix:
    - pointcut: example.services.foo.Foo.pipe # 指定切点表达式
      order: 20 # 织入连接点时，多个切面的执行排序，数字越小越外层（切面执行为洋葱模型）
  profiler:
    - pointcut: example.apis.*.*Api.get
      order: 1
```

## ChangeLog

- 2.1.0
    
    增强了切点表达式的语法
    
    - 且点表达式中加入','条件切分符号
    - 切点表达式中加入'^'逻辑判断符号
