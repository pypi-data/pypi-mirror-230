__version__ = "0.0.10"
from .cons import Spec
from .utils import update_specs, setkwsdef, getdattr, setdattr
from .core import specabc, spec, aspec
__all__ = [
    'Spec', 'spec', 'specabc', 'aspec', 
    'update_specs', 'setkwsdef', 'getdattr', 'setdattr'
]