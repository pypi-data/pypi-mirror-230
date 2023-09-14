
/* Chrysalide - Outil d'analyse de fichiers binaires
 * restricted.c - prototypes pour l'équivalent Python du fichier "analysis/contents/restricted.c"
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "restricted.h"


#include <pygobject.h>


#include <i18n.h>


#include <analysis/contents/restricted.h>


#include "../content.h"
#include "../storage/serialize.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../arch/vmpa.h"



/* Crée un nouvel objet Python de type 'BinContent'. */
static PyObject *py_restricted_content_new(PyTypeObject *, PyObject *, PyObject *);

/* Indique l'espace de restriction appliqué à un contenu. */
static PyObject *py_restricted_content_get_range(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'BinContent'.            *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_restricted_content_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Instance GLib correspondante*/
    mrange_t range;                         /* Restriction à appliquer     */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *restricted;                /* Création GLib à transmettre */

#define RESTRICTED_CONTENT_DOC                                                  \
    "RestrictedContent restricts access to a given area for a binary content."  \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    RestrictedContent(content, range)"                                     \
    "\n"                                                                        \
    "Where content is a pychrysalide.analysis.BinContent instance and range"    \
    " a Python object which can be converted into pychrysalide.arch.mrange."

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_binary_content, &content, convert_any_to_mrange, &range);
    if (!ret) return NULL;

    restricted = g_restricted_content_new(content, &range);

    result = pygobject_new(G_OBJECT(restricted));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique l'espace de restriction appliqué à un contenu.       *
*                                                                             *
*  Retour      : Couverture mémoire associée au contenu restreint.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_restricted_content_get_range(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GRestrictedContent *content;            /* Contenu binaire à consulter */
    mrange_t range;                         /* Couverture à transmettre    */

#define RESTRICTED_CONTENT_RANGE_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    range, py_restricted_content,                               \
    "Give the restricting range applied to a binary content."   \
)

    content = G_RESTRICTED_CONTENT(pygobject_get(self));

    g_restricted_content_get_range(content, &range);

    result = build_from_internal_mrange(&range);

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

PyTypeObject *get_python_restricted_content_type(void)
{
    static PyMethodDef py_restricted_content_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_restricted_content_getseters[] = {
        RESTRICTED_CONTENT_RANGE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_restricted_content_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.contents.RestrictedContent",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RESTRICTED_CONTENT_DOC,

        .tp_methods     = py_restricted_content_methods,
        .tp_getset      = py_restricted_content_getseters,
        .tp_new         = py_restricted_content_new

    };

    return &py_restricted_content_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....RestrictedContent'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_restricted_content_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'Restricted...' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_restricted_content_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.contents");

        dict = PyModule_GetDict(module);

        if (!ensure_python_serializable_object_is_registered())
            return false;

        if (!ensure_python_binary_content_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_RESTRICTED_CONTENT, type))
            return false;

    }

    return true;

}
