
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named.c - prototypes pour l'équivalent Python du fichier "gtkext/named.c"
 *
 * Copyright (C) 2020 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "named.h"


#include <pygobject.h>


#include <gtkext/named-int.h>
#include <plugins/dt.h>


#include "../access.h"
#include "../helpers.h"
#include "../glibext/named.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_built_named_widget_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_built_named_widget_init(PyObject *, PyObject *, PyObject *);



/* --------------------------- MANIPULATION DE COMPOSANTS --------------------------- */


/* Fournit le constructeur facilitant l'affichage. */
static PyObject *py_built_named_widget_get_builder(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du nouvel objet à mettre en place.               *
*                args = éventuelle liste d'arguments.                         *
*                kwds = éventuel dictionnaire de valeurs mises à disposition. *
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_built_named_widget_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_built_named_widget_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(GTK_TYPE_BUILT_NAMED_WIDGET, type->tp_name, NULL, NULL, NULL);

    if (first_time)
    {
        status = register_class_for_dynamic_pygobject(gtype, type);

        if (!status)
        {
            result = NULL;
            goto exit;
        }

    }

    /* On crée, et on laisse ensuite la main à PyGObject_Type.tp_init() */

 simple_way:

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet à initialiser (théoriquement).                  *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Initialise une instance sur la base du dérivé de GObject.    *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_built_named_widget_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *name;                       /* Désignation courte à lier   */
    const char *lname;                      /* Description longue associée */
    const char *path;                       /* Fichier à charger           */
    int ret;                                /* Bilan de lecture des args.  */
    GtkBuiltNamedWidget *widget;            /* Instance native à consulter */

#define BUILT_NAMED_WIDGET_DOC                                              \
    "The BuiltNamedWidget object offers a quick way to get a working"       \
    " implementation of the pychrysalide.glibext.NamedWidget interface by"  \
    " relying on an external resource file for widgets.\n"                  \
    "\n"                                                                    \
    "These widgets are managed using a Gtk.Builder instance internally.\n"  \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    BuiltNamedWidget(name, lname, filename)"                           \
    "\n"                                                                    \
    "Where *name* is a short description to link to the result, *lname* is" \
    " a longer version of this description and *filename* points to the"    \
    " file containing the widgets definition to load."                      \

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "sss", &name, &lname, &path);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    widget = GTK_BUILT_NAMED_WIDGET(pygobject_get(self));

    widget->name = strdup(name);
    widget->lname = strdup(lname);

    widget->builder = gtk_builder_new_from_file(path);

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                             MANIPULATION DE COMPOSANTS                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le constructeur facilitant l'affichage.              *
*                                                                             *
*  Retour      : Constructeur mis en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_built_named_widget_get_builder(PyObject *self, void *closure)
{
    PyObject *result;                       /* Contenu binaire à retourner */
    GtkBuiltNamedWidget *widget;            /* Instance native à consulter */
    GtkBuilder *builder;                    /* Constructeur à retourner    */

#define BUILT_NAMED_WIDGET_BUILDER_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                                   \
    builder, py_built_named_widget,                                 \
    "Gtk.Builder instance handling all the widgets loaded from a"   \
    " resource file, or None in case of loading errors."            \
)

    widget = GTK_BUILT_NAMED_WIDGET(pygobject_get(self));

    builder = gtk_built_named_widget_get_builder(widget);

    if (builder != NULL)
    {
        result = pygobject_new(G_OBJECT(builder));
        g_object_unref(G_OBJECT(builder));
    }

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_built_named_widget_type(void)
{
    static PyMethodDef py_built_named_widget_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_built_named_widget_getseters[] = {
        BUILT_NAMED_WIDGET_BUILDER_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_built_named_widget_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gtkext.BuiltNamedWidget",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BUILT_NAMED_WIDGET_DOC,

        .tp_methods     = py_built_named_widget_methods,
        .tp_getset      = py_built_named_widget_getseters,

        .tp_init        = py_built_named_widget_init,
        .tp_new         = py_built_named_widget_new

    };

    return &py_built_named_widget_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....BuiltNamedWidget'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_built_named_widget_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'BuiltNamedWidget'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_built_named_widget_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gtkext");

        dict = PyModule_GetDict(module);

        if (!ensure_python_named_widget_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, GTK_TYPE_BUILT_NAMED_WIDGET, type))
            return false;

    }

    return true;

}
