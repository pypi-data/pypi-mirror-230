## Copyright 2019-present The qocttools developing team
##
## This file is part of qocttools.
##
## qocttools is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## qocttools is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with qocttools.  If not, see <https://www.gnu.org/licenses/>.

"""This module holds a graphene tight-binding model


"""


import numpy as np
import qutip as qt

# There are three constants that must be set for the simple tight-binding model that
# we will be using: t (the hopping parameter), a (the lattice constant) and vf (the Fermi velocity).
# In fact, I think that they are linked by:
#
# vf = 3*a*t/2
#
# I am not sure about the right value for all these constants. I will use the following:
# (in atomic units)

vf = 0.512
a = 2.68
t = 2*vf / (3*a)

a1 = (a/2.0) * np.array([3.0,  np.sqrt(3.0)])
a2 = (a/2.0) * np.array([3.0, -np.sqrt(3.0)])

b1 = (2.0*np.pi/(3.0*a)) * np.array([1, np.sqrt(3)])
b2 = (2.0*np.pi/(3.0*a)) * np.array([1, -np.sqrt(3)])

delta = np.zeros([3, 2])
delta[0, :] = (a/2) * np.array([1.0,  np.sqrt(3.0)])
delta[1, :] = (a/2) * np.array([1.0, -np.sqrt(3.0)])
delta[2, :] = - a * np.array([1.0, 0.0])

Kpoint = (2*np.pi / (3*np.sqrt(3)*a)) * np.array([np.sqrt(3.0), 1.0])
Kpointp = (2*np.pi / (3*np.sqrt(3)*a)) * np.array([np.sqrt(3.0), -1.0])
Mpoint = (2*np.pi / (3*np.sqrt(3)*a)) * np.array([np.sqrt(3.0), 0.0])
Gammapoint = np.array([0.0, 0.0])

def deltak(kvec):
    y = 0j
    for j in range(3):
        y = y + np.exp(1j * np.dot(delta[j], kvec))
    return y

def graddeltak(kvec):
    y = np.zeros(2, dtype = complex)
    for j in range(3):
        y = y + 1j * delta[j, :] * np.exp(1j * np.dot(delta[j], kvec))
    return y

def H0k(kvec):
    dk = deltak(kvec)
    h0kmatrix = np.zeros([2, 2], dtype = complex)
    h0kmatrix[0, 1] = dk
    h0kmatrix[1, 0] = np.conj(dk)
    h0k = qt.Qobj(h0kmatrix)
    return -t * h0k

def H0gappedk(kvec):
    dk = deltak(kvec)
    h0kmatrix = np.zeros([2, 2], dtype = complex)
    h0kmatrix[1, 1] = 0.01/2
    h0kmatrix[0, 0] = -0.01/2
    h0kmatrix[0, 1] = dk
    h0kmatrix[1, 0] = np.conj(dk)
    h0k = qt.Qobj(h0kmatrix)
    return -t * h0k

def Hxk(kvec):
    ggk = graddeltak(kvec)
    mat = np.zeros([2, 2], dtype = complex)
    mat[0, 1] = t * ggk[0]
    mat[1, 0] = np.conj(mat[0, 1])
    return qt.Qobj(mat)

def Hyk(kvec):
    ggk = graddeltak(kvec)
    mat = np.zeros([2, 2], dtype = complex)
    mat[0, 1] = t * ggk[1]
    mat[1, 0] = np.conj(mat[0, 1])
    return qt.Qobj(mat)



