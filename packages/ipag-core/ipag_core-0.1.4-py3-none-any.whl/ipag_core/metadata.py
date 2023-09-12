from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Type, Union, Any
from typing_extensions import Annotated

from pydantic import AfterValidator, RootModel, TypeAdapter

from ipag_core.define import MetadataLike, _Empty, MetaSetter, MetaGetter, MetadataPopulator, MetadataUpdator
from astropy.io import fits 


def fix_meta_key(key):
    if len(key)>8 or " " in key:
        return "HIERARCH "+key 
    return key

def join_meta_keys(*keys):
    return " ".join( k for k in keys if k )

MetaValue = Union[int, float, complex, str, bytes, bool]

def _passthrue(x):
    return x

class _Empty:
    ...


def _get_meta_value( key, metadata, default):
    try:
        return metadata[key]
    except KeyError:
        if default is _Empty:
            raise ValueError( f"{key} is not part of the metadata. Provide a default to avoid error" )
        return default 

def _set_meta_value( metadata,  key, value, comment):
    try:
        setter = metadata.set 
    except AttributeError:
        # support for normal dictionary 
        metadata[key] = value 
    else:
        setter( key, value, comment) 


_default_parsers = {
    str:str, 
    float:float, 
    int:int, 
    bool:bool, 
    complex:complex, 
    bytes:bytes, 
    Any: _passthrue
}
def _type2parser(vtype):
    try:
        return _default_parsers[vtype]
    except KeyError:
        return TypeAdapter( vtype ).validate_python

def valueof(enum):
    return Annotated[enum, AfterValidator(lambda m:m.value)]


def vtype2parsers(vtype):
    try:
        pin,pout = vtype
    except (TypeError, ValueError):
        if isinstance(vtype, type) and issubclass( vtype, Enum):
            return _type2parser( valueof(vtype) ), vtype
        return _type2parser(vtype), _passthrue 
    
    return _type2parser(pin), _type2parser(pout)
        


@dataclass
class MetaField( MetaGetter, MetaSetter):
    metakey: str 
    description: str = ""
    vtype: Callable|type|tuple = Any    
    
    @property
    def vtype(self):
        return self._vtype 
    
    @vtype.setter
    def vtype(self, vtype):
        self._type_parsers = vtype2parsers( vtype ) 
        self._vtype = vtype


    def set_to(self,  metadata: MetadataLike, value: Any,prefix:str = "")-> None:
        key = fix_meta_key(  join_meta_keys( prefix, self.metakey ) )
        parse,_ = self._type_parsers 
        _set_meta_value( metadata, key, parse(value), self.description )
    
    def get_from(self, metadata: MetadataLike, default = _Empty, prefix: str ="", )->None:
        key = join_meta_keys( prefix, self.metakey )
        _,parse = self._type_parsers
        return parse( _get_meta_value( key, metadata, default) )

@dataclass
class MetaNamedField(MetaGetter, MetaSetter):
    metakey: str 
    name: str
    description: str = ""
    vtype: Callable|type|tuple = Any    
    unit: str | None = None
    
    @property
    def vtype(self):
        return self._vtype 
    
    @vtype.setter
    def vtype(self, vtype):
        self._type_parsers = vtype2parsers( vtype ) 
        self._vtype = vtype
 
    def set_to(self,  metadata: MetadataLike, value: Any,prefix: str =""):
         key = fix_meta_key(  join_meta_keys( prefix, self.metakey, "VAL" ) )
         parse,_ = self._type_parsers     
         _set_meta_value(metadata,  key, parse(value), self.description)

         key = fix_meta_key(  join_meta_keys( prefix, self.metakey, "NAME" ) )
         _set_meta_value(metadata,  key, self.name, f"name of {self.metakey} value")
         if self.unit:
            key = fix_meta_key(  join_meta_keys( prefix, self.metakey, "UNIT" ) )
            _set_meta_value(metadata,  key,  self.unit, f"Unit of {self.metakey} value") 
        
    def get_from(self,  metadata: MetadataLike, default=_Empty,  prefix: str = ""):
        _, parse = self._type_parsers
        key = join_meta_keys( prefix, self.metakey, "VAL" )
        return parse( _get_meta_value( key, metadata, default) )


class Extra(str, Enum):
    Ignore = "ignore"
    Allow = "allow"
    Forbid = "forbid"

@dataclass
class MetadataIo:
    model: dict[str, Union[MetaGetter, MetaSetter]] = field(default_factory=dict )
    extra: Extra = Extra.Ignore 
    
    def set_to(self, metadata: MetadataLike, field_name: str, value: Any, prefix:str = "")->None:
        try:
            meta_field = self.model[field_name]
        except KeyError:
            if self.extra == Extra.Ignore:
                return 
            if self.extra == Extra.Allow:
                _set_meta_value( metadata, join_meta_keys(prefix, field_name.upper()), value, "")
            else:
                raise ValueError( "no fields found with the name {field_name} in the metadata model" )
        else:
            meta_field.set_to( metadata, value, prefix=prefix)
    
    def get_from(self, metadata: MetadataLike, field_name: str, default = _Empty, prefix:str ="")->Any:
        try:
            meta_field = self.model[field_name]
        except KeyError:
            return _get_meta_value(join_meta_keys(prefix, field_name), metadata, default)
        else:
            return meta_field.get_from( metadata, default, prefix=prefix)



