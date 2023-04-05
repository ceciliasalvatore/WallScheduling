import pandas as pd

from parser import read_data
from WallScheduling import WS

from config import cfg

if __name__ == "__main__":
    cfg.set_seed(-1)
    p, q = read_data()
    #WS(p, q, 'pos_exp')
    #WS(p, q, 'pos_poly')
    #WS(p, q, 'disj_exp')

    n_list = [10]

    for n in n_list:
        cfg.n = n
        if cfg.processing_times == 'integer':
            initial_seed = n * 10
        else:
            initial_seed = n * 100
        for seed in range(10):
            cfg.set_seed(initial_seed+seed)
            p, q = read_data()
            #WS(p, q, 'pos_exp')
            WS(p, q, 'pos_poly')
            #WS(p, q, 'disj_exp')


