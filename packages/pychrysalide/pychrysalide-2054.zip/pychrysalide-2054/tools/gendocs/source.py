#!/usr/bin/python3
# -*- coding: utf-8 -*-


class SourceReader(object):
    """Lecteur attentif de code source."""


    def __init__(self, parent, name, output):
        """Initialise l'identité d'une partie de documentation."""

        self._parent = parent
        self._name = name
        self._output_cls = output
        self._output = output()


    def build(self, validation):
        """Construit de façon générique une documentation complète."""

        self._output.open(self._name, self._fullname)

        others, mod_desc = self.prepare_module()
        classes = self.list_all_classes()

        # Contenu du module

        self._output.start_main_section('Content')

        self._output.show_list_sub_modules(self._parent, self._fullname, others, self.make_path)

        self._output.show_list_sub_classes(self._fullname, classes, self.make_path)

        self._output.describe_module(mod_desc)

        # Description des classes

        if len(classes) > 0:

            self._output.start_main_section('Classes')

            for cls in classes:
                self.describe_class(cls, validation)

        # Eléments propres au module

        self.describe_module_items()

        # Fermeture et suite

        self._output.close()

        for o in others:
            o.build(validation)
