"""
采用红黑树作为基础实现区间树
过于麻烦，暂时弃用
"""

from .itv import *

__all__ = [
    'ItvSet'
]



# 每个节点的区间保证不相交
# 按照node.a构建二叉搜索树
# 使用红黑树为基础
class ItvNode:
    def __init__(self, itv: Itv, red=True):
        self.itv = itv
        self.lch: 'ItvNode' = None  # 左子节点
        self.rch: 'ItvNode' = None  # 右子节点
        self.prnt: 'ItvNode' = None # 父节点
        self.red = red    # 是否为红色

    @property
    def a(self):
        return self.itv.a

    @a.setter
    def _(self, x):
        self.itv.a=x

    @property
    def b(self):
        return self.itv.b

    @b.setter
    def _(self, x):
        self.itv.b = x

    @property
    def left_open(self):
        return self.itv.left_open
    
    @left_open.setter
    def _(self, x):
        self.itv.left_open = x
    
    @property
    def right_open(self):
        return self.itv.right_open

    @right_open.setter
    def _(self, x):
        self.itv.right_open = x

    def rotate_l(self):
        x = self
        y = x.rch
        b = y.lch

        y.lch = x
        x.rch = b
        self._rotate_set_prnt(y)
        return y

    def rotate_r(self):
        y = self
        x = y.lch
        b = x.rch

        x.rch = y
        y.lch = b
        self._rotate_set_prnt(x)
        return x

    def min(self):
        lch = self.lch
        if lch is None:
            return self
        else:
            return lch.min()
        
    def max(self):
        rch =self.rch
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

    def find(self, x):
        """
        x是一个点，返回落入的区间的节点
        """
        if x in self.itv:
            return self
        if x <= self.a:
            ch = self.lch
        else:
            ch = self.rch
        if ch is not None:
            return ch.find(x)

    def find_neareast(self, x) -> 'ItvNode':
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

    def _rotate_set_prnt(self, n):
        prnt = self.prnt
        if prnt is None:
            return
        if self is prnt.lch:
            prnt.lch = n
        else:
            prnt.rch = n

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

    def is_root(self):
        return self.prnt is None

    @property
    def sibling(self):
        prnt = self.prnt
        if prnt is None:
            return
        
        lch = prnt.lch
        if self is lch:
            return prnt.rch
        else:
            return lch


def _abc_order_iter(n: ItvNode):
    if n is None:
        return
    yield from _abc_order_iter(n.lch)
    yield n
    yield from _abc_order_iter(n.rch)

def _cba_order_iter(n: ItvNode):
    if n is None:
        return
    yield from _cba_order_iter(n.rch)
    yield n
    yield from _cba_order_iter(n.lch)


def _iter_from_nearest(self: ItvNode, x, it_next=_abc_order_iter):
    if self is None:
        return

    if x in self.itv:
        yield self
    if x<=self.a:
        yield from _iter_from_nearest(self.lch, x)
        yield self
        yield from it_next(self.rch)
    else:
        yield from _iter_from_nearest(self.rch, x)
        yield self
        yield from it_next(self.lch)
    


def _find_nearest(self: ItvNode, x):
    if self is None:
        return

    if x in self.itv:
        return self
    if x<=self.a:
        n = _find_nearest(self.lch, x)
    else:
        n = _find_nearest(self.rch, x)
    if n is None:
        return self
    return n


def _find_by_lower(self: ItvNode, x):
    if self is None:
        return

    if x in self.itv:
        return self
    if x <= self.a:
        n = _find_by_lower(self.lch, x)
        if n is None:
            return self
        return n
    else:
        return _find_by_lower(self.rch, x)

def _find_by_upper(self: ItvNode, x):
    if self is None:
        return

    if x in self.itv:
        return self
    if x <= self.a:
        return _find_by_upper(self.lch, x)
    else:
        n = _find_by_upper(self.rch, x)
        if n is None:
            return self
        return n


def _find_max(n: ItvNode):
    for x in _cba_order_iter(n):
        return x

def _find_min(n: ItvNode):
    for x in _abc_order_iter(n):
        return x


def _resolve_insert(n: ItvNode):
    prnt = n.prnt
    if prnt is None or not prnt.red:
        return

    # pprnt 一定存在
    prnt_s = prnt.sibling
    if prnt_s is not None and prnt_s.red:
        prnt.red = False
        prnt_s.red = False
        pprnt = prnt.prnt
        pprnt.red = True
        n = pprnt

    if n is prnt.rch:
        prnt.rotate_l()
        n = prnt    # 使得n为lch
        prnt = n.prnt
    prnt.red = False
    pprnt = prnt.prnt
    pprnt.red = True
    pprnt.rotate_r()


def _resolve_remove(n: ItvNode):
    pass



class ItvSet:
    """
    interval set
    """

    def __init__(self, iterable=None):
        """
        iterable中的元素类型为Itv
        """
        raise NotImplementedError
        self._root:ItvNode = None
        for itv in iterable:
            self.add(ItvNode(itv))

    def add(self, itv: Itv):
        """
        插入区间，并且合并相交的区间
        """
        root = self._root
        if root is None:
            self._root=ItvNode(itv, False)
            return

        n1 = root.find_neareast(itv.a)
        if itv.a in n1.itv: # 相交，需要合并
            n1.itv=itv  
            # TODO: 删除右边相交的节点
            return

        #不相交
        n = ItvNode(itv)
        if itv.a <= n1.a:
            n1.lch = n
        else:
            n1.rch = n
        _resolve_insert(n)



    def remove(self, itv: Itv):
        """
        删除区间
        """
    
    def __iand__(self, s: ItvSet):
        """
        相交集合
        """

    def __ior__(self, s:ItvSet):
        """
        合并集合
        """

    def __isub__(self, s:ItvSet):
        """
        减去集合
        """

    def __in__(self, x):
        """
        判定一个点是否在集合内
        """

    def min(self):
        pass

    def max(self):
        pass

    def iter_from_lower(self, x):
        pass

    def inter_from_upper(self, x):
        pass

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __eq__(self, other):
        pass

    def __str__(self):
        return super().__str__()

    def __iter__(self):  # 从小到大返回
        yield

