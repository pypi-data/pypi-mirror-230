#!/usr/bin/python3
# -*- coding: utf-8 -*-


class DocExporter:
    """Exporte une documentation d'une façon donnée."""


    def open(self, name, fullname):
        """Initialise les propriétés utiles."""

        pass


    def close(self):
        """Termine l'édition de la documentation."""

        pass


    def show_list_sub_modules(self, gparent, parent, others, builder):
        """Affiche des renvois vers les sous-parties présentes."""

        pass


    def show_list_sub_classes(self, parent, classes, builder):
        """Affiche des renvois vers les sous-parties présentes."""

        pass


    def describe_module(self, desc):
        """Affiche la description du module courant."""

        pass


    def start_main_section(self, title):
        """Affiche un en-tête pour la zone des classes."""

        pass


    def show_class_info(self, name, desc):
        """Affiche les informations générales d'une classe."""

        pass


    def show_info_section(self, title):
        """Affiche une section d'informations particulières."""

        pass


    def begin_hierarchy_level(self):
        """Démarre une arborescence hiérarchique."""

        pass


    def terminate_hierarchy_level(self):
        """Arrête une arborescence hiérarchique."""

        pass


    def print_hierarchy_level(self, fullname, name, page, level):
        """Affiche un élément hiérarchique."""

        pass


    def show_constant_info(self, name):
        """Affiche un élément de type 'constant'."""

        pass


    def show_data_info(self, name, value):
        """Affiche un élément de type 'donnée'."""

        pass

    def show_attribute_info(self, name, desc):
        """Affiche un élément de type 'attribut'."""

        pass


    def show_callable_info(self, ret, name, args, desc):
        """Affiche un élément de type 'routine'."""

        pass
