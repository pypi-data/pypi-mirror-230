from __future__ import annotations

import io
from enum import Enum
from typing import Annotated, Any, Type, TypeVar
from pydantic import GetCoreSchemaHandler, PlainSerializer
from pydantic_core import core_schema
from typing_extensions import Self



class BaseEnum(Enum):
    
    def __str__(self):
        return self.value
    
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema()
        )
    
    @classmethod
    def validate(cls, v: str):
        value = v
        try:
            value = cls[v]
        except KeyError:
            value = cls(v)
        finally:
            return value
    
    @staticmethod
    def serialize(v: 'BaseEnum'):
        if isinstance(v, BaseEnum):
            return v.name
        return v
    
    @classmethod
    def option(cls, member: Self, default: str = None) -> str:
        selected = 'selected' if default in (member.name, member.value) else ""
        return f'<option id="{cls.__name__}.{member.name}" value="{member.name}" {selected}>{member.value}</option>'
    
    @classmethod
    def options(cls, default: str = None):
        with io.StringIO() as file:
            for member in cls.__members__.values():
                file.write(cls.option(member, default))
            return file.getvalue()




class Months(BaseEnum):
    JAN = 1
    FEV = 2
    MAR = 3
    ABR = 4
    MAI = 5
    JUN = 6
    JUL = 7
    AGO = 8
    SET = 9
    OUT = 10
    NOV = 11
    DEZ = 12
    
    
class Gender(BaseEnum):
    M = 'Masculino'
    F = 'Feminino'
    N = 'Não Binário'
    G = 'Trans Masculino'
    W = 'Trans Feminino'
    
    
class ProfileName(BaseEnum):
    Doctor = 'Médico'
    Patient = 'Paciente'
    Therapist = 'Terapeuta'
    Employee = 'Funcionário'