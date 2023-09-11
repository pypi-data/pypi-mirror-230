import numpy as np
from teneva_bm import Bm


class BmFunc(Bm):
    def __init__(self, d=7, n=16, seed=42):
        super().__init__(d, n, seed)

        self.set_desc("""Function""")

        self.set_grid(-1., +1., sh=True)

        self.set_min(x=[0.]*self.d, y=0.)

    @property
    def is_func(self):
        return True
