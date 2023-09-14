
/* Chrysalide - Outil d'analyse de fichiers binaires
 * file.c - prototypes pour l'équivalent Python du fichier "analysis/contents/file.c"
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


#include "file.h"


#include <pygobject.h>


#include <analysis/contents/file.h>


#include "memory.h"
#include "../storage/serialize.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'BinContent'. */
static PyObject *py_file_content_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit le nom de fichier associé au contenu binaire. */
static PyObject *py_file_content_get_filename(PyObject *, void *);



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

static PyObject *py_file_content_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *filename;                   /* Nom du fichier à charger    */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du contenu     */

#define FILE_CONTENT_DOC                                                    \
    "FileContent handles binary content loaded from a file.\n"              \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    FileContent(filename)"                                             \
    "\n"                                                                    \
    "Where filename is a path to an existing file."

    ret = PyArg_ParseTuple(args, "s", &filename);
    if (!ret) return NULL;

    content = g_file_content_new(filename);

    result = pygobject_new(G_OBJECT(content));

    if (content != NULL)
        g_object_unref(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom de fichier associé au contenu binaire.        *
*                                                                             *
*  Retour      : Chemin d'accès au contenu binaire.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_file_content_get_filename(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GFileContent *content;                  /* Contenu binaire à consulter */
    const char *filename;                   /* Chemin d'accès à transmettre*/

#define FILE_CONTENT_FILENAME_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                           \
    filename, py_file_content,                              \
    "Provide the access path to the binary content."        \
)

    content = G_FILE_CONTENT(pygobject_get(self));

    filename = g_file_content_get_filename(content);

    result = PyUnicode_FromString(filename);

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

PyTypeObject *get_python_file_content_type(void)
{
    static PyMethodDef py_file_content_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_file_content_getseters[] = {
        FILE_CONTENT_FILENAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_file_content_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.contents.FileContent",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = FILE_CONTENT_DOC,

        .tp_methods     = py_file_content_methods,
        .tp_getset      = py_file_content_getseters,
        .tp_new         = py_file_content_new

    };

    return &py_file_content_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....FileContent'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_file_content_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'FileContent'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_file_content_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.contents");

        dict = PyModule_GetDict(module);

        if (!ensure_python_memory_content_is_registered())
            return false;

        if (!ensure_python_serializable_object_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_FILE_CONTENT, type))
            return false;

    }

    return true;

}
