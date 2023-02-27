import numpy as np
import pandas as pd
import itertools as it

from config import cfg

def generate_instance():
    q = np.zeros((cfg.n, cfg.m, cfg.c))

    if cfg.seed == -1:
        operations = pd.read_csv('WS_original_operations.CSV', header=None, sep='\t').to_numpy()
        row = 0
        for t in range(int(cfg.v_k[-1,-1])):
            for k in range(cfg.m):
                if t >= cfg.v_k[k, 0] and t < cfg.v_k[k, 1]:
                    for i in range(cfg.n):
                        q[i, k, t] = operations[row, i]
                    row += 1
    else:
        row = 0
        for t in range(cfg.c):
            for k in range(cfg.m):
                if len(np.where((t>=cfg.v_k[:,0])&(t<cfg.v_k[:,1]))[0])==1:
                    m1 = np.random.randint(10, 26)
                    m2 = np.random.randint(m1+1, 30)
                else:
                    m1 = np.random.randint(2, 13)
                    m2 = np.random.randint(m1+1, 16)
                if t >= cfg.v_k[k, 0] and t < cfg.v_k[k, 1]:
                    for i in range(cfg.n):
                        q[i,k,t] = np.random.randint(m1,m2)
                    row += 1

    #cuts = np.array(np.meshgrid(*(np.arange((v)[k]) for k in range(m)))).T.reshape(-1,m)+1
    cuts_1 = np.array(list(it.product(*(np.arange((cfg.v1+1)[k]) for k in range(cfg.m)))))
    cuts_2 = np.array(list(it.product(*(np.arange((cfg.v2+1)[k]) for k in range(cfg.m)))))

    p = np.zeros((cfg.n, cfg.m, cfg.o))

    l = 0
    for c1 in cuts_1:
        for c2 in cuts_2:
            #print(f"Cuts: {c1} - {c2}")
            for k in range(cfg.m):
                operations_lk = np.arange(cfg.v_k[k,0] + (c1[k-1] if k>1 else 0) + (cfg.v2[k]-c2[k]), cfg.v_k[k,1] + (c1[k] - cfg.v1[k]) - (c2[k+1] if k<cfg.m-1 else 0)).astype(int)
                #print(f"Working station {k}: {operations_lk}")
                for i in range(cfg.n):
                    p[i, k, l] = np.sum(q[i,k,operations_lk])
            l+=1

    log = open(cfg.get_file('log'), 'a')
    for j in range(cfg.c):
        for k in range(cfg.m):
            if j >= cfg.v_k[k, 0] and j < cfg.v_k[k, 1]:
                print(f"op. {j}, machine {k}, p between {np.min(q[:, k, j])} and {np.max(q[:, k, j])}", file=log)

    """seed = None
    n = 20
    p_orig, n, m, o = read_data(n, seed)

    for i in range(n):
        for k in range(m):
            for l in range(o):
                #print(f"Job {i}, Machine {k}, Cut {l}: {p_orig[i, k, l]} / {p[i, k, l]}")
                if p_orig[i, k, l] != p[i, k, l]:
                    print(f"Job {i}, Machine {k}, Cut {l}: {p_orig[i, k, l]} / {p[i, k, l]}")"""

    save_data(p, cfg.n * cfg.m, cfg.o, cfg.get_file('p'))
    save_data(q, cfg.n * cfg.m, cfg.c, cfg.get_file('q'))

    return p,q

def save_data(p, r, c, file):
    matrix = p.reshape((r, c))
    pd.DataFrame(matrix).to_csv(file,header=None,index=None)


"""def subsample_data(p, n, m, o, n_star):
    jobs = np.random.choice(np.arange(n), n_star, replace=False)

    p_star = {}
    for i in range(n_star):
        for k in range(m):
            for l in range(o):
                p_star[i,k,l] = p[jobs[i],k,l]
    return p_star, n_star, m, o


def perturbate_data(p, n, m, o):
    p_star = {}
    for i in range(n):
        for k in range(m):
            delta = np.random.choice(np.concatenate((np.arange(-5,0),np.arange(1,6))), 1)[0]
            for l in range(o):
                p_star[i,k,l] = p[i,k,l] + delta
    return p_star, n, m, o"""

