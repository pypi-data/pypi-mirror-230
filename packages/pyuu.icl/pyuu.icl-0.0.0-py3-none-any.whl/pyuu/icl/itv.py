
from __future__ import annotations
from .inf import *

__all__ = [
    'Itv'
]


def _left_or_eq_to(a, b, open_a, open_b):
    """
    a <= b 当两个全是close
    a < b 其他情况
    """
    if open_a or open_b:
        return a < b
    else:
        return a <= b


def _left_or_near_to(a, b, open_a, open_b):
    """
    a <= b 一个是close
    a < b 其他情况
    """
    if open_a and open_b:
        return a < b
    else:
        return a <= b


def _create_itv(a, b, left_open, right_open):
    itv = Itv.__new__(Itv)
    itv.a = a
    itv.b = b
    itv.left_open = left_open
    itv.right_open = right_open
    itv._normalize()
    return itv


class Itv:
    """
    Interval
    应当视为不可变对象，任何属性创建后不应当更改
    """

    def __init__(self, a, b, kind='[]'):
        """
        kind表示区间类型, 根据数学上的表示，[]表示闭区间， ()表示开区间
        a,b分别表示左断点和右端点
        """
        self.a = a
        self.b = b
        self.left_open = kind[0] == '('
        self.right_open = kind[1] == ')'
        self._normalize()

    @staticmethod
    def empty_set():
        return Itv(inf, -inf)

    @property
    def kind(self):
        """
        此属性应当只被用作比较，而不应当有其他用途
        """
        return (self.left_open << 1) + self.right_open

    def create_like(self, a = None, b = None, left_open = None, right_open = None):
        a = a if a is not None else self.a
        b = b if b is not None else self.b
        left_open = left_open if left_open is not None else self.left_open
        right_open = right_open if right_open is not None else self.right_open
        return _create_itv(a, b, left_open, right_open)

    def _normalize(self):
        """
        保证空集表示一致
        """
        if self.a > self.b or \
                (self.a == self.b and (self.left_open or self.right_open)):
            # 方便比较
            self.a = inf
            self.b = -inf
            self.left_open = True
            self.right_open = True

    def empty(self):
        return self.a > self.b

    def __contains__(self, x):
        """
        判定某个点是否在区间内
        """
        return self.right_to_a(x) and self.left_to_b(x)

    def right_to_a(self, x):
        """
        x在a端点的右边
        """
        if self.left_open:
            return self.a < x
        else:
            return self.a <= x

    def left_to_b(self, x):
        """
        x在b断点的左边
        """
        if self.right_open:
            return self.b > x
        else:
            return self.b >= x

    def intersect(self, other: 'Itv') -> bool:
        """
        是否相交
        """
        return _left_or_eq_to(self.a, other.b, self.left_open, other.right_open) \
            and _left_or_eq_to(other.a, self.b, other.left_open, self.right_open)

    def intersect_or_near(self, other: 'Itv') -> bool:
        """
        是否相交或紧挨着
        """
        return _left_or_near_to(self.a, other.b, self.left_open, other.right_open) \
               and _left_or_near_to(other.a, self.b, other.left_open, self.right_open)

    def split(self, x, is_open=False):
        left = _create_itv(self.a, x, self.left_open, is_open)
        right = _create_itv(x, self.b, is_open, self.right_open)
        return left, right

    def splits(self, xs, is_open=False):
        res = []
        v2 = self
        for i in xs:
            v1, v2 = v2.split(i, is_open)
            res.append(v1)
        res.append(v2)
        return res

    def __and__(self, other: 'Itv') -> 'Itv':
        a = max(self.a, other.a)
        b = min(self.b, other.b)

        if a == self.a == other.a:
            left_open = self.left_open or other.left_open
        elif a == self.a:
            left_open = self.left_open
        else:  # a == x.a:
            left_open = other.left_open

        if b == self.b == other.b:
            right_open = self.right_open or other.right_open
        elif b == self.b:
            right_open = self.right_open
        else:  # b == x.b:
            right_open = other.right_open

        res = _create_itv(a, b, left_open, right_open)
        return res

    def __or__(self, other: 'Itv'):
        assert self.intersect_or_near(other)

        a = min(self.a, other.a)
        b = max(self.b, other.b)

        if a == self.a == other.a:
            left_open = self.left_open and other.left_open
        elif a == self.a:
            left_open = self.left_open
        else:  # a == itv.a:
            left_open = other.left_open

        if b == self.b == other.b:
            right_open = self.right_open and other.right_open
        elif b == self.b:
            right_open = self.right_open
        else:  # b == itv.b:
            right_open = other.right_open

        res = _create_itv(a, b, left_open, right_open)
        return res

    __iand__ = __and__
    __ior__ = __or__

    def __sub__(self, other: 'Itv'):
        if self.intersect(other):
            tmp = self.split(other.a, not other.left_open)
            v1 = tmp[0]
            tmp = self.split(other.b, not other.right_open)
            v2 = tmp[1]
            return v1, v2
        else:
            return self

    def __gt__(self, x):
        if self.left_open:
            return x <= self.a
        else:
            return x < self.a

    def __ge__(self, x):
        if self.right_open:
            return x < self.b
        else:
            return x <= self.b

    def __lt__(self, x):
        if self.right_open:
            return x >= self.b
        else:
            return x > self.b

    def __le__(self, x):
        if self.left_open:
            return x >= self.a
        else:
            return x > self.a

    def __eq__(self, other: 'Itv'):
        return self.kind == other.kind and self.a == other.a and self.b == other.b

    def __hash__(self):
        return hash((self.a, self.b, self.kind))

    def __str__(self):
        a, b = self.a, self.b
        l = '[('[self.left_open]
        r = '])'[self.right_open]
        return f'{l}{a}, {b}{r}'

    __repr__ = __str__
