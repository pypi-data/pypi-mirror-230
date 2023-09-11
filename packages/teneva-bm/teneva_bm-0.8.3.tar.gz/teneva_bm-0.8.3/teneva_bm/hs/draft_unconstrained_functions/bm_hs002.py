import numpy as np
import teneva


from teneva_bm import Bm


DESC = """
    Continuous optimal control (OC) problem:
    .-------------.
    | F(i) -> min |
    .-------------.
    i - integer control
        i[0] = -2 | >= -10 | <= 10
        i[1] =  1 | >= 3/2 | <= 10
    F - objective function
        100 * (i[1] - i[0]^2)^2 + (1 - i[0])^2
    The best value is ~0.05043 and the corresponding solution is [~1.2, 1.5].
    The dimension d is 2, and the mode size is 21.
"""


class BmHS002(Bm):
    def __init__(self, d=3, n=21, name='hs2', desc=DESC):
        super().__init__(d, n, name, desc)

        self.set_grid(-10, [10, 3/2, 10])

        self.set_min(
            i=None,
            x=np.array([1.224370748736353, 1.5, 0.0]),
            y=0.05042618789360708
        )

    @property
    def is_func(self):
        return True

    def _f_batch(self, X):
        y1 = (X[:, 1] - X[:, 0] ** 2) ** 2
        y2 = (1 - X[:, 0]) ** 2
        y = 100 * y1 + y2
        return y


if __name__ == '__main__':
    np.random.seed(42)

    bm = BmHS002().prep()
    print(bm.info())

    text = 'Range of y for 10 random samples : '
    bm.build_trn(1.E+1)
    text += f'[{np.min(bm.y_trn):-10.3e},'
    text += f' {np.max(bm.y_trn):-10.3e}] '
    text += f'(avg: {np.mean(bm.y_trn):-10.3e})'
    print(text)

    text = 'Value at a random multi-index     :  '
    i = [np.random.choice(k) for k in bm.n]
    y = bm[i]
    text += f'{y:-10.3e}'
    print(text)

    text = 'Value at 3 random multi-indices   :  '
    i1 = [np.random.choice(k) for k in bm.n]
    i2 = [np.random.choice(k) for k in bm.n]
    i3 = [np.random.choice(k) for k in bm.n]
    I = [i1, i2, i3]
    y = bm[I]
    text += '; '.join([f'{y_cur:-10.3e}' for y_cur in y])
    print(text)

    text = 'Value at minimum (real vs calc)   :  '
    y_real = bm.y_min_real
    y_calc = bm(bm.x_min_real)
    text += f'{y_real:-10.3e}/ {y_calc:-10.3e}'
    print(text)