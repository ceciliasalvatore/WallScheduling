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
        p, q = generate_instance()
    else:
        p = pd.read_csv(p_file, header=None).to_numpy().reshape(cfg.n,cfg.m,cfg.o)
        q = pd.read_csv(q_file, header=None).to_numpy().reshape(cfg.n,cfg.m,cfg.c)

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

