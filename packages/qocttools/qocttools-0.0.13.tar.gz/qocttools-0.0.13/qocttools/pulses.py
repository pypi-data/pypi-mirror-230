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

""" This module includes the 'pulse' class, that is used to contain
the time-dependent real function that is used to define the perturbation
part of the Hamiltonian.

Also, it contains definitions of 'typical' pulse forms, such as the
pi-pulse.
"""

import numpy as np
import scipy as sp
import qocttools.cythonfuncs as cyt
import qutip as qt



class pulse:
    """Definition of a class to hold control functions, a.k.a. pulses.

    The "pulses" are real time-dependent functions defined in the interval
    :math:`[0, T]`, defined as functions :math:`f(u_1, u_2, ..., u_P, T)`, where 
    :math:`u = u_1, ..., u_P` are parameters (the *control parameters*). These pulses
    are the control functions used by qocttools.

    Depending on the `type` of the pulse, the parametrized form of these pulses is:

    1. fourier

       In this case, the pulse is a simple Fourier expansion:

       .. math::
          f(u, t) = \\frac{u_0}{\sqrt{T}} + \\frac{2}{\\sqrt{T}}
          \\sum_{i=1}^M \\left[ u_{2i}\\cos(\\omega_i t) + u_{2i-1}\\sin(\\omega_i t)\\right]

       The pulse therfore requires an odd number of parameters, :math:`P = 2M + 1`. The
       frequencies are :math:`\omega_i = i\omega_0 = i\\frac{2\\pi}{T}` for :math:`i=1, \\dots, M`.
       The cutoff M will be decided by the number of parameters that are passed when
       initializing the object. Therefore, in order to initialize a Fourier pulse with :math:`M=5`:

       .. code-block:: python

          M = 5
          u = np.zeros(2*M+1)
          f = pulses.pulse('fourier', T, u)

    2. bound_fourier

       This is a modification of the normal Fourier expansion, that ensures that the absolute value
       of the pulse is never larger than a certain bound. The definition is:

       .. math::
          f(u, t) = \\Phi(g(u, t))

       where :math:`g(u, t)` is a normal Fourier expansion as the one given above, and:

       .. math::
          \\Phi(x) = \\frac{\\kappa x}{\\kappa+\\vert x\\vert}

       The value of :math:`\kappa` must be supplied by the `bound` argument:

       .. code-block:: python

          M = 5
          kappa = 3.0
          u = np.zeros(2*M+1)
          f = pulses.pulse('fourier', T, u, bound = kappa)


    3. realtime

       In this case, the pulse is given by a piecewise-constant function. If the time
       discretization is given by :math:`t_0 = 0, t_1 = \Delta t, t_2 = 2\Delta t,\dots,t_{N-1}=(N-1)\Delta t = T`,
       then the function is given by:

       .. math::
          f(u, t) = \\sum_{i=0}^{N-1} u_i {\\bf 1}_{[t_i,t_{i+1}]}

       where :math:`{\\bf 1}_{[t_i,t_{i+1}]}` is the indicator function in the interval
       :math:`[t_i,t_{i+1}]`

       The number :math:`N` is given by the number of elements in the numpy array `u` used
       when creating th epulse, and therefore :math:`\Delta t` is computed accordingly, given :math:`T`.

       In fact, although still experimental and therefore undocumented, one can also use some interpolating
       function to obtain the values in the interior of the intervals, so that the function is smooth


    4. enveloped_fourier

       This is a normal Fourier expansion, but multiplied by a function :math:`S(t)`:

       .. math::
          f(u, t) = S(t) g_{\\rm Fourier}(u, t)

       The function :math:`S(t)` must be passed to the function :meth:`assign_envelope_function`,
       and is simply a function of time:

       .. code-block:: python

          def S(t):
              return np.sin(t)
          f = pulses.pulse('enveloped_fourier', T, u, bound = kappa)
          f.assign_envelope_function(S)

    5. user_defined

       This is the most general possibility: the user defines the pulse as a
       a python function. The function must be communicated to the pulse object
       using the :meth:`assign_user_defined_function`. One should also define
       a function with the derivatives of the function with respect to the parameters.
       Here is an example using only three of parameters:

       .. math::

          f(u, t) = u_0 \\cos(u_1 t+ u_2)

       .. code-block:: python

          def fu(t, u):
              return u[0] * np.cos(u[1]*t + u[2])
          def dfdu(t, u, m):
              # m is an integer that signals what is the parameter with respect to which the 
              # derivative is taken
              if m == 0:
                  return np.cos(u[1]*t + u[2])
              elif m == 1:
                  return -u[0] * t * np.sin(u[1]*t + u[2])
              elif m == 2:
                  return -u[0] * np.sin(u[1]*t + u[2])
          u = np.array([1.0, 0.5, 0.0])
          f = pulses.pulse('user_defined', T, u)
          f.assign_user_defined_function(fu, dfdu)

       If one is going to use a gradient-less QOCT algorithm, there is no need to define
       the derivative function, and one can just pass the None value.


    Parameters
    ----------
    type : string
        The type of function: 'fourier', 'bound_fourier', 'realtime', 'user_defined', or
        'enveloped' fourier
    T : float
        The duration of the pulse
    u : ndarray
        The parameters
    bound : float, default = None
        For the 'bound_fourier' type, the bound


    Attributes
    ----------
    type : string
    T : float
    u : ndarray
    nu : int
    bound : float

    """
    def __init__(self, type, T, u, bound = None):
        self.type = type
        self.T = T
        self.set_parameters(u)
        self.nu = u.shape[0]
        self.constraints = []
        self.bound = bound

    def print(self, filename):
        """ Prints a pulse to a file called 'filename'.

        It does not print the possible constraint functions.

        Parameters
        ----------
        filename : str
            Name of the file where the info about the pulse is written.
        """
        f = open(filename, 'w')
        f.write(self.type+'\n')
        f.write('{}\n'.format(self.T))
        f.write('{}\n'.format(self.nu))
        for j in range(self.nu):
            f.write(' {} '.format(self.u[j]))
        f.write('\n')
        f.write('{}\n'.format(self.bound))
        f.write('{}\n'.format(len(self.constraints)))
        f.close()

    def set_constraint(self, which, val = 0.0):
        """ Sets a constraint on the shape of the pulse

        """
        if which == 'zero_boundaries':
            def g(u, grad):
                M = len(u) // 2
                if grad.size > 0:
                    gu = 0.5 * u[0]
                    grad[:] = 0.0
                    grad[0] = 0.5
                    for k in range(1, M+1):
                        gu = gu + u[2*k]
                        grad[2*k] = 1.0
                else:
                    gu = 0.0
                    for k in range(1, M+1):
                        gu = gu + u[2*k]
                return gu
            self.constraints.append(g)
        elif which == 'boundaries_values':
            def g(u, grad):
                M = len(u) // 2
                if grad.size > 0:
                    gu = u[0]
                    grad[:] = 0.0
                    grad[0] = 1.0
                    for k in range(1, M+1):
                        gu = gu + 2.0 * u[2*k]
                        grad[2*k] = 2.0
                else:
                    gu = u[0]
                    for k in range(1, M+1):
                        gu = gu + 2.0 * u[2*k]
                return gu - val * np.sqrt(self.T)
            self.constraints.append(g)
        elif which == 'zero_average':
            def g(u, grad):
                if grad.size > 0:
                    gu = u[0]
                    grad[0] = 1.0
                    grad[1:] = 0.0
                else:
                    gu = u[0]
                return gu
            self.constraints.append(g)
        else:
            print("Unknown constraint: {}.".format(which))
        return None

    def set_parameters(self, u):
        """Sets the parameters :math:`u = u_1, \dots, u_P` on the pulse.

        """
        self.u = u.copy()
        self.nu = u.shape[0]
        if self.type == 'realtime':
            times = np.linspace(0.0, self.T, u.shape[0])
            self.interpolator = sp.interpolate.interp1d(times, u, fill_value = 'extrapolate')

    def f(self, t, args):
        """The value of the pulse at time t

        """
        return self.fu(t)

    def assign_user_defined_function(self, fu, dfu):
        """For user-defined functions, set the function definition, and the definition of the gradient of the function.

        """
        self.user_defined_function = fu
        self.user_defined_dfunction = dfu


    def assign_envelope_function(self, efunc):
        """Sets the envelope function that may be multiplied by the pulse itself.

        """
        self.user_envelope_function = efunc


    def envelope(self, t):
        """Returns the value of the envelope function at time t

        """
        if self.type == 'enveloped_fourier' :
            if isinstance(t, float):
                return cyt.fourierexpansion(t, self.T, self.nu, self.u)
            else:
                return f_FE(t, self.T, self.u)
        else:
            return None


    def fu(self, t, u = None):
        """Returns the value of pulse at time t

        Optionally, one can pass the control parameters u and in that way those
        are updated before the computation.
        """
        if isinstance(t, int):
            t = float(t)
        if u is not None:
            self.u = u.copy()
        if self.type == 'fourier' :
            return cyt.fourierexpansion(t, self.T, self.nu, self.u)
        elif self.type == 'realtime' :
            return self.interpolator(t)
        elif self.type == 'user_defined' :
            return self.user_defined_function(t, self.u)
        elif self.type == 'enveloped_fourier' :
            return cyt.fourierexpansion(t, self.T, self.nu, self.u) * self.user_envelope_function(t)
        elif self.type == 'bound_fourier' :
            ft = cyt.fourierexpansion(t, self.T, self.nu, self.u)
            return self.bound * ft / (self.bound + np.abs(ft))


    def gradf(self, t):
        """Grdient of the function at time t

        "Gradient of the function" means the gradient with respect to all
        the control parameters.
        """
        res = np.zeros(self.nu)
        if self.type == 'fourier':
            res = cyt.gradfourierexpansion(t, self.T, self.nu, self.u)
        elif self.type == 'realtime':
            for m in range(self.nu):
                res[m] = f_realtime_der(t, self.T, self.u, m)
        elif self.type == 'user_defined' :
            for m in range(self.nu):
                res[m] = self.user_defined_dfunction(t, self.u, m)
        elif self.type == 'enveloped_fourier' :
            res = cyt.dfourierexpansion(t, self.T, self.nu, self.u) * self.user_envelope_function(t)
        elif self.type == 'bound_fourier' :
            ft = cyt.fourierexpansion(t, self.T, self.nu, self.u)
            dft = cyt.gradfourierexpansion(t, self.T, self.nu, self.u)
            res = self.bound**2 * dft / ( self.bound + np.abs(ft) )**2
        return res


    def dfu(self, t, m, u = None):
        """Derivative of the pulse with respect to the m-th parameter, at time t

        """
        if u is not None:
            self.u = u.copy()
        if self.type == 'fourier' :
            return cyt.dfourierexpansion(t, self.T, self.nu, self.u, m)
        elif self.type == 'realtime' :
            return f_realtime_der(t, self.T, self.u, m)
        elif self.type == 'user_defined' :
            return self.user_defined_dfunction(t, self.u, m)
        elif self.type == 'enveloped_fourier' :
            return cyt.dfourierexpansion(t, self.T, self.nu, self.u, m) * self.user_envelope_function(t)
        elif self.type == 'bound_fourier' :
            dft = cyt.dfourierexpansion(t, self.T, self.nu, self.u, m)
            ft = cyt.fourierexpansion(t, self.T, self.nu, self.u)
            return self.bound**2 * dft / ( self.bound + np.abs(ft) )**2


    def fitparams(self, fref, times, u0):
        """Fit the parameters of a function to the best mpossible much wrt a reference function

        """
        def fitfunction(t, *u):
            return self.fu(t, np.array(u))
        optu, cov = sp.optimize.curve_fit(fitfunction, times, fref, p0 = u0)
        return optu


    def fw(self, t, u, w = None, explicit_formula = False):
        """Fourier transform of the pulse

        """
        if w is not None:
            if not explicit_formula:
                fw = np.zeros(w.size, dtype = complex)
                for j in range(w.size):
                    omega = w[j]
                    for i in range(t.size-1):
                        fw[j] = fw[j] + np.exp(-1j * t[i] * w[j]) * self.fu(t[i])
                return fw * (t[1]-t[0]) / (np.sqrt(2*np.pi))
            else:
                def Piw(w, T):
                    return (T * np.exp(1j*w*T/2) / np.sqrt(2*np.pi)) * np.sinc((w*T/2.0)/np.pi)
                nfreqs = w.size
                M = int((u.size-1)/2)
                T = self.T
                fw = np.zeros(w.size, dtype = complex)
                freqs = np.zeros(M+1)
                for j in range(1, M+1):
                    freqs[j] = (2.0*np.pi/T)*j
                for i in range(nfreqs):
                    fw[i] = Piw(w[i], T) * u[0]
                    for j in range(1, M+1):
                        fw[i] = fw[i] \
                                -1j * 0.5 * (Piw(w[i]-freqs[j], T) - Piw(w[i]+freqs[j], T)) * 2 * u[2*j-1]
                        fw[i] = fw[i] \
                                + 0.5 * (Piw(w[i]-freqs[j], T) + Piw(w[i]+freqs[j], T)) * 2 * u[2*j]
                return fw / np.sqrt(T)
        else:
            fw_ = sp.fft.fft(self.fu(t[:-1])) * (t[1]-t[0])/(np.sqrt(2.0*np.pi))
            w = np.zeros_like(t[:-1])
            for j in range(w.size):
                w[j] = (2.0*np.pi/t[-1])*j
            return fw_, w


