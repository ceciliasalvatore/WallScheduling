import copy
import os.path
import sys
import time
import numpy as np
import pandas as pd

from WS_pos import WS_positional_implicit,WS_positional_explicit
from WS_prec import WS_precedence_explicit,WS_precedence_implicit
from gurobipy import GRB
from config import cfg


def WS(p, q, type_):
    # p: dict p[i,k,l] = processing time of job i con working station k according to cut t
    file = f'log_file_{type_}.txt'
    if os.path.exists(file):
        log = open(file,'a')
    else:
        log = open(file, 'x')
        print("seed,n,solved,solvingtime,totaltime,objectivevalue,MIPgap", file=log)

    t0 = time.time()

    if type_=='pos_expl':
        model, x, y, s, P = WS_positional_explicit(q)
    elif type_=='pos_impl':
        model, x, s = WS_positional_implicit(p)
    elif type_=='prec_expl':
        model, x, y, s, cmax = WS_precedence_explicit(q, p)
    elif type_=='prec_impl':
        model, x, y, s, cmax = WS_precedence_implicit(p)
    else:
        sys.exit(f'Unknown model type {type_}')
    t1 = time.time()

    model.setParam(GRB.Param.TimeLimit, cfg.timelimit)

    solved=True
    if cfg.read_solution:
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

    print(f"{cfg.seed},{cfg.n},{solved},{t2-t1},{t2-t0},{model.getAttr('ObjVal')},{model.getAttr('MIPGap')}", file=log)


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
