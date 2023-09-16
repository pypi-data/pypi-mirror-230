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

import numpy as np
import scipy as sp
import sys
import nlopt
from qutip import *
from time import time as clocktime
from qocttools.solvers import solve, intoper, solvep
import qocttools.math_extra as math_extra
import qocttools.target as target
import qocttools.krotov as krotov
import qocttools.hamiltonians as hamiltonians
import qocttools.pulses as pulses
import qocttools.floquet as floquet

"""qoct is the main module of the qocttools package

It holds the Qoct class, that is used to setup the optimization
problem.

"""

of = sys.stdout
comm = None
rank = 0

class Qoct:
    """The class that is used to setup the optimization.

    It stores the Hamiltonian, the definition of the target,
    the pulses, the initial state, and some parameters that determine
    how the optimization is done.

    Parameters
    ----------
    H : hamiltonian or list of hamiltonian
        A hamiltonian class instance, or list of instances for multitarget optimizations.
    T : float
        total propagation time
    ntsteps : int
        number of time steps
    tg : Target
        The object that defines the target functional.
    f : pulse or list of pulse
        The pulse object, or list of pulse objects (in the case the Hamiltonian(s) have
        more than one perturbations)
    y0 : Qobj or list of Qobj
        The initial state(s) for the optimization. It should be a list for multitarget
        optimizations. It can be a Hilbert space state, a density matrix, or a propagator.
    interaction_picture : bool, default = False
        The calculations can be done in the interaction picture, or in Schrödinger's picture.
    solve_method: str, default = 'cfmagnus4'
        The method to use for the propagations.
    equality_constraints : list, default = None
        The optimization can be done with constraints, that should be specified as
        a list of [func, tol] objects: func is a function that defines the constraint,
        and tol is a float that sets the tolerance accepted for the fulfillment of that
        constraint.
    sparse : bool, default = False
        It forces the use of sparse algebra only (otherwise, some parts of the calculation
        are done with dense matrices).
    output_file : file, default = sys.stdout
        One may ask the internal procedures of the qoct object to output messages to a
        file different from standard output

    Attributes
    ----------

    y0 : list of Qobj
    H : list of hamiltonian

    """
    def __init__(self, H, T, ntsteps, tg, f, y0,
                 interaction_picture = False,
                 solve_method = 'cfmagnus4',
                 equality_constraints = None,
                 sparse = False, 
                 output_file = sys.stdout,
                 new_parametrization = False,
                 mpi_comm = None,
                 floquet_mode = 'qoct'):

        global of
        global comm
        global rank

        # If y0 and H are not lists, lets us make them lists (with equal number of elements).
        if isinstance(y0, list):
            self.y0 = y0
        else:
            self.y0 = [y0]
        if isinstance(H, list):
            if not (len(H) == len(self.y0)):
                raise Exception("The number of Hamiltonians should be equal to the number of initial states")
            else:
                self.H = H
        else:
            # Normally, all Hamiltonians are equal.
            self.H = []
            for j in range(len(self.y0)):
                (self.H).append(H)
        self.T = T
        self.ntsteps = ntsteps
        self.time = np.linspace(0, T, ntsteps)
        if tg.targettype == 'generic':
            self.O = tg.operator
        elif tg.targettype == 'expectationvalue':
            self.O = tg.operator
        elif tg.targettype == 'evolutionoperator':
            self.O = tg.Utarget
        self.tg = tg

        if isinstance(f, list):
            self.f = []
            for j in range(len(f)):
                (self.f).append(f[j])
        else:
            self.f = [f]
        self.solve_method = solve_method
        self.interaction_picture = interaction_picture

        # The equality constraints
        eqc = []
        eq_tol = 1.0e-6
        for j in range(len(self.f)):
            g = pulses.pulse_constraint_functions(self.f[j], pulses.pulse_collection_parameter_range(self.f, j))
            for k in range(len(g)):
                eqc.append([g[k], eq_tol])
        if len(eqc) > 0:
            self.equality_constraints = []
            for cs in eqc:
                self.equality_constraints.append(cs)
            if equality_constraints is not None:
                for cs in equality_constraints:
                    self.equality_constraints.append(cs)
        else:
            self.equality_constraints = equality_constraints

        self.sparse = sparse
        self.of = output_file
        of = output_file
        self.convergence = None
        self.nprops = 0
        self.optimum = None
        self.new_parametrization = new_parametrization
        comm = mpi_comm
        if comm is not None:
            self.nprocs = comm.Get_size()
            rank = comm.Get_rank()
            if rank == 0:
                of.write("Number of processors = {}\n".format(self.nprocs))
            comm.Barrier()
        else:
            self.nprocs = 1
            rank == 0
        if not (tg.targettype == 'floquet'):
             self.floquet_mode = None
             self.nessopt = None
        else:
             self.floquet_mode = floquet_mode
             if floquet_mode == 'ness':
                  self.nessopt = floquet.Nessopt(tg.operator, T, ntsteps, hamiltonians.toliouville(H), f)
             else:
                  self.nessopt = None


    def almost_converged(self, fraction = 0.99):
        """Returns the iteration number at which the convergence was almost achieved

        It analyzes the convergence history of an optimization, and looks for the
        iteration at which the value of the functional was already a fraction (0.99
        by default) of the maximum.

        Parameters
        ----------
        fraction : float, default = 0.99
            The fraction of the maximum value at which the process is considered
            to be almost converged. If, at iteration 76, the value of the
            functional is already fraction * maximum, then this function
            will return 76 (along with the number of propagations necessary
            to reach iteration 76.

        Returns
        -------
        float
            The iteration at which the process was almost converged
        float
            The number of propagations done until that iteration.
        """
        for iter in self.convergence:
            if(iter[2] >= fraction * self.optimum):
                break
        return iter[0], iter[1]



    def gfunc(self, u):
        """Returns the value of the target functional for a set of parameters u.

        It just calls the gfunction function, using all the information contained
        in the class object.

        Parameters
        ----------
        u : ndarray
            A numpy array holding all the control parameters

        Returns
        -------
        float
            The value of the target parameter.
        """
        tg = self.tg
        Ffunction = tg.Fyu
        H = self.H
        f = self.f
        psi0 = self.y0
        time = self.time
        nessopt = self.nessopt

        if self.floquet_mode == 'pt':
            nkpoints = len(H)
            dim = H[0].dim
            eps = np.zeros([nkpoints, dim])
            for k in range(nkpoints):
                eps[k, :] = floquet.epsilon3(H[k], f, u, time[-1])
            return tg.f(eps)
        elif self.floquet_mode == 'ness':
            return nessopt.G(u)

        if len(psi0) > 1:
            multitarget = True
        else:
            multitarget = False

        pulses.pulse_collection_set_parameters(f, u)

        result = solvep(self.solve_method, H, f, psi0, time,
                        returnQoutput = False, interaction_picture = self.interaction_picture,
                        options = Options(normalize_output = False),
                        comm = comm)
        dim = len(psi0)
        result_states = []
        for i in range(dim):
            result_states.append(Qobj(result[i][time.size-1]))

        return Ffunction(result_states, u) if multitarget else Ffunction(result_states[0],u)


    def dgfunc(self, u):
        """Returns the value and gradient of the target functional for a set of parameters u.


        It just calls the dgfunction function, using all the information contained
        in the class object.

        Parameters
        ----------
        u : ndarray
            A numpy array holding all the control parameters

        Returns
        -------
        float
            The value of the target parameter.
        ndarray
            The gradient of the target functional.
        """

        solve_method = self.solve_method
        tg = self.tg
        Ffunction = tg.Fyu
        dFfunction = tg.dFdy
        H = self.H
        f = self.f
        psi0 = self.y0
        time = self.time
        floquet_mode = self.floquet_mode
        nessopt = self.nessopt
        sparse = self.sparse
        interaction_picture = self.interaction_picture
        dFdu = tg.dFdu
        new_parametrization = self.new_parametrization

        if floquet_mode == 'pt':
            nkpoints = len(H) # This should be generalized eventually.
            dim = H[0].dim
            eps = np.zeros([nkpoints, dim])
            for k in range(nkpoints):
                eps[k, :] = floquet.epsilon3(H[k], f, u, time[-1])
            dfval = tg.dfdepsilon(eps)
            deps = np.zeros((nkpoints, dim, u.shape[0]))
            for k in range(nkpoints):
                deps[k, :, :] = floquet.gradepsilon(H[k], f, u, time[-1])
            val = np.zeros((u.shape[0]))
            for m in range(u.shape[0]):
                val[m] = 0.0
                for k in range(nkpoints):
                    for alpha in range(dim):
                        val[m] = val[m] + dfval[k, alpha] * deps[k, alpha, m]
            return tg.f(eps), val

        elif floquet_mode == 'ness':
            return nessopt.gradG(u)

        # # All the Hamiltonians must be either functions or Qobj's.
        # if H[0].function:
        #      return dgfunction_h_is_function(self, u)

        if len(psi0) > 1:
            multitarget = True
        else:
            multitarget = False

        pulses.pulse_collection_set_parameters(f, u)

        # What are we propagating?
        obj = None
        if psi0[0].type == 'oper':
            if H[0].A is not None:
                obj = 'density'
            else:
                obj = 'propagator'
        else:
            obj = 'state'

        if obj is None:
            raise Exception('Do not know what is the object to propagate')
    
        dim = len(psi0)

        # We propagate the state(s) psi0 to know it in every instant of time
        if sparse:
            result = solvep(solve_method, H, f, psi0, time,
                            returnQoutput = True, interaction_picture = interaction_picture,
                            options = Options(normalize_output = False),
                            comm = comm)
        else:
            result = solvep(solve_method, H, f, psi0, time,
                            returnQoutput = False, interaction_picture = interaction_picture,
                            options = Options(normalize_output = False),
                            comm = comm)

        state_T = [] # States of the system at time T
        for i in range(dim):
            if sparse:
                state_T.append(result[i].states[-1])
            else:
                state_T.append(Qobj(result[i][-1]))

        # Costate(s) of the system at time T. These will be our "initial conditions" for the backpropagation
        costate_T = dFfunction(state_T, u) if multitarget else dFfunction(state_T[0], u)
        if not isinstance(costate_T, list):
            costate_T = [costate_T]

        # Backpropagation
        T = time[time.size - 1]
        tau = T - time #qutip allows backward propagation if an inverted time array is given

        Hclist = []
        for k in range(len(H)):
            if H[k].function:
                Hc = hamiltonians.hamiltonian(H[k].H0, [H[k].V[j] for j in range(len(H[k].V))],
                                              A = H[k].A, 
                                              g = H[k].g)
            else:
                Hc = hamiltonians.hamiltonian(H[k].H0.dag(), [H[k].V[j].dag() for j in range(len(H[k].V))],
                                              A = H[k].A, 
                                              g = H[k].g)
            Hclist.append(Hc)

        if sparse:
            result_costate = solvep(solve_method, Hclist, f, costate_T, tau,
                                    returnQoutput = True, interaction_picture = interaction_picture,
                                    options = Options(normalize_output = False),
                                    comm = comm)
        else:
            result_costate = solvep(solve_method, Hclist, f, costate_T, tau,
                                    returnQoutput = False, interaction_picture = interaction_picture,
                                    options = Options(normalize_output = False),
                                    comm = comm)

        # Calculation of the gradient using the propagated state and the backpropagated costate
        if new_parametrization:
            int_factor = np.zeros([time.size, u.size], dtype = float)
            for c in range(dim):
                int_factor += integration_factor_new(self, u, obj, psi0[c], H[c], result[c], result_costate[c])
        else:
            int_factor = integration_factor(self, u, obj, psi0, H, result, result_costate)

        grad = np.zeros(u.size)
        j = 0
        for k in range(len(f)):
            for m in range(f[k].nu):
                if f[0].type == 'realtime':
                    grad[j] += int_factor[m, j]
                else:
                    grad[j] = 2.0 * sp.integrate.simps(int_factor[:, j], time)
                if dFdu is not None:
                    grad[j] = grad[j] + dFdu(u, j)
                j = j + 1
    
        if multitarget:
            aux=[]
            for c in range (dim):
                if sparse:
                    aux.append(result[c].states[time.size-1])
                else:
                    aux.append(Qobj(result[c][time.size-1]))
            return Ffunction(aux, u), grad
        else:
            if sparse:
                return Ffunction(result[0].states[time.size-1], u), grad
            else:
                return Ffunction(Qobj(result[0][time.size-1]), u), grad


    def check_grad(self, u, m = None, delta = 0.01):
        """A check on the accuracy of the gradient calculation

        It computes one component of the gradient of the target functional using both
        the QOCT expression, and a finite-difference algorithm (the Ridders algorithm).

        Parameters
        ----------
        u : ndarray
            A numpy array holding all the control parameters
        m : int, default = None
            Which gradient component to compute. If None, it will use the one with the
            largest absolute value
        delta : float, default = 0.01
            A parameter determining the starting finite difference in the Ridders
            algorithm.

        Returns
        -------
        float
            The gradient component as computed with the QOCT formula.
        float
            The gradient component as computed with the finite-difference formula.
        float
            An estimation of the gradient accuracy computed with the finite difference formula.
        """
        t0 = clocktime()
        val, grad = self.dgfunc(u)
        t1 = clocktime()
        if rank == 0:
            of.write("Computed the gradient with the QOCT formula. Elapsed time = {} s.\n".format(t1-t0))

        if m is None:
            n = np.argmax(np.abs(grad))
            if rank == 0:
                of.write("Will compute the {} component of the gradient (the largest one).\n".format(n))
                of.flush()
        else:
            n = m
            if rank == 0:
                of.write("Will compute the {} component of the gradient.\n".format(m))
                of.flush()

        def G(x):
            unew = np.copy(u)
            unew[n] = x
            t0 = clocktime()
            gval = self.gfunc(unew)
            t1 = clocktime()
            if rank == 0:
                of.write("G(u) = {} . Elapsed time = {} s.\n".format(gval, t1-t0))
                of.flush()
            return gval
        derivate = math_extra.diff_ridders(G, u[n], delta)
        pulses.pulse_collection_set_parameters(self.f, u)
        return grad[n], derivate[0], derivate[1]


    def maximize(self,
                 maxeval = 100,
                 stopval = None,
                 verbose = False,
                 algorithm = nlopt.LD_LBFGS,
                 local_algorithm = None,
                 upper_bounds = None,
                 lower_bounds = None,
                 tolerance = 1E-06):
        """Performs the QOCT maximization

        This is the main procedure of the class, as it is the one that launches the
        optimization process. There are a number of parameters controlling the way
        in which this optimization is done, that can be controlled here.

        The starting guess parameters for the optimizatio are read from the values
        of the pulses, that were associated to the class object when it was created.

        Parameters
        ----------
        maxeval: int, default = 100
            The maximum number of function evaluations that the optimization algorithm
            is allowed to do. Note that, depending on the algorithm that is used, this 
            may not be strictly enforced.
        stopval: float, default = None
            The optimization will stop if the value of the target function reaches a
            value above stopval.
        verbose: bool, default = False
            The code will output more or less data, depending on the value of this parameter
        algorithm: int, default = nlopt.LD_LBFGS
            The function maximization algorith to be used. qocttools relies on the nlopt
            optimization library:

            https://nlopt.readthedocs.io/en/latest/

            and therefore one can use any of the algorithms that are defined there. See

            https://nlopt.readthedocs.io/en/latest/NLopt_Algorithms/

            for a list. If you include the nlopt module in your driver Python code, you
            can use the parameters that are defined there. Although note that in the case
            of Python, the nomenclature would be ``nlopt.LD_MMA``, ``nlopt.LN_COBYLA``, etc., 
            and not ``NLOPT_LD_MMA``, ``NLOPT_LN_COBYLA``, etc. as it is done when using C.

            In addition, if you set ``algorithm = -1``, the code will not use any of the
            nlopt algorithms, but a fairly basic implementation of Krotov's algorithm.
        local_algorithm: int, default = None
            Some nlopt algorithms use a *global* algorithm and a *local* algorithm. If this
            is the case, you need to specify here the local one (whereas the argument of "algorithm"
            would be the global one).
        upper_bounds: ndarray, default = None
            You may specify upper bound for the parameters -- although this is only possible
            with some of the nlopt algorithms; the code will stop if bounds are requested and
            the algorithm is not capable. See the documetation of nlopt for guidance.
        lower_bounds: ndarray, default = None
            The lower bounds for the parameters.
        tolerance: float, default = 1E-06
            The algorithm will consider that a *successful* optimization has been achieved,
            if a certain tolerance is obtained, characterized by this parameter. This is a tolerance
            imposed on the function vale: when the algorithm is not capable of modifying the function
            value beyond this tolerance, the code will stop and, in principle, a local maximum has
            been found. Note, however, that this local maximum may not be a good one. If that is the
            case, one should change the initial guess, the algorithm, or any of the other choices
            that is done.

        Returns
        -------
        ndarray:
            A numpy array with the optimized control parameters.
        float:
            The value of the local maximum that has been achieved
        int:
            An error code; if it is not zero, something went wrong.

        """
        if algorithm == -1:
            x, optimum, self.convergence, result = krotov.krotov(self.solve_method, self.H[0],
                                  self.f, self.y0[0], self.time, self.O[0], self.tg.S,
                                  alpha = self.tg.alpha,
                                  tolerance = tolerance,
                                  verbose = verbose,
                                  maxeval = maxeval,
                                  interaction_picture = self.interaction_picture)
        else:
            def G(u, grad):
                if grad.size > 0:
                    Gval, grad[:] = self.dgfunc(u)
                else:
                    Gval = self.gfunc(u)
                return Gval
            u = pulses.pulse_collection_get_parameters(self.f)
            x, optimum, self.convergence, result = math_extra.maximize(G, u,
                                       maxeval = maxeval,
                                       stopval = stopval,
                                       verbose = verbose,
                                       algorithm = algorithm,
                                       local_algorithm = local_algorithm,
                                       ftol_abs = tolerance,
                                       upper_bounds = upper_bounds,
                                       lower_bounds = lower_bounds,
                                       equality_constraints = self.equality_constraints,
                                       of = self.of)

        if len(self.convergence) > 0:
            self.nprops = self.convergence[-1][1]
        else:
            self.nprops = 0
        self.optimum = optimum
        return x, optimum, result


