
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encapsulated.c - prototypes pour l'équivalent Python du fichier "analysis/contents/encapsulated.c"
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


#include "encapsulated.h"


#include <pygobject.h>


#include <analysis/contents/encapsulated.h>


#include "../content.h"
#include "../storage/serialize.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'BinContent'. */
static PyObject *py_encaps_content_new(PyTypeObject *, PyObject *, PyObject *);

/* Indique la base d'un contenu binaire encapsulé. */
static PyObject *py_encaps_content_get_base(PyObject *, void *);

/* Fournit le chemin vers le contenu interne représenté. */
static PyObject *py_encaps_content_get_path(PyObject *, void *);

/* Indique le contenu binaire embarqué dans une encapsulation. */
static PyObject *py_encaps_content_get_endpoint(PyObject *, void *);



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

static PyObject *py_encaps_content_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *base;                      /* Base de l'extraction        */
    const char *path;                       /* Chemin vers le contenu final*/
    GBinContent *endpoint;                  /* Contenu accessible au final */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du contenu     */

#define ENCAPS_CONTENT_DOC                                                  \
    "EncapsulatedContent gathers items relative to a binary encapsulated"   \
    " content.\n"                                                           \
    "\n"                                                                    \
    "For instance, if a ZIP archive is processed, the encapsulated content" \
    " stores:\n"                                                            \
    "* the archive as a base;\n"                                            \
    "* the access path to the archive member;\n"                            \
    "* the content of this extracted member.\n"                             \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    EncapsulatedContent(base, path, endpoint)"                         \
    "\n"                                                                    \
    "Where base, path and endpoint are the previously described expected"   \
    " properties. The base and the endpoint must be"                        \
    " pychrysalide.analysis.BinContent instances and the access path must"  \
    " be provided as a string."

    ret = PyArg_ParseTuple(args, "O&sO&",
                           convert_to_binary_content, &base,
                           &path,
                           convert_to_binary_content, &endpoint);
    if (!ret) return NULL;

    content = g_encaps_content_new(base, path, endpoint);

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
*  Description : Indique la base d'un contenu binaire encapsulé.              *
*                                                                             *
*  Retour      : Instance de contenu binaire ou None si aucune.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_encaps_content_get_base(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GEncapsContent *content;                /* Contenu binaire à consulter */
    GBinContent *target;                    /* Contenu binaire visé        */

#define ENCAPS_CONTENT_BASE_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    base, py_encaps_content,                                \
    "Give access to the base of the encapsulated content."  \
)

    content = G_ENCAPS_CONTENT(pygobject_get(self));

    target = g_encaps_content_get_base(content);

    if (target == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(target));
        g_object_unref(G_OBJECT(target));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le chemin vers le contenu interne représenté.        *
*                                                                             *
*  Retour      : Chemin d'accès au contenu binaire.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_encaps_content_get_path(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GEncapsContent *content;                /* Contenu binaire à consulter */
    const char *path;                       /* Chemin d'accès à transmettre*/

#define ENCAPS_CONTENT_PATH_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    path, py_encaps_content,                                \
    "Provide the access path to the inner binary content."  \
)

    content = G_ENCAPS_CONTENT(pygobject_get(self));

    path = g_encaps_content_get_path(content);

    result = PyUnicode_FromString(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le contenu binaire embarqué dans une encapsulation.  *
*                                                                             *
*  Retour      : Instance de contenu binaire ou None si aucune.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_encaps_content_get_endpoint(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GEncapsContent *content;                /* Contenu binaire à consulter */
    GBinContent *target;                    /* Contenu binaire visé        */

#define ENCAPS_CONTENT_ENDPOINT_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                           \
    endpoint, py_encaps_content,                            \
    "Give access to the encapsulated binary content."       \
)

    content = G_ENCAPS_CONTENT(pygobject_get(self));

    target = g_encaps_content_get_base(content);

    if (target == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(target));
        g_object_unref(G_OBJECT(target));
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

PyTypeObject *get_python_encaps_content_type(void)
{
    static PyMethodDef py_encaps_content_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_encaps_content_getseters[] = {
        ENCAPS_CONTENT_BASE_ATTRIB,
        ENCAPS_CONTENT_PATH_ATTRIB,
        ENCAPS_CONTENT_ENDPOINT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_encaps_content_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.contents.EncapsulatedContent",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = ENCAPS_CONTENT_DOC,

        .tp_methods     = py_encaps_content_methods,
        .tp_getset      = py_encaps_content_getseters,
        .tp_new         = py_encaps_content_new

    };

    return &py_encaps_content_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...EncapsulatedContent'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_encaps_content_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'EncapsulatedContent'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_encaps_content_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.contents");

        dict = PyModule_GetDict(module);

        if (!ensure_python_serializable_object_is_registered())
            return false;

        if (!ensure_python_binary_content_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ENCAPS_CONTENT, type))
            return false;

    }

    return true;

}
