#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import deque
from source import SourceReader
import importlib
import inspect


is_callable = lambda t: inspect.isroutine(t[2]) \
              or isinstance(t[2], staticmethod) \
              or isinstance(t[2], classmethod)

is_attribute = lambda t: not(is_callable(t)) and (inspect.isgetsetdescriptor(t[2]) or isinstance(t[2], property))

is_constant = lambda t: not(is_attribute(t) or is_callable(t)) and t[0].isupper()

is_data = lambda t: not(is_constant(t) or is_attribute(t) or is_callable(t))


class PythonReader(SourceReader):
    """Lecteur attentif de code Python."""


    def __init__(self, parent, name, output):
        """Initialise l'identité d'une partie de documentation."""

        super(PythonReader, self).__init__(parent, name, output)

        self._fullname = self.make_path(parent, name)


    def make_path(self, parent, target):
        """Construit le chemin complet d'un élément d'un module donné."""

        return parent + '.' + target if parent != None else target


    def prepare_module(self):
        """Charge le module courant et liste tous ses sous-modules."""

        result = [ ]

        self._module = importlib.import_module(self._fullname)

        submodules = inspect.getmembers(self._module, inspect.ismodule)

        for name, inst in submodules:
            other = PythonReader(self._fullname, name, self._output_cls)
            result.append(other)

        return result, self._module.__doc__


    def list_all_classes(self):
        """Liste toutes les classes présentes dans le module courant."""

        result = [ ]

        classes = inspect.getmembers(self._module, inspect.isclass)

        for name, inst in classes:
            result.append(name)

        return result


    def is_visible(self, name):
        """Sélectionne les éléments à faire apparaître dans une documenation."""

        # On évite les noms spéciaux internes et redondants
        if name in {'__author__', '__builtins__', '__cached__', '__credits__',
                    '__date__', '__doc__', '__file__', '__spec__',
                    '__loader__', '__module__', '__name__', '__package__',
                    '__path__', '__qualname__', '__slots__', '__version__'}:
            return False

        # Les noms spéciaux restants ne sont pas invisibles
        if name.startswith('__') and name.endswith('__'):
            return True

        return not name.startswith('_')


    def describe_module_items(self):
        """Décrit tous les éléments du module qui n'ont pas déjà été présentés."""

        processed = lambda v: inspect.ismodule(v) or inspect.isclass(v)

        attrs = [(key, self._module, self._module.__dict__[key])
                 for key in dir(self._module)
                 if self.is_visible(key) and not(processed(self._module.__dict__[key]))
        ]

        self.describe_attribs_list(attrs)


    def describe_class(self, name, validation):

        cls = getattr(self._module, name)

        self._output.show_class_info(cls.__name__, cls.__doc__)

        self._output.show_info_section('Class Hierarchy')

        self._output.begin_hierarchy_level()

        mro = deque(inspect.getmro(cls))
        mro.reverse()
        level = 0

        for base in mro:

            if (level + 1) == len(mro) or not validation(base.__module__):
                page = None
            else:
                page = base.__module__

            fullname = self.make_path(base.__module__, base.__name__)

            self._output.print_hierarchy_level(fullname, base.__name__, page, level)

            level = level + 1

        self._output.terminate_hierarchy_level()

        attrs = [(name, owner, value)
                 for (name, kind, owner, value) in inspect.classify_class_attrs(cls)
                 if owner == cls and self.is_visible(name)
        ]

        self.describe_attribs_list(attrs)


    def describe_attribs_list(self, attrs):
        """Describe some module/class attributes in a given order."""

        def filter_attrs(lst, predicate, title):

            remaining = []

            first = True

            for a in lst:
                if predicate(a):
                    if first:
                        self._output.show_info_section(title)
                        first = False
                    self.describe_item(a)
                else:
                    remaining.append(a)

            return remaining

        attrs = filter_attrs(attrs, is_constant, 'Constants')
        attrs = filter_attrs(attrs, is_data, 'Data')
        attrs = filter_attrs(attrs, is_attribute, 'Attributes')
        attrs = filter_attrs(attrs, is_callable, 'Methods')

        assert(len(attrs) == 0)


    def describe_item(self, item):
        """Describe one module/class item."""

        name, homecls, value = item

        if is_callable(item):

            value = getattr(homecls, name)

            if hasattr(value, '__text_signature__') and value.__text_signature__ != None:

                args = ''

                for p in inspect.signature(value).parameters.values():
                    if len(args) > 0:
                        args = args + ', '
                    args = args + p.name

            else:

                args = '...'

            # method_descriptor -> value.__doc__

            doc = getattr(homecls, name).__doc__

            self._output.show_callable_info('', name, args, doc)


        elif is_attribute(item):

            self._output.show_attribute_info(name, value.__doc__)

        elif is_constant(item):

            self._output.show_constant_info(name)

        elif is_data(item):

            self._output.show_data_info(name, value)


        else:

            assert(False)
