""" This is the public API for the ipag_core package """

from ipag_core.log import init_logger, get_logger

from ipag_core.define import (
    DataProcessor,
    DataReader, 
    DataTuple,
    DataWriter, 
    PathGetter,
    MetadataLike, 
    SupportsUpdate, 
    SuportsSetup, 
    MetaSetter, 
    MetaGetter, 
    MetadataPopulator
)

from ipag_core.io.base import (
    ProcessedDataIo, 
    ProcessAndWrite, 
    MergeDataIo, 
    DataPipe
)

from ipag_core.io.fits import (
    FitsIo,
    FitsReader, 
    FitsWriter, 
    FitsFilesReader, 
)

from ipag_core.io.array import (
     RandomDataReader, OnesDataReader, ZerosDataReader
)

from ipag_core.data import( 
    DataContainer
)

from ipag_core.log import ( 
    init_logger, 
    get_logger,
)

from ipag_core.processor import (
    data_processor, 
    AxisLooper, 
    ProcessChain, 
    DataReducer, 
    DarkSubstractor, 
)

from ipag_core.path import (
    Path, 
    AutoPath, 
    UniquePath, 
    TodayPath, 
    ResourcePath
)

#place holder of an IPAG configured BaseModel 
from ipag_core.pydantic import (
    Field, 
    UserModel, 
    StateModel, 
    user_model_config
)

from ipag_core.metadata import (
    new_metadata, 
    populate_metadata, 
    update_from_metadata, 
    auto_populate_metadata, 
    auto_update_from_metadata, 
    MetaField, 
    MetaNamedField, 
    MetadataIo, 
)


from ipag_core import types


from ipag_core.metadata_model import ( 
    ipag_metadata_model, 
    ipag_metadata_io
)
