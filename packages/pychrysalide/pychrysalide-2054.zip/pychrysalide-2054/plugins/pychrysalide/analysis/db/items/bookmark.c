
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmark.c - équivalent Python du fichier "analysis/db/items/bookmark.c"
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


#include "bookmark.h"


#include <malloc.h>
#include <pygobject.h>


#include <analysis/db/items/bookmark.h>
#include <plugins/dt.h>


#include "../collection.h"
#include "../item.h"
#include "../../../access.h"
#include "../../../helpers.h"
#include "../../../arch/vmpa.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Crée un nouvel objet Python de type 'DbBookmark'. */
static PyObject *py_db_bookmark_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_db_bookmark_init(PyObject *, PyObject *, PyObject *);

/* Fournit l'adresse associée à un signet. */
static PyObject *py_db_bookmark_get_address(PyObject *, void *);

/* Fournit le commentaire associé à un signet. */
static PyObject *py_db_bookmark_get_comment(PyObject *, void *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Crée un nouvel objet Python de type 'BookmarkCollection'. */
static PyObject *py_bookmark_collection_new(PyTypeObject *, PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'DbBookmark'.            *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_bookmark_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_db_bookmark_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DB_BOOKMARK, type->tp_name, NULL, NULL, NULL);

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
*  Retour      : 0 en cas de succès, -1 sinon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_db_bookmark_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à renvoyer            */
    vmpa2t *addr;                           /* Emplacement ciblé           */
    const char *comment;                    /* Commentaire éventuel associé*/
    int ret;                                /* Bilan de lecture des args.  */
    GDbBookmark *bookmark;                  /* Version GLib du signet      */
    bool status;                            /* Bilan de l'initialisation   */

#define DB_BOOKMARK_DOC                                                         \
    "DbBookmark provides support for bookmarks inside the disassembled code.\n" \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    DbBookmark(addr, comment=None)\n"                                      \
    "\n"                                                                        \
    "Where *addr* is a location of type pychrysalide.arch.vmpa and"             \
    " *comment* is a string or None.\n"                                         \
    "\n"                                                                        \
    "An empty comment is not enough to delete a bookmark for a given address;"  \
    " the *ERASER* flag from the pychrysalide.analysis.db.DbItem.DbItemFlags"   \
    " enumeration must be explicitly add to the item by a call to the"          \
    " pychrysalide.analysis.db.DbItem.add_flag() function."

    result = -1;

    /* Récupération des paramètres */

    comment = NULL;

    ret = PyArg_ParseTuple(args, "O&|s", convert_any_to_vmpa, &addr, &comment);
    if (!ret) goto exit;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1)
    {
        clean_vmpa_arg(addr);
        goto exit;
    }

    /* Eléments de base */

    bookmark = G_DB_BOOKMARK(pygobject_get(self));

    status = g_db_bookmark_fill(bookmark, addr, comment);
    if (!status)
    {
        clean_vmpa_arg(addr);
        goto exit;
    }

    clean_vmpa_arg(addr);

    result = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'adresse associée à un signet.                      *
*                                                                             *
*  Retour      : Adresse mémoire.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_bookmark_get_address(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbBookmark *bookmark;                  /* Signet à consulter          */
    const vmpa2t *addr;                     /* Localisation de ce signet   */

#define DB_BOOKMARK_ADDRESS_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                       \
    address, py_db_bookmark,                            \
    "Location of the bookmark, provided as a"           \
    " pychrysalide.arch.vmpa instance."                 \
)

    bookmark = G_DB_BOOKMARK(pygobject_get(self));

    addr = g_db_bookmark_get_address(bookmark);

    result = build_from_internal_vmpa(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le commentaire associé à un signet.                  *
*                                                                             *
*  Retour      : Commentaire existant ou None.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_bookmark_get_comment(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbBookmark *bookmark;                  /* Signet à consulter          */
    const char *comment;                    /* Contenu textuel associé     */

#define DB_BOOKMARK_COMMENT_ATTRIB PYTHON_GET_DEF_FULL                          \
(                                                                               \
    comment, py_db_bookmark,                                                    \
    "Comment linked to the bookmark or None if the bookmark has been unset."    \
)

    bookmark = G_DB_BOOKMARK(pygobject_get(self));

    comment = g_db_bookmark_get_comment(bookmark);

    if (comment != NULL)
        result = PyUnicode_FromString(comment);

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

PyTypeObject *get_python_db_bookmark_type(void)
{
    static PyMethodDef py_db_bookmark_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_db_bookmark_getseters[] = {
        DB_BOOKMARK_ADDRESS_ATTRIB,
        DB_BOOKMARK_COMMENT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_db_bookmark_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.items.DbBookmark",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = DB_BOOKMARK_DOC,

        .tp_methods     = py_db_bookmark_methods,
        .tp_getset      = py_db_bookmark_getseters,

        .tp_init        = py_db_bookmark_init,
        .tp_new         = py_db_bookmark_new,

    };

    return &py_db_bookmark_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...db.items.DbBookmark'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_db_bookmark_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbBookmark'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_db_bookmark_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db.items");

        dict = PyModule_GetDict(module);

        if (!ensure_python_db_item_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_DB_BOOKMARK, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en signet de collection.                  *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_db_bookmark(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_db_bookmark_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to collection bookmark");
            break;

        case 1:
            *((GDbBookmark **)dst) = G_DB_BOOKMARK(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA COLLECTION ASSOCIEE                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'BookmarkCollection'.    *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bookmark_collection_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

#define BOOKMARK_COLLECTION_DOC                                         \
    "BookmarkCollection remembers all bookmark definitions.\n"          \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    BookmarkCollection()\n"                                        \
    "\n"                                                                \
    "There should be no need for creating such instances manually."

    /* Validations diverses */

    base = get_python_db_bookmark_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DB_BOOKMARK, type->tp_name, NULL, NULL, NULL);

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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_bookmark_collection_type(void)
{
    static PyMethodDef py_bookmark_collection_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_bookmark_collection_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_bookmark_collection_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.items.BookmarkCollection",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BOOKMARK_COLLECTION_DOC,

        .tp_methods     = py_bookmark_collection_methods,
        .tp_getset      = py_bookmark_collection_getseters,

        .tp_new         = py_bookmark_collection_new,

    };

    return &py_bookmark_collection_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....BookmarkCollection'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_bookmark_collection_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbBookmark'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_bookmark_collection_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db.items");

        dict = PyModule_GetDict(module);

        if (!ensure_python_db_collection_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BM_COLLECTION, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en collection de signets.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_bookmark_collection(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_bookmark_collection_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to bookmark collection");
            break;

        case 1:
            *((GBookmarkCollection **)dst) = G_BM_COLLECTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
