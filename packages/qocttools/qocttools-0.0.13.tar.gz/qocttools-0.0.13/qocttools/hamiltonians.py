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

"""This module holds the class that holds the Hamiltonian.


"""

import numpy as np
import qutip as qt

class hamiltonian:
    """A class to hold and manipulate the Hamiltonian and dissipation terms.

    The Hamiltonian should contain a static part, a list of possible perturbations,
    and also a list of dissipative terms for the Lindblad equation (which is not,
    of course, a proper term of the Hamiltonian)

    There are two options for the user to pass the Hamiltonian to qocttools: as
    a list of Qobj objects, or as a Qobj-valued user-defined function.

    1. In the first case, the Hamiltonian has the form:

       .. math::
          H(t) = H_0 + \sum_{i=1}^N f_i(t) V_i

       The pulses :math:`f_i(t)` are not described in the hamiltonian object.
       The user must then pass H0 and a list of perturbations V (it may also
       be just one). In addition, for open systems, the hamiltonian object
       should also contain the Lindblad operators, which should be supplied
       by the user as a list of Qobj objects.

    2. In the second case, the user should supply Qobj-valued functions. In this
       case, the H0 function contains the full Hamiltonian, and depends on time
       and on the set of "pulses" :math:`f_i(t)`:

       .. math::
          H_0 = H_0(t, f_1(t), \dots, f_N(t))

       The user must then also supply, in the argument V, a list with the
       derivatives of :math:`H0` with respect to each :math:`f_i` argument:

       .. math::
          V_i(t, f_1(t), \dots, f_N(t)) = \\frac{\partial H_o}{\partial f_i}(t, f_1(t), \dots, f_N(t))

       The function H0 (and the functions in the V list) should have the following inteface:

       .. code-block:: python

          def H0(t, args):
              f = args["f"]
              # f[0], f[1], f[2], ..., f[N-1] are the time-dependent functions

       The arguments are a float t that means time, and a dictionary args with just one element
       with name "f", and whose value is a list of functions of time.


    Parameters
    ----------
    H0 : Qobj or Qobj-valued function
        The qutip Qobj instance holding the static part of the Hamiltonian.
    V : Qobj or list of Qobj or Qobj-valued function or list of Qobj-valued functions.
        One or various Qobj instances holding external perturbations.
    A : Qobj or list of Qobj, default = None
        One or various Qobj instances holding the jump operators defining
        the Lindbladian.
    g : still undocumnted, default = None
    gradg: still undocumented, default = None    

    Attributes
    ----------
    H0 : Qobj
        The qutip Qobj instance holding the static part of the Hamiltonian.
    V : list of Qobj
        One or various Qobj instances holding external perturbations.
    A : list of Qobj
        One or various Qobj instances holding the jump operators defining
        the Lindblad operator.

    """

    def __init__(self, H0, V, A = None, g = None, gradg = None):
        if not isinstance(H0, qt.qobj.Qobj):
            self.function = True
            self.H0 = H0
            if isinstance(V, list):
                self.V = []
                for j in range(len(V)):
                    (self.V).append(V[j])
            else:
                self.V = [V]
            self.dim = H0(0.0, args = { "f" : [lambda t : 0]*len(self.V) } ).dims[0][0]
        else:
            self.function = False
            self.dim = H0.dims[0][0]
            self.H0 = H0.copy()
            if isinstance(V, list):
                self.V = []
                for j in range(len(V)):
                    (self.V).append(V[j].copy())
            else:
                self.V = [V.copy()]

        self.A = A
        if g is not None:
            self.g = g
        if gradg is not None:
            self.gradg = gradg

    def has_dissipative_terms(self):
        """Returns True if the dissipative terms are not None

        Returns
        -------
        bool:
            True if the attribute holding the dissipative terms
            is not None, False otherwise.

        """
        return (self.A is not None)

    def gradg(self, f, j, l):
        if j == l:
            return 1
        else:
            return 0

    def g(self, f, j):
        return f[j]


def toliouville(h):
    """
    This function transforms a Hamiltonian, defined in Hilbert
    space, together with the set of Lindblad operators, to the corresponding
    Liouvillian in Liouville space. It is also returned as a hamiltonian
    object

    Parameters
    ----------
    h : hamiltonian
       The input Hamiltonian, to be transformed.

    Returns
    -------
    hamiltonian
       A hamiltonian object with the transformed Hamiltonian.

    """
    dim = h.dim**2
    #print("dim = {}".format(dim))
    v__ = []
    l0__ = qt.Qobj(qt.liouvillian(h.H0, h.A), dims = [[dim], [dim]])
    for j in range(len(h.V)):
        v__.append( qt.Qobj(qt.liouvillian(h.V[j]), dims = [[dim], [dim]]) )
    return hamiltonian(l0__, v__)
