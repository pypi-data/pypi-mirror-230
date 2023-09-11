# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_dun.ipynb.

# %% auto 0
__all__ = ['getdunder', 'getmro', 'getnew', 'getinit', 'getini', 'getcall', 'getannots', 'getsup', 'getsupnew', 'getname']

# %% ../nbs/04_dun.ipynb 4
from typing import Any, Type, Callable
from atyp import AnyQ, StrQ, CallQ, DictQ, TupleQ, CallQ

from idfunc import passable
from .utils import (typenone,)

# %% ../nbs/04_dun.ipynb 6
def getdunder(obj: Any, name: str, default: AnyQ = passable) -> Any:
    '''
    Retrieve a "dunder" (double-underscore) attribute from an object (i.e. `__dunder__`).

    Parameters
    ----------
    obj : Any
        The object to inspect.
    name : str
        The name of the dunder attribute, without double underscores.
    default : Any, optional
        The value to return if the attribute is not found, by default passable.

    Returns
    -------
    Any
        The value of the dunder attribute or the default value.
    '''
    return getattr(obj, f'__{name}__', default)

def getmro(obj, default: AnyQ = tuple()) -> TupleQ:    
    '''
    Retrieve `__mro__` (method resolution order) from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: tuple()
        The value to return if the attribute is not found, by default `tuple()`.

    Returns
    -------
    Optional[Tuple]
        `obj.__mro__` or the default value.
    '''
    return typenone(getdunder(obj, 'mro', None) or default, tuple)

def getnew(obj, default: AnyQ = passable) -> CallQ:    
    '''
    Retrieve `__new__` from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: `passable`
        The value to return if the attribute is not found, by default `passable`.

    Returns
    -------
    Optional[Callable]
        `obj.__new__` or the default value.
    '''
    return typenone(getdunder(obj, 'new', default), Callable)

def getinit(obj, default: AnyQ = passable) -> CallQ:
    '''
    Retrieve `__init__` from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: `passable`
        The value to return if the attribute is not found, by default `passable`.

    Returns
    -------
    Optional[Callable]
        `obj.__init__` or the default value.
    '''    
    return typenone(getdunder(obj, 'init', default), Callable)


def getini(obj, default: AnyQ = passable) -> CallQ:
    '''
    Alias for `getinit`. Retrieve `__init__` from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: `passable`
        The value to return if the attribute is not found, by default `passable`.

    Returns
    -------
    Optional[Callable]
        `obj.__init__` or the default value.

    See Also
    --------
    getinit
    '''    
    return typenone(getdunder(obj, 'init', default), Callable)

def getcall(obj, default: AnyQ = passable) -> CallQ:
    '''
    Retrieve `__call__` from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: `passable`
        The value to return if the attribute is not found, by default `passable`.

    Returns
    -------
    Optional[Callable]
        `obj.__call__` or the default value.
    '''    
    return typenone(getdunder(obj, 'call', default), Callable)

def getannots(obj, default: AnyQ = dict()) -> DictQ:
    '''
    Retrieve `__annotations__` from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: dict()
        The value to return if the attribute is not found, by default `dict()`.

    Returns
    -------
    Optional[dict]
        `obj.__annotations__` or the default value.
    '''
    return typenone(getdunder(obj, 'annotations', None) or default, dict)


def getsup(cls, obj: AnyQ = None) -> Type:
    '''
    Retrieve an object's superclass.

    Parameters
    ----------
    cls : Type
    obj : Any, optional
        The object of which to get the superclass of, default is `cls`.

    Returns
    -------
    Type
        `super(cls, (obj or cls))`
    '''
    supcls = super(cls, (obj or cls))
    return supcls

def getsupnew(cls, obj: AnyQ = None, default: AnyQ = None) -> CallQ:
    '''
    Retrieve `__new__` from an object's superclass.

    Parameters
    ----------
    cls : Type
    obj : Any, optional
        The object of which to get the superclass of, default is `cls`.
    default : Any, default: `None`
        The value to return if `__new__` is not found, by default `None`.

    Returns
    -------
    Optional[Callable]
        `super(cls, obj).__new__` or the default value.
    '''
    return getnew(getsup(cls, obj), default)

def getname(obj, default: AnyQ = None) -> StrQ:    
    '''
    Retrieve `__mro__` (method resolution order) from an object.

    Parameters
    ----------
    obj : Any
        The object to inspect.    
    default : Any, default: tuple()
        The value to return if the attribute is not found, by default `tuple()`.

    Returns
    -------
    Optional[Tuple]
        `obj.__mro__` or the default value.
    '''
    return typenone(getdunder(obj, 'name', None) or default, str)
