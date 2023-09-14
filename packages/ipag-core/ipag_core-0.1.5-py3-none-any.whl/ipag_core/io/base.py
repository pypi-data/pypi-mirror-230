from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from ipag_core.define import DataReader, DataWriter, DataProcessor, DataTuple, MetadataLike
from ipag_core.processor import data_processor


def _get_read_method( obj ):
    if hasattr(obj, "read_data"):
        return  obj.read_data 
    if hasattr(obj, "__call__"):
        return  obj 
    raise ValueError("input io must have a read_data() method or shall be callable")     

def _get_write_method( objs ):
    wrfuncs = []
    for io in objs:
        if hasattr(io, "write_data"):
            wrfuncs.append(io.write_data)
        elif hasattr(io, "__call__"):
            wrfuncs.append( io ) 
        else:
            raise ValueError("outputio must have a write_data() method or shall be callable")

    def write(data, metadata=None):
        for wr in wrfuncs:
            wr( data, metadata)
    return write 
    

class MergeDataIo(DataReader, DataWriter):
    """ Merge one 'input' io and one or more 'output' io 

    Args:
        io_in: A single io object or a callable with signature f() called at read_data
        *io_outs: A list of io object or functions with signature f(data,metadata). 
            They are executed with the same order when write method is called 

    Note the read and write function are built at init. Therefore the input and output 
    io(s) cannot be change after object creation. 
    """
    def __init__(self, io_in, *io_outs):
        self.read_data  = _get_read_method(io_in) 
        self.write_data = _get_write_method( io_outs)
    
    def read_data(self):
        raise ValueError("PipeIo wasn't initialised")

    def write_data(self, data:Any, metadata: MetadataLike | None = None):
        raise ValueError("PipeIo wasn't initialised")


class DataPipe(DataReader, DataWriter, DataProcessor):
    def __init__(self, reader_or_proc: DataReader, *proc_and_write):
        if not isinstance( reader_or_proc, DataReader):
            raise ValueError(f"first argument must be a DataRead like object got a {type(reader_or_proc)}")
        
        output_ios = []
        if isinstance( reader_or_proc, DataReader):
            self._input_io = reader_or_proc 
        else:
            try:
                output_ios.append( data_processor(reader_or_proc) )
            except ValueError:
                raise ValueError( "First argument must be a date reader or a data processor ") 
            self._input_io = None 
            
        self._has_writer = False 
        for obj in proc_and_write:
            if isinstance( obj, DataWriter):
                output_ios.append( (True, obj))
                self._has_writer = True 
            else:
                output_ios.append( (False, data_processor(obj)))

        self._output_ios = output_ios

    def read_data(self) -> DataTuple:
        if self._input_io is None:
            raise ValueError( "This Data Pipe has no data_reader ")
        
        data, metadata = self._input_io.read_data()
        for is_writer, obj in self._output_ios:
            if is_writer:
                obj.write_data( data, metadata)
            else:
                data, metadata = obj.process_data( data, metadata)
        return DataTuple( data, metadata) 
    
    def write_data(self, data: Any, metadata:MetadataLike|None = None):
        if not self._has_writer:
            raise ValueError( "This Data Pipe has no data_writer defined" )

        for is_writer, obj in self._output_ios:
            if is_writer:
                obj.write_data( data, metadata)
            else:
                data, metadata = obj.process_data( data, metadata)
    
    def process_data(self, data, metadata=None) -> DataTuple:
        for is_writer, obj in self._output_ios:
            if not is_writer:
                data, metadata = obj.process_data( data, metadata)
        return DataTuple(data, metadata)


class ProcessedDataIo(DataReader, DataWriter):
    """ An Io Processing data before returning it 

    Args:
        io: The Io object use to first retrieve the data 
        *procs: list of processor. can be 
            - a Process object 
            - a callable with signature  f(data) 
            - a list of one of these three types

    Exemple:
        
        import numpy as np 
        from ipag_core.ipag import ProcessedIo, FitsIo, procfunc 
        
        image_io = ProcessedIo( FitsIo("my_cube.fits"), procfunc(np.mean, axis=0) )
        data, metdata = image_io.read()     

    """
    def __init__(self, io: DataReader | DataWriter, *procs: DataProcessor):
        self.io = io 
        self.proc = data_processor(procs) 
    
    def write_data(self, data, metadata=None):
        self.io.write_data( data, metadata )

    def read_data(self):
        data, metadata = self.io.read_data() 
        data, metadata = self.proc.process_data( data, metadata)
        return DataTuple( data, metadata )

class ProcessAndWrite:
    def __init__(self, *args):
        *processes, writer = args 
        if not isinstance( writer, DataWriter):
            raise ValueError("Last argument must be  DataWriter compatible")
        self.io = writer 
        self.proc = data_processor(processes)

    def write_data(self, data, metadata=None):
        data, metadata = self.proc.process_data( data, metadata)
        self.io.write_data(data, metadata)

    def read_data(self):
        return self.io.read_data()
