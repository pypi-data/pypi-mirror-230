# `pycw_fn` - efficient piecewise functions in Python

This package is a Python wrapper around the `pcw_fn` Rust crate built using maturin. It supports arbitrary piecewise functions on the real line.

# Example

This example constructs a few piecewise functions, does some basic arithmetic with them and finally plots them:

```python
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
from pycw_fn import PcwFn

g_0 = PcwFn.from_funcs_and_jumps(
    [
        Polynomial([1, 5, -10], window=np.array([-1., 1.]),
                   domain=np.array([-1., 1.])),
        Polynomial([0, 10, -20, 10], window=np.array([-1., 1.]),
                   domain=np.array([-1., 1.])),
    ],
    [
        0.5,
    ],
)


g_1 = PcwFn.from_funcs_and_jumps(
    [
        Polynomial([0.4*a**2, -4*a, 10], window=np.array([-1., 1.]),
                   domain=np.array([-1., 1.])) for a in range(6)
    ],
    [
        0.1,
        0.3,
        0.5,
        0.7,
        0.9,
    ],
)

b_2 = Polynomial([1/10, -4, 40])
g_2 = PcwFn.from_funcs_and_jumps(
    [b_2(Polynomial([-0.1*a, 1])) for a in range(10)],
    np.linspace(0.1, 1, num=9, endpoint=False),
)

g = g_0 + 5 * g_2

ts = np.linspace(0, 1, num=1000)
ys = g(ts)
plt.plot(ts, ys)
plt.show()

```
