from __future__ import annotations

import io
from abc import ABC
from collections import deque, UserDict, UserList, UserString
from collections.abc import Sequence
from typing import Any, Callable, ClassVar, Optional, overload, Union
from typing_extensions import Self

from . import functions as fn

__all__ = [
        'DataList',
        'Li',
        'A',
        'Span',
        'H1',
        'H2',
        'H3',
        'H4',
        'H5',
        'H6',
        'Div',
        'BaseElement',
        'Element',
        'Document',
        'Option',
        'HR',
        'Ol',
        'Ul',
        'TagNamedElement',
        'Button',
        'ElementStyles',
        'ElementMeta',
        'ElementHTMX',
        'ElementChildren',
        'ElementAttributes',
        'ElementProperties',
        'ElementClassNames',
        'IoDocument',
        'Script'
]


EMPTY: tuple[str, ...] = ('input', 'img', 'meta', 'hr', 'br', 'link')


class ElementMeta(ABC):
    ...

class BaseElement(ABC):
    ...

    
class ElementClassNames(UserList, ElementMeta):
    def __init__(self, value: str | list[str]):
        super().__init__([*value] if isinstance(value, (list, tuple, deque)) else [value] if value else [])
        
    def __str__(self):
        if len(self.data) > 0:
            return f'class="{fn.join(self.data)}"'
        return ''
    
class ElementAttributes(UserList, ElementMeta):
    def __str__(self):
        if len(self.data) > 0:
            return fn.join(self.data)
        return ''
    
class ElementProperties(UserDict, ElementMeta):
    def __str__(self):
        if self.data:
            return fn.join(self.data, underscored=False, sep=' ')
        return ''

class ElementHTMX(UserDict, ElementMeta):
    def __str__(self):
        if self.data:
            return fn.join(self.data, prefix='data-hx-', underscored=False, sep=' ')
        return ''
    
class ElementStyles(UserDict, ElementMeta):
    def __str__(self):
        if self.data:
            return f'style="{fn.join(self.data, junction=": ", sep="; ", boundary="", underscored=False)}"'
        return ''
    

class ElementChildren(deque, ElementMeta):
    def __init__(self, data: Sequence[Element | str] | Element | str | None = None):
        super().__init__()
        self.include(data)
        
    def __str__(self):
        return fn.join(self)
    
    @overload
    def include(self, data: None) -> None:...
    
    @overload
    def include(self, data: Element | str) -> None:...
    
    @overload
    def include(self, data: Sequence[Element | str]) -> None:...
    
    def include(self, data: Sequence[Element | str] | Element | str) -> None:
        if isinstance(data, (Element, str)):
            self.append(data)
        elif isinstance(data, Sequence):
            self.extend(data)