def read_pulse(filename):
    """ Reads a pulse from the info contained in file.

    Parameters
    ----------
    filename : str
        Name of the file where the info about the pulse is written.

    Returns
    -------
    pulse
        The pulse whose information was previously written to filename.
    """

    f = open(filename, 'r')
    lines = f.read().splitlines()
    pulse_type = str(lines[0])
    T = float(lines[1])
    nu = int(lines[2])
    u = np.zeros(nu)
    for j in range(nu):
        u[j] = lines[3].split()[j]
    try:
        bound = float(lines[4])
    except:
        bound = None
    fpulse = pulse(pulse_type, T, u, bound = bound)
    f.close()
    return fpulse


def pulse_collection_parameter_range(f, j):
    """Returns the 'parameter range' of a given pulse in a collection

    Given a list of pulses 'f', the full control parameter list will
    be an array joining all the control parameters of each of of them.
    This function returns the indexes that would correspond, in that
    array, to one of the pulses.

    Thus, for example, if we have two pulses with nu1 and nu2 parameters
    each, the range of the first one would be (0, nu1), whereas the range
    of the second would be (nu1, nu1+nu2).

    Parameters
    ----------
    f : list of pulse
        A list with pulse objects
    j : int
        The pulse for which we want to get the parameter range.

    Returns
    -------
    list of int
        a list of two integer numbers, with the starting index of the parameters
        corresponding to the first pulse, and the final index.
    """
    k = 0
    if j > 0:
        for n in range(j):
            k = k + f[j].nu
    l = k + f[j].nu
    return [k, l]


