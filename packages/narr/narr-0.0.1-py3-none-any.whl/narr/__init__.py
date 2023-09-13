__version__ = "0.0.1"
from .cons import SCOPY, DCOPY
from .atyp import AxisKey, IterAxes, IterAxesQ
from .copy import safecopy
from .strs import first_line, first_digit_loc
from .errs import AxisError, DimsError
from .axis import naxis
from .axes import naxes
from .narr import narr

__all__ = [
    'SCOPY', 'DCOPY', 
    'AxisKey', 'IterAxes', 'IterAxesQ', 
    'safecopy', 
    'first_line', 'first_digit_loc', 
    'AxisError', 'DimsError', 
    'naxis', 'naxes', 'narr'
]