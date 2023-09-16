
import numpy as np
import jax.numpy as jnp
import qutip as qt
import jax; jax.config.update('jax_platform_name', 'cpu')
from jax import grad
#import reciprocal.kpoints as kpoints
from reciprocal.kpoints import Kpointset
#import os

angstromtobohr = 1.8897261
eVtohartree = 0.036749322

#TNN parameters for MoS2 (GGA) (data from Table III)  
aa   = 3.190 * angstromtobohr 
e1   = 0.683 * eVtohartree
e2   = 1.707 * eVtohartree
t0   =-0.146 * eVtohartree
t1   =-0.114 * eVtohartree
t2   = 0.506 * eVtohartree
t11  = 0.085 * eVtohartree
t12  = 0.162 * eVtohartree
t22  = 0.073 * eVtohartree
r0   = 0.060 * eVtohartree
r1   =-0.236 * eVtohartree
r2   = 0.067 * eVtohartree
r11  = 0.016 * eVtohartree
r12  = 0.087 * eVtohartree
u0   =-0.038 * eVtohartree
u1   = 0.046 * eVtohartree
u2   = 0.001 * eVtohartree
u11  = 0.266 * eVtohartree
u12  =-0.176 * eVtohartree
u22  =-0.150 * eVtohartree

#TNN functions
def getab(kx, ky):
    # if (len(kgrid.shape)<2):
    #     a,b = (kgrid[0],kgrid[1])
    # else:
    #     a,b = (kgrid[:,0],kgrid[:,1])
    a,b = (aa * kx, aa * ky)
    return a*0.5,b*jnp.sqrt(3)*0.5


def V0(kx, ky):
    a,b = getab(kx, ky)
    v0 = e1 + 2*t0*(2*jnp.cos(a)  *jnp.cos(b)  + jnp.cos(2*a))\
            + 2*r0*(2*jnp.cos(3*a)*jnp.cos(b)  + jnp.cos(2*b))\
            + 2*u0*(2*jnp.cos(2*a)*jnp.cos(2*b)+ jnp.cos(4*a))
    return v0
V0x = grad(V0, argnums = 0)
V0y = grad(V0, argnums = 1)

def reV1(kx, ky):
    a,b = getab(kx, ky)
    rev1 = -2*jnp.sqrt(3)*t2*jnp.sin(a)*jnp.sin(b) + 2*(r1+r2)*jnp.sin(3*a)*jnp.sin(b) \
           -2*jnp.sqrt(3)*u2*jnp.sin(2*a)*jnp.sin(2*b)
    return rev1
reV1x = grad(reV1, argnums = 0)
reV1y = grad(reV1, argnums = 1)

def imV1(kx, ky):
    a,b = getab(kx, ky)
    imv1 = 2*t1*jnp.sin(a)*(2*jnp.cos(a)+jnp.cos(b)) + 2*(r1-r2)*jnp.sin(3*a)*jnp.cos(b) \
          +2*u1*jnp.sin(2*a)*(2*jnp.cos(2*a)+jnp.cos(2*b)) 
    return imv1
imV1x = grad(imV1, argnums = 0)
imV1y = grad(imV1, argnums = 1)
    
def reV2(kx, ky):
    a,b = getab(kx, ky)
    rev2 = 2*t2*(jnp.cos(2*a)-jnp.cos(a)*jnp.cos(b))\
          -2/jnp.sqrt(3)*(r1+r2)*(jnp.cos(3*a)*jnp.cos(b)-jnp.cos(2*b))\
          +2*u2*(jnp.cos(4*a)-jnp.cos(2*a)*jnp.cos(2*b))
    return rev2
reV2x = grad(reV2, argnums = 0)
reV2y = grad(reV2, argnums = 1)

def imV2(kx, ky):
    a,b = getab(kx, ky)
    imv2 = 2*jnp.sqrt(3)*t1*jnp.cos(a)*jnp.sin(b) \
          +2/jnp.sqrt(3)*jnp.sin(b)*(r1-r2)*(jnp.cos(3*a)+2*jnp.cos(b))\
          +2*jnp.sqrt(3)*u1*jnp.cos(2*a)*jnp.sin(2*b)
    return imv2
imV2x = grad(imV2, argnums = 0)
imV2y = grad(imV2, argnums = 1)

def V11(kx, ky):
    a,b = getab(kx, ky)
    v11 = e2 + (t11+3*t22)*jnp.cos(a)*jnp.cos(b) + 2*t11*jnp.cos(2*a)\
         + 4*r11*jnp.cos(3*a)*jnp.cos(b) + 2*(r11+jnp.sqrt(3)*r12)*jnp.cos(2*b)\
         + (u11+3*u22)*jnp.cos(2*a)*jnp.cos(2*b) + 2*u11*jnp.cos(4*a)
    return v11
V11x = grad(V11, argnums = 0)
V11y = grad(V11, argnums = 1)
    
def reV12(kx, ky):
    a,b = getab(kx, ky)
    rev12 = jnp.sqrt(3)*(t22-t11)*jnp.sin(a)*jnp.sin(b) + 4*r12*jnp.sin(3*a)*jnp.sin(b)\
           +jnp.sqrt(3)*(u22-u11)*jnp.sin(2*a)*jnp.sin(2*b)
    return rev12
reV12x = grad(reV12, argnums = 0)
reV12y = grad(reV12, argnums = 1)

def imV12(kx, ky):
    a,b = getab(kx, ky)
    imv12 = 4*t12*jnp.sin(a)*(jnp.cos(a)-jnp.cos(b))\
           +4*u12*jnp.sin(2*a)*(jnp.cos(2*a)-jnp.cos(2*b))
    return imv12
