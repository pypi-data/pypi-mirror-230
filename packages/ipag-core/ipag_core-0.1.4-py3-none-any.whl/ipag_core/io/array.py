from __future__ import annotations
from typing import Callable
from dataclasses import dataclass, field 
import numpy as np

from ipag_core.define import DataTuple, DataWriter, DataReader


# The folowing are mostly for simulators 

@dataclass
class RandomDataReader(DataReader):
    """ A generating Random Data 
    
    Attributes:
        loc:  "mean", center of the distribution
        scale: Standard deviation (spread or "width") of the distribution
        shape: Output shape 
        generator: cllable taking the 3 above argument (e.g. np.random.normal)
    """
    loc: float = 0.0
    scale: float = 1.0 
    shape: tuple[int] = tuple()
    generator: Callable = field( default=np.random.normal )

    def read_data(self)->DataTuple:
        return DataTuple( 
            self.generator( self.loc,  self.scale, self.shape), 
            {'loc':self.loc, 
             'scale': self.scale, 
             'distrib': getattr(self.generator, "__name__", "unknown")
            } 
        )

@dataclass 
class _ArrayIo(DataReader):
    shape: tuple 
    dtype: type = np.float64 
    creator: Callable = field( default=np.ndarray)

    def read_data(self)->DataTuple:
        return DataTuple( self.creator(self.shape, self.dtype), {} )

@dataclass 
class OnesDataReader(_ArrayIo):
    """ A DataReader returning array filles with ones """
    creator: Callable = field(default=np.ones) 

@dataclass 
class ZerosDataReader(_ArrayIo):
    """ A DataReader returning array filles with zeros """
    creator: Callable = field(default=np.zeros) 


