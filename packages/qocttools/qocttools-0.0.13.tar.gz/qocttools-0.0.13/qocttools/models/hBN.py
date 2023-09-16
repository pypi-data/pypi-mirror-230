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

"""This module holds a hBN model


"""

import numpy as np
import qutip as qt

#a  =  2.5  #A
a = 4.7243153 # a.u.
#c  =  6.6  #A
c = 12.472192 # a.u.
#eb =  2.46 #eV
eb = 0.090403333 # a.u.
#en = -2.55 #eV
en = -0.093710772 # a.u.

#gam =[-2.16,-0.04,-0.08] # eV
gam =[-0.093710772, -0.0014699729, -0.0029399458] # eV

a1 = a * np.array([np.sqrt(3.0)/2.0,  1.0/2.0])
a2 = a * np.array([0.0, 1.0])

delta1 = np.zeros([3, 2])
delta2 = np.zeros([6, 2])
delta3 = np.zeros([3, 2])

d1 = (1.0/3.0) * np.sqrt(3) * a
d2 = a
#d3 = 2*a / ( np.sqrt(2.0)*np.sqrt(1-np.cos(np.pi/3)) )
d3 = d1 * (1+2*np.cos(np.pi/3))

for j in range(3):
    theta = np.pi/3 + j*(2.0*np.pi/3)
    delta1[j, :] = d1 * np.array([np.cos(theta), np.sin(theta)])

for j in range(6):
    theta = np.pi/6 + j*(2.0*np.pi/6)
    delta2[j, :] = d2 * np.array([np.cos(theta), np.sin(theta)])

for j in range(3):
    theta = j*(2.0*np.pi/3)
    delta3[j, :] = d3 * np.array([np.cos(theta), np.sin(theta)])


#print(d1, d2, d3)

kd = 4.0 * np.pi / (np.sqrt(3) * a)

b1 = kd * np.array([1.0, 0.0])
b2 = kd * np.array([-1.0/2.0, np.sqrt(3.0)/2.0])

Gammapoint = np.array([0.0, 0.0])
Kpoint  = kd * np.array([0.5, 1.0/(2.0*np.sqrt(3.0))])
Mpoint = kd * np.array([0.5, 0.0])

#Path in regiprocal space
dir=np.array([2/3,1/3])
kgrid = np.linspace(-3.5, 3.5, 101)[:,None]*dir[None,:]
klen  = np.sign(kgrid[:,0])*np.sqrt((kgrid**2).sum(axis=1))

def ffk(kgrid):
    #fk = np.exp(-1j*a*kgrid[0]/np.sqrt(3.)) + 2.*np.exp(1j*a*kgrid[0]/(2.*np.sqrt(3.)))*np.cos(a/2.*kgrid[1])
    fk = 0.0
    for j in range(3):
        fk = fk + np.exp(1j * (kgrid[0] * delta1[j, 0] + kgrid[1] * delta1[j, 1]) )
    return fk

def fgk(kgrid):
    #gk = 2.*np.cos(a*kgrid[1]) + 2.*np.cos(a*np.sqrt(3.)/2.*kgrid[0]+ a/2.*kgrid[1]) \
    #                             + 2.*np.cos(a*np.sqrt(3.)/2.*kgrid[0]- a/2.*kgrid[1])
    gk = 0.0
    for j in range(6):
        gk = gk + np.exp(1j * (kgrid[0] * delta2[j, 0] + kgrid[1] * delta2[j, 1]) )
    return gk

def fhk(kgrid):
    #hk = np.exp(1j*2.*a*kgrid[0]/np.sqrt(3.)) + 2.*np.exp(-1j*a*kgrid[0]/np.sqrt(3.))*np.cos(a*kgrid[1])
    hk = 0.0
    for j in range(3):
        hk = hk + np.exp(1j * (kgrid[0] * delta3[j, 0] + kgrid[1] * delta3[j, 1]) )
    return hk

def dfk(kgrid):
    dfk = np.zeros(2, dtype = complex)
    for j in range(3):
        dfk = dfk + np.exp(1j * (kgrid[0] * delta1[j, 0] + kgrid[1] * delta1[j, 1]) ) * delta1[j, :]
    return 1j * dfk

def dgk(kgrid):
    dgk = np.zeros(2, dtype = complex)
    for j in range(6):
        dgk = dgk + np.exp(1j * (kgrid[0] * delta2[j, 0] + kgrid[1] * delta2[j, 1]) ) * delta2[j, :]
    return 1j * dgk

def dhk(kgrid):
    dhk = np.zeros(2, dtype = complex)
    for j in range(3):
        dhk = dhk + np.exp(1j * (kgrid[0] * delta3[j, 0] + kgrid[1] * delta3[j, 1]) ) * delta3[j, :]
    return 1j * dhk


def H0k(kvec):
    h0kmatrix = np.zeros([2, 2], dtype = complex)
    h0kmatrix[0, 0] = eb + gam[1] * fgk(kvec)
    h0kmatrix[0, 1] = gam[0] * ffk(kvec)  + gam[2] * fhk(kvec)
    h0kmatrix[1, 0] = np.conj(h0kmatrix[0, 1])
    h0kmatrix[1, 1] = en + gam[1] * fgk(kvec)
    return qt.Qobj(h0kmatrix)

def Hxk(kvec):
    hxkmatrix = np.zeros([2, 2], dtype = complex)
    hxkmatrix[0, 0] = gam[1] * dgk(kvec)[0]
    hxkmatrix[0, 1] = gam[0] * dfk(kvec)[0]  + gam[2] * dhk(kvec)[0]
    hxkmatrix[1, 0] = np.conj(hxkmatrix[0, 1])
    hxkmatrix[1, 1] = gam[1] * dgk(kvec)[0]
    return qt.Qobj(hxkmatrix)

def Hyk(kvec):
    hykmatrix = np.zeros([2, 2], dtype = complex)
    hykmatrix[0, 0] = gam[1] * dgk(kvec)[1]
    hykmatrix[0, 1] = gam[0] * dfk(kvec)[1]  + gam[2] * dhk(kvec)[1]
    hykmatrix[1, 0] = np.conj(hykmatrix[0, 1])
    hykmatrix[1, 1] = gam[1] * dgk(kvec)[1]
    return qt.Qobj(hykmatrix)


