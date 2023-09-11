from . import pcw_fn_py as _rs

from dataclasses import dataclass
import numpy as np

from delegateto import DelegateTo
from functools import wraps


class PcwFn():
    """A piecewise function"""
    _native: _rs.PcwFn

    def __init__(self, native):
        self._native = native

    @classmethod
    def from_funcs_and_jumps(Self, funcs, jumps):
        return Self(_rs.PcwFn(jumps, funcs))

    @classmethod
    def const(Self, func):
        return Self(_rs.PcwFn((), (func, )))

    def __call__(self, arg):
        if isinstance(arg, np.ndarray):
            return np.array([self._native(x) for x in arg])
        else:
            return self._native(arg)

    @staticmethod
    def combine_with_action(action):
        @wraps(action)
        def combine(self, other):
            return PcwFn(action(self._native, other._native))
        return combine

    @staticmethod
    def combine_with_const_lifted_action(action):
        @wraps(action)
        def combine(self, other):
            return action(self, PcwFn.const(other))
        return combine

    def __rmul__(self, other):
        return self * PcwFn.from_funcs_and_jumps([other], [])

    def __neg__(self):
        return PcwFn(-self._native)

    def __not__(self):
        return PcwFn(~self._native)

    __str__ = DelegateTo("_native")
    __repr__ = DelegateTo("_native")


for base_action in ("add", "sub", "mul", "div", "pow", "lshift", "rshift", "and", "xor", "or"):
    action = f"__{base_action}__"
    setattr(PcwFn, action, PcwFn.combine_with_action(
        getattr(_rs.PcwFn, action)))

    right_action = f"__r{base_action}__"
    setattr(PcwFn, right_action, PcwFn.combine_with_const_lifted_action(
        getattr(PcwFn, action)))
