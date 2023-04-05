import copy
import os.path
import sys
import time
import numpy as np
import pandas as pd
#from sklearn.linear_model import LinearRegression

from WS_pos import WS_positional_poly,WS_positional_exp
from WS_disj import WS_disjunctive_exp
from gurobipy import GRB
from config import cfg


def WS(p, q, type_):
    # p: dict p[i,k,l] = processing time of job i con working station k according to cut t
    file = f'log_file_{type_}.txt'
    if os.path.exists(file):
        log = open(file,'a')
    else:
        log = open(file, 'x')
        print("seed, n, solved, solving time, total time, objective value, MIP gap", file=log)

    t0 = time.time()

    if type_=='pos_exp':
        model, x, s = WS_positional_exp(p)
    elif type_=='pos_poly':
        model, x, y, s, P = WS_positional_poly(q)
    elif type_=='disj_exp':
        model, x, y, s, cmax = WS_disjunctive_exp(p)
    else:
        sys.exit(f'Unknown model type {type_}')
    t1 = time.time()

    model.setParam(GRB.Param.TimeLimit, cfg.timelimit)

    solved=True
    try:
        model.update()
        model.read(cfg.get_file(f'solution_{type_}', 'sol'))
        model.setParam(GRB.Param.TimeLimit, 1)
        solved=False
    except:
        pass

    model.optimize()

    t2 = time.time()

    print(f"Completed in {t2-t1} seconds")

    try:
        model.write(cfg.get_file(f'solution_{type_}', 'sol'))
    except:
        pass

    if False:#type_ == 'pos_exp':
        x_ = model.getAttr('X', x)
        x_ = pd.DataFrame(index=x_.keys(), data=x_.values()).to_numpy().reshape((cfg.n, cfg.n, cfg.o))
        cuts_used = np.where(x_>1-1.e-4)
        jobs_order = np.argsort(cuts_used[1])
        cuts_order = cuts_used[2][jobs_order]
        p_order = p[jobs_order, 1:4, cuts_order]

        stats = np.concatenate((cuts_order.reshape((-1,1)), p_order),axis=1)
        cuts_ranking = []
        for i in range(cfg.n):
            cuts_ranking.append(np.where(np.argsort(np.std(p[jobs_order[i],1:4,:],axis=0))==cuts_order[i])[0][0])
        stats = np.concatenate((stats, np.std(p_order, axis=1).reshape(-1,1), np.array(cuts_ranking).reshape((-1,1))),axis=1)
        cuts_ranking = []
        for i in range(cfg.n):
            cuts_ranking.append(np.where(np.argsort(np.max(p[jobs_order[i],1:4,:],axis=0))==cuts_order[i])[0][0])
        stats = np.concatenate((stats, np.max(p_order, axis=1).reshape(-1,1), np.array(cuts_ranking).reshape((-1,1))),axis=1)

        """reg = lambda p: LinearRegression().fit(np.array([1,2,3]).reshape(-1,1),p).coef_[0]
        slope = lambda p: np.array([reg(p[:,i]) for i in range(p.shape[1])])
        cuts_ranking = []
        for i in range(cfg.n):
            cuts_ranking.append(np.where(np.argsort(slope(p[jobs_order[i],1:4,:]))==cuts_order[i])[0][0])
        stats = np.concatenate((stats, np.max(p_order, axis=1).reshape(-1,1), np.array(cuts_ranking).reshape((-1,1))),axis=1)"""

        np.savetxt(cfg.get_file('cuts_ranking'), stats, fmt='%.2f', header='cut, p2, p3, p4, std(p2,p3,p4), rank_std, max(p2,p3,p4), rank_max')
    """if type_ == 'positional':
        x_ = model.getAttr('X', x)
        s_ = model.getAttr('X', s)
        cuts_frequency = np.array([x_.sum('*', '*', l).getValue() for l in range(o)])
        order = find_order_positional(x_, n, o)
        duration = np.zeros((n,m))
        cut = np.zeros((n))
        for pos in range(n):
            for k in range(m):
                for l in range(o):
                    if np.abs(x_[order[pos],pos,l]-1)<1.e-4:
                        duration[order[pos],k] = p[order[pos],k,l]
                        cut[order[pos]] = l
        print(order)
        print(cut)
    if type_ == 'disjunctive':
        x_ = model.getAttr('X', x)
        s_ = model.getAttr('X', s)
        y_ = model.getAttr('X', y)
        cuts_frequency = np.array([y_.sum('*', l).getValue() for l in range(o)])
        order = find_order_disjunctive(x_, n)
        duration = np.zeros((n,m))
        cut = np.zeros((n))
        for i in range(n):
            for l in range(o):
                if np.abs(y_[i,l]-1)<1.e-4:
                    cut[i] = l
                    for k in range(m):
                        duration[i,k] = p[i,k,l]
        print(order)
        print(cut)"""

    """for k in range(m):
        print(f"--- Machine {k} ---")
        for job in order:
            print(f"Starting time of job {job}: {s_[job,k]}, duration: {duration[job,k,]}")"""

    #frequent_cuts = (np.argsort(cuts_frequency)[::-1])[:len(np.where(cuts_frequency>0)[0])]
    #print(f"Frequent cuts: {frequent_cuts+1}")
    print(f"{cfg.seed}, {cfg.n}, {solved}, {t2-t1}, {t2-t0}, {model.getAttr('ObjVal')}, {model.getAttr('MIPGap')}", file=log)


def find_order_disjunctive(x_, n):
    x_ = copy.deepcopy(x_)
    order = []
    for pos in range(n):
        for i in range(n):
            if i not in order:
                is_i = True
                for j in range(i + 1, n):
                    if j not in order and np.abs(x_[i, j]) < 1.e-4:
                            is_i = False
                for j in range(i):
                    if j not in order and np.abs(x_[j, i] - 1) < 1.e-4:
                            is_i = False

                if is_i:
                    order.append(i)
                    for j in range(i + 1, n):
                        if j not in order:
                            x_.pop((i, j))
                    for j in range(i):
                        if j not in order:
                            x_.pop((j, i))
    return order



def find_order_positional(x_, n, o):
    order = []
    for pos in range(n):
        for i in range(n):
            for l in range(o):
                if np.abs(x_[i,pos,l]-1)<1.e-4:
                    order.append(i)
    return order
