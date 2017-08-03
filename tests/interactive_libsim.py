"""
Saves time creating variables and importing the basics for quick interactive
testing of libsim.

Run this from toplevel project directory like so:

    $ PYTHONPATH="$PYTHONPATH:." python -i tests/interactive_libsim.py
"""
from zcsim.util.libsim import *
import matplotlib.pyplot as plt

def id(_):
    return _

var = FirstOrderVar('angular-velocity', id, 0.1, 20)
step = SimulationStep(20, 100, 25)
