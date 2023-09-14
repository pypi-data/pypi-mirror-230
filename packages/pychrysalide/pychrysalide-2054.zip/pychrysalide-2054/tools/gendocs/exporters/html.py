#!/usr/bin/python3
# -*- coding: utf-8 -*-

from exporter import DocExporter


class HtmlExporter(DocExporter):
    """Exporte une documentation sous forme HTML."""


    def open(self, name, fullname):
        """Initialise les propriétés utiles."""

        self._filename = fullname + '.html'
        self._fd = open(self._filename, 'w')

        self._fd.write("""\
<HTML>
<HEAD>
    <META http-equiv="Content-Type" content="text/xhtml;charset=UTF-8"/>
    <TITLE>Documentation</TITLE>
    <STYLE>
    <!--
    H1 {
        background-color: rgb(218, 218, 218);
        border: 1px solid rgb(184, 184, 184);
        border-radius: 3px 3px 3px 3px;
        padding: 8px;
    }
    H2 {
        background-color: rgb(238, 238, 238);
        border: 1px solid rgb(204, 204, 204);
        border-radius: 3px 3px 3px 3px;
        padding: 4px;
    }
    .info {
        background-color: #efc;
        border: 1px solid #ac9;
        border-radius: 3px;
        margin-left: 40px;
        padding: 8px;
    }
    .steps {
        font-family: monospace;
    }
    .constant_name {
        font-weight: bold;
    }
    .data_name { 
        font-weight: bold;
    }
    .data_value {
    }
    .property_name { 
        font-weight: bold;
    }
    .property_desc {
        padding-left: 40px;
    }
    .callable_name {
        font-weight: bold;
    }
    .callable_desc {
        padding-left: 40px;
    }
    -->
    </STYLE>
<BODY>
        """)


    def close(self):
        """Termine l'édition de la documentation."""

        self._fd.write("""
</BODY>
</HTML>
        """)

        self._fd.close()


    def _normalize_desc(self, desc):
        """S'assure d'un bon rendu HTML d'un commentaire prévu pour."""

        return desc.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<BR>")



    def show_list_sub_modules(self, gparent, parent, others, builder):
        """Affiche des renvois vers les sous-parties présentes."""

        if len(others) > 0 or gparent != None:

            self._fd.write('<H2>Sub modules</H2>')

            self._fd.write('<UL>')

            if gparent != None:
                self._fd.write('<LI><A href="%s.html">..</A></LI>' % gparent)

            for o in others:
                fullname = builder(parent, o._name)
                self._fd.write('<LI><A href="%s.html">%s</A></LI>' % (fullname, fullname))

            self._fd.write('</UL>')


    def show_list_sub_classes(self, parent, classes, builder):
        """Affiche des renvois vers les sous-parties présentes."""

        if len(classes) > 0:

            self._fd.write('<H2>Classes</H2>')

            self._fd.write('<UL>')

            for cls in classes:
                self._fd.write('<LI><A href="%s.html#%s">%s</A></LI>'
                               % (parent, cls, builder(parent, cls)))

            self._fd.write('</UL>')


    def describe_module(self, desc):
        """Affiche la description du module courant."""

        self._fd.write('<H2>Description</H2>')

        self._fd.write('<P class="info">%s</P>' % self._normalize_desc(desc))


    def start_main_section(self, title):
        """Affiche un en-tête pour la zone des classes."""

        self._fd.write('<H1>%s</H1>' % title)


    def show_class_info(self, name, desc):
        """Affiche les informations générales d'une classe."""

        self._fd.write('<A name="%s"><H2>%s</H2></A>' % (name, name))

        self._fd.write('<P class="info">%s</P>' % self._normalize_desc(desc))


    def show_info_section(self, title):
        """Affiche une section d'informations particulières."""

        self._fd.write('<H3>%s</H3>' % title)


    def print_hierarchy_level(self, fullname, name, page, level):
        """Affiche un élément hiérarchique."""

        if level > 0:

            self._fd.write('<SPAN class="steps">')

            for i in range(level - 1):
                self._fd.write('&nbsp;' * 5)

            self._fd.write('&nbsp;╰──&nbsp;')

            self._fd.write('</SPAN>')

        if page != None:
            self._fd.write('<A href="%s.html#%s">' % (page, name))

        self._fd.write(fullname)

        if page != None:
            self._fd.write('</A>')

        self._fd.write('<BR>')


    def show_constant_info(self, name):
        """Affiche un élément de type 'constant'."""

        self._fd.write('<P><SPAN class="constant_name">%s</SPAN></P>' % name)


    def show_data_info(self, name, value):
        """Affiche un élément de type 'donnée'."""

        self._fd.write('<P><SPAN class="data_name">%s</SPAN> = <SPAN class="data_value">%s</SPAN></P>' % (name, self._normalize_desc(value)))

    def show_attribute_info(self, name, desc):
        """Affiche un élément de type 'attribut'."""

        self._fd.write('<P><SPAN class="property_name">%s</SPAN><BR><DIV class="property_desc">%s</DIV></P>' % (name, self._normalize_desc(desc)))


    def show_callable_info(self, ret, name, args, desc):
        """Affiche un élément de type 'routine'."""

        if args == None:
            args = '()'

        self._fd.write('<P><SPAN class="callable_name">%s</SPAN>(%s)<BR><DIV class="callable_desc">%s</DIV></P>' % (name, args, self._normalize_desc(desc)))
