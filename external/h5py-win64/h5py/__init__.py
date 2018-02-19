# This file is part of h5py, a Python interface to the HDF5 library.
#
# http://www.h5py.org
#
# Copyright 2008-2013 Andrew Collette and contributors
#
# License:  Standard 3-clause BSD; see "license.txt" for full license terms
#           and contributor agreement.

"""
    This is the h5py package, a Python interface to the HDF5
    scientific data format.
"""

from __future__ import absolute_import


# --- Library setup -----------------------------------------------------------

# When importing from the root of the unpacked tarball or git checkout,
# Python sees the "h5py" source directory and tries to load it, which fails.
# We tried working around this by using "package_dir" but that breaks Cython.
try:
    from . import _errors
except ImportError:
    import os.path as _op
    if _op.exists(_op.join(_op.dirname(__file__), '..', 'setup.py')):
        raise ImportError("You cannot import h5py from inside the install directory.\nChange to another directory first.")
    else:
        raise
    
_errors.silence_errors()

from ._conv import register_converters as _register_converters
_register_converters()

from .h5z import _register_lzf
_register_lzf()


# --- Public API --------------------------------------------------------------

from . import h5a, h5d, h5ds, h5f, h5fd, h5g, h5r, h5s, h5t, h5p, h5z

from ._hl import filters
from ._hl.base import is_hdf5, HLObject, Empty
from ._hl.files import File
from ._hl.group import Group, SoftLink, ExternalLink, HardLink
from ._hl.dataset import Dataset
from ._hl.datatype import Datatype
from ._hl.attrs import AttributeManager

from .h5 import get_config
from .h5r import Reference, RegionReference
from .h5t import special_dtype, check_dtype

from . import version
from .version import version as __version__

from .tests import run_tests

def enable_ipython_completer():
    """ Call this from an interactive IPython session to enable tab-completion
    of group and attribute names.
    """
    import sys
    if 'IPython' in sys.modules:
        ip_running = False
        try:
            from IPython.core.interactiveshell import InteractiveShell
            ip_running = InteractiveShell.initialized()
        except ImportError:
            # support <ipython-0.11
            from IPython import ipapi as _ipapi
            ip_running = _ipapi.get() is not None
        except Exception:
            pass
        if ip_running:
            from . import ipy_completer
            return ipy_completer.load_ipython_extension()

    raise RuntimeError('Completer must be enabled in active ipython session')


# --- Legacy API --------------------------------------------------------------

from .h5t import py_new_vlen as new_vlen
from .h5t import py_get_vlen as get_vlen
from .h5t import py_new_enum as new_enum
from .h5t import py_get_enum as get_enum



