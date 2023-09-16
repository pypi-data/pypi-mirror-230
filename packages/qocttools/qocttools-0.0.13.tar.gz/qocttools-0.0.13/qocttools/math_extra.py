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
import scipy.linalg as la
import sys
import nlopt
from qutip import *
from time import time as clocktime


# The diff_ridders routine is taken from the derivcheck distribution.

# Derivcheck is robust and very sensitive tester for analytic derivatives.
# Copyright (C) 2017 Toon Verstraelen <Toon.Verstraelen@UGent.be>.
#
# This file is part of Derivcheck.
#
# Derivcheck is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Derivcheck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --

def diff_ridders(function, origin, stepsize, con=1.4, safe=2.0, maxiter=15):
    """Estimate first-order derivative with Ridders' finite difference method.

    This implementation is based on the one from the book Numerical Recipes. The code
    is pythonized and no longer using fixed-size arrays. Also, the output of the function
    can be an array.

    Parameters
    ----------
    function : function
        The function to be differentiated.
    origin : float
        The point at which must be differentiated.
    stepsize : float
        The initial step size.
    con : float
        The rate at which the step size is decreased (contracted). Must be larger than
        one.
    safe : float
        The safety check used to terminate the algorithm. If Errors between successive
        orders become larger than ``safe`` times the error on the best estimate, the
        algorithm stop. This happens due to round-off errors.
    maxiter : int
        The maximum number of iterations, equals the maximum number of function calls and
        also the highest polynomial order in the Neville method.

    Returns
    -------
    estimate : float
        The best estimate of the first-order derivative.
    error : float
        The (optimistic) estimate of the error on the derivative.

    """
    if stepsize == 0.0:
        raise ValueError('stepsize must be nonzero.')
    if con <= 1.0:
        raise ValueError('con must be larger than one.')
    if safe <= 1.0:
        raise ValueError('safe must be larger than one.')

    con2 = con*con
    table = [[(
        np.asarray(function(origin + stepsize))
        - np.asarray(function(origin - stepsize))
    )/(2.0*stepsize)]]
    estimate = None
    error = None

    # Loop based on Neville's method.
    # Successive rows in the table will go to smaller stepsizes.
    # Successive columns in the table go to higher orders of extrapolation.
    for i in range(1, maxiter):
        # Reduce step size.
        stepsize /= con
        # First-order approximation at current step size.
        table.append([(
            np.asarray(function(origin + stepsize))
            - np.asarray(function(origin - stepsize))
        )/(2.0*stepsize)])
        # Compute higher-orders
        fac = con2
        for j in range(1, i+1):
            # Compute extrapolations of various orders, requiring no new
            # function evaluations. This is a recursion relation based on
            # Neville's method.
            table[i].append((table[i][j-1]*fac - table[i-1][j-1])/(fac-1.0))
            fac = con2*fac

            # The error strategy is to compare each new extrapolation to one
            # order lower, both at the present stepsize and the previous one:
            current_error = max(abs(table[i][j] - table[i][j-1]).max(),
                                abs(table[i][j] - table[i-1][j-1]).max())

            # If error has decreased, save the improved estimate.
            if error is None or current_error <= error:
                error = current_error
                estimate = table[i][j]

        # If the highest-order estimate is growing larger than the error on the best
        # estimate, the algorithm becomes numerically instable. Time to quit.
        if abs(table[i][i] - table[i-1][i-1]).max() >= safe * error:
            break
        i += 1
    return estimate, error


def timegrid(H0, T, delta):
    """ Generates a time grid in the interval [0, T]"""
    dt0 = delta/H0.norm(norm = 'fro')
    ntsteps_ = T / dt0
    ntsteps = int(ntsteps_)
    time = np.linspace(0, T, ntsteps + (ntsteps+1)%2 )
    return time

def rk4(xi, eom, t, dt):
    k1 = dt * eom(t, xi)
    k2 = dt * eom(t + 0.5*dt, xi + 0.5*k1)
    k3 = dt * eom(t + 0.5*dt, xi + 0.5*k2)
    k4 = dt * eom(t + dt, xi + k3)
    return xi + (1.0/6.0)*(k1 + 2.0*k2 + 2.0*k3 + k4)


def infidelity(U, dmi, dmo):
    """ Returns a measure of the infidelity of a quantum process.

    (...)
    """
    n = len(dmi)
    infs = np.zeros(n)
    infidelity = 0.0
    for j in range(n):
        a = U * dmi[j] * U.dag()
        b = dmo[j]
        dist = ((a-b).dag() * (a-b)).tr()
        infs[j] = dist
        infidelity += dist
    return infidelity/n, np.max(infs)