def pulse_collection_set_parameters(f, u):
    """Sets the parameters of a collection of pulses

    It receives a numpy array of parameters u, whose dimension should
    be equal to the summ of parameters of the pulses in the collection f.

    """
    k = 0
    for j in range(len(f)):
        f[j].set_parameters(u[k:k+f[j].nu])
        k = k + f[j].nu


def pulse_collection_get_parameters(f):
    """Sets the parameters of a collection of pulses

    It receives a numpy array of parameters u, whose dimension should
    be equal to the summ of parameters of the pulses in the collection f.

    """
    nutotal = 0
    for j in range(len(f)):
        nutotal = nutotal + f[j].nu
    u = np.zeros(nutotal)
    k = 0
    for j in range(len(f)):
        u[k:k+f[j].nu] = f[j].u[:]
        k = k + f[j].nu
    return u


def pulse_collection_l(f, m):
    n = len(f)
    k = 0
    for i in range(n):
        k = k + f[i].nu
        if m < k:
            return i

def pulse_collection_j(f, m):
    n = len(f)
    l = pulse_collection_l(f, m)
    if l is not None:
        nprevious = 0
        for k in range(l):
            nprevious = nprevious + f[k].nu
            #print("nprevious = {}".format(nprevious))
        return m - nprevious


def pulse_constraint_functions(f, param_range):
    """Given a pulse, returns a list with all its constraint functions.

    The constraint functions contained in the pulse object are functions
    of the nu control parameters on which the pulse depends. In contrast,
    the functions returned by this function are functions of all the
    control parameters in a list of pulses. Therefore, we need
    as an input a 'parameter range', i.e. the starting and finishin indexes
    of the parameters of this particular pulse in the list.

    """
    g = []
    for cnstr in f.constraints:
        def make_f(cnstr):
            def g(u, grad):
                if grad.size > 0:
                    grad[:] = 0
                k = param_range[0]
                l = param_range[1]
                uj = u[k:l]
                gu = cnstr(uj, grad[k:l])
                return gu
            return g
        g.append(make_f(cnstr))
    return g


