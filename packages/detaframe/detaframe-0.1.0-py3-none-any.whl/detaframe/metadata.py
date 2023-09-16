from __future__ import annotations

import dataclasses
from collections import UserString
from typing import Any, Callable, Generic, Optional, overload, TypeVar, Annotated, Union
from pydantic.fields import FieldInfo

from detaframe import  functions as fn, keymodel as bm

TT = TypeVar('TT', bound=type)


class ContainerClassName(UserString):
    ...

class FormFieldConfig(UserString):
    ...

@dataclasses.dataclass
class MetaData:
    form_field: Optional[str] = None
    step: Optional[Union[int, float]] = None
    height: Optional[str] = None
    tables: list[str] = dataclasses.field(default_factory=list)
    col: Optional[str] = 'col-12'
    config: Optional[str] = ''
    
    def __repr__(self):
        fds = (f for f in dataclasses.fields(self) if getattr(self, f.name))
        return 'MetaData({})'.format(', '.join([f'{f.name}={getattr(self, f.name)}' for f in list(fds)]))

    def asdict(self):
        return dataclasses.asdict(self)
    
    @property
    def tag(self):
        if self.form_field:
            if self.form_field in ['select', 'textarea']:
                return self.form_field
            return 'input'
        return None
    
    @property
    def input_type(self):
        if self.tag == 'input':
            return self.form_field
        return None
    
@dataclasses.dataclass
class FullMetaData(MetaData):
    name: Optional[str] = None
    model: Optional[bm.ModelType] = None
        
    @property
    def field_metadata(self):
        if info:= self.field_info:
            return info.metadata
        return None
    
    @property
    def field_info(self):
        return get_field_info(self.model, self.name)


def get_metadata(meta_type: type[dict] | type[MetaData] | type[str] | type[list], metadata: FieldInfo.metadata) -> \
list[dict | str]:
    result = [i for i in metadata if isinstance(i, meta_type)]
    print(result)
    return result


@overload
def merge_metadata(meta_type: type[list], metadata: FieldInfo.metadata) -> list: ...


@overload
def merge_metadata(meta_type: type[dict] | type[MetaData], metadata: FieldInfo.metadata) -> dict: ...


@overload
def merge_metadata(meta_type: type[str], metadata: FieldInfo.metadata) -> list[str]: ...


def merge_metadata(meta_type: type[dict] | type[str] | type[list], metadata: FieldInfo.metadata):
    if meta_type == MetaData:
        result = dict()
        for item in fn.filter_by_type(metadata, meta_type):
            result.update(**{k:v for k, v in item.asdict().items() if v})
        return result
    elif meta_type == dict:
        result = dict()
        for item in fn.filter_by_type(metadata, meta_type):
            result.update(**item)
        return result
    elif issubclass(meta_type, str):
        return fn.filter_by_type(metadata, meta_type)
    
    
def get_field_info(model: type[bm.ModelType], name: str) -> FieldInfo:
    return model.model_fields[name]

def get_field_metadata(model: type[bm.ModelType], name: str) -> list:
    return get_field_info(model, name).metadata


def fullmetadata(model: type[bm.ModelType], name: str) -> FullMetaData:
    metadata = get_field_metadata(model, name)
    return FullMetaData(model=model, name=name, *metadata)