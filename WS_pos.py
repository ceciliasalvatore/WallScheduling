import gurobipy as gb
from gurobipy import GRB, quicksum
from utils import generate_warmstart_p, generate_warmstart_q

from config import cfg

def WS_positional_exp(p):
    # p: dict p[i,k,l] = processing time of job i con working station k according to cut t
    print("------------------ POSITIONAL EXPONENTIAL WALL SCHEDULING MODEL ------------------")
    model = gb.Model()

    # x[i,j,l] := 1 if job i is in position j and it executes cut l
    x = model.addVars([(i,j,l) for i in range(cfg.n) for j in range(cfg.n) for l in range(cfg.o)], vtype=GRB.BINARY, name='x')
    # s[j,k] is the starting time of job in position j on working station k
    s = model.addVars([(j,k) for j in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='s')
    # cmax := completing time of the last job
    # cmax = model.addVar(lb=0, vtype=GRB.CONTINUOUS)

    v1 = model.addConstrs((x.sum(i,'*','*')==1 for i in range(cfg.n)), name='v1')
    v2 = model.addConstrs((x.sum('*',j,'*')==1 for j in range(cfg.n)), name='v2')

    # TODO CHECK REDUNDANCY OF v3
    #v3 = model.addConstrs((s[0,k+1] == quicksum(p[i,k,l]*x[i,0,l] for i in range(cfg.n) for l in range(cfg.o)) + s[0,k] for k in range(cfg.m-1)), name='v3')
    v4 = model.addConstrs((s[j,k+1] >= s[j,k] + quicksum(p[i,k,l]*x[i,j,l] for i in range(cfg.n) for l in range(cfg.o)) for j in range(cfg.n) for k in range(cfg.m-1)), name='v4')
    v5 = model.addConstrs((s[j+1,k] >= s[j,k] + quicksum(p[i,k,l]*x[i,j,l] for i in range(cfg.n) for l in range(cfg.o)) for k in range(cfg.m) for j in range(cfg.n-1)), name='v5')
    v6 = model.addConstrs((s[j,k]>=s[j-1,k+1] for j in range(1,cfg.n) for k in range(cfg.m-1)),name='v6')

    model.setObjective(s[cfg.n-1,cfg.m-1]+quicksum(p[i,cfg.m-1,l]*x[i,cfg.n-1,l] for i in range(cfg.n) for l in range(cfg.o)), sense=GRB.MINIMIZE)

    # Generate an initial solution
    jobs_order, cuts_order = generate_warmstart_p(p)
    model.update()

    init_Constraints = []
    for pos in range(cfg.n):
        for i in range(cfg.n):
            for l in range(cfg.o):
                if jobs_order[pos]==i and cuts_order[pos]==l:
                    #x[i,pos,l].Start=1
                    v = 1
                else:
                    #x[i,pos,l].Start=0
                    v = 0
                init_Constraints.append(model.addConstr(x[i,pos,l]==v))
    model.optimize()
    model.remove(init_Constraints)
    return model, x, s

def WS_positional_poly(q):
    # q: dict q[j,k,i] = processing time of operation i of job j on working station k

    print("------------------ POSITIONAL WALL SCHEDULING MODEL ------------------")
    model = gb.Model()

    # x[j,h] := 1 if job j is in position h
    x = model.addVars([(j,h) for j in range(cfg.n) for h in range(cfg.n)], vtype=GRB.BINARY, name='x')
    # y[i,j,k] := 1 if operation i of job j is assigned to machine k
    y = model.addVars([(i,j,k) for j in range(cfg.n) for k in range(cfg.m) for i in range(cfg.v_k[k, 0], cfg.v_k[k, 1])], vtype=GRB.BINARY, name='y')
    # s[h,k] := starting time of job in position h on machine k
    s = model.addVars([(h,k) for h in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='s')
    # P[h,k] := processing time of job in position h on machine k
    P = model.addVars([(h,k) for h in range(cfg.n) for k in range(cfg.m)], vtype=GRB.CONTINUOUS, lb=0, name='P')

    M = {}
    for j in range(cfg.n):
        for k in range(cfg.m):
            M[j,k]=0
            for i in range(cfg.v_k[k, 0], cfg.v_k[k, 1]):
                M[j,k] += q[j,k,i]

    v1 = model.addConstrs((x.sum(j,'*')==1 for j in range(cfg.n)))
    v2 = model.addConstrs((x.sum('*',h)==1 for h in range(cfg.n)))
    v3 = model.addConstrs((P[h,k] >= quicksum(q[j,k,i]*y[i,j,k] for i in range(cfg.v_k[k, 0], cfg.v_k[k, 1])) - M[j, k] * (1 - x[j, h]) for h in range(cfg.n) for k in range(cfg.m) for j in range(cfg.n)))

    # TODO REMOVE v4
    #v4 = model.addConstrs((s[0,k+1]==s[0,k]+P[0,k] for k in range(cfg.m-1)))
    v5 = model.addConstrs((s[h,k+1]>=s[h,k]+P[h,k] for k in range(cfg.m-1) for h in range(cfg.n)))
    v6 = model.addConstrs((s[h+1,k]>=s[h,k]+P[h,k] for k in range(cfg.m) for h in range(cfg.n-1)))
    v7 = model.addConstrs((s[h,k]>=s[h-1,k+1] for k in range(cfg.m-1) for h in range(1,cfg.n)))
    v8 = model.addConstrs((y.sum(i,j,'*')==1 for i in range(cfg.c) for j in range(cfg.n)))
    v9 = model.addConstrs((y[i+1,j,k1]+y[i,j,k2]<=1 for j in range(cfg.n) for i in range(cfg.c-1) for k1 in cfg.Machine[i+1] for k2 in cfg.Machine[i] if k1<k2))

    model.setObjective(s[cfg.n-1,cfg.m-1]+P[cfg.n-1,cfg.m-1], sense=GRB.MINIMIZE)

    jobs_order, operations_order = generate_warmstart_q(q)
    model.update()

    init_Constraints = []
    for pos in range(cfg.n):
        for i in range(cfg.n):
            if jobs_order[pos]==i:
                v = 1
            else:
                v = 0
            init_Constraints.append(model.addConstr(x[i,pos]==v))
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
    return model, x, y, s, P