#!/usr/bin/env pyhton3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize as mini

from qfi_opt import spin_models as sm
from qfi_opt.examples import calculate_qfi as calc_qfi

# set up initial params
pts = 1
runs = 1
N = 2
key = 'z'
pi = np.pi; method = 'Nelder-Mead'; bnds =((0,1), (0,1), (0,1), (0,1/2)); tol=1e-6;
# set up data saving matrices
dat = np.zeros((pts, runs, 5), dtype='float64')
starters = np.zeros((pts, runs, 4), dtype='float64')

# set up collective operator and max bounds
G = sm.collective_op(sm.PAULI_Z, N) / (2 * N)
x0 = np.array([1/2,1/2,1/2,1/4])


# set up dissipation sets
dis_vec = np.logspace(-2,2.5,pts)
blank_vec = np.zeros((pts))
dis = {'all':np.array([dis_vec, dis_vec, dis_vec]), 'none': np.array([blank_vec, blank_vec, blank_vec]),
       'x':np.array([dis_vec, blank_vec, blank_vec]), 'y': np.array([blank_vec, dis_vec, blank_vec]),
       'z': np.array([blank_vec, blank_vec, dis_vec])}

# print(dis[key])
# print(dis[key][:,-1])

x = 0

# define cost function
def funct(x0_:np.array, args:tuple):
       print(x0_, args)
       global x
       x += 1
       if x > 10:
              exit()
       args = tuple(args)
       rho = sm.simulate_OAT(params=x0_, num_qubits=N, dissipation_rates = args)
       print(type(rho))
       return -calc_qfi.compute_QFI(rho, G)


for k in range(pts):
       params = x0 * np.random.rand(4)
       for i in range(runs):
              print('k =', k+1,'\n', 'i =', i+1)
              starters[k,i,:] = params

              out = mini(funct, params, args=dis[key][:,k], method=method, bounds=bnds, options={'xatol':tol, 'fatol':tol})
              dat[k,i,:4] = out.x
              dat[k,i,4] = -out.fun



# pth = '/home/zunigjua/Workspace/Projects/QFI-Opt/MyCode/OAT_Code/OAT_Histogram_Generation/Data'
# for k in range(pts):
#        if k==1:
#               break
#        np.savetxt(pth + '/starting_point_%s.txt'%(k+1), starters[k,:,:])
#        np.savetxt(pth + '/ops_and_qfi_%s.txt'%(k+1), dat[k, :,:])