class Element(UserString):
    def __init__(self, tag: str | None, *args: str, **kwargs):
        self._tag = tag
        if self._tag is None:
            super().__init__('')
        else:
            self._class_name = ElementClassNames(kwargs.pop('class_names', list()))
            self._htmx: ElementHTMX = ElementHTMX(kwargs.pop('htmx', dict()))
            self._before = ElementChildren(kwargs.pop('before', list()))
            self._children = ElementChildren(kwargs.pop('children', list()))
            self._after = ElementChildren(kwargs.pop('after', list()))
            self._styles = ElementStyles(kwargs.pop('styles', dict()))
            self._attributes = ElementAttributes([i for i in args if isinstance(i, str)])
            self._properties = ElementProperties(kwargs)
            super().__init__(str(self))
        
    def __html__(self):
        return str(self)
        
    @property
    def tag(self):
        return self._tag
    
    @property
    def id(self):
        return self.properties.get('id', '')
    
    @id.setter
    def id(self, value: str):
        self.properties.update(id=value)
        
    @property
    def class_names(self):
        return self._class_name
    
    @property
    def htmx(self):
        return self._htmx
    
    @property
    def children(self):
        return self._children
    
    @property
    def styles(self):
        return self._styles
    
    @property
    def attributes(self):
        return self._attributes
    
    @property
    def properties(self):
        return self._properties
    
    @property
    def before(self):
        return self._before
    
    @property
    def after(self):
        return self._after
        
    def __str__(self):
        if self.tag in EMPTY:
            data = f'{self.before}<{self.tag} {self.htmx} {self.class_names} {self.properties} {self.styles} ' \
                   f'{self.attributes}>{self.after}'
        else:
            data = f'{self.before}<{self.tag} {self.htmx} {self.class_names} {self.properties} {self.styles} ' \
                   f'{self.attributes}>{self.children}</{self.tag}>{self.after}'
        return fn.remove_extra_whitespaces(data)
    
        
    def add_styles(self, **styles) -> Self:
        self.styles.data.update(**styles)
        return self
    
    def add_properties(self, **kwargs) -> Self:
        self.properties.data.update(kwargs)
        return self
    
    @overload
    def add_children(self, data: Element | str) -> Self:...
    
    @overload
    def add_children(self, data: Sequence[Element | str]) -> Self:...

    def add_children(self, data: Element | str) -> Self:
        if isinstance(data, (Element, str)):
            self.children.append(data)
        elif isinstance(data, Sequence):
            self.children.extend(data)
        return self
    
    def append_child(self, child: Element | str) -> Self:
        self.children.append(child)
        return self
    
    def append_before(self, child: Element | str) -> Self:
        self.before.append(child)
        return self
    
    def append_after(self, child: Element | str) -> Self:
        self.after.append(child)
        return self
    
    def prepend_child(self, child: Element | str) -> Self:
        self.children.appendleft(child)
        return self
    
    def prepend_before(self, child: Element | str) -> Self:
        self.before.appendleft(child)
        return self
    
    def prepend_after(self, child: Element | str) -> Self:
        self.after.appendleft(child)
        return self
    
    
class TagNamedElement(Element):
    TAG: ClassVar[str] = None
    def __init__(self, *args: str, **kwargs):
        super().__init__(self.TAG or self.__class__.__name__.lower(), *args, **kwargs)


class Div(TagNamedElement):
    ...


class Button(TagNamedElement):
    ...


class DataList(TagNamedElement):
    ...


class H1(TagNamedElement):
    ...


class H2(TagNamedElement):
    ...


class H3(TagNamedElement):
    ...


class H4(TagNamedElement):
    ...


class H5(TagNamedElement):
    ...


class H6(TagNamedElement):
    ...


class HR(TagNamedElement):
    ...


class Span(TagNamedElement):
    ...


class Ul(TagNamedElement):
    ...


class A(TagNamedElement):
    ...


class Ol(TagNamedElement):
    ...


class Li(TagNamedElement):
    ...


class Script(TagNamedElement):
    ...


class Option(TagNamedElement):
    def __init__(self, value: str = None, children: str | Element | list[Element | str] = None, id: str = None, **kwargs):
        super().__init__(value=value, children=children, id=id, **kwargs)


class Document(ElementChildren):
    def __init__(self, children: Element | str | list[Element | str] = None, **kwargs):
        self.kwargs = kwargs
        super().__init__(children or list())
        
        
    def __str__(self):
        return '\n'.join([str(i) for i in self])
    
        
    def file(self):
        return IoDocument(children=[*self])
        
        
class IoDocument(io.StringIO):
    def __init__(self, children: Element | str | list[Element | str] = None, *args, **kwargs):
        self.children: Document[Element | str] = Document(children if isinstance(children, list) else list() if not children else [children])
        self.kwargs = kwargs
        super().__init__(*args)

    def __str__(self):
        try:
            return self.getvalue()
        finally:
            self.close()

    def __html__(self):
        return str(self)
    
    def include(self, *args):
        self.children.include(args)

    def append(self, child: Element | str):
        self.children.append(child)

    def extend(self, children: [Element | str]):
        self.children.extend(children)

    def prepend(self, child: Element | str):
        self.children.appendleft(child)
        
    def wrap(self, parent: Element):
        parent.children.extend(self.children)
        self.__init__(parent)

    def getvalue(self) -> str:
        super().__init__(str(self.children))
        return super().getvalue()
        

