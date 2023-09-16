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

"""This module holds the GdW30 model


"""

import numpy as np
import qutip as qt

def hGdW30(D, E, H):
    """Creates a spin-7/2 Hamiltonian, tailored for the GdW30 molecular nanomagnet.

    Parameters
    ----------
    D : float
       One anysotropy parameter used to construct the Hamiltonian (see notes below).
    E : float
       One anysotropy parameter used to construct the Hamiltonian (see notes below).
    H : ndarray
       A three-dimensional numpy array used to construct the Hamitonian (see notes below).

    Returns
    -------
    Qobj:
        A Qobj operator with the static Hamiltonian modeling the spin system.

    Notes
    -----
    The operator returned follows the formula:

    .. math:: \hat{H}_0 = D(\hat{S}_z^2 - (1/3 S(S+1)) + E(\hat{S}_x^2-\hat{S}_y^2) \
              - g\mu_B \hat{\overrightarrow{S}}\overrightarrow{H}

    """
    S = 7/2
    g = 2.0
    mub = 13996.245 # Bohr magneton, in units of (MHz * h)/tesla
    Sx = qt.jmat(S, "x")
    Sy = qt.jmat(S, "y")
    Sz = qt.jmat(S, "z")
    H0 = D*(Sz**2 - (1/3 * S*(S + 1))) + E*(Sx**2 - Sy**2) - g * mub * (Sx*H[0] + Sy*H[1] + Sz*H[2])
    return H0


def vGdW30(H_m):
    """Creates a perturbation term for the for the GdW30 molecular nanomagnet.

    Parameters
    ----------
    H: : ndarray
       A three-dimensional numpy array used to construct the perturbation term (see notes below).

    Returns
    -------
    Qobj:
        A Qobj operator with the perturbation operator.

    Notes
    -----
    The operator returned follows the formula:

    .. math:: \hat{V} = - g\mu_B \hat{\overrightarrow{S}}\overrightarrow{H}_m

    """
    S = 7/2
    g = 2.0
    mub = 13996.245 # Bohr magneton, in units of (MHz * h)/tesla
    Sx = qt.jmat(S, "x")
    Sy = qt.jmat(S, "y")
    Sz = qt.jmat(S, "z")
    V = -g*mub*(Sx*H_m[0] + Sy*H_m[1] + Sz*H_m[2])
    return V

