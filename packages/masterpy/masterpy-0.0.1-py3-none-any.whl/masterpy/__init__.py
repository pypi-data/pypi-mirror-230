#!/usr/bin/env python
"""
__init__
===========
Initializes masterpy package and discovers all modules.

Authors:   Michael Landis, Ammon Thompson
Copyright: (c) 2022-2023, Michael Landis and Ammon Thompson
License:   MIT
"""

__project__ = 'masterpy'
__version__ = '0.0.1'
__author__ = 'Michael Landis and Ammon Thompson'
__copyright__ = '(c) 2022-2023, Michael Landis and Ammon Thompson'

# DEFAULT
MASTERPY_VERSION = __version__

from . import util
from .util import (
    load,
    param_dict_to_str,
    write_to_file,
    convert_phy2dat_nex
)

from . import models
from .models import (
    model,
    GeosseModel,
    SirModel
)
