
qocttools is a python package that implements quantum
optimal control theory (QOCT). 

You may download it from its `gitlab page <https://gitlab.com/acbarrigon/qocttools>`_.
Documentation `here <https://qocttools.readthedocs.io/>`_.

It solves typical optimization problems defined on generic quantum systems. These
may be closed (described by the Schrödinger equation) or open (described by Lindblad's equation).
It relies heavily on the `QuTiP <https://qutip.org/>`_ program to handle internally
the quantum objects representation, manipulation, etc., and on the `nlopt <https://nlopt.readthedocs.io/en/latest/>`_
library for function optimization algorithms.