def pi_pulse(t, u):
    """A pi-pulse value at time t, parameters specifiey by the ndarray u

    Returns the pi-pulse value at a specific time
    
    Input
        A: pi-pulse amplitude
        w: pi-pulse frecuency
        t0: time in which start the propagation of the pulse
        t: time in which the pulse is calculated
        t_duration: pi-pulse duration
    Output:
        if the t value in which the pulse calculation is requested
        is between t0 and t0 + t_duration, return the value of a pi-pulse
        with frecuency w and amplitude A, otherwise return 0.
    """
    A = u[0]
    w = u[1]
    t0 = u[2]
    t_duration = u[3]
    phi = u[4]
    if isinstance(t, np.ndarray):
        ft = np.zeros_like(t)
        for j in range(t.shape[0]):
            if t[j] >= t0 and t[j] <= (t0 + t_duration):
                ft[j] = A * np.cos(w*(t[j]-t0)+phi)
            else:
                ft[j] = 0.0
        return ft
    else:
        if t >= t0 and t <= (t0 + t_duration):
            return A*np.cos(w*(t-t0)+phi)
        else:
            return 0.0

def pi_pulse_chain(t, u):
    """
    Returns the value of a chain of pi pulse at a specific time
    """
    A = u[0]
    n = int(u[1])
    w = np.zeros(n)
    length = np.zeros(n)
    for i in range(n):
        w[i] = u[2+i]
        length[i] = u[2+n+i]

    y = 0.0
    t_acumulation = 0.0
    for i in range(n):
        y += pi_pulse(t, np.array([A, w[i], t_acumulation, length[i], 0.0]))
        t_acumulation += length[i]
    return y


