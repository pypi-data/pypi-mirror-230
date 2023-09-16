from __future__ import annotations

import dataclasses
from typing import Any, Optional

from annotated_types import Ge, Le
from pydantic_core import PydanticUndefined
from starlette.requests import Request

from . import (element as el, functions as fn, enums as en, metadata as mt, model as md)


class BasicFormField(el.Element):
    def __init__(self, name: str, model: md.ModelType | type[md.ModelType], *args, **kwargs):
        self.name = name
        self.model = model
        self.item_name = self.model.item_name()
        kwargs['id'] = f'{self.item_name}__{self.name}'
        self.info = mt.get_field_info(model, name)
        kwargs['data-label'] = self.info.title or self.name
        kwargs['class_names'] = 'form-field'
        self.meta = mt.MetaData(**mt.merge_metadata(mt.MetaData, self.info.metadata))
        print(self.info.metadata)
        if col:= mt.get_metadata(mt.ContainerClassName, self.info.metadata):
            kwargs['data-col'] = str(col[0])
        if conf:= mt.get_metadata(mt.FormFieldConfig, self.info.metadata):
            self.meta.config = str(conf[0])
        if ff:= self.meta.form_field:
            if ff not in ['textarea', 'select']:
                super().__init__('input', self.meta.config, *args, name=self.name, type=ff, **kwargs)
            elif ff == 'textarea':
                super().__init__(ff, *args, self.meta.config, name=self.name,  styles=dict(height=self.meta.height), **kwargs)
            else:
                super().__init__(ff, *args, self.meta.config, name=self.name, **kwargs)
        else:
            super().__init__('input', 'disabled', self.meta.config, name=self.name, styles=dict(display='none'))
        
