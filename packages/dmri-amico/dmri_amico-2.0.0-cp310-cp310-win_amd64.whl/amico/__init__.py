from __future__ import absolute_import, division, print_function


# start delvewheel patch
def _delvewheel_patch_1_5_0():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'dmri_amico.libs'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_5_0()
del _delvewheel_patch_1_5_0
# end delvewheel patch

from .core import Evaluation, setup
from .util import set_verbose, get_verbose
from . import core
from . import scheme
from . import lut
from . import models
from . import util

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
__version__ = version('dmri-amico')
