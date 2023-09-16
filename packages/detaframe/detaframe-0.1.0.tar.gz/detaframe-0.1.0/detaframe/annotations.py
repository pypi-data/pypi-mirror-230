from __future__ import annotations

import datetime
import re
from decimal import Decimal
from typing import Optional, TypeVar, Annotated
from pydantic import AfterValidator, BeforeValidator, Field, PlainSerializer

from . import enums as en, keymodel as bm, functions as fn, metadata as mt

GenericType = TypeVar('GenericType', bound=type)
StrType = TypeVar('StrType', bound=str)
NumberType = TypeVar('NumberType', float, int, Decimal)


def string_to_list(v: list[str] | str):
    if v in ['', None]:
        return []
    elif isinstance(v, str):
        return fn.filter_not_none(re.split(r'[\n;]', v))
    elif isinstance(v, list):
        return fn.filter_not_none(v)
    return v

def list_to_string(value):
    if isinstance(value, list):
        return ', '.join(value)
    return value

OptionalField = Annotated[Optional[GenericType], BeforeValidator(lambda x: x if x else None), Field(None)]
BaseEnumType = TypeVar('BaseEnumType', bound=en.BaseEnum)
EnumField = Annotated[BaseEnumType, PlainSerializer(en.BaseEnum.serialize, return_type=str)]
OptionalDate = Annotated[OptionalField[datetime.date], Field(None)]

TextField = Annotated[StrType, mt.MetaData(form_field='text')]
NumberField = Annotated[NumberType, mt.MetaData(form_field='number')]
GenericIntNumber = Annotated[int, mt.MetaData(step='1', form_field='number')]
GenericFloatNumber = Annotated[float, mt.MetaData(step='0.01', form_field='number')]
TextAreaField = Annotated[mt.TT, mt.MetaData(form_field='textarea', height='200px')]
CheckBox = Annotated[bool, mt.MetaData(form_field='checkbox')]
NoFormField = Annotated[GenericType, mt.MetaData(form_field=None)]
Percentage = Annotated[float, Field(0, ge=0, le=100)]

DateField = Annotated[datetime.date, Field(title='data'), mt.MetaData(form_field='date')]
OptionalKeyField = Annotated[Optional[bm.KeyModel.Key], PlainSerializer(lambda x: x.data, return_type=str), BeforeValidator(lambda x: bm.KeyModel.Key(x)), mt.MetaData(form_field='text')]
KeyField = Annotated[bm.KeyModel.Key, PlainSerializer(lambda x: x.data, return_type=str), BeforeValidator(lambda x: bm.KeyModel.Key(x)), mt.MetaData(form_field='text')]
DefaultDate = Annotated[datetime.date, Field(default_factory=datetime.date.today), PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='date')]
DefaultDateTime = Annotated[datetime.datetime, Field(default_factory=datetime.datetime.now), PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='datetime-local')]
ModelType = TypeVar('ModelType', bound=bm.KeyModel)
DecimalField = Annotated[Decimal, PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='number', step='0.01')]
OptionalDecimalField = Annotated[Optional[Decimal], PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='number', step='0.01')]
PositiveDecimal = Annotated[DecimalField, Field(ge=0)]
CapitalName = Annotated[str, mt.MetaData(form_field='text'), AfterValidator(lambda x: fn.join([i.title() for i in x.split()]))]
PositiveInt = Annotated[int, mt.MetaData(form_field='number', step='1'), Field(ge=0)]
OptionalPositiveInt = Annotated[OptionalField[int], mt.MetaData(form_field='number', step='1'), Field(ge=0, default=None)]
CreatedDate = Annotated[datetime.date, mt.MetaData(form_field=None), Field(title='data da criação')]
CreatedDateTime = Annotated[datetime.datetime, mt.MetaData(form_field=None), Field(title='data e hora da criação', default_factory=fn.now)]
StringListField = Annotated[list[str], BeforeValidator(string_to_list), Field(default_factory=list)]

# OptionalField = Annotated[Optional[mt.TT], BeforeValidator(lambda x: x if x else None)]
# BaseEnumType = TypeVar('BaseEnumType', bound=en.BaseEnum)
# EnumField = Annotated[BaseEnumType, PlainSerializer(en.BaseEnum.serialize, return_type=str), mt.MetaData(form_field='select')]
# OptionalDate = Annotated[OptionalField[datetime.date], mt.MetaData(form_field='date')]
# TextField = Annotated[mt.TT, mt.MetaData(form_field='text')]
# NumberField = Annotated[mt.TT, mt.MetaData(form_field='number')]
# GenericIntNumber = Annotated[mt.TT, mt.MetaData(step='1', form_field='number')]
# GenericFloatNumber = Annotated[mt.TT, mt.MetaData(step='0.01', form_field='number')]
# TextAreaField = Annotated[mt.TT, mt.MetaData(form_field='textarea', height='200px')]
# CheckBox = Annotated[bool, mt.MetaData(form_field='checkbox')]
# NoFormField = Annotated[mt.TT, mt.MetaData(form_field=None)]
# Percentage = Annotated[float, Field(0, ge=0, le=100), mt.MetaData(form_field='number', step='1')]
# DateField = Annotated[datetime.date, Field(title='data'), mt.MetaData(form_field='date')]
# OptionalKeyField = Annotated[Optional[bm.KeyModel.Key], PlainSerializer(lambda x: x.data, return_type=str), BeforeValidator(lambda x: bm.KeyModel.Key(x)), mt.MetaData(form_field='text')]
# KeyField = Annotated[bm.KeyModel.Key, PlainSerializer(lambda x: x.data, return_type=str), BeforeValidator(lambda x: bm.KeyModel.Key(x)), mt.MetaData(form_field='text')]
# DefaultDate = Annotated[datetime.date, Field(default_factory=datetime.date.today), PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='date')]
# DefaultDateTime = Annotated[datetime.datetime, Field(default_factory=datetime.datetime.now), PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='datetime-local')]
# ModelType = TypeVar('ModelType', bound=bm.KeyModel)
# DecimalField = Annotated[Decimal, PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='number', step='0.01')]
# OptionalDecimalField = Annotated[Optional[Decimal], PlainSerializer(lambda x: str(x), return_type=str), mt.MetaData(form_field='number', step='0.01')]
# PositiveDecimal = Annotated[DecimalField, Field(ge=0)]
# CapitalName = Annotated[str, mt.MetaData(form_field='text'), AfterValidator(lambda x: fn.join([i.title() for i in x.split()]))]
# PositiveInt = Annotated[int, mt.MetaData(form_field='number', step='1'), Field(ge=0)]
# OptionalPositiveInt = Annotated[OptionalField[int], mt.MetaData(form_field='number', step='1'), Field(ge=0, default=None)]
# CreatedDate = Annotated[datetime.date, mt.MetaData(form_field=None), Field(title='data da criação')]
# CreatedDateTime = Annotated[datetime.datetime, mt.MetaData(form_field=None), Field(title='data e hora da criação', default_factory=fn.now)]
# StringListField = Annotated[list[str], BeforeValidator(string_to_list), Field(default_factory=list)]