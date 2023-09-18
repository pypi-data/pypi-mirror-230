from pathlib import Path
from typing import BinaryIO, Union, Optional, Iterator, Dict, TypedDict

from .MessageTypes import MessageTypes


class cIO_wrapper(object):
    def __init__(self, stream: BinaryIO):
        ...

    ...


class BusMsg(object):
    timestamp: float
    id: int
    data: bytes
    message_type: MessageTypes
    ...


class cCANDataFrameMsg(BusMsg):
    ...

class cCANErrorFrameMsg(BusMsg):
    error_type: int
    ...

class cLINFrameMsg(BusMsg):
    ...


class MdfMetaData(TypedDict):
    name: str
    description: str
    unit: str
    read_only: bool
    value_type: str
    value_raw: str
    ...


class MdfFile(object):
    def __init__(self, io: Union[BinaryIO, cIO_wrapper, Path, str], passwords: Optional[Dict[str, str]] = None, buffer_size: Optional[int] = None):
        ...

    def get_iterator(self, message_types: Optional[Union[MessageTypes, int]] = None) -> Iterator[BusMsg]:
        ...

    def get_first_measurement(self) -> float:
        ...
    
    def get_metadata(self) -> Dict[str, MdfMetaData]:
        ...

    def get_data_frame(self):
        ...

    def get_can_data_frame(self):
        ...

    def get_can_error_data_frame(self):
        ...

    def get_lin_data_frame(self):
        ...

    ...
