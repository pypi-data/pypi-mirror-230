
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binarycursor.c - équivalent Python du fichier "glibext/gbinarycursor.h"
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "binarycursor.h"


#include <pygobject.h>


#include <i18n.h>
#include <glibext/gbinarycursor.h>


#include "linecursor.h"
#include "../access.h"
#include "../helpers.h"
#include "../arch/vmpa.h"



/* Crée un nouvel objet Python de type 'BinaryCursor'. */
static PyObject *py_binary_cursor_new(PyTypeObject *, PyObject *, PyObject *);

/* Met à jour la position suivi dans un panneau de chargement. */
static PyObject *py_binary_cursor_update(PyObject *, PyObject *);

/* Transmet la position de suivi dans un panneau de chargement. */
static PyObject *py_binary_cursor_retrieve(PyObject *, PyObject *);

/* Indique la représentation de l'emplacement. */
static PyObject *py_binary_cursor_get_raw(PyObject *, void *);

/* Précise la représentation de l'emplacement. */
static int py_binary_cursor_set_raw(PyObject *, PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'BinaryCursor'.          *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_cursor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GLineCursor *cursor;                    /* Création GLib à transmettre */

#define BINARY_CURSOR_DOC                                                           \
    "BinaryCursor handles a position into a disassembly view.\n"                    \
    "\n"                                                                            \
    "Instances can be created using the following constructor:\n"                   \
    "\n"                                                                            \
    "    BinaryCursor()\n"

    cursor = g_binary_cursor_new();

    g_object_ref_sink(G_OBJECT(cursor));
    result = pygobject_new(G_OBJECT(cursor));
    g_object_unref(cursor);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = variable non utilisée ici.                            *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Met à jour la position suivi dans un panneau de chargement.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_cursor_update(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *addr;                           /* Emplacement fourni          */
    int ret;                                /* Bilan de lecture des args.  */
    GBinaryCursor *cursor;                  /* Version GLib du type        */

#define BINARY_CURSOR_UPDATE_METHOD PYTHON_METHOD_DEF           \
(                                                               \
    update, "$self, addr",                                      \
    METH_VARARGS, py_binary_cursor,                             \
    "Update the location of the cursor.\n"                      \
    "\n"                                                        \
    "The *addr* argument must be able to get converted into"    \
    " a pychrysalide.arch.vmpa instance."                       \
)

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    cursor = G_BINARY_CURSOR(pygobject_get(self));

    g_binary_cursor_update(cursor, addr);

    result = Py_None;
    Py_INCREF(result);

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = variable non utilisée ici.                            *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Transmet la position de suivi dans un panneau de chargement. *
*                                                                             *
*  Retour      : Emplacement courant.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_cursor_retrieve(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryCursor *cursor;                  /* Version GLib du type        */
    vmpa2t addr;                            /* Emplacement fourni          */

#define BINARY_CURSOR_RETRIEVE_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    retrieve, "$self",                                              \
    METH_NOARGS, py_binary_cursor,                                  \
    "Retrieve the location of the cursor.\n"                        \
    "\n"                                                            \
    "The result is provided as a pychrysalide.arch.vmpa instance."  \
)

    cursor = G_BINARY_CURSOR(pygobject_get(self));

    g_binary_cursor_retrieve(cursor, &addr);

    result = build_from_internal_vmpa(&addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la représentation de l'emplacement.                  *
*                                                                             *
*  Retour      : True so la représentation de l'emplacement est brute.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_cursor_get_raw(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinaryCursor *cursor;                  /* Instance à manipuler        */
    bool raw;                               /* Statut défini               */

#define BINARY_CURSOR_RAW_ATTRIB PYTHON_GETSET_DEF_FULL             \
(                                                                   \
    raw, py_binary_cursor,                                          \
    "Type of rendering in the status bar for the binary location."  \
)

    cursor = G_BINARY_CURSOR(pygobject_get(self));
    raw = g_binary_cursor_is_raw(cursor);

    result = raw ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Précise la représentation de l'emplacement.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_cursor_set_raw(PyObject *self, PyObject *value, void *closure)
{
    bool raw;                               /* Statut à définir            */
    GBinaryCursor *cursor;                  /* Instance à manipuler        */

    raw = (value == Py_True);

    cursor = G_BINARY_CURSOR(pygobject_get(self));

    g_binary_cursor_set_raw(cursor, raw);

    return 0;

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

PyTypeObject *get_python_binary_cursor_type(void)
{
    static PyMethodDef py_binary_cursor_methods[] = {
        BINARY_CURSOR_UPDATE_METHOD,
        BINARY_CURSOR_RETRIEVE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_binary_cursor_getseters[] = {
        BINARY_CURSOR_RAW_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_binary_cursor_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.BinaryCursor",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = BINARY_CURSOR_DOC,

        .tp_methods     = py_binary_cursor_methods,
        .tp_getset      = py_binary_cursor_getseters,
        .tp_new         = py_binary_cursor_new,

    };

    return &py_binary_cursor_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.BinaryCursor'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_cursor_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinaryCursor'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_cursor_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!ensure_python_line_cursor_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BINARY_CURSOR, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en curseur pour ligne.                    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_cursor(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_binary_cursor_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, _("unable to convert the provided argument to binary cursor"));
            break;

        case 1:
            *((GBinaryCursor **)dst) = G_BINARY_CURSOR(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
