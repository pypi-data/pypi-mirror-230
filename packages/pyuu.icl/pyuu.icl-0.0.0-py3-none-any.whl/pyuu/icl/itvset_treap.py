"""
使用treap实现itvset
"""

from __future__ import annotations
import random
from itertools import zip_longest
from typing import Tuple, Union

from . import inf
from .itv import *

__all__ = [
    'ItvSet'
]


class Node:
    def __init__(self, itv: Itv):
        self.itv = itv
        self.priority = random.random()
        self.lch: 'Node' = None
        self.rch: 'Node' = None
        self.prnt: 'Node' = None

    @staticmethod
    def _create(itv, priority, lch=None, rch=None, prnt=None):
        n = Node.__new__(Node)
        n.itv = itv
        n.priority = priority
        n.lch = lch
        n.rch = rch
        n.prnt = prnt
        return n

    @property
    def k(self):
        return self.itv.a

    @property
    def a(self):
        return self.itv.a

    @property
    def b(self):
        return self.itv.b

    def is_root(self):
        return self.prnt is None

    def set_rch(self, rch: 'Node'):
        self.rch = rch
        if rch is not None:
            rch.prnt = self

    def set_lch(self, lch: 'Node'):
        self.lch = lch
        if lch is not None:
            lch.prnt = self

    def find(self, x):
        """
        x是一个点，返回落入的区间的节点
        """
        if x in self.itv:
            return self
        if x <= self.k:
            ch = self.lch
        else:
            ch = self.rch
        if ch is not None:
            return ch.find(x)

    def find_neareast(self, x):
        return _find_nearest(self, x)

    def find_by_lower(self, x):
        """
        x表示下界，是一个点
        如果落入了某个区间，则返回这个区间
        否则返回以x为下界的最接近x的区间
        """
        return _find_by_lower(self, x)

    def find_by_upper(self, x):
        return _find_by_upper(self, x)

    def abc_order_iter(self):
        """
        左中右DFS
        """
        yield from _abc_order_iter(self)

    def cba_order_iter(self):
        """
        右中左DFS
        """
        yield from _cba_order_iter(self)

    __iter__ = abc_order_iter

    def min(self) -> 'Node':
        lch = self.lch
        if lch is None:
            return self
        else:
            return lch.min()

    def max(self) -> 'Node':
        rch = self.rch
        if rch is None:
            return self
        else:
            return rch.max()

    def next_low(self):
        lch = self.lch
        if lch is not None:
            return lch.max()

        prnt = self.prnt
        n = self
        while prnt is not None:
            if prnt.rch is n:
                return prnt
            else:
                n = prnt
                prnt = n.prnt

    def next_high(self):
        rch = self.rch
        if rch is not None:
            return rch.min()

        prnt = self.prnt
        n = self
        while prnt is not None:
            if prnt.lch is n:
                return prnt
            else:
                n = prnt
                prnt = n.prnt

    def copy(self):
        return self._copy(None)

    def _copy(self, prnt):
        n = self._create(self.itv, self.priority, None, None, prnt)
        if self.lch is not None:
            n.lch = self.lch._copy(n)
        if self.rch is not None:
            n.rch = self.rch._copy(n)
        return n

    def height(self):
        lch,rch = self.lch, self.rch
        l = 0 if lch is None else lch.height()
        r = 0 if rch is None else rch.height()
        return max(l,r)+1

    def __len__(self):
        lch,rch = self.lch, self.rch
        l = 0 if lch is None else len(lch)
        r = 0 if rch is None else len(rch)
        return l+r+1



def _remove_node(root: Node, n: Node):
    assert n.lch is None or n.rch is None
    prnt = n.prnt

    def _set_ch(x):
        if n is prnt.lch:
            prnt.set_rch(x)
        else:
            prnt.set_rch(x)

    if prnt is None:
        if n.lch is None:
            return n.rch
        else:
            return n.lch
    else:
        if n.lch is None:
            _set_ch(n.rch)
        else:
            _set_ch(n.lch)
        return root


def _abc_order_iter(n):
    if n is None:
        return
    yield from _abc_order_iter(n.lch)
    yield n
    yield from _abc_order_iter(n.rch)


def _cba_order_iter(n):
    if n is None:
        return
    yield from _cba_order_iter(n.rch)
    yield n
    yield from _cba_order_iter(n.lch)


def _iter_from_nearest(self, x, it_next=_abc_order_iter):
    if self is None:
        return

    if x in self.itv:
        yield self
    if x <= self.k:
        yield from _iter_from_nearest(self.lch, x)
        yield self
        yield from it_next(self.rch)
    else:
        yield from _iter_from_nearest(self.rch, x)
        yield self
        yield from it_next(self.lch)


def _find_nearest(self, x):
    if self is None:
        return

    if x in self.itv:
        return self
    if x <= self.k:
        n = _find_nearest(self.lch, x)
    else:
        n = _find_nearest(self.rch, x)
    if n is None:
        return self
    return n


def _find_by_lower(self, x):
    if self is None:
        return

    if x in self.itv:
        return self
    if x <= self.k:
        n = _find_by_lower(self.lch, x)
        if n is None:
            return self
        return n
    else:
        return _find_by_lower(self.rch, x)


def _find_by_upper(self, x):
    if self is None:
        return

    if x in self.itv:
        return self
    if x <= self.k:
        return _find_by_upper(self.lch, x)
    else:
        n = _find_by_upper(self.rch, x)
        if n is None:
            return self
        return n


