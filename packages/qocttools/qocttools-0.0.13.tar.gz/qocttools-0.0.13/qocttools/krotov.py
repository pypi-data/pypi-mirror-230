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

"""This module implements the Krotov's algorithm :cite:p:`Reich2012`.

The current implementation is rather restrictive, and it can only
be applied when:

1. The state is a wavefunction (no density matrices or evolution
   operators).

2. The Hamiltonian is linear in the control field, with only one
   perturbation, i.e. it has the form:

   .. math::
      H(t) = H_0 + f(t) V

3. The pulse is parametrized in real time.

4. The only allowed propagators are RK4 and cfmagnus4.

5. The target has the form:

   .. math::
      F(\\psi(T)) = \\langle \\psi(T)\\vert O  \\vert\\psi(T)\\rangle 
      - \\int_0^T\\!\\!{\\rm d}t\\; \\frac{\\alpha}{S(t)}f^2(t)

   i.e. the objective is to maximize the expectation value of some
   operator :math:`O`, and we have to add a penalty function, depending
   on the parameter :math:`\\alpha > 0` and on the weigth function :math:`S(t)`,
   that can be supplied by the user.


The algorithm that is implemented here is the following:

1. :math:`k = 0`; :math:`f^{(0)}` is the initial guess pulse. Solve:

   .. math::
      i\\frac{\\partial}{\\partial t} \\psi^{(0)}(t) = [H_0 + f^{(0)}V(t)]\\psi^{0}(t)
   .. math::
      \\psi^{(0)}(0) = \\psi_0
   .. math::
      i\\frac{\\partial}{\\partial t} \\chi^{(0)}(t) = [H_0 + f^{(0)}V(t)]\\chi^{0}(t)
   .. math::
      \\chi^{(0)}(T) = O\\psi^{(0)}(T)

2. For :math:`k=1,\dots` until convergence:

   .. math::
      i\\frac{\\partial}{\\partial t} \\psi^{(k)}(t) = 
      [H_0 + \\frac{S(t)}{\\alpha} 
      {\\rm Im} [\\langle \\chi^{(k-1)}\\vert V \\vert\\psi^{(k)}(t)\\rangle ]\\psi^{(k)}(t)
   .. math::
      \\psi^{(k)}(0) = \\psi_0
   .. math::
      f^{(k)}(t) = \\frac{S(t)}{\\alpha} {\\rm Im} 
      [\\langle \\chi^{(k-1)}\\vert V \\vert\\psi^{(k)}(t)\\rangle ]
   .. math::
      i\\frac{\\partial}{\\partial t} \\chi^{(k)}(t) = [H_0 + f^{(k)}V(t)]\\chi^{k}(t)
   .. math::
      \\chi^{(k)}(T) = O\\psi^{(k)}(T)


Convergence is checked by comparing :math:`f^{(k+1)}` with :math:`f^{(k)}`.

"""

import numpy as np
import scipy as sp
import nlopt
import math
from qutip import *
import qocttools.math_extra as math_extra
import qocttools.pulses as pulses
import qocttools.solvers as solvers
from time import time as clocktime


convergence = []