def _auto_populate_metadata_one( metadata: MetadataLike, model: MetadataIo, obj: Any , prefix: str = ""):
    
    fields = getattr( obj, "model_fields", {})
    for k in fields:
        child = getattr( obj, k)
        new_prefix = join_meta_keys( prefix, k.upper())
        
        if isinstance( child, MetadataPopulator):
            child.populate_metadata( metadata, prefix=new_prefix)
            continue 
        try:
            model.set_to( metadata, k, getattr(obj, k), prefix = prefix)
        except ValueError:
            _auto_populate_metadata_one( metadata, model, child, new_prefix)


def auto_populate_metadata( metadata: MetadataLike, model: dict|MetadataIo, *objects, prefix: str = ""):
    """ Try to populate objects (e.g. data structure) from metadata and a model of metadata 

    This is best effort basis where keys are matched between field in the data structure and fields in the model. 
    The normal way is to implement the ``populate_metadata(metadta, prefix = "")`` method on the objects.

    Args:
        metadata: contains the keys/value pairs e.g. fits header 
        model: A metadata model containing fields definition. A dictionary or a :class:`ipag_core.ipag.MetadataIo``
        *objects: list of object containing the data. 
    """
    if isinstance( model, dict):
        model = MetadataIo( model)

    for obj in objects:
        _auto_populate_metadata_one( metadata, model, obj, prefix)

def _auto_update_from_metadata_one( obj: Any,  model: dict|MetadataIo,  metadata: MetadataLike,prefix: str = ""):
    
    fields = getattr( obj, "model_fields", {})
    for k in fields:
        child = getattr( obj, k)
        new_prefix = join_meta_keys( prefix, k.upper())
        
        if isinstance( child, MetadataUpdator):
            child.update_from_metadata( metadata, prefix=new_prefix)
            continue 
        try:
            val = model.get_from( metadata, k, prefix = prefix)
        except ValueError:
            _auto_update_from_metadata_one( child, model, metadata, new_prefix)
        else:
            setattr( obj, k, val)

def auto_update_from_metadata(obj: Any,  model: dict|MetadataIo, *metadatas: list[MetadataLike], prefix: str = ""):
    if isinstance( model, dict):
        model = MetadataIo( model)
    for metadata in metadatas:
        _auto_update_from_metadata_one( obj, model , metadata, prefix) 




def populate_metadata(metadata: MetadataLike, *objects: list[Any], model: dict|MetadataIo|None = None, prefix: str = ""):
    """ Populate a metadata from one or several objects          
    
    if model is not providated, it will only work on object having the ``.populate_metadata(metadata, prefix="")`` method 
    and ignore other objects

    if a model is providated object without the ``.populate_metadata`` method will be used to automaticaly populate metadata
    by mathing fields name with model names. 
    
    .. warning:: 

        Do not use this method on self inside a ``.populate_metadata`` method -> infinite loop.
        Instead use :func:`ipag_core.ipag.auto_populate_metadata`
    
    Args:
        metadata: the metadata disciotnary
        *object: list of objects 
        model: optional, a metadata definition dictionary of a :class:`~ipag_core.ipag.MetadataIo` 
        prefix: optional metadata prefix  
    """
    if isinstance( model, dict):
        model = MetadataIo( model)

    for obj in objects:
        if isinstance( obj, MetadataPopulator):
            obj.populate_metadata( metadata, prefix)
        elif model:
            auto_populate_metadata( metadata, model, obj, prefix=prefix)

def update_from_metadata(obj: Any, *metadatas: list[MetadataLike], model: dict|MetadataIo|None = None, prefix: str = ""):
    """ Updata an object (data strucuture) from one or several metadata 

    If model is not provided, this just use the method ``update_from_metadata(metadta, prefix="")`` of the input object. 
    
    
    If model is provided and object has not the method ``update_from_metadata`` an attempt is done to update the data structure 
    from the metadata and by matching keys between the model and the data structure. 

    Args:
        obj: data structure 
        *metadatas: list of metadata 
        model:  optional, a metadata definition dictionary of a :class:`~ipag_core.ipag.MetadataIo` 
        prefix: optional metadata prefix  

    """
    if isinstance( model, dict):
        model = MetadataIo( model)

    if isinstance( obj, MetadataUpdator):
        for metadata in metadatas:
            obj.update_from_metadata( metadata, prefix = prefix)
    elif model:
        auto_update_from_metadata( obj, model, metadata, prefix= prefix)

def new_metadata()->MetadataLike:
    """ create a new Metadata dictionary like object 
    
    .. note::

        So far this is a fits.Header, but this can change in future
    """
    return fits.Header()



if __name__ == "__main__":

    m = new_metadata()
    DIT = MetaField('DIT', description="Detector Integration Time", vtype=(complex,float))
    print( DIT._type_parsers )
    DIT.set_to(m, 3.45, prefix='DET')
    TEMP1 = MetaNamedField( "TEMP1", "board", description="temperature [celcius]", unit="c")
    TEMP1.set_to(m,  6.7, prefix='SENS1')
    print(repr(m))
    assert DIT.get_from(m, prefix='DET') == 3.45
    assert TEMP1.get_from(m,  prefix='SENS1') == 6.7
    
    from pydantic import NonNegativeInt
    w = WithParser()
    w.vtype = NonNegativeInt 
    w.vtype = (str, float)
    print( w._parsers) 
    


