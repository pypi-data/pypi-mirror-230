#!/usr/bin/env python
# -*- coding: utf-8 -*-

#calculates the arma matrices for GARCH and ARIMA

from pathlib import Path
import os
import numpy.ctypeslib as npct
import ctypes as ct
p = os.path.join(Path(__file__).parent.absolute(),'cfunctions')
if os.name=='nt':
  cfunct = npct.load_library('ctypes.dll',p)
else:
  cfunct = npct.load_library('ctypes.so',p)
import numpy as np


CDPT = ct.POINTER(ct.c_double) 
CIPT = ct.POINTER(ct.c_uint) 


def set_garch_arch(panel,args,u, h_add, G):
  """Solves X*a=b for a where X is a banded matrix with 1 or zero, and args along
  the diagonal band"""
  N, T, _ = u.shape
  rho=np.insert(-args['rho'],0,1)
  psi=args['psi']
  psi=np.insert(args['psi'],0,0) 



  lmbda = args['lambda']
  gmma = -args['gamma']
  
  parameters = np.array(( N , T , 
                  len(lmbda), len(rho), len(gmma), len(psi), 
                  panel.options.EGARCH.value, panel.lost_obs, 
                  h_add))
  if True:
    AMA_1,AMA_1AR,GAR_1,GAR_1MA, e, var, h = inv_c(parameters, lmbda, rho, gmma, psi, N, T, u, G, panel.T_arr)
  else:
    AMA_1,AMA_1AR,GAR_1,GAR_1MA, e, var, h = inv_python(parameters, lmbda, rho, gmma, psi, N, T, u, G, panel.T_arr)

  r=[]
  #Creating nympy arrays with name properties. 
  for i in ['AMA_1','AMA_1AR','GAR_1','GAR_1MA']:
    r.append((locals()[i],i))
  for i in ['e', 'var', 'h']:
    r.append(locals()[i])

  return r

def inv_c(parameters,lmbda, rho,gmma, psi, N, T, u, G, T_arr):
  AMA_1,AMA_1AR,GAR_1,GAR_1MA, e, var, h=(
          np.append([1],np.zeros(T-1)),
                np.zeros(T),
                np.append([1],np.zeros(T-1)),
                np.zeros(T),
                np.zeros((N,T,1)),
                np.zeros((N,T,1)),
                np.zeros((N,T,1))
        )

  T_arr = np.array(T_arr.flatten(),dtype = float)
  cfunct.armas(parameters.ctypes.data_as(CIPT), 
                     lmbda.ctypes.data_as(CDPT), rho.ctypes.data_as(CDPT),
                                                  gmma.ctypes.data_as(CDPT), psi.ctypes.data_as(CDPT),
                                                  AMA_1.ctypes.data_as(CDPT), AMA_1AR.ctypes.data_as(CDPT),
                                                  GAR_1.ctypes.data_as(CDPT), GAR_1MA.ctypes.data_as(CDPT),
                                                  u.ctypes.data_as(CDPT), 
                                                  e.ctypes.data_as(CDPT), 
                                                  var.ctypes.data_as(CDPT),
                                                  h.ctypes.data_as(CDPT),
                                                  G.ctypes.data_as(CDPT), 
                                                  T_arr.ctypes.data_as(CIPT)
                                                  )		
  return AMA_1,AMA_1AR,GAR_1,GAR_1MA, e, var, h
  
def inv_python(parameters,lmbda, rho,gmma, psi, N, T, u, G, T_arr):
  AMA_1,AMA_1AR,GAR_1,GAR_1MA, e, var, h=(
      np.append([1],np.zeros(T-1)),
            np.zeros(T),
            np.append([1],np.zeros(T-1)),
            np.zeros(T),
            np.zeros(N*T),
            np.zeros(N*T),
            np.zeros(N*T)
    )

  u = u.reshape(N*T)
  G = G.reshape(N*T)
  armas(parameters,lmbda, rho,gmma, psi,
         AMA_1, AMA_1AR,GAR_1, GAR_1MA,u, e, 
         var,h,G, T_arr.flatten())		
  
  e, var, h, u, G=(e.reshape((N,T,1)),
            var.reshape((N,T,1)),
            h.reshape((N,T,1)), 
            u.reshape((N,T,1)), 
            G.reshape((N,T,1)))  
  return AMA_1,AMA_1AR,GAR_1,GAR_1MA, e, var, h