@dataclasses.dataclass
class FormField:
    model: type[model.ModelType] = None
    name: str = None
    default: Any = None
    metadata: mt.MetaData = None
    
    def __post_init__(self):
        self.metadata = mt.MetaData(**mt.merge_metadata(mt.MetaData, self.field_metadata))
        
    @property
    def tag(self):
        return self.metadata.tag
    
    @property
    def tables(self):
        return self.metadata.tables
    
    @property
    def input_type(self):
        return self.metadata.input_type
    
    def input_number_setup(self):
        metadata = self.field_metadata
        arg = f'step="{self.metadata.step or 1}" '
        if ge := fn.filter_by_type(metadata, Ge):
            arg += f'min="{fn.find_numbers(repr(ge[-1]))[0]}" '
        if le := fn.filter_by_type(metadata, Le):
            arg += f'max="{fn.find_numbers(repr(le[-1]))[0]}" '
        return arg
    
    @property
    def required(self):
        return 'required' if self.field_info.is_required() else ''
    
    @property
    def field_info(self):
        return self.model.model_fields.get(self.name)
    
    @property
    def field_annotation(self):
        if self.field_info:
            return self.field_info.annotation
        return None
    
    @property
    def field_metadata(self):
        if self.field_info:
            return self.field_info.metadata
        return []
    
    @property
    def default_value(self):
        if self.default not in [None, PydanticUndefined]:
            return self.default
        elif isinstance(self.model, type):
            return self.field_info.get_default(call_default_factory=True)
        return getattr(self.model, self.name)
    
    @property
    def value(self):
        default = self.default_value
        if default not in [None, PydanticUndefined]:
            if self.tag == 'input':
                if self.input_type == 'checkbox':
                    return ' checked '
                return default or ''
            elif self.tag == 'textarea':
                return default or ''
        elif self.tag == 'select':
            if annotation := self.field_annotation:
                if issubclass(annotation, en.BaseEnum):
                    return annotation.options(default)
        return ''
    
    @property
    def field_id(self):
        return f'{self.model.item_name()}_{self.name}'
    
    @property
    def label_id(self):
        return f'{self.field_id}_label'
    
    @property
    def container_id(self):
        return f'{self.field_id}_container'
    
    @property
    def datalist_id(self):
        return f'{self.field_id}_datalist'
    
    @staticmethod
    def table_htmx(table: str):
        return el.Div(htmx=dict(get=f'/options/{fn.cls_name_to_slug(table)}', trigger='load', swap='outerHTML'))
        
    @property
    def datalist(self):
        return el.DataList(id=self.datalist_id, children=[self.table_htmx(table) for table in self.tables])

    
    @property
    def title(self):
        return self.field_info.title or self.name
    
    @property
    def label(self):
        if self.input_type == 'checkbox':
            return el.Element('label', id=self.label_id, class_names='form-check-label', children=self.title, **{'for': self.field_id})
        return el.Element('label', id=self.label_id, class_names='form-label', children=self.title, **{'for': self.field_id})
    
    @property
    def field_class_name(self):
        if self.input_type =='checkbox':
            return 'form-check-input'
        elif self.input_type =='range':
            return 'form-range'
        elif self.tag == 'select':
            return 'form-select'
        return 'form-control'
    
    def render_form_field(self):
        if self.tag:
            if self.tag == 'input':
                if self.input_type == 'checkbox':
                    return el.Element(self.tag, self.required, self.value, name=self.name, type=self.input_type, id=self.field_id, class_names=self.field_class_name)
                elif self.is_key:
                    return el.Element(self.tag, self.required, name=self.name, type=self.input_type, value=self.value, id=self.field_id,
                                      class_names=self.field_class_name, list=self.datalist_id, placeholder=self.name)
                elif self.input_type == 'number':
                    return el.Element(self.tag, self.required, self.input_number_setup(), name=self.name, type=self.input_type, value=self.value, id=self.field_id,
                                      class_names=self.field_class_name, placeholder=self.name)
                return el.Element(self.tag, self.required, name=self.name, type=self.input_type, value=self.value, id=self.field_id, class_names=self.field_class_name, placeholder=self.name)
            elif self.tag == 'textarea':
                return el.Element(self.tag, self.required, name=self.name, children=self.value, id=self.field_id,
                                  class_names=self.field_class_name, placeholder=self.name, styles=dict(height=self.metadata.height))
            
            return el.Element(self.tag, self.required, name=self.name,  children=self.value, id=self.field_id, class_names=self.field_class_name, placeholder=self.name)
        return ''
    
    @property
    def is_key(self):
        return self.field_annotation in [md.KeyModel.Key, Optional[md.KeyModel.Key]]
    
    
    def element(self):
        if self.input_type == 'checkbox':
            return el.Div(class_names='form-check me-2 mb-2 form-switch', children=[self.render_form_field(), self.label])
        elif self.tag == 'input':
            if self.is_key:
                return el.Div(class_names='form-floating mb-2', children=[
                        self.render_form_field(),
                        self.label,
                        self.datalist
                ])
        return el.Div(class_names='form-floating mb-2', children=[self.render_form_field(), self.label])


class Form(el.TagNamedElement):
    def __init__(
            self,
            model: type[md.KeyModel] | md.KeyModel,
            request: Request,
            *args,
            preset: dict[str, str] = None,
            title: str = None,
            button_content: str = 'salvar',
            button_class_name: str = 'btn btn-dark form-control',
            **kwargs
    ):
        self.request = request
        self.preset = preset or dict()
        self.button_content = button_content
        self.button_class_name = button_class_name
        action = kwargs.pop('action', None)
        if isinstance(model, type):
            if issubclass(model, md.KeyModel):
                self.model = model
                self.instance = None
                self._title = title or f'Adicionar {self.model.singular()}'
                action = action or f'/new/{self.model.item_name()}'
        
        else:
            self.instance = model
            self.model = type(self.instance)
            self._title = title or f'Atualizar {self.model.singular()}'
            action = action or f'/update/{self.model.item_name()}/{self.instance.key}'

        super().__init__(*args, method='post', action=action, **kwargs)
        # self.children.append(el.H3(children=self._title))

        for k in self.model.model_fields.keys():
            ff = FormField(self.instance or self.model, k, self.preset.get(k))
            if ff.tag:
                self.children.append(ff.element())
        
        self.children.append(self.button())
        if hasattr(self.model, '__form_script__'):
            self.children.append(self.model.__form_script__())
        self.class_names.append('p-3')
        
    def request_data(self):
        data = {**self.request.query_params}
        data.update({**self.request.path_params})
        data.update({**self.request.session})
        return data
    
    def button(self):
        return el.Element('button', class_names=self.button_class_name, children=self.button_content)
        
        
