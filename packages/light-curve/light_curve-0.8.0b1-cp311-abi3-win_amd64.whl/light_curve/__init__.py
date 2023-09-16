# Import all Python features


# start delvewheel patch
def _delvewheel_patch_1_5_1():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'light_curve.libs'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_5_1()
del _delvewheel_patch_1_5_1
# end delvewheel patch

from .light_curve_py import *

# Hide Python features with Rust equivalents
from .light_curve_ext import *

# Hide Rust Extractor with universal Python Extractor
from .light_curve_py import Extractor

from .light_curve_ext import __version__
