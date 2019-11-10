# AOP
无侵入的AOP实现，参考了aspectJ使用方式，实现了运行时代理function的功能。

作为FAss工具包功能上的补充


## Demo

```python

# app/server.py
class Service:
    def hello(self):
        print("HelloWord!")

# app/aspects/log.py
class Log(Aspect):
    def before(self):
        print("do before")

# main.py

from fass.aop import weaveAll
from app.server import Service 

cfg = [{
    "pointcut": "app.server.Service.hello",
    "aspect": "app.aspects.log.Log"
}]
weaveAll(cfg)

Service().hello()

```
控制台输出:
```
> do before
> HelloWord!
```





## WHY NOT

1. 为什么不是spring-python中的AOP?
    
    相对 spring-python 包，该实现属于monkey patch形式，对于项目结构、抽象、Wrapper无强制要求，随时集成入项目过程。

2. 为什么不是python-aspectlib?
    
    python-aspectlib包的设计理念与fass-aop极为接近，但考虑到该库活跃度较低且fass-aop后续需要对fass的进行定制化集成。所以不进行考虑。

## FAQ

1. 若同一pointcut的“代码配置”与“规则配置”同时对同一“切面”以不同参数进行了配置如何处理?
   
   “规则配置”与“代码配置”中对同一pointcut配置相同的apsect时，“规则配置”会覆盖“代码配置”中的参数设置。

## TODO

- [x] 基于装饰器的“代码设置”功能
- [ ] Aspect可配置after_exception指定拦截的异常类型
- [ ] AOP模块内部Aspect、ProceedingJoinPoint、PointCut等的依赖解耦
- [x] Aspect实例获取的方式，单例？或者交由Aspect自身决定？
    
    交由Aspect自身决定是否单例，并且在切面配置时，加入aspect_args传递给切面的实例化程序。

- [ ] `性能` PointcutParser对同一切点的多次获取应是唯一实例
- [ ] weave时可传递额外参数(cache等)给Aspect。 

#### 需要多次weave的情景，如Test

- [x] 取消所有AOP切面Proxy
    
    Pointcut.unset_proxy_all()
    
- [ ] 多次weave时，"装饰器设置"不重复加载