def inverse(n, x_args, nx, b_args, nb, a, ab):
  a[0] = 1.0
  ab[0] = b_args[0]

  for i in range(1, n):
    sum_ax = 0
    sum_ab = 0
    for j in range(min(i, nx)):
      sum_ax += x_args[j] * a[i-j-1]
    a[i] = -sum_ax
    for j in range(min(i+1, nb)):
      sum_ab += b_args[j] * a[i-j]
    ab[i] = sum_ab

  return a, ab

def armas(parameters, lambda_, rho, gamma, psi, AMA_1, AMA_1AR, GAR_1, GAR_1MA, u, e, var, h, W, T_arr):
  N = int(parameters[0])
  T = int(parameters[1])
  nlm = int(parameters[2])
  nrh = int(parameters[3])
  ngm = int(parameters[4])
  npsi = int(parameters[5])
  egarch = int(parameters[6])
  lost_obs = int(parameters[7])
  h_add = parameters[8]

  inverse(T, lambda_, nlm, rho, nrh, AMA_1, AMA_1AR)
  inverse(T, gamma, ngm, psi, npsi, GAR_1, GAR_1MA)

  for k in range(N):  # individual dimension
    for i in range(T_arr[k]):  # time dimension TODO: the upper limit here should be the maximum date for each group. 
      # ARMA:
      sum_e = 0
      for j in range(i+1):  # time dimension, backtracking
        sum_e += AMA_1AR[j] * u[(i-j) + k*T]
      e[i + k*T] = sum_e
      # GARCH:
      if i >= lost_obs:
        h[i + k*T] = sum_e**2 + h_add
        if egarch:
          h[i + k*T] = np.log(h[i + k*T] + 1e-18 * (h[i + k*T] == 0))
      sum_var = 0
      for j in range(i+1):  # time dimension, backtracking
        sum_var += GAR_1[j] * W[(i-j) + k*T] + GAR_1MA[j]*h[(i-j) + k*T]
      var[i + k*T] = sum_var

  return 0

  
def set_garch_arch_scipy(panel,args):
  #after implementing ctypes, the scipy version might be dropped entirely
  p,q,d,k,m=panel.pqdkm
  nW,n=panel.nW,panel.max_T

  AAR=-lag_matr(-panel.I,args['rho'])
  AMA_1AR,AMA_1=solve_mult(args['lambda'], AAR, panel.I)
  if AMA_1AR is None:
    return
  GMA=lag_matr(panel.I*0,args['psi'])
  GAR_1MA,GAR_1=solve_mult(-args['gamma'], GMA, panel.I)
  if GAR_1MA is None:
    return
  r=[]
  for i in ['AMA_1','AMA_1AR','GAR_1','GAR_1MA']:
    r.append((locals()[i],i))
  return r

def solve_mult(args,b,I):
  """Solves X*a=b for a where X is a banded matrix with 1  and args along
  the diagonal band"""
  import scipy
  n=len(b)
  q=len(args)
  X=np.zeros((q+1,n))
  X[0,:]=1
  X2=np.zeros((n,n))
  w=np.zeros(n)
  r=np.arange(n)	
  for i in range(q):
    X[i+1,:n-i-1]=args[i]
  try:
    X_1=scipy.linalg.solve_banded((q,0), X, I)
    if np.any(np.isnan(X_1)):
      return None,None			
    X_1b=fu.dot(X_1, b)
  except:
    return None,None

  return X_1b,X_1