def integration_factor_new(opt, u, obj, psi0, H, result, result_costate):
    solve_method = opt.solve_method
    f = opt.f
    time = opt.time
    interaction_picture = opt.interaction_picture
    sparse = opt.sparse

    int_factor = np.zeros([time.size, u.size], dtype = float)

    H0 = H.H0
    V = H.V

    n = len(f)
    npert = len(V)
    nu = u.shape[0]

    if not sparse:
        v = []
        for k in range(len(H.V)):
            v.append(V[k].full())
        diagH0 = np.diag(H0.full())

    z = np.zeros(len(V))
    for i in range(time.size):
        #j = 0
        for k in range(len(V)):
            # We calculate the matrix form of the perturbation V

            if sparse:
                pass # No interaction picture allowed here.
            else:
                if interaction_picture:
                    vp = intoper(v[k], diagH0, time[i])
                else:
                    vp = V[k].full()

            # We compute z, which is the matrix element of the costate and the state with V
            if psi0.type == 'ket' or psi0.type == 'bra':
                if sparse:
                    #z = np.imag( result_costate.states[time.size-1-i].dag() * V[k] * result.states[i]   )
                    z[k] = np.imag( result_costate.states[time.size-1-i].overlap( V[k]*result.states[i] ))
                else:
                    z[k] = np.imag( np.vdot(result_costate[time.size-1-i], np.matmul(vp, result[i])) )
            elif psi0.type == 'oper':
                if obj == 'density':
                    p = np.matmul(vp, result[i]) - np.matmul(result[i], vp)
                else:
                    p = np.matmul(vp, result[i])
                z[k] = np.imag( math_extra.frobenius_product(result_costate[time.size - 1 - i], p ))

        ft = np.array( [f[j].fu(time[i]) for j in range(n)] )
        gradf = []
        for j in range(n):
            gradf.append( f[j].gradf(time[i]) )
        for m in range(nu):
            lm = pulses.pulse_collection_l(f, m)
            jm = pulses.pulse_collection_j(f, m)
            int_factor[i, m] = 0.0
            if f[lm].type == 'realtime':
                if m == jm:
                    int_factor[i, m] += 2.0 * z[lm] * time[1]
                    if (i == 0) or (i == time.shape[0]-1):
                        int_factor[i, m] /= 2.0
            else:
                for j in range(npert):
                    int_factor[i, m] = int_factor[i, m] + gradf[lm][jm] * H.gradg(ft, j, lm) * z[j]

    return int_factor


