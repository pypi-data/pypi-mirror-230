import hyclib as lib
from addict import Dict

options = Dict(lib.config.load_package_config('tdfl'))
options.freeze()

del Dict, lib

from .dataframe import *