def krotov(solve_method, H, f_initial, psi0, times, O, S,
           alpha = 2.0, 
           tolerance = 1E-03, 
           verbose = False, 
           maxeval = 100, 
           interaction_picture = False):
    """This is the main function on the module.

    It performs the optimization and returns the optimal value of the
    functional, the optimal parameters, and a code signaling the success
    or failure of the process.

    Parameters
    ----------
    solve_method: string
        string indicating the propagation method
    H: hamiltonian
        Hamiltonian
    f_initial: pulse
        pulse to be used as initial guess (on output, it will contain the
        optimized pulse.
    psi0: Qobj
        initial state.
    time: ndarray
        array that contains each time step.
    O: Qobj
        The target operator that we want to optimize.
    S: function
        The penalty function :math:`S(t)`
    alpha: float, default = 2.0
        Penalty factor :math:`alpha`
    tolerance: float, default = 1.0e-3
        Precision for the algorithm
    verbose: bool, default = True
        Whether or not the algorithm will print info to stdout
    maxeval: int, default = 100
        The maximum number of iterations that will be done before the algorithm stops.
    interaction_picture: bool, default = False
        The code will transform the equations to the interaction picture if this is set to True

    Returns
    -------
    ndarray:
        The optimal parameters
    float:
        The optimal target function value
    list:
        A list with data about the convergence history of the algorith
    int:
        An integer flag about the outcome: zero if successful, non-zero otherwise
    """
    global convergence
    H0 = H.H0
    V = H.V
    times_inverted = times[::-1]
    f = []
    for ft in f_initial:
        f.append( check_pulse(ft, times) )
    dim = H0.shape[0]
    obj = psi0.type
    if verbose:  
        print('Object to propagate', obj)
        print('Tolerance', tolerance)
        print('Alpha', alpha)


    # We do iteration zero, which is special.    
    counter = 0
    nprops = 0
    t0 = clocktime()
    psi = solvers.solve(solve_method, H, f, psi0, times, 
                        returnQoutput = False, interaction_picture = interaction_picture)
    psi_final = psi[-1]
    gvalue, pvalue, tvalue = compute_target_function(obj, f, psi_final, times, O, S, alpha, dim)
    chi = coestate_eq(solve_method, H, f, psi_final, times_inverted, O, obj,
                      interaction_picture = interaction_picture)
    t1 = clocktime()
    nprops = nprops + 2
    convergence.append([counter, nprops, tvalue, t1-t0])
    if verbose: write_status(gvalue, pvalue, tvalue, t0, t1, counter)

    old_pulse = f
    counter = 1
    t0 = clocktime()
    psi_final, f = state_eq(solve_method, H0, V, f, chi, psi0, times, S,
                            alpha = alpha,
                            interaction_picture = interaction_picture)
    gvalue, pvalue, tvalue = compute_target_function(obj, f, psi_final, times, O, S, alpha, dim)
    chi = coestate_eq(solve_method, H, f, psi_final, times_inverted, O, obj,
                      interaction_picture = interaction_picture)
    t1 = clocktime()
    nprops = nprops + 2
    convergence.append([counter, nprops, tvalue, t1-t0])
    if verbose: write_status (gvalue, pvalue, tvalue, t0, t1, counter)

    counter=1
    flag=0
    t0 = clocktime()
    while not have_converged(old_pulse, f, times, epsilon = tolerance):
        t0  = clocktime()
        old_pulse = f
        psi_final, f = state_eq(solve_method, H0, V, f, chi, psi0, times, S,
                                alpha = alpha,
                                interaction_picture = interaction_picture)
        gvalue, pvalue, tvalue = compute_target_function(obj, f, psi_final, times, O, S, alpha, dim)
        chi = coestate_eq(solve_method, H, f, psi_final, times_inverted, O, obj,
                          interaction_picture = interaction_picture)
        t1 = clocktime()
        nprops = nprops + 2
        convergence.append([counter, nprops, tvalue, t1-t0])
        if verbose: write_status(gvalue, pvalue, tvalue, t0, t1, counter)
        counter = counter + 1
        if counter+1 >= maxeval:
            print('Maximun number of iterations reached')
            flag=1
            break
    
    if verbose: print("End of optimization")
    gvalue, pvalue, tvalue = compute_target_function(obj, f, psi_final, times, O, S, alpha, dim)    
    #return f.u, gvalue, convergence, flag
    return pulses.pulse_collection_get_parameters(f), gvalue, convergence, flag


def state_eq(solve_method, H0, V, f, chi, psi0, times, S, alpha = 2,
             interaction_picture = False):
    """ This function solves the non-linear Schrödinger equation that is part of
    Krotov's algorithm.
    """
    if solve_method == 'rk4':
        return rk4_nonlinear(H0, V, f, chi, Qobj(psi0), times, S, alpha = alpha, 
                             interaction_picture = interaction_picture)
    elif solve_method == 'cfmagnus4':
        return cfmagnus4_nonlinear(H0, V, f, chi, Qobj(psi0), times, S, alpha = 2,
                                   interaction_picture = interaction_picture)#Function in progress