def integration_factor(opt, u, obj, psi0_, H_, result_, result_costate_):
    solve_method = opt.solve_method
    f = opt.f
    time = opt.time
    interaction_picture = opt.interaction_picture
    sparse = opt.sparse

    int_factor = np.zeros([time.size, u.size], dtype = float)

    ns = len(psi0_)

    for n in range(ns):
        psi0 = psi0_[n]
        H = H_[n]
        result = result_[n]
        result_costate = result_costate_[n]

        H0 = H.H0
        V = H.V

        if H.function:
            args = { "f": [f[l].fu for l in range(len(f))] }
        else:
            if not sparse:
                v = []
                for k in range(len(H.V)):
                    v.append(V[k].full())
                diagH0 = np.diag(H0.full())

        for i in range(time.size):
            j = 0
            for k in range(len(V)):
                # We calculate the matrix form of the perturbation V

                if not H.function:
                    if sparse:
                        pass # No interaction picture allowed here.
                    else:
                        if interaction_picture:
                            vp = intoper(v[k], diagH0, time[i])
                        else:
                            vp = V[k].full()

                # We compute z, which is the matrix element of the costate and the state with V
                if psi0.type == 'ket' or psi0.type == 'bra':
                    if H.function:
                        vp = V[k](time[time.size-1-i], args).full()
                        z = np.imag( np.vdot(result_costate[time.size-1-i], np.matmul(vp, result[i])) )
                    else:
                        if sparse:
                            z = np.imag( result_costate.states[time.size-1-i].overlap( V[k]*result.states[i] ))
                        else:
                            z = np.imag( np.vdot(result_costate[time.size-1-i], np.matmul(vp, result[i])) )
                elif psi0.type == 'oper':
                    if H.function:
                        vp = V[k](time[i], args).full()
                        if obj == 'density':
                            p = np.matmul(vp, result[i]) - np.matmul(result[i], vp)
                        else:
                            p = np.matmul(vp, result[i])
                        z = np.imag( math_extra.frobenius_product(result_costate[time.size - 1 - i], p ))
                    else:
                        if obj == 'density':
                            p = np.matmul(vp, result[i]) - np.matmul(result[i], vp)
                        else:
                            p = np.matmul(vp, result[i])
                        z = np.imag( math_extra.frobenius_product(result_costate[time.size - 1 - i], p ))

                gradf = f[k].gradf(time[i])
                for m in range(f[k].nu):
                    if f[k].type == 'realtime': # In this case, the parameters are the amplitude in each time. 
                        if m == i:
                            int_factor[i, j] += 2.0 * z * time[1]
                            if (i == 0) or (i == time.shape[0]-1):
                                int_factor[i, j] /= 2.0
                    else:
                        int_factor[i, j] += gradf[m] * z
                    j = j + 1 # j runs over all the parameters u, and, unless the pulse is 'realtime', j=m

    return int_factor
