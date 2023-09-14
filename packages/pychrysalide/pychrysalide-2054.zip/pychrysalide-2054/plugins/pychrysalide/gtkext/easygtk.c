
/* Chrysalide - Outil d'analyse de fichiers binaires
 * easygtk.c - équivalent Python du fichier "gtkext/easygtk.c"
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


#include "easygtk.h"


#include <pygobject.h>


#include <gtkext/easygtk.h>


#include "../access.h"
#include "../helpers.h"



#define EASYGTK_DOC                                         \
    "The EasyGtk class is a kind of toolbox gathering some" \
    " useful features GTK is missing."


/* Identifie la couleur de base associée à un style GTK. */
static PyObject *py_easygtk_get_color_from_style(PyObject *, PyObject *);

/* Détermine l'indice d'un composant dans un conteneur GTK. */
static PyObject *py_easygtk_find_contained_child_index(PyObject *, PyObject *);

/* Récupère le nième composant d'un conteneur GTK. */
static PyObject *py_easygtk_get_nth_contained_child(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Identifie la couleur de base associée à un style GTK.        *
*                                                                             *
*  Retour      : Bilan présumé de l'opération.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_easygtk_get_color_from_style(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Coloration à retourner      */
    const char *class;                      /* Classe de style GTK         */
    int background;                         /* Nature du traitement        */
    int ret;                                /* Bilan de lecture des args.  */
    GdkRGBA color;                          /* Couleur obtenue             */
    bool status;                            /* Bilan de la récupération    */

#define EASYGTK_GET_COLOR_FROM_STYLE_METHOD PYTHON_METHOD_DEF           \
(                                                                       \
    get_color_from_style, "cls, background, /",                         \
    METH_VARARGS | METH_STATIC, py_easygtk,                             \
    "Find the index of a given child widget inside a GTK container"     \
    " children.\n"                                                      \
    "\n"                                                                \
    "The *containter* argument must be a Gtk.Container instance and"    \
    " *child* a Gtk.Widget instance.\n"                                 \
    "\n"                                                                \
    "The result is the found index or -1 in case of error."             \
)

    ret = PyArg_ParseTuple(args, "sp", &class, &background);
    if (!ret) return NULL;

    status = get_color_from_style(class, background, &color);

    if (status)
        result = create_gdk_rgba(&color);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Détermine l'indice d'un composant dans un conteneur GTK.     *
*                                                                             *
*  Retour      : Indice du composant dans le conteneur ou -1 si non trouvé.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_easygtk_find_contained_child_index(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    GtkContainer *container;                /* Composant GTK à analyser    */
    GtkWidget *child;                       /* Composant GTK à retrouver   */
    int ret;                                /* Bilan de lecture des args.  */
    gint index;                             /* Indice obtenu ou -1         */

#define EASYGTK_FIND_CONTAINED_CHILD_INDEX_METHOD PYTHON_METHOD_DEF     \
(                                                                       \
    find_contained_child_index, "container, child, /",                  \
    METH_VARARGS | METH_STATIC, py_easygtk,                             \
    "Find the index of a given child widget inside a GTK container"     \
    " children.\n"                                                      \
    "\n"                                                                \
    "The *containter* argument must be a Gtk.Container instance and"    \
    " *child* a Gtk.Widget instance.\n"                                 \
    "\n"                                                                \
    "The result is the found index or -1 in case of error."             \
)

    ret = PyArg_ParseTuple(args, "O&O&", &convert_to_gtk_container, &container, convert_to_gtk_widget, &child);
    if (!ret) return NULL;

    index = find_contained_child_index(container, child);

    result = PyLong_FromLong(index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Récupère le nième composant d'un conteneur GTK.              *
*                                                                             *
*  Retour      : Composant à la position donnée ou NULL en cas d'absence.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_easygtk_get_nth_contained_child(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    GtkContainer *container;                /* Composant GTK à analyser    */
    unsigned int n;                         /* Indice du composant GTK visé*/
    int ret;                                /* Bilan de lecture des args.  */
    GtkWidget *child;                       /* Composant GTK retrouvé      */

#define EASYGTK_GET_NTH_CONTAINED_CHILD_METHOD PYTHON_METHOD_DEF    \
(                                                                   \
    get_nth_contained_child, "container, n, /",                     \
    METH_VARARGS | METH_STATIC, py_easygtk,                         \
    "Find the widget contained inside a GTK container at the n-th"  \
    " position.\n"                                                  \
    "\n"                                                            \
    "The *containter* argument must be a Gtk.Container instance"    \
    " and *n* an integer.\n"                                        \
    "\n"                                                            \
    "The result is a Gtk.Widget instance, or Nonein case of error." \
)

    ret = PyArg_ParseTuple(args, "O&I", &convert_to_gtk_container, &container, &n);
    if (!ret) return NULL;

    child = get_nth_contained_child(container, n);

    if (child == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(child));
        g_object_unref(G_OBJECT(child));
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

PyTypeObject *get_python_easygtk_type(void)
{
    static PyMethodDef py_easygtk_methods[] = {
        EASYGTK_GET_COLOR_FROM_STYLE_METHOD,
        EASYGTK_FIND_CONTAINED_CHILD_INDEX_METHOD,
        EASYGTK_GET_NTH_CONTAINED_CHILD_METHOD,
        { NULL }
    };

    static PyGetSetDef py_easygtk_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_easygtk_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gtkext.EasyGtk",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = EASYGTK_DOC,

        .tp_methods     = py_easygtk_methods,
        .tp_getset      = py_easygtk_getseters,

        .tp_new         = no_python_constructor_allowed,

    };

    return &py_easygtk_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gtkext.EasyGtk'.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_easygtk_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python pour 'EasyGtk'  */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_easygtk_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.gtkext");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}
