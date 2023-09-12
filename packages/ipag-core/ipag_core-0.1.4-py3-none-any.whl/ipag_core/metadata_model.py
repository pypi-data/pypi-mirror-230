""" So base model for metadata """


from datetime import date, datetime
from typing_extensions import Annotated

from pydantic import AfterValidator
from ipag_core.metadata import MetaField, MetadataIo
from ipag_core import types

ipag_metadata_model =  dict( 

    datetime = MetaField( "DATETIME", "ISO Date time", (types.build(None, datetime, str), datetime) ), 
    date = MetaField("DATE" , "ISO Date", (types.build(None, datetime, str), date)  ), 
    dit = MetaField('DIT',  "[s] Detector integration time", float), 
    ndit = MetaField('NDIT', "# Number of integration", int), 
)

ipag_metadata_io = MetadataIo(ipag_metadata_model)

if __name__ == "__main__":
    m = {}
    ipag_metadata_model['datetime'].set_to( m , datetime.now())
    print( m ) 
    print ( repr( ipag_metadata_model['datetime'].get_from( m ) ))

