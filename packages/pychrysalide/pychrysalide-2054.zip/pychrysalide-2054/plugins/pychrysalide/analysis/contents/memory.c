
/* Chrysalide - Outil d'analyse de fichiers binaires
 * memory.c - prototypes pour l'équivalent Python du fichier "analysis/contents/memory.c"
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


#include "memory.h"


#include <pygobject.h>


#include <analysis/contents/memory.h>


#include "../content.h"
#include "../storage/serialize.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'BinContent'. */
static PyObject *py_memory_content_new(PyTypeObject *, PyObject *, PyObject *);



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

static PyObject *py_memory_content_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *data;                       /* Tampon interne de Python    */
    Py_ssize_t length;                      /* Taille utilisé de ce tampon */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du contenu     */

#define MEMORY_CONTENT_DOC                                                  \
    "MemoryContent builds a binary content from memory data only."          \
    " Thus no existing file backend is needed."                             \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    MemoryContent(data)"                                               \
    "\n"                                                                    \
    "Where data is provided as string or read-only bytes-like object."      \
    " The string may contain embedded null bytes."

    /**
     * La taille doit être de type 'int' et non 'Py_ssize_t', sinon les 32 bits
     * de poids fort ne sont pas initialisés !
     */

    ret = PyArg_ParseTuple(args, "s#", &data, &length);
    if (!ret) return NULL;

    content = g_memory_content_new((const bin_t *)data, length);

    result = pygobject_new(G_OBJECT(content));

    if (content != NULL)
        g_object_unref(content);

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

PyTypeObject *get_python_memory_content_type(void)
{
    static PyMethodDef py_memory_content_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_memory_content_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_memory_content_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.contents.MemoryContent",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = MEMORY_CONTENT_DOC,

        .tp_methods     = py_memory_content_methods,
        .tp_getset      = py_memory_content_getseters,
        .tp_new         = py_memory_content_new

    };

    return &py_memory_content_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....MemoryContent'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_memory_content_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'MemoryContent' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_memory_content_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.contents");

        dict = PyModule_GetDict(module);

        if (!ensure_python_serializable_object_is_registered())
            return false;

        if (!ensure_python_binary_content_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_MEMORY_CONTENT, type))
            return false;

    }

    return true;

}
