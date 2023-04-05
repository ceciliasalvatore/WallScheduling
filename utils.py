import numpy as np
from config import cfg

def generate_warmstart_p(p):
    np.random.seed(100)
    jobs_order = np.argsort(p[:,0,0])
    cuts_order = np.random.choice(np.arange(cfg.o),cfg.n) # cuts_order[l,i]:= 1 if job in position  i follows cut l
    return jobs_order, cuts_order

def generate_warmstart_q(q):
    np.random.seed(100)
    jobs_order = np.argsort(q[:,0,0])
    operations_order = np.zeros((cfg.n, cfg.c))
    for i in range(cfg.n):
        for j in range(cfg.c):
            operations_order[i,j] = np.random.choice(cfg.Machine[j],1) # operation_order[i,j]:=k if operation j of job in position i is assigned to machine k
    return jobs_order, operations_order