def dmset(dim, n):
    dm = []
    if n == 2:
        rho1diag = np.zeros(dim)
        for j in range(dim):
            rho1diag[j] = 2*(dim-j) / (dim * (dim+1))
        dm.append( Qobj(np.diag(rho1diag)) )
        dm.append( Qobj(np.ones((dim, dim))/dim) )
    elif n == 3:
        rho1diag = np.zeros(dim)
        for j in range(dim):
            rho1diag[j] = 2*(dim-j) / (dim * (dim+1))
        dm.append( Qobj(np.diag(rho1diag)) )
        dm.append( Qobj(np.ones((dim, dim))/dim) )
        dm.append( qeye(dim)/dim )
    elif n == (dim+1):
        for j in range(dim):
            dm.append( fock_dm(dim, j) )
        dm.append( Qobj(np.ones((dim, dim))/dim) )
    elif n == dim*dim:
        for j in range(dim):
            dm.append(basis(dim, j) * basis(dim, j).dag())
        for j in range(dim):
            for k in range(j+1, dim):
                vec1 = basis(dim, j) + basis(dim, k)
                vec2 = basis(dim, j) + 1j * basis(dim, k)
                dm.append( 0.5 * vec1 * vec1.dag() )
                dm.append( 0.5 * vec2 * vec2.dag() )
    return dm

    
def frobenius_product(A, B):
    """return the Frobenius product between the operators A and B"""
    if type(A) is qutip.qobj.Qobj:
        return (A.dag()*B).tr()
    else:
        return (np.matmul( A.transpose().conjugate(), B)).trace()

uvals = []
maxval = -sys.float_info.max
counter = 0
maxu = 0
nprops = 0
convergence = []
rescode =  { nlopt.SUCCESS: "Success", 
             nlopt.STOPVAL_REACHED: "Stop value reached",
             nlopt.FTOL_REACHED: "Function tolerance reached",
             nlopt.XTOL_REACHED: "Value tolerance reached",
             nlopt.MAXEVAL_REACHED: "Maximum evaluations reached",
             nlopt.MAXTIME_REACHED: "Maximum execution time reached" }

def maximize(func, u0, 
             ftol_abs = 1.0e-6, 
             maxeval = 10,
             stopval = None,
             algorithm = nlopt.LD_LBFGS,
             local_algorithm = None,
             upper_bounds = None,
             lower_bounds = None,
             equality_constraints = None,
             verbose = False,
             of = sys.stdout):
    global maxval
    global counter
    global maxu
    global uvals
    global nprops
    global convergence
    maxval = -sys.float_info.max
    counter = 0
    maxu = 0
    uvals = []
    nprops = 0
    convergence = []
    def wrapper_function(u, grad):
        global uvals
        global maxval
        global counter
        global maxu
        global convergence
        global nprops
        t0 = clocktime()
        uvals.append(u.copy())
        val = func(u, grad)
        if grad.size > 0:
            nprops = nprops + 2
        else:
            nprops = nprops + 1
        if val > maxval:
            maxval = val
            u0 = u.copy()
            maxu = counter
        t1 = clocktime()
        if verbose and of is not None:
            of.write("{:d} {:f} ({:f} s)\n".format(counter, val, t1-t0))
            of.flush()
        convergence.append([counter, nprops, val, t1-t0])
        counter = counter + 1
        return val
    dim = u0.size
    if local_algorithm == None:
        opt = nlopt.opt(algorithm, dim)
    else:
        local_opt = nlopt.opt(local_algorithm, dim)
        local_opt.set_maxeval(maxeval)
        local_opt.set_ftol_abs(ftol_abs)
        opt = nlopt.opt(algorithm, dim)
        opt.set_local_optimizer(local_opt)
    opt.set_max_objective(wrapper_function)
    opt.set_ftol_abs(ftol_abs)
    opt.set_maxeval(maxeval)
    if upper_bounds is not None:
        opt.set_upper_bounds(upper_bounds)
    if lower_bounds is not None:
        opt.set_lower_bounds(lower_bounds)
    if equality_constraints is not None:
        for constraint in equality_constraints:
            opt.add_equality_constraint(constraint[0], constraint[1])
    if stopval is not None:
        opt.set_stopval(stopval)
    try:
        x = opt.optimize(u0)
    except RuntimeError:
        if of is not None:
            of.write("Runtime error\n")
        result = opt.last_optimize_result()
        x = uvals[maxu]
        optimum = maxval
    except ValueError:
        if of is not None:
            of.write("Invalid arguments\n")
        result = opt.last_optimize_result()
        x = u0.copy()
        optimum = maxval
    except MemoryError:
        if of is not None:
            of.write("Memory error\n")
        result = opt.last_optimize_result()
        x = uvals[maxu]
        optimum = maxval
    except nlopt.RoundoffLimited:
        if of is not None:
            of.write("Round-off error\n")
        result = opt.last_optimize_result()
        x = uvals[maxu]
        optimum = maxval
    except nlopt.ForcedStop:
        if of is not None:
            of.write("Forced stop\n")
        result = opt.last_optimize_result()
        x = uvals[maxu]
        optimum = maxval
    except:
        if of is not None:
            of.write("Unknown error {}".format(sys.exc_info()[0]))
        result = opt.last_optimize_result()
        x = uvals[maxu]
        optimum = maxval
    else:
        result = opt.last_optimize_result()
        x = uvals[maxu]
        optimum = maxval
        if verbose and of is not None: of.write ("Successfull termination with result code = {:d}\n".format(result))
        if verbose and of is not None: of.write('("{}")\n'.format(rescode[result]))
    return x, optimum, convergence, result

