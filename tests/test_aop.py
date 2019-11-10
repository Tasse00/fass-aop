import unittest

from fass_aop import weaveAll, Pointcut
from tests.something.aspects.log import get_run_log, reset_run_log


class TestAop(unittest.TestCase):

    def tearDown(self) -> None:
        Pointcut.unset_proxy_all()
        reset_run_log()

    def test_config_result_logic(self):
        """Aspect中各增强的执行顺序及Aspect的优先级"""
        cfg = [{
            "pointcut": "tests.something.service.svc01.Service01.get_name",
            "aspect": "tests.something.aspects.log.Log01",
            "order": 2,
        }, {
            "pointcut": "tests.something.service.svc01.Service01.get_name",
            "aspect": "tests.something.aspects.log.Log02",
            "order": 1,
        }]

        weaveAll(cfg)

        from tests.something.service.svc01 import Service01

        name = Service01(name="S1").get_name()
        self.assertEqual(get_run_log(), [
            "@Log02 around start",
            "@Log02 before",
            "@Log01 around start",
            "@Log01 before",
            "@Log01 after",
            "@Log01 after_result",
            "@Log01 around end",
            "@Log02 after",
            "@Log02 after_result",
            "@Log02 around end",
        ])
        self.assertEqual(name, "S1")

    def test_config_exception_logic(self):
        cfg = [{
            "pointcut": "tests.something.service.svc01.Service01.raise_exception",
            "aspect": "tests.something.aspects.log.Log01",
            "order": 16,
        }, {
            "pointcut": "tests.something.service.svc01.Service01.raise_exception",
            "aspect": "tests.something.aspects.log.Log02",
            "order": 17,
        }]
        weaveAll(cfg)

        from tests.something.service.svc01 import Service01
        self.assertRaises(RuntimeError, lambda: Service01(name="T2").raise_exception(RuntimeError()))
        self.assertEqual(get_run_log(), [
            "@Log01 around start",
            "@Log01 before",
            "@Log02 around start",
            "@Log02 before",
            "@Log02 after",
            "@Log02 after_exception",
            # "@Log02 around end",
            "@Log01 after",
            "@Log01 after_exception",
            # "@Log01 around end",
        ])

    def test_decorated_result_logic(self):
        from tests.something.service.svc02 import ServiceDecorated
        weaveAll([])

        name = ServiceDecorated(name="S1").get_name()
        self.assertEqual(get_run_log(), [
            "@Log02 around start",
            "@Log02 before",
            "@Log01 around start",
            "@Log01 before",
            "@Log01 after",
            "@Log01 after_result",
            "@Log01 around end",
            "@Log02 after",
            "@Log02 after_result",
            "@Log02 around end",
        ])
        self.assertEqual(name, "S1")

    def test_decorated_exception_logic(self):
        from tests.something.service.svc02 import ServiceDecorated
        weaveAll([])

        self.assertRaises(RuntimeError, lambda: ServiceDecorated(name="T2").raise_exception(RuntimeError()))
        self.assertEqual(get_run_log(), [
            "@Log01 around start",
            "@Log01 before",
            "@Log02 around start",
            "@Log02 before",
            "@Log02 after",
            "@Log02 after_exception",
            # "@Log02 around end",
            "@Log01 after",
            "@Log01 after_exception",
            # "@Log01 around end",
        ])

    def test_union_config_and_decorated_config_low_priority(self):
        from tests.something.service.svc02 import ServiceDecorated

        weaveAll([{
            "pointcut": "tests.something.service.svc02.ServiceDecorated.get_name_decorated_log1",
            "aspect": "tests.something.aspects.log.Log02",
            "order": 17,  # 高于Log1默认
        }])

        name = ServiceDecorated(name="S1").get_name_decorated_log1()

        self.assertEqual(get_run_log(), [
            "@Log01 around start",
            "@Log01 before",
            "@Log02 around start",
            "@Log02 before",
            "@Log02 after",
            "@Log02 after_result",
            "@Log02 around end",
            "@Log01 after",
            "@Log01 after_result",
            "@Log01 around end",
        ])
        self.assertEqual(name, "S1")

    def test_union_config_and_decorated_config_high_priority(self):
        from tests.something.service.svc02 import ServiceDecorated

        weaveAll([{
            "pointcut": "tests.something.service.svc02.ServiceDecorated.get_name_decorated_log1",
            "aspect": "tests.something.aspects.log.Log02",
            "order": 15,  # 高于Log1默认
        }])

        name = ServiceDecorated(name="S1").get_name_decorated_log1()

        self.assertEqual(get_run_log(), [
            "@Log02 around start",
            "@Log02 before",
            "@Log01 around start",
            "@Log01 before",
            "@Log01 after",
            "@Log01 after_result",
            "@Log01 around end",
            "@Log02 after",
            "@Log02 after_result",
            "@Log02 around end",
        ])
        self.assertEqual(name, "S1")


class TestPointcutParser(unittest.TestCase):

    def tearDown(self) -> None:
        Pointcut.unset_proxy_all()
        reset_run_log()

    def test_regexp_parser(self):
        from fass_aop.pointcut import PointcutParser
        pp = PointcutParser()
        reg = "tests.something.service.multi_level_svcs.level0[1|2].level0[1|2]svc.[0-9a-zA-Z]+.[get|post]"
        pointcuts = pp.parse(reg)
        self.assertEqual(len(pointcuts), 4)

        self.assertListEqual([
            "Level01Svc.get",
            "Level01Svc.post",
            "Level02Svc.get",
            "Level02Svc.post",
        ], [pt.identifier for pt in pointcuts], "PointcutParser regexp failed.")

        reg = "tests.something.service.multi_level_svcs.level0[1|2].level0[1|2]svc.[0-9a-zA-Z]+.[get]"
        pointcuts = pp.parse(reg)
        self.assertEqual(len(pointcuts), 2)

        self.assertListEqual([
            "Level01Svc.get",
            "Level02Svc.get",
        ], [pt.identifier for pt in pointcuts], "PointcutParser regexp failed.")
