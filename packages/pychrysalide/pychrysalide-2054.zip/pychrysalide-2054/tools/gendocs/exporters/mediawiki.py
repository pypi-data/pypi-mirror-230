#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pywikibot
from exporter import DocExporter


class MWExporter(DocExporter):
    """Exporte une documentation vers un site Mediawiki."""


    def open(self, name, fullname):
        """Initialise les propriétés utiles."""

        self._site = pywikibot.Site()
        self._page = pywikibot.Page(self._site, self._build_page_name(fullname))

        self._content = '__NOTOC__'
        self._content += '\n'


    def close(self):
        """Termine l'édition de la documentation."""

        if self._content != self._page.text:
            self._page.text = self._content
            self._page.save('API update')


    def _build_page_name(self, orig):
        """Définit le nom final d'une page faisant référence à un module."""

        return orig + ' Python Module'


    def show_list_sub_modules(self, gparent, parent, others, builder):
        """Affiche des renvois vers les sous-parties présentes."""

        if len(others) > 0 or gparent != None:

            self._content += '<div class="h2">\n==Sub modules==\n</div>\n'

            if gparent != None:
                self._content += '* [[%s|..]]\n' % self._build_page_name(gparent)

            for o in others:
                fullname = builder(parent, o._name)
                self._content += '* [[%s|%s]]\n' % (self._build_page_name(fullname), fullname)


    def show_list_sub_classes(self, parent, classes, builder):
        """Affiche des renvois vers les sous-parties présentes."""

        if len(classes) > 0:

            self._content += '<div class="h2">\n==Classes==\n</div>\n'

            for cls in classes:
                self._content += '* [[%s#%s|%s]]\n' % (self._build_page_name(parent), cls, builder(parent, cls))


    def describe_module(self, desc):
        """Affiche la description du module courant."""

        self._content += '<div class="h2">\n==Description==\n</div>\n'

        self._content += '<div class="fakepre info">%s</div>\n' % desc


    def start_main_section(self, title):
        """Affiche un en-tête pour la zone des classes."""

        self._content += '<div class="h1">\n=%s=\n</div>\n' % title


    def show_class_info(self, name, desc):
        """Affiche les informations générales d'une classe."""

        self._content += '<div id="%s" class="h2">\n==%s==\n</div>\n' % (name, name)

        self._content += '<pre class="fakepre info">%s</pre>\n' % desc


    def show_info_section(self, title):
        """Affiche une section d'informations particulières."""

        self._content += '<div class="h3">\n===%s===\n</div>\n' % title


    def begin_hierarchy_level(self):
        """Démarre une arborescence hiérarchique."""

        self._content += '<div class="fakepre treeclasses">\n'


    def terminate_hierarchy_level(self):
        """Arrête une arborescence hiérarchique."""

        self._content += '</div>\n\n'


    def print_hierarchy_level(self, fullname, name, page, level):
        """Affiche un élément hiérarchique."""

        if level > 0:

            for i in range(level - 1):
                self._content += ' ' * 5

            self._content += ' ╰── '

        if page != None:
            self._content += '[[%s#%s|' % (self._build_page_name(page), name)

        self._content += fullname

        if page != None:
            self._content += ']]'

        self._content += '\n'


    def show_constant_info(self, name):
        """Affiche un élément de type 'constant'."""

        self._content += '\n'
        self._content += '<span class="constant_name">%s</span>\n' % name


    def show_data_info(self, name, value):
        """Affiche un élément de type 'donnée'."""

        self._content += '\n'
        self._content += '<span class="data_name">%s</span> = ' % name
        self._content += '<span class="data_value">%s</span>\n' % value


    def show_attribute_info(self, name, desc):
        """Affiche un élément de type 'attribut'."""

        self._content += '\n'
        self._content += '<span class="property_name">%s</span>\n' % name
        self._content += '\n'
        self._content += '<span class="property_desc">%s</span>\n' % desc


    def show_callable_info(self, ret, name, args, desc):
        """Affiche un élément de type 'routine'."""

        if args == None:
            args = '()'

        self._content += '\n'
        self._content += '<span class="callable_name">%s</span>(%s)\n' % (name, args)
        self._content += '\n'
        self._content += '<pre class="fakepre callable_desc">%s</pre>\n' % desc
