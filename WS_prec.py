import gurobipy as gb
from gurobipy import GRB, quicksum
from utils import generate_warmstart_p, generate_warmstart_q
import numpy as np

from config import cfg

def WS_precedence_explicit(p):
    # p: dict p[i,k,l] = processing time of job i con working station k according to cut t

    print("------------------ PRECEDENCE EXPLICIT WALL SCHEDULING MODEL ------------------")

    model = gb.Model()

    M = p.sum(axis=1).max(axis=1).sum()

    # x[i,j] := 1 if job i preceeds job j
    x = model.addVars([(i,j) for i in range(cfg.n-1) for j in range(i+1,cfg.n)], vtype=GRB.BINARY, name='x')
    # s[j,k] is the starting time of job j on working station k
    s = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='s')
    # y[j,l] := 1 if job j follows cut l
    y = model.addVars([(j,l) for j in range(cfg.n) for l in range(cfg.o)], vtype=GRB.BINARY, name='y')
    # P[j,k] is the processing time of job j on working station k
    P = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='P')
    # cmax := completing time of the last job
    cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='cmax')

    v1 = model.addConstrs((s[i,k+1]>=s[i,k]+P[i,k] for i in range(cfg.n) for k in range(cfg.m-1)), name='v1')
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
                v = 1
            else:
                v = 0
            init_constraints.append(model.addConstr(y[jobs_order[i],l]==v))
    for i in range(cfg.n - 1):
        for j in range(i+1, cfg.n):
            if np.where(jobs_order==i)[0][0] < np.where(jobs_order==j)[0][0]:
                v = 1
            else:
                v = 0
            init_constraints.append(model.addConstr(x[i,j]==v))
    model.optimize()
    model.remove(init_constraints)

    return model, x, y, s, cmax

def WS_precedence_implicit(q, p):
    # q: dict q[j,k,i] = processing time of operation i of job j on working station k

    print("------------------ POSITIONAL IMPLICIT WALL SCHEDULING MODEL ------------------")
    model = gb.Model()

    M = p.sum(axis=1).max(axis=1).sum()

    # x[i,j] := 1 if job i preceeds job j
    x = model.addVars([(i,j) for i in range(cfg.n-1) for j in range(i+1,cfg.n)], vtype=GRB.BINARY, name='x')
    # y[i,j,k] := 1 if operation i of job j is executed on machine k
    y = model.addVars([(i,j,k) for j in range(cfg.n) for k in range(cfg.m) for i in range(cfg.v_k[k, 0], cfg.v_k[k, 1])], vtype=GRB.BINARY, name='y')

    # s[j,k] is the starting time of job j on working station k
    s = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='s')
    # P[j,k] is the processing time of job j on working station k
    P = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='P')
    # cmax := completing time of the last job
    cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='cmax')

    v1 = model.addConstrs((s[i,k+1]>=s[i,k]+P[i,k] for i in range(cfg.n) for k in range(cfg.m-1)), name='v1')
    #v2 = model.addConstrs((s[j,k]>=s[i,k]+P[i,k]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m)), name='v2')
    #v3 = model.addConstrs((s[i,k]>=s[j,k]+P[j,k]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m)), name='v3')
    v2 = model.addConstrs((s[j,cfg.m-1]>=s[i,cfg.m-1]+P[i,cfg.m-1]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n)), name='v2')
    v3 = model.addConstrs((s[i,cfg.m-1]>=s[j,cfg.m-1]+P[j,cfg.m-1]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n)), name='v3')
    v4 = model.addConstrs((s[j,k]>=s[i,k+1]-M*(1-x[i,j]) for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m-1)), name='v4')
    v5 = model.addConstrs((s[i,k]>=s[j,k+1]-M*x[i,j] for i in range(cfg.n-1) for j in range(i+1,cfg.n) for k in range(cfg.m-1)), name='v5')
    v6 = model.addConstrs((cmax>=s[i,cfg.m-1]+P[i,cfg.m-1] for i in range(cfg.n)), name='v6')
    v7 = model.addConstrs((y.sum(i,j,'*')==1 for i in range(cfg.c) for j in range(cfg.n)), name='v7')
    v8 = model.addConstrs((y[i+1,j,k1]+y[i,j,k2]<=1 for j in range(cfg.n) for i in range(cfg.c-1) for k1 in cfg.Machine[i+1] for k2 in cfg.Machine[i] if k1<k2), name='v8')
    v9 = model.addConstrs((P[j,k] == quicksum(q[j,k,i]*y[i,j,k] for i in range(cfg.v_k[k,0],cfg.v_k[k,1])) for j in range(cfg.n) for k in range(cfg.m)), name='v9')
    model.setObjective(cmax, sense=GRB.MINIMIZE)

    jobs_order, operations_order = generate_warmstart_q(q)
    model.update()

    init_Constraints = []
    for i in range(cfg.n - 1):
        for j in range(i+1, cfg.n):
            if np.where(jobs_order==i)[0][0] < np.where(jobs_order==j)[0][0]:
                v = 1
            else:
                v = 0
            init_Constraints.append(model.addConstr(x[i,j]==v))
    for j in range(cfg.n):
        for k in range(cfg.m):
            for i in range(cfg.v_k[k,0],cfg.v_k[k,1]):
                if operations_order[jobs_order[j],i]==k:
                    v = 1
                else:
                    v = 0
                init_Constraints.append(model.addConstr(y[i,jobs_order[j],k]==v))
    model.optimize()
    model.remove(init_Constraints)

    return model, x, y, s, cmax