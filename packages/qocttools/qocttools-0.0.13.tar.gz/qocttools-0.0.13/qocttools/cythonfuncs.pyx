#cython: boundscheck=False, wraparound=False, nonecheck=True, cdivision = True

import numpy as np
from libc.math cimport sin, cos, sqrt


def fe(double t, double T, int M, double [:] u):
    cdef int k
    cdef double y, w
    cdef double pi = np.pi
    y = u[0] / sqrt(T)
    for k in range(M):
        w = 2*(k+1)*pi/T
        y += (2/sqrt(T)) * (u[2*k+1]*sin(w*t) +
                            u[2*k+2]*cos(w*t))
    return y


def dfe(double t, double T, int M, double [:] u, int m):
    cdef int m2
    cdef double w
    cdef double pi = np.pi
    if(m == 0):
        return 1.0/sqrt(T)
    elif(m % 2 == 0):
        m2 = int(m/2)
        w = 2*m2*np.pi/T
        return (2/sqrt(T)) * cos(w*t)
    else:
        m2 = int((m+1)/2)
        w = 2*m2*np.pi/T
        return (2/sqrt(T)) * sin(w*t)


def gradfe(double t, double T, int M, double [:] u):
    cdef int m2
    cdef double w
    cdef double pi = np.pi
    cdef int m
    grad = np.zeros(2*M+1)
    for m in range(2*M+1):
        if(m == 0):
            #return 1.0/sqrt(T)
            grad[m] = 1.0/sqrt(T)
        elif(m % 2 == 0):
            m2 = int(m/2)
            w = 2*m2*np.pi/T
            #return (2/sqrt(T)) * cos(w*t)
            grad[m] = (2/sqrt(T)) * cos(w*t)
        else:
            m2 = int((m+1)/2)
            w = 2*m2*np.pi/T
            #return (2/sqrt(T)) * sin(w*t)
            grad[m] = (2/sqrt(T)) * sin(w*t)
    return grad


def fourierexpansion(t, double T, int nu, double [:] u):
    cdef int M, j
    M = int((nu-1)/2)
    cdef double [:] ts
    cdef double [:] yy
    if isinstance(t, float):
        return fe(t, T, M, u)
    else:
        ts = t
        yt = np.zeros(t.shape[0])
        yy = yt
        for j in range(t.shape[0]):
            yy[j] = fe(ts[j], T, M, u)
        return yt


def dfourierexpansion(t, double T, int nu, double [:] u, int m):
    cdef int M, j
    M = int((nu-1)/2)
    cdef double [:] ts
    cdef double [:] yy
    if isinstance(t, float):
        return dfe(t, T, M, u, m)
    else:
        ts = t
        yt = np.zeros(t.shape[0])
        yy = yt
        for j in range(t.shape[0]):
            yy[j] = dfe(ts[j], T, M, u, m)
        return yt


def gradfourierexpansion(t, double T, int nu, double [:] u):
    cdef int M, j
    M = int((nu-1)/2)
    cdef double [:] ts
    cdef double [:] yy
    if isinstance(t, float):
        #return dfe(t, T, M, u, m)
        return gradfe(t, T, M, u)
    else:
        ts = t
        #yt = np.zeros(t.shape[0])
        yt = np.zeros([t.shape[0], nu])
        #yy = yt
        for j in range(t.shape[0]):
            #yy[j] = dfe(ts[j], T, M, u, m)
            yt[j, :] = dfe(ts[j], T, M, u)
        return yt


cdef int kdelta(int i, int j):
    if i == j:
        return 1
    else:
        return 0


def floquetcomponent(int dim, int ntsteps, double[:] ws, double complex[:, :, :] lindw):
    cdef int fdim
    cdef int alpha
    cdef int beta
    cdef int m, n, i, j
    fdim = dim * ntsteps
    lindb = np.zeros([fdim, fdim], dtype = complex)
    cdef double complex[:, :] lindb_view = lindb
    for i in range(fdim):
        alpha = i // ntsteps
        n = i % ntsteps
        for j in range(fdim):
            beta = j // ntsteps
            m = j % ntsteps
            if n-m < 0:
                lindb_view[i, j] = lindw[alpha, beta, ntsteps + (n-m)] - 1j * ws[m] * kdelta(i, j)
            else:
                lindb_view[i, j] = lindw[alpha, beta, n-m] - 1j * ws[m] * kdelta(i, j)
    return lindb


def floquetcomponent2(int Nu, int dim, int ntsteps, double complex[:, :, :, :] dlindw):
    cdef int fdim
    cdef int alpha
    cdef int beta
    cdef int m, n, i, j
    fdim = dim * ntsteps
    dlindb = np.zeros([Nu, fdim, fdim], dtype = complex)
    cdef double complex[:, :, :] dlindb_view = dlindb
    for k in range(Nu):
        for i in range(fdim):
            alpha = i // ntsteps
            n = i % ntsteps
            for j in range(fdim):
                beta = j // ntsteps
                m = j % ntsteps
                if n-m < 0:
                    dlindb_view[k, i, j] = dlindw[k, alpha, beta, ntsteps +  (n-m)]
                else:
                    dlindb_view[k, i, j] = dlindw[k, alpha, beta, n-m]
    return dlindb