imV12x = grad(imV12, argnums = 0)
imV12y = grad(imV12, argnums = 1)

def V22(kx, ky):
    a,b = getab(kx, ky)
    v22 = e2 + (3*t11+t22)*jnp.cos(a)*jnp.cos(b) + 2*t22*jnp.cos(2*a)\
         +2*r11*(2*jnp.cos(3*a)*jnp.cos(b)+jnp.cos(2*b))\
         +2/jnp.sqrt(3)*r12*(4*jnp.cos(3*a)*jnp.cos(b)-jnp.cos(2*b))\
         +(3*u11+u22)*jnp.cos(2*a)*jnp.cos(2*b) + 2*u22*jnp.cos(4*a) 
    return v22
V22x = grad(V22, argnums = 0)
V22y = grad(V22, argnums = 1)

##Path in regiprocal space
#Gamma = np.array([0.,0.])
## K     = np.array([4*np.pi/3/aa,0])
## M     = np.array([np.pi/aa  ,np.pi/np.sqrt(3)/aa])
#K     = np.array([4*np.pi/3,0])                # in units of 1/a
#M     = np.array([np.pi ,np.pi/np.sqrt(3)])   # in units of 1/a
#Gammapoint = np.array([0.0, 0.0])
#Kpoint = np.array([4*np.pi/3,0])                # in units of 1/a
#Mpoint = np.array([np.pi ,np.pi/np.sqrt(3)])   # in units of 1/a
Gammapoint = np.array([0.0, 0.0]) / aa
Kpoint = np.array([4*np.pi/3,0]) / aa               # in units of 1/a
Mpoint = np.array([np.pi ,np.pi/np.sqrt(3)]) / aa  # in units of 1/a

# SOC (tab IV)
lam = 0.073 * eVtohartree
Lz  = np.array([[0, 0    ,0    ],\
                [0, 0    ,2*1.j],\
                [0,-2*1.j,0    ]])

def H0k(kk):
    htnn = np.array([[V0(*kk)                 , reV1(*kk) + 1j*imV1(*kk)  , reV2(*kk) + 1j*imV2(*kk)  ],\
                     [reV1(*kk) - 1j*imV1(*kk), V11(*kk)                  , reV12(*kk) + 1j*imV12(*kk)],\
                     [reV2(*kk) - 1j*imV2(*kk), reV12(*kk) - 1j*imV12(*kk), V22(*kk)]                 ])

    HH0= htnn
    #soc
    #H = qt.Qobj(np.kron(np.eye(2),HH0)+np.kron(qt.sigmaz(),lam/2*Lz))
    #no soc
    H = qt.Qobj(HH0)
    return H - 0.028151402249932324

def Hxk(kk):
    htnn = np.array([[V0x(*kk)                  , reV1x(*kk) + 1j*imV1x(*kk)  , reV2x(*kk) + 1j*imV2x(*kk)  ],\
                     [reV1x(*kk) - 1j*imV1x(*kk), V11x(*kk)                   , reV12x(*kk) + 1j*imV12x(*kk)],\
                     [reV2x(*kk) - 1j*imV2x(*kk), reV12x(*kk) - 1j*imV12x(*kk), V22x(*kk)]                  ])
    HH0= htnn
    #soc
    #H = qt.Qobj(np.kron(np.eye(2),HH0))
    #no soc
    H = qt.Qobj(HH0)
    return H

def Hyk(kk):
    htnn = np.array([[V0y(*kk)                  , reV1y(*kk) + 1j*imV1y(*kk)  , reV2y(*kk) + 1j*imV2y(*kk)  ],\
                     [reV1y(*kk) - 1j*imV1y(*kk), V11y(*kk)                   , reV12y(*kk) + 1j*imV12y(*kk)],\
                     [reV2y(*kk) - 1j*imV2y(*kk), reV12y(*kk) - 1j*imV12y(*kk), V22y(*kk)]                  ])
    HH0= htnn
    #soc
    #H = qt.Qobj(np.kron(np.eye(2),HH0))
    #no soc
    H = qt.Qobj(HH0)
    return H


def gammakmgammaset(nps = 50):
    #Kpoint = tmd.Kpoint
    #Mpoint = tmd.Mpoint
    #Gammapoint = tmd.Gammapoint

    GammaK = np.zeros([nps, 2])
    GammaK[:, 0] = np.linspace(Gammapoint[0], Kpoint[0], nps)
    GammaK[:, 1] = np.linspace(Gammapoint[1], Kpoint[1], nps)

    KM = np.zeros([nps, 2])
    KM[:, 0] = np.linspace(Kpoint[0], Mpoint[0], nps)
    KM[:, 1] = np.linspace(Kpoint[1], Mpoint[1], nps)

    MGamma = np.zeros([nps, 2])
    MGamma[:, 0] = np.linspace(Mpoint[0], Gammapoint[0], nps)
    MGamma[:, 1] = np.linspace(Mpoint[1], Gammapoint[1], nps)

    GammaKset = Kpointset(kpoints = GammaK,
                          line = True,
                          startpoint = '$\Gamma$', endpoint = 'K')
    KMset = Kpointset(kpoints = KM,
                      line = True, 
                      coordorigin = GammaKset.coord[-1],
                      startpoint = 'K', endpoint = 'M')
    MGammaset = Kpointset(kpoints = MGamma,
                          line = True,
                          coordorigin = KMset.coord[-1],
                          startpoint = 'M', endpoint = '$\Gamma$')

    kset = GammaKset
    kset.join(KMset)
    kset.join(MGammaset)

    return kset