def compute_target_function(obj, f, psi_final, times, O, S, alpha, dim):
    if obj == 'oper':
        U_target = O.full()
        gvalue = np.matmul(U_target.conj().T, psi_final).trace()
        gvalue = np.absolute(gvalue)**2 / (dim**2)
    else:
        gvalue = abs(expect(O,Qobj(psi_final)))
    #pvalue = - alpha * sp.integrate.simps( f.fu(times[1:-1]) * f.fu(times[1:-1]) / S(times[1:-1]), times[1:-1] )
    pvalue = 0.0
    for ft in f:
        pvalue = pvalue - alpha * sp.integrate.simps( ft.fu(times[1:-1]) * ft.fu(times[1:-1]) / S(times[1:-1]), times[1:-1] )
    tvalue = gvalue + pvalue
    return gvalue, pvalue, tvalue


def write_status(gvalue, pvalue, tvalue, t0, t1, counter):
    print("{:d} gvalue = {:f}\tpvalue = {:f}\ttvalue = {:f} ({:f} s)".format(counter, gvalue, pvalue, tvalue, t1-t0))


def coestate_eq(solve_method, H, f, psiF, times, O, obj, interaction_picture = False):
    """This function calculate the coestate equation with the final condition described by

    .. math::
       \\vert\\chi(T)\\rangle = O\\vert \\Psi(t=T)\\rangle

    In the case of having a state propagating, and

    .. math::                           
       \\vert B(T)\\rangle = Tr [U(T)+*O]*O/d^2

    in the case of having an operator propagating.

    The main idea is to solve it as an linear schrödinger equation but
    *backwards*, so we have to take care of the time and the pulse in order to
    make this correctly (with *realtime* parametrized pulses only is needed to 
    invert the time).
    In principle this should work with any solve_method: rk4, cfm2 or cmf4.
    """
    #Calculating the "initial" coestate (actually the final)
    H0 = H.H0
    v = H.V
    if obj == 'oper':
        dim = H0.shape[0]
        U_target = O.full()
        
        #|B(T)>= Tr[U(T)*U_targ^H]*U_targ/d^2
        ini = U_target * np.matmul(U_target.conj().T, psiF).trace() /dim/dim
        #ini = ini * 2
        ini = Qobj(ini)
    
    else:
        #|Coestate(t=T)>=O|ψ(t=T)>  
        ini = O*Qobj(psiF)
        

    #Solving the equation "backwards"
    coestate=solvers.solve(solve_method, H, f, ini, times,
                           returnQoutput = False,
                           interaction_picture = interaction_picture)

    #Returning the coestate "fordwards", so we can operate with it directly
    return coestate[::-1]


def have_converged (old, new, times, epsilon = 1E-06):
    """ This function checks if the algorithm have converged enough. 

    The idea is to check every time of the pulse.

    Parameters
    ----------
    old:
        The pulse before solving the non-linear schrodinger
    new:
        The pulse after solving the non-linear schrodinger
    epsilon:
        The tolerance we have so we can say the pulse have converged enough

    Returns
    -------
    A boolean which is 'True' if every amplitude have converged, and is 'False' if any
    of the amplitudes have not converged enough
    """
    return False
    for i in range(times.shape[0]):
        if np.abs(old.fu(times[i])-new.fu(times[i]))>epsilon :
            return False
        if new.fu(times[i]) is np.nan:
            raise Exception('Pulse divergence')
        
    return True


def check_pulse (f, times):
    """ This function checks if the pulse parametrization is *realtime*.

    If it is not, it convert the pulse
    into *realtime* parametrization.
    """
    if f.type =='realtime':
        return f
    
    elif f.type =='fourier':
        ut = f.fu(times)
        ft = pulses.pulse("realtime", times[-1], u = ut)
        print('Initial pulse is in Fourier parametrization, changed into Realtime.')
        return ft

    elif f.type =='user_defined':
        ut = f.fu(times)
        ft = pulses.pulse("realtime", times[-1], u = ut)
        print('Initial pulse is in user_defined parametrization, changed into Realtime.')
        return ft

    else:
        raise Exception('The pulse is not well defined')


