import pandas as pd

from parser import read_data
from WallScheduling import WS

from config import cfg

if __name__ == "__main__":
    cfg.set_seed(-1)
    p, q = read_data()
    WS(p, q, 'pos_expl')
    WS(p, q, 'pos_impl')
    WS(p, q, 'prec_expl')
    WS(p, q, 'prec_impl')

    n_list = [5]

    for n in n_list:
        cfg.n = n
        initial_seed = n * 10
        for seed in range(5):
            cfg.set_seed(initial_seed+seed)
            p, q = read_data()
            WS(p, q, 'pos_expl')
            WS(p, q, 'pos_impl')
            WS(p, q, 'prec_expl')
            WS(p, q, 'prec_impl')