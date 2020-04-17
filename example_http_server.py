from flask import render_template_string

import example
import logging

logging.basicConfig(level=logging.DEBUG)
app = example.create_app()

print("http://localhost:5000/api/user/ben")
print("http://localhost:5000/api/config")

if __name__ == "__main__":
    import aop
    import yaml

    with open("example_aop.yml", "r", encoding="utf8") as fr:
        config = yaml.load(fr, yaml.BaseLoader)
        aop.from_config(config)


    @app.route('/tree_cost')
    def tree_cost():

        details_profiler = aop.aspect_store.get_aspect('details_profiler')
        html, rows = details_profiler.prepare_cost_view()
        return render_template_string(html, rows=rows)

    try:
        app.run()
    except KeyboardInterrupt:
        pass

    profiler = aop.aspect_store.get_aspect('profiler')
    profiler.console_report()

'''
flask_re


No Aspect
Fun                  |Count     |AveCost   
example.apis.user.get|      12.0|0.08841355641682943e-04



Profiler Aspect
Fun                          |Count     |AveCost(s)
example.apis.user.UserApi.get|      12.0|0.12636184692382812e-04



Profiler Aspect + Empty Aspect
Fun                          |Count     |AveCost   
example.apis.user.UserApi.get|      16.0|0.21502375602722168e-04


Profiler Aspect + Empty Aspect + Empty Aspect
Fun                          |Count     |AveCost   
example.apis.user.UserApi.get|      20.0|0.4494190216064453e-04



Profiler Aspect + Logger Aspect + StrPrefix Aspect 
Fun                          |Count     |AveCost   
example.apis.user.UserApi.get|      20.0|3.12042236328125e-04

'''