def _split(n: Node, x, is_open=False, t1=None, t2=None) -> Union[Tuple[None, None], Tuple[Node, Node]]:
    if n is None:
        return None, None

    def to_t1():
        nonlocal t1, t2
        t1 = n
        rch, t2 = _split(n.rch, x, is_open, n.rch, t2)
        n.set_rch(rch)

    def to_t2():
        nonlocal t1, t2
        t2 = n
        t1, lch = _split(n.lch, x, is_open, n.lch, t1)
        n.set_lch(lch)

    if n.itv.a <= x:
        if is_open and n.itv.left_open and n.itv.a == x:
            to_t2()
        else:
            to_t1()
    else:
        to_t2()
    return t1, t2


def _merge(t1: Node, t2: Node) -> Node:
    if t1 is None:
        return t2
    if t2 is None:
        return t1

    if t1.priority > t2.priority:
        t1.set_rch(_merge(t1.rch, t2))
        return t1
    else:
        t2.set_lch(_merge(t1, t2.lch))
        return t2


class ItvSet:
    """
    interval set
    """

    def __init__(self, iterable=None):
        """
        iterable中的元素类型为Itv
        """
        self._root: Node = None
        if iterable is None:
            return
        for itv in iterable:
            self.add(itv)

    @staticmethod
    def _create(root):
        new_ = ItvSet.__new__(ItvSet)
        new_._root = root
        return new_

    def add(self, itv: Itv):
        """
        插入区间，并且合并相交的区间
        """
        if itv.empty():
            return

        if self._root is None:
            self._root = Node(itv)
            return

        root = self._root


        t1, t2, t3 = None, None, None
        t1, t2 = _split(root, itv.a)
        if t2 is not None:
            t2, t3 = _split(t2, itv.b, itv.right_open)

        create_flag = True
        if t1 is not None:
            t1_max = t1.max()
            if itv.intersect_or_near(t1_max.itv):
                itv |= t1_max.itv
                t1_max.itv = itv
                create_flag = False

        if t2 is not None:
            t2_max = t2.max()
            if itv.intersect_or_near(t2_max.itv):
                itv |= t2_max.itv
                if not create_flag:
                    t1_max.itv = itv

        n = None
        if create_flag:
            n = Node(itv)

        self._root = _merge(_merge(t1, n), t3)

        return

    def remove(self, itv: Itv):
        """
        移除区间
        """
        if itv.empty() or self.empty():
            return

        root = self._root

        t1, t2, t3 = None, None, None
        t1, t2 = _split(root, itv.a)
        if t2 is not None:
            t2, t3 = _split(t2, itv.b, itv.right_open)

        n = None
        if t1 is not None:
            t1_max = t1.max()
            tmp = t1_max.itv - itv
            if tmp is not t1_max.itv:
                v1, v2 = tmp
                if not v1.empty():  # v1不空
                    t1_max.itv = v1
                    if not v2.empty():
                        n = Node(v2)
                elif v2.empty():  # v1和v2都空
                    t1 = _remove_node(t1, t1_max)
                else:  # v1空，v2不空
                    t1_max.itv = v2

        if t2 is not None:
            t2_max = t2.max()
            tmp = t2_max.itv - itv
            if tmp is not t2_max.itv:
                v1, v2 = tmp
                assert v1.empty()
                if not v2.empty():
                    assert n is None
                    n = Node(v2)
        self._root = _merge(_merge(t1, n), t3)

    def intersection(self, itv: 'Itv'):
        """
        和区间取交集
        """
        root = self._root
        if root is None:
            return

        if itv.empty():
            self._root = None

        t1, t2, t3 = None, None, None
        t1, t2 = _split(root, itv.a)
        if t2 is not None:
            t2, t3 = _split(t2, itv.b, itv.right_open)

        n = None
        if t1 is not None:
            t1_max = t1.max()
            tmp = t1_max.itv & itv
            if not tmp.empty():
                n = Node(tmp)

        if t2 is not None:
            t2_max = t2.max()
            t2_max.itv &= itv
            if t2_max.itv.empty():
                t2 = _remove_node(t2, t2_max)

        self._root = _merge(n, t2)

    def empty(self):
        return self._root is None

    def __neg__(self):
        return ItvSet([Itv(-inf, inf)]) - self

    def __contains__(self, x):
        """
        判定一个点是否在集合内
        """
        root = self._root
        if root is not None:
            return root.find(x) is not None
        return False

    def __iand__(self, other: 'ItvSet'):
        """
        相交集合
        """
        res = self & other
        self._root = res._root
        return self

    def __ior__(self, s: 'ItvSet'):
        """
        合并集合
        """
        for v in s:
            self.add(v)
        return self

    def __isub__(self, s: 'ItvSet'):
        """
        减去集合
        """
        for v in s:
            self.remove(v)
        return self

    def __and__(self, other):
        tmp = []
        for v in other:
            x = self.copy()
            x.intersection(v)
            tmp.append(x)
        res = ItvSet.union(*tmp)
        return res

    def __or__(self, other):
        res = self.copy()
        res |= other
        return res

    def __sub__(self, other):
        res = self.copy()
        res -= other
        return res

    def __eq__(self, other):
        for a, b in zip_longest(self, other):
            if a is None or b is None or a != b:
                return False
        return True

    def __str__(self):
        tmp = ', '.join(map(str, self))
        return 'ItvSet{' + tmp + '}'

    __repr__ = __str__

    def __iter__(self):  # 从小到大返回
        for n in _abc_order_iter(self._root):
            yield n.itv

    def __len__(self):
        return len(self._root)

    def union(self, *args):
        """
        取多个集合的并集
        """
        for arg in args:
            self|=arg
        return self

    or_ = union

    def copy(self):
        if self._root is None:
            root = None
        else:
            root = self._root.copy()

        return self._create(root)
