import pandas as pd

from parser import read_data
from WallScheduling import WS

from config import cfg

if __name__ == "__main__":
    cfg.set_seed(-1)
    p, q = read_data()
    WS(p, q, 'pos_exp')
    WS(p, q, 'pos_poly')
    WS(p, q, 'disj_exp')

    n_list = [10, 15, 20, 25]

    for n in n_list:
        cfg.n = n
        for seed in range(20):
            cfg.set_seed(n*10+seed)
            p, q = read_data()
            WS(p, q, 'pos_exp')
            WS(p, q, 'pos_poly')
            WS(p, q, 'disj_exp')


