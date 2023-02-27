import os
import sys
import numpy as np
import pandas as pd
from generator import generate_instance

from config import cfg

def read_data():
    p_file = cfg.get_file('p')
    q_file = cfg.get_file('q')
    if not os.path.exists(p_file) or not os.path.exists(q_file):
        #data_old = pd.read_excel('SheetDati.xlsx', sheet_name=1, header=None)
        #p = pandasToDict(data_old, n, m, o)
        p, q = generate_instance()
    else:
        p = pd.read_csv(p_file, header=None).to_numpy().reshape(cfg.n,cfg.m,cfg.o)
        #p = pandasToDict(p_df, cfg.n, cfg.m, cfg.o)
        q = pd.read_csv(q_file, header=None).to_numpy().reshape(cfg.n,cfg.m,cfg.c)
        #q = pandasToDict(q_df, cfg.n, cfg.m, cfg.c)
    """if seed != None:
        np.random.seed(seed)
        file = f'perturbation_{n_star}_{seed}.csv'
        if os.path.exists(file):
            data_old = pd.read_csv(file, header=None)
            n = int(len(data_old) / m)
            p = pandasToDict(data_old, n, m, o)
        else:
            if n_star < n:
                p, n, m, o = subsample_data(p, n, m, o, n_star)
            p, n, m, o = perturbate_data(p, n, m, o)
            save_data(p, n, m, o, file)"""

    return p, q


def pandasToDict(data, n, m, o):
    p = {}
    index = 0
    for i in range(n):
        for k in range(m):
            for l in range(o):
                p[i,k,l] = data.iloc[index][l]
            index += 1
    return p