def rk4_nonlinear(H0, V, f, chi, psi0, times, S, alpha = 2,
                  interaction_picture = False):
    """ This function solves the nonlinear schordinger equation using rk4 as the integrator algorithm.

    It is a modification of the function rk4solver in the solvers module of 
    qocttools, so it can solve a slightly different equation and it can return the new state 
    and the new pulse.
    """
    if type(H0) is not qutip.qobj.Qobj:
        raise TypeError

    #u_new=[]
    u_new = np.zeros((len(f), times.size))
    h0 = H0.full()
    #v = V.full()
    v = [x.full() for x in V]
    dt = times[1]-times[0]
    dim = H0.shape[0]

    #What are we propagating?
    if psi0.type == 'oper':
        psi = psi0.full()
        y = np.zeros((2, dim, dim), dtype = complex)
        y[0] = psi
        y[1] = chi[0].copy()
        obj = 'oper'
    else:
        psi = psi0.full()[:, 0]
        y = np.zeros((2, dim), dtype = complex)
        y[0] = psi
        y[1] = chi[0].copy()
        obj = 'ket'


    def nlf(t, y):
        psi = y[0]
        chi = y[1]
        fy = y.copy()
        if interaction_picture:
            htpsi = np.zeros_like(h0)
            htchi = np.zeros_like(h0)
            for k in range(len(f)):
                vi = solvers.intoper(v[k], np.diag(h0), t)
                if obj == 'ket' :
                    V_Matrix_Element = np.vdot(chi, np.matmul(vi, psi))
                elif obj == 'oper':
                    V_Matrix_Element = np.matmul(chi.conj().T, np.matmul(vi, psi)).trace()
                htpsi = htpsi + (S(t) * V_Matrix_Element.imag / alpha) * vi
                htchi = htchi + f[k].fu(t) * vi
            fpsi = - 1j * np.matmul(htpsi, psi)
            fchi = - 1j * np.matmul(htchi, chi)
        else:
            htpsi = h0.copy()
            htchi = h0.copy()
            #for vi in v:
            for k in range(len(f)):
                if obj == 'ket' :
                    V_Matrix_Element = np.vdot(chi, np.matmul(v[k], psi))
                elif obj == 'oper':
                    V_Matrix_Element = np.matmul(chi.conj().T, np.matmul(v[k], psi)).trace()
                htpsi = htpsi + (S(t) * V_Matrix_Element.imag / alpha) * v[k]
                htchi = htchi + f[k].fu(t) * v[k]
            fpsi = - 1j * np.matmul(htpsi, psi)
            fchi = - 1j * np.matmul(htchi, chi)

        fy[0] = fpsi
        fy[1] = fchi
        return fy

    # u_new.append(S(0) * V_Matrix_Element.imag / alpha)
    for k in range(len(f)):
        if obj == 'ket' :
            V_Matrix_Element = np.vdot(chi[0], np.matmul(v[k], psi))
        elif obj == 'oper':
            V_Matrix_Element = np.matmul(chi[0].conj().T, np.matmul(v[k], psi)).trace()
        u_new[k, 0] = S(0) * V_Matrix_Element.imag / alpha

    for j in range(times.size-1):
        y = math_extra.rk4(y, nlf, times[j], dt)

        psi_ = y[0]
        chi_ = y[1]

        for k in range(len(f)):
            if interaction_picture:
                vi = solvers.intoper(v[k], np.diag(h0), times[j+1])
            else:
                vi = v[k].copy()
            if obj == 'ket' :
                V_Matrix_Element = np.vdot(chi_, np.matmul(vi, psi_))
            elif obj == 'oper':
                V_Matrix_Element = np.matmul(chi_.conj().T, np.matmul(vi, psi_)).trace()
            u_new[k, j+1] = S(times[j+1]) * V_Matrix_Element.imag / alpha
    
    #Creating the new pulse
    #f_new = pulses.pulse("realtime", times[-1], u = np.array(u_new))
    f_new = []
    for k in range(len(f)):
        f_new.append( pulses.pulse("realtime", times[-1], u = u_new[k, :]) )

    return psi_, f_new

    
