# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['fuzstr']

# %% ../nbs/00_core.ipynb 5
from abc import ABC, abstractmethod
from typing import List, Iterable
from atyp import (BoolQ, FloatQ, StrLike, StrLikeQ,)

# %% ../nbs/00_core.ipynb 6
from ispec import AttrPref, setkws, getattrs, kwsopt, funkws, newkws
from pstr.sens import sens
from pstr.fuzz import fuzzfind
from aspec import aspec
#| export
# from aprep import aprep

# %% ../nbs/00_core.ipynb 8
class fuzstr(str, aspec, ABC):
    '''Fuzzy String Class

    Parameters
    ----------
    value : str
        The original string.

    icase : bool, default: True
        Whether to ignore case when matching, by default True.

    ispace : bool, default: True
        Whether to ignore spaces when matching, by default True.

    iunder : bool, default: True
        Whether to ignore underscores when matching, by default True.
        
    cutoff : float, default: 0.8
        The cutoff for fuzzy matching, by default 0.8.

    Attributes
    ----------
    raw : str
        The raw string.

    aspec : list | tuple | dict, default: ('icase', 'ispace', 'iunder', 'cutoff', )
        The attribute specification. Must be either an iterable of strings 
        or a dictionary of `str: Any`. Defaults to an empty tuple.
    
    dspec : list | tuple | dict, default: ()
        The dynamic attribute specification. Must be either an iterable of strings 
        or a dictionary of `str: str`. Defaults to an empty tuple.

    specs: {('aspec', ), ('aspec', 'dspec', ), ('aspec', 'dspec), (), }, default: (Spec.aspec.value, Spec.dspec.value)
        The attribute specifications to use.
        
    __readonly__ : tuple, default: (Spec.aspec.value, Spec.dspec.value)
        Attributes that cannot be set.

    Methods
    -------
    tostr() -> str:
        Convert the instance to a string.

    prep(s: StrLikeQ = None) -> str:
        Prepare a string by applying case and space insensitivity rules.

    find(strseq: Iterable[StrLike], **kwargs) -> List[str]:
        Find the closest matches (same-ish) in the provided sequence using fuzzy matching.

    iseq(other: str) -> bool:
        Check if the provided string is an alias of this entity using fuzzy matching.

    __eq__(other):
        Check if the provided value is an alias of this entity using fuzzy matching.

    __str__():
        Return the raw string.

    __hash__():
        Return the hash of the raw string.

    __setattr__(name, value):
        Set the class attribute if it's not read-only.

    getattrkeys(spec: str, dyn: bool = False) -> tuple[str, ...]:
        Return attribute keys stored in `spec`.

    getattrvals(self, spec: str, dyn: bool = False) -> tuple[Any, ...]:
        Return default attribute values stored in `spec`.
    
    skeys() -> tuple[str, ...]:
        Return all attribute keys stored for each spec stored in `specs`.

    svals() -> tuple[str, ...]:
        Return default attribute values stored for each spec stored in `specs`.
    
    getattrs(**kwargs):
        Get instance parameters with optional overrides.
        
    makesame(*args, **kwargs):
        Call class constructor with the same attributes as the current instance.
    
    isinst(other):
        Check if the provided value is an instance of this class.
        
    sameattrs(other):
        Check if the provided value is an instance of this class with the same attributes.
        
    diffattrs(other):
        Check if the provided value is an instance of this class with different attributes.

    getattrname(dattr: str) -> str:
        Get the name of the dynamic attribute.
    
    getdattr(dattr: str, default: Any = None) -> Any:
        Get the value of the dynamic attribute.

    setdattr(dattr: str, value: Any = None):
        Set the value of the dynamic attribute.

    update_attrname(dattr: str, **kwargs):
        Update the name of the dynamic attribute.
    
    update_dattrval(aname: str, **kwargs):
        Update the value of the dynamic attribute.
    
    update_dattr(dattr: str, **kwargs):
        Update the name and value of the dynamic attribute.

    update_aspec(**kwargs):
        Update the attribute specification.

    update_dspec(**kwargs):
        Update the dynamic attribute specification.

    update_specs(**kwargs):
        Update the specifications in `specs` e.g. `aspec` and / or `dspec`.

    getclsattr(attr: str, default: Any = None) -> Any:
        Get the value of the class attribute.

    setclsattr(attr: str, val: Any = None):
        Set the value of the class attribute.

    copy():
        Return a shallow copy of the instance.
    
    deepcopy():
        Return a deep copy of the instance.
    '''
    icase:  bool  = True # Whether to ignore case when matching
    ispace: bool  = True # Whether to ignore spaces when matching
    iunder: bool  = True # Whether to ignore underscores when matching    
    cutoff: float = 0.8  # The cutoff for fuzzy matching
    
    aspec = ('icase', 'ispace', 'iunder', 'cutoff', )

    def __new__(
        cls, 
        value:  StrLikeQ, 
        icase:  BoolQ  = True, # Case insensitive
        ispace: BoolQ  = True, # Space insensitive
        iunder: BoolQ  = True, # Underscore insensitive
        cutoff: FloatQ = 0.8,  # Fuzzy cutoff
        *args, **kwargs
    ):  
        # Put all variables in a dictionary for easy access
        kwargs.update(icase=icase, ispace=ispace, iunder=iunder, cutoff=cutoff) 
     
        # Create the base string object    
        # NOTE: funkws(func, **kwargs) will fail if 'func' is also a kwarg    
        # pkws = funkws(cls.__prep__, **kwargs)
        # NOTE: since __prep__ handles all the kwargs, we can just use kwargs
        # pwks = {k: v for k, v in kwargs.items() if k in ['icase', 'ispace', 'iunder']}
        pkws = kwargs
        pstr = cls.__prep__(value, **pkws)
        nstr = super().__new__(cls, pstr)   
        nstr._raw = value # The raw string
        return nstr
        
    def __init__(
        self, 
        value: str,        
        icase:  BoolQ  = True, # Case insensitive
        ispace: BoolQ  = True, # Space insensitive
        iunder: BoolQ  = True, # Underscore insensitive
        cutoff: FloatQ = 0.8,  # Fuzzy cutoff
        *args, **kwargs
    ):        
        kwargs.update(icase=icase, ispace=ispace, iunder=iunder, cutoff=cutoff)
        super().__init__(value, *args, **kwargs)
        
        # Store the original string for reference
        self._raw = value # The raw string
        self = setkws(self, type(self), pref=AttrPref.KOC, **kwargs)  

    @staticmethod
    @abstractmethod
    def __prep__(s: StrLike, icase: bool = True, ispace: bool = True, iunder: bool = True, **kwargs) -> str:
        '''Prepare a string by applying case and space insensitivity rules.'''
        return sens(s, icase, ispace, iunder)        

    @property
    def raw(self) -> str:
        '''The raw string.'''
        return getattr(self, '_raw', '')
    @raw.setter
    def raw(self, value):
        raise AttributeError("Cannot set the 'raw' property")
    
    def tostr(self) -> str:
        '''Convert the instance to a string.'''
        return str(self.raw)

    def prep(self, s: StrLikeQ = None) -> str:
        '''Prepare a string by applying case and space insensitivity rules.

        Parameters
        ----------
        s : StrLikeQ, optional
            The string to prepare, by default None. If `None`, the original 
            string (`self`) is used.
        
        Notes
        -----
        If no string is provided, the original string is used i.e. `self.raw`.

        See Also
        --------
        __prep__
        '''
        return self.__prep__((s or self.raw), icase=self.icase, ispace=self.ispace, iunder=self.iunder)    
    
    def find(self, strseq: Iterable[StrLike], **kwargs) -> List[str]:
        '''Find the closest matches (same-ish) in the provided sequence using fuzzy matching.
        
        See Also
        --------
        pstr.fuzzfind
        difflib.get_close_matches
        '''
        kwargs.setdefault('n', 1)
        kwargs.setdefault('cutoff', self.cutoff)
        return fuzzfind(self.raw, strseq, prep=True, prepfunc=self.prep, **kwargs)
            
    def iseq(self, other: str) -> bool:
        '''Check if the provided string is an alias of this entity using fuzzy matching.'''
        strseqs = (self.prep(other), )
        matches = self.find(strseqs, n=1)
        return len(matches) > 0

    def __eq__(self, other):
        if isinstance(other, (str, type(self))):
            return self.iseq(other)
        return super().__eq__(other)

    def __str__(self):
        return self.raw

    def __hash__(self):
        return super().__hash__()
