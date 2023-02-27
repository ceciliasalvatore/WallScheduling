import gurobipy as gb
from gurobipy import GRB, quicksum

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
    cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='cmax')

    v1 = model.addConstrs((s[i,k+1]>=s[i,k]+quicksum(p[i,k,l]*y[i,l] for l in range(cfg.o)) for i in range(cfg.n) for k in range(cfg.m-1)), name='v1')
    v2 = model.addConstrs((s[j,k]>=s[i,k]+quicksum(p[i,k,l]*y[i,l] for l in range(cfg.o))-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m)), name='v2')
    v3 = model.addConstrs((s[i,k]>=s[j,k]+quicksum(p[j,k,l]*y[j,l] for l in range(cfg.o))-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m)), name='v3')
    v4 = model.addConstrs((s[j,k]>=s[i,k+1]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m-1)), name='v4')
    v5 = model.addConstrs((s[i,k]>=s[j,k+1]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m-1)), name='v5')
    v6 = model.addConstrs((cmax>=s[i,cfg.m-1]+quicksum(p[i,cfg.m-1,l]*y[i,l] for l in range(cfg.o)) for i in range(cfg.n)), name='v6')
    v7 = model.addConstrs((y.sum(i,'*')==1 for i in range(cfg.n)), name='v7')

    model.setObjective(cmax, sense=GRB.MINIMIZE)

    return model