def cfmagnus4_nonlinear(H0, V, f, chi, psi0, time, S, alpha = 2,
                        interaction_picture = False, cops = None):
    """ This function solves the nonlinear schordinger equation using cfmagnus4 as the integrator algorithm.
    """
    if type(H0) is not qutip.qobj.Qobj:
        raise TypeError

    u_new = []
    h0 = H0.full()
    dt = time[1]-time[0]
    dim = H0.shape[0]

    if psi0.type == 'oper':
        psi = psi0.full()
        obj = 'oper'
    else:
        psi = psi0.full()[:, 0]
        obj = 'ket'

    a1 = (3.0-2.0*np.sqrt(3.0))/12.0
    a2 = (3.0+2.0*np.sqrt(3.0))/12.0
    c1 = 0.5 - np.sqrt(3.0)/6.0
    c2 = 0.5 + np.sqrt(3.0)/6.0

    if obj == 'ket':
        V_Matrix_Element = np.vdot(chi[0], np.matmul(V.full(), psi))
   
    else:
        V_Matrix_Element = np.matmul(chi[0].conjugate().T, np.matmul(V.full(), psi)).trace()

    u_new.append(S(0) * V_Matrix_Element.imag / alpha)
    for j in range(time.size-1):
        t1 = time[j] + c1*dt
        t2 = time[j] + c2*dt
        if interaction_picture:
            # We will assume that H0 is diagonal on entry.
            M1 = np.zeros_like(h0)
            M2 = np.zeros_like(h0)
            #for k in range(len(V)):
            vi1 = solvers.intoper(V.full(), np.diag(h0), t1)
            vi2 = solvers.intoper(V.full(), np.diag(h0), t2)
            
            if obj == 'ket':
                V_Matrix_Element_1 = np.vdot(chi[j], np.matmul(vi1, psi))
                V_Matrix_Element_2 = np.vdot(chi[j], np.matmul(vi2, psi))

            else:
                V_Matrix_Element_1 = np.matmul(chi[j].conjugate().T, np.matmul(vi1, psi)).trace()
                V_Matrix_Element_2 = np.matmul(chi[j].conjugate().T, np.matmul(vi2, psi)).trace()

            #u_new.append(S(time[t])*)

            M1 = M1 + a1 * S(t1) * V_Matrix_Element_1.imag / alpha * vi1 + a2 * S(t2) * V_Matrix_Element_2.imag / alpha * vi2
            M2 = M2 + a2 * S(t1) * V_Matrix_Element_1.imag / alpha * vi1 + a1 * S(t2) * V_Matrix_Element_2.imag / alpha * vi2


        else:
            M1 = (a1 + a2) * h0
            M2 = (a1 + a2) * h0
            #for k in range(len(V)):
            
            M1 = M1 + a1 * S(t1) * V_Matrix_Element.imag / alpha * V.full() + a2 * S(t2) * V_Matrix_Element.imag / alpha * V.full()
            M2 = M2 + a2 * S(t1) * V_Matrix_Element.imag / alpha * V.full() + a1 * S(t2) * V_Matrix_Element.imag / alpha * V.full()

        M = M2
        psi = solvers.exppsi(2*M, cops, dt/2, psi)
        M = M1
        psi = solvers.exppsi(2*M, cops, dt/2, psi)

        #Saving Values
        if obj == 'ket':
            V_Matrix_Element = np.vdot(chi[j+1], np.matmul(V.full(), psi))
            
        else:
            V_Matrix_Element = np.matmul(chi[j+1].conjugate().T, np.matmul(V.full(), psi)).trace()
        
        u_new.append(S(time[j+1]) *V_Matrix_Element.imag / alpha)



    #Creating the new pulse
    f_new=pulses.pulse("realtime", time[-1], u = np.array(u_new))
    
    return psi, f_new


def coestate_interpolator(chi, times, coestate_flag, solve_method):
    """ This function interpolates the value of the coestate.

    In this way, we can solve properly the non-linear Schrodinger equation with the rk4 and cfmagnus4 integrators.
    This function returns the value of the coestate in the time that´s required
    """
    #We separate coestate_flag into int number (i), and decimal number (flag)
    flag, i = math.modf(coestate_flag)
    i=int(i)
    #If coestate_flag is an int number it´s not needed to interpolate
    if flag == 0:
        return chi[i]
    
    else:
        #Lets see if it´s solve by rk4 or cfmagnus4
        if solve_method == 'rk4':
            #If it´s rk4 and coestate_flag is not an int, neccesary we are in the case were we need to get the coestate in t+dt*0,5
            t_obj=times[i]+(times[i+1]-times[i])/2
            return chi[i]+(chi[i+1]-chi[i])/(times[i+1]-times[i])*(t_obj-times[i])

        elif solve_method == 'cfmagnus4':  
            return
        else:
            raise Exception('Don´t know propagation method')
