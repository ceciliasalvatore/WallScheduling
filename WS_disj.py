import gurobipy as gb
from gurobipy import GRB, quicksum
from utils import generate_warmstart_p, generate_warmstart_q
import numpy as np

from config import cfg

def WS_disjunctive_exp(p):
    # p: dict p[i,k,l] = processing time of job i con working station k according to cut t

    print("------------------")
    print("DISJUNCTIVE WALL SCHEDULING MODEL")
    print("------------------")
    model = gb.Model()

    M = 1000

    # x[i,j] := 1 if job i preceeds job j
    x = model.addVars([(i,j) for i in range(cfg.n-1) for j in range(i+1,cfg.n)], vtype=GRB.BINARY, name='x')
    # s[j,k] is the starting time of job j on working station k
    s = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='s')
    # y[j,l] := 1 if job j follows cut l
    y = model.addVars([(j,l) for j in range(cfg.n) for l in range(cfg.o)], vtype=GRB.BINARY, name='y')
    # cmax := completing time of the last job
    P = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='P')

    cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='cmax')

    v1 = model.addConstrs((s[i,k+1]>=s[i,k]+P[i,k] for i in range(cfg.n) for k in range(cfg.m-1)), name='v1')
    # TODO CHECK redundancy constraint 22-24 and 23-25
    # TODO v2 and v3 changed
    #v2 = model.addConstrs((s[j,k]>=s[i,k]+P[i,k]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m)), name='v2')
    #v3 = model.addConstrs((s[i,k]>=s[j,k]+P[j,k]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m)), name='v3')
    v2 = model.addConstrs((s[j,cfg.m-1]>=s[i,cfg.m-1]+P[i,cfg.m-1]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n)), name='v2')
    v3 = model.addConstrs((s[i,cfg.m-1]>=s[j,cfg.m-1]+P[j,cfg.m-1]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n)), name='v3')
    v4 = model.addConstrs((s[j,k]>=s[i,k+1]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m-1)), name='v4')
    v5 = model.addConstrs((s[i,k]>=s[j,k+1]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m-1)), name='v5')
    v6 = model.addConstrs((cmax>=s[i,cfg.m-1]+P[i,cfg.m-1] for i in range(cfg.n)), name='v6')
    v7 = model.addConstrs((y.sum(i,'*')==1 for i in range(cfg.n)), name='v7')
    v8 = model.addConstrs((P[j,k] == quicksum(p[j,k,l]*y[j,l] for l in range(cfg.o)) for j in range(cfg.n) for k in range(cfg.m)), name='v8')
    model.setObjective(cmax, sense=GRB.MINIMIZE)

    # Generate an initial solution
    jobs_order, cuts_order = generate_warmstart_p(p)
    model.update()
    init_constraints = []
    for i in range(cfg.n):
        for l in range(cfg.o):
            if cuts_order[i] == l:
                #y[jobs_order[i], l].Start = 1
                v = 1
            else:
                #y[jobs_order[i], l].Start = 0
                v = 0
            init_constraints.append(model.addConstr(y[jobs_order[i],l]==v))
    for i in range(cfg.n - 1):
        for j in range(i+1, cfg.n):
            if np.where(jobs_order==i)[0][0] < np.where(jobs_order==j)[0][0]:
                #x[i,j].Start = 1
                v = 1
            else:
                #x[i,j].Start = 0
                v = 0
            init_constraints.append(model.addConstr(x[i,j]==v))
    model.optimize()
    model.remove(init_constraints)

    return model, x, y, s, cmax