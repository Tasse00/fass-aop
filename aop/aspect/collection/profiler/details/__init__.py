import collections
import os
import threading
import time
import uuid
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from aop import Aspect
from aop.joinpoint.proceeding import ProceedingJoinPoint


@dataclass
class CostTree:
    identity: str
    children: Dict[str, 'CostTree']
    count: int
    average: float


@dataclass
class RenderRow:
    id: str
    count: int
    average: float
    parent: str


def parse(parent: str, node: CostTree) -> List[RenderRow]:
    return [RenderRow(id=node.identity, parent=parent, count=node.count, average=node.average)] + sum(
        [parse(node.identity, cnode) for cnode in node.children.values()], []
    )


class DetailsProfiler(Aspect):
    """
    限制：计算当前线程内的调用堆栈

    若目标抛出异常则不计入统计范围内
    """

    def __init__(self):
        """
        统计各个路径的时间开销
        part1.part2

        """
        self.local = threading.local()
        # 存储当前线程内的调用堆栈
        # self.local.stack = []
        # print(self.local)
        # local.stack = []
        self.counter = collections.OrderedDict()  # {joinpoint: [count, average_cost]}

        self.name = str(uuid.uuid4())[-6:]

    def around(self, pjp: ProceedingJoinPoint):
        """"""
        if not hasattr(self.local, "stack"):
            self.local.stack = []

        self.local.stack.append(pjp.join_point.get_name())

        stack_id = "->".join(self.local.stack)

        item = self.counter.setdefault(stack_id, [0.0, 0.0])  # [count, cost]

        start_at = time.time()

        try:
            ret = pjp.proceed()
        except Exception as e:
            # 不记录时间
            self.local.stack.pop()
            raise e

        cost = time.time() - start_at
        item[1] = (item[0] * item[1] + cost) / (item[0] + 1)
        item[0] += 1

        self.local.stack.pop()
        return ret

    def console_report(self):
        """控制台打印执行次数、耗时统计"""
        print(self.format_console_report())

    def format_console_report(self) -> str:
        name_len = max(len(k) for k in self.counter.keys())
        total = ""
        fmt = '{k:%d}|{c:10}|{v:10}\n' % name_len
        total += '\n' + fmt.format(k="Fun", c="Count", v="AveCost")
        for k, v in self.counter.items():
            total += fmt.format(k=k, c=v[0], v=v[1])
        return total

    def get_cost_trees(self) -> CostTree:

        # {
        #   identity:
        # }

        stacks_count_average = []

        for stack_name, prof in self.counter.items():
            count, average = prof
            stacks = stack_name.split('->')
            stacks_count_average.append((stacks, count, average))

        root = CostTree(identity='', children={}, count=0, average=0)

        def find_parent_node(tree: CostTree, stacks: List[str]) -> Optional[CostTree]:
            if len(stacks) == 0:
                return tree
            target_next = stacks[0]
            rest_stacks = stacks[1:]
            if target_next in tree.children:
                return find_parent_node(tree.children[target_next], rest_stacks)
            else:
                return None

        while stacks_count_average:
            rest = []
            for stacks, count, average in stacks_count_average:
                self_identity = stacks[-1]
                path_identity = stacks[:-1]
                leaf = find_parent_node(root, path_identity)

                if leaf is None:
                    rest.append((stacks, count, average))
                else:
                    leaf.children[self_identity] = CostTree(identity=self_identity,
                                                            children={},
                                                            count=count,
                                                            average=average)
            stacks_count_average = rest

        return root

    def parse_render_rows(self, root: CostTree) -> List[RenderRow]:
        def parse(parent: str, node: CostTree) -> List[RenderRow]:
            return [RenderRow(id=node.identity, parent=parent, count=node.count, average=node.average)] + sum(
                [parse(node.identity, cnode) for cnode in node.children.values()], []
            )

        return parse('', root)

    def prepare_cost_view(self, render_template: Optional[str] = None, root_name: str='root') -> Tuple[str, List[RenderRow]]:
        render_template = render_template or os.path.join(os.path.dirname(__file__), "cost_tree.html")
        with open(render_template, 'r', encoding='utf-8') as fr:
            html = fr.read()
        root = self.get_cost_trees()
        root.identity = root_name
        rows = self.parse_render_rows(root)
        return html, rows