def f_realtime(t, T, u):
    M = u.shape[0]
    deltat = T / (M-1)
    i = (np.round(t/deltat)).astype(int)
    return u[i]


def f_realtime_der(t, T, u, m):
    if isinstance(t, np.ndarray):
        ntimes = t.shape[0]
        M = u.shape[0]
        deltat = T / (M-1)
        dfdu = np.zeros(ntimes)
        for k in range(ntimes):
            i = (np.round(t[k]/deltat)).astype(int)
            if m == i:
                dfdu[k] = 1.0
        return dfdu
    else:
        M = u.shape[0]
        deltat = T / (M-1)
        i = (np.round(t/deltat)).astype(int)
        if m == i:
            return 1.0
        else:
            return 0.0


def rotation(theta, n, dim = 2, i = None, j = None):
    """Returns a rotation operator between two levels, given an angle an axis.

    The rotation affects level i and j (or the only two levels, if dim = 2, which
    is the default). The angle of rotation is given by theta, and the axis is
    given by the unitary vector n.

    Parameters
    ----------
    theta : float
        The rotation angle.
    n : ndarray
        A three-dimensional float array containing a unit vector.
    dim : int, default = 2
        The dimension of the rotation operator that will be created.
    i : int, default = None
        One of the states affected by the rotation.
    j : int, default = None
        One of the states affected by the rotation.

    Returns
    -------
    Qobj:
        A Qobj operator with the rotation operator.

    """
    rot_ = (-1j * (theta/2) * (n[0] * qt.sigmax() + n[1] * qt.sigmay() + n[2] * qt.sigmaz()) ).expm()
    if dim > 2:
        rotmatrix = np.eye(dim, dtype = complex)
        rotmatrix[i, i] = rot_.full()[0, 0]
        rotmatrix[i, j] = rot_.full()[0, 1]
        rotmatrix[j, i] = rot_.full()[1, 0]
        rotmatrix[j, j] = rot_.full()[1, 1]
        return qt.Qobj(rotmatrix)
    else:
        return rot_


