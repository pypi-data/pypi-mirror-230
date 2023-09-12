__version__ = "0.0.11"
from .types import AttrLvl, ArgsTuple
from .enums import *
from .utils import *
# from .preps import *
# from .dun import *
from .sig import *
from .ann import *
from .kws import *
# from .val import *
from .agg import *
from .src import *
from .rnk import *
from .set import *

__all__ = [
    # types
    'AttrLvl', 'ArgsTuple',
    'AttrSrcs', 'AttrSrcsQ', 'AttrPrefQ',

    # enums
    'AttrSrc', 'AttrPref',

    # utils
    'key1st', 'idx1st', 'arg1st',
    'getattrs',
    'funkws', 'kwskws', 'kwsadd',

    # sig
    'getspecdef', 'getsigdef', 'getspeckws', 'getsigkws',
    
    # ann
    'getannkws', 'getdefkws',

    # kws
    'newkws', 'inikws', 'annkws', 'supkws', 
    'defkws', 'allkeys', 'nilkws',

    # agg
    'aggattrs',

    # src
    'srcdict'

    # rnk
    'rankattr', 'rankattrs', 

    # set
    'setnil', 'setcur', 'setkws', 
]