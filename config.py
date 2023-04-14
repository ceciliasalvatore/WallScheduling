import os
import numpy as np

class Config:
    def __init__(self):
        self.folder = 'data'

        self.timelimit = 1800
        self.read_solution = True

        self.seed = -1
        self.n = 20
        self.m = 5

        self.v1 = np.zeros((self.m,)).astype(int)  # v1[i] := number of operations between i and i+1
        self.v1[1] = 7
        self.v2 = np.zeros((self.m,)).astype(int)  # v2[i] := number of operations between i and i-1
        self.v2[3] = 4

        self.v_k = np.zeros((self.m, 2)).astype(int)  # v_k[k,0/1] = index of the first/last operation on machine k

        for k in range(self.m):
            self.v_k[k, 0] = (self.v_k[k - 1, 1] if k > 0 else 0) - (self.v1[k - 1] if k > 0 else 0) - self.v2[k]
            self.v_k[k, 1] = self.v_k[k, 0] + 1 + self.v1[k] + self.v2[k] + (self.v1[k - 1] if k > 0 else 0) + (
                self.v2[k + 1] if k < self.m - 1 else 0)

        self.c = int(self.v_k[-1,-1])

        self.Machine = {}
        for i in range(self.c):
            self.Machine[i] = [k for k in range(self.m) if i in range(self.v_k[k,0],self.v_k[k,1])]

        self.o = int(np.product(self.v1+1)*np.product(self.v2+1))

    def get_file(self, name, ext='txt'):
        dir = f"{self.folder}/{self.n}"
        os.makedirs(dir,exist_ok=True)
        file = f"{dir}/{name}_{self.seed}.{ext}"
        return file

    def set_seed(self, seed):
        self.seed = seed
        if seed > 0:
            np.random.seed(seed)

cfg = Config()