def rotationpulse(axis, A, omega, mu0, theta, t0 = None):
    """Returns a pulse that implements a rotation betwen two states.

    Given an amplitude for a pulse A, and two levels characterized
    by an energy difference omega and a coupling mu0, creates a pulse
    object that implements a rotation between those two levels
    in direction given by axis (0 => x, 1 => y, 2 => z), and angle 
    theta.

    Parameters
    ----------
    axis : int
        The rotation index (0 => x, 1 => y, 2 => z).
    A : float
        The amplitude of the pulse.
    omega : float
        The frequency difference between the levels.
    mu0 : float
        The coupling matrix element
    theta : float
        The rotation angle

    Returns
    -------
    pulse:
        A pulse object with the pulse that produces the
        rotation.

    """
    argmu0 = np.angle(mu0)
    if axis == 1:
        if theta > 0:
            phi = -np.pi/2 - argmu0
        else:
            phi = np.pi/2 - argmu0
        if t0 is not None: phi = phi + omega * t0
    elif axis == 0:
        if theta > 0:
            phi = - argmu0
        else:
            phi = -argmu0 + np.pi
        if t0 is not None: phi = phi + omega * t0
    elif axis == 2:
        res = []
        if t0 is None:
            res.append(rotationpulse(0, A, omega, mu0, -np.pi/2)[0])
            res.append(rotationpulse(1, A, omega, mu0, theta)[0])
            res.append(rotationpulse(0, A, omega, mu0, np.pi/2)[0])
        else:
            res.append(rotationpulse(0, A, omega, mu0, -np.pi/2, t0 = t0)[0])
            res.append(rotationpulse(1, A, omega, mu0, theta, t0 = res[-1].T)[0])
            res.append(rotationpulse(0, A, omega, mu0, np.pi/2, t0 = res[-1].T)[0])
        return res
    duration = np.abs(theta) / (A * np.abs(mu0))
    if t0 is None:
        T = duration
        u = np.array([A, omega, 0.0, duration, phi])
    else:
        T = duration + t0
        u = np.array([A, omega, t0, duration, phi])
    ft = pulse('user_defined', T, u)
    ft.assign_user_defined_function(pi_pulse, None)
    return [ft]



