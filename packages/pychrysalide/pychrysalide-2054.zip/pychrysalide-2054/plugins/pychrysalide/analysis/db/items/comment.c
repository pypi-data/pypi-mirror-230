
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comment.c - équivalent Python du fichier "analysis/db/items/comment.c"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "comment.h"


#include <malloc.h>
#include <pygobject.h>


#include <analysis/db/items/comment.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../collection.h"
#include "../item.h"
#include "../../../access.h"
#include "../../../helpers.h"
#include "../../../arch/vmpa.h"
#include "../../../glibext/constants.h"
#include "../../../glibext/bufferline.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Crée un nouvel objet Python de type 'DbComment'. */
static PyObject *py_db_comment_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_db_comment_init(PyObject *, PyObject *, PyObject *);

/* Fournit l'adresse associée à un commentaire. */
static PyObject *py_db_comment_get_address(PyObject *, void *);

/* Indique le type d'incrustation prévue pour un commentaire. */
static PyObject *py_db_comment_get_embedding_type(PyObject *, void *);

/* Fournit les particularités d'accroche liées à un commentaire. */
static PyObject *py_db_comment_get_flags(PyObject *, void *);

/* Fournit le commentaire associé à un commentaire. */
static PyObject *py_db_comment_get_text(PyObject *, void *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Crée un nouvel objet Python de type 'CommentCollection'. */
static PyObject *py_comment_collection_new(PyTypeObject *, PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'DbComment'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_comment_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_db_comment_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DB_COMMENT, type->tp_name, NULL, NULL, NULL);

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

static int py_db_comment_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à renvoyer            */
    vmpa2t *addr;                           /* Emplacement ciblé           */
    CommentEmbeddingType type;              /* Type d'incrustation         */
    BufferLineFlags flags;                  /* Particularités de l'accroche*/
    const char *text;                       /* Eventuel contenu textuel    */
    int ret;                                /* Bilan de lecture des args.  */
    GDbComment *comment;                    /* Version GLib du signet      */
    bool status;                            /* Bilan de l'initialisation   */

#define DB_COMMENT_DOC                                                          \
    "DbComment provides support for comments to embed into the disassembled"    \
    " code.\n"                                                                  \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    DbComment(addr, addr, type, flags, text=None)\n"                       \
    "\n"                                                                        \
    "Where *addr* is a location of type pychrysalide.arch.vmpa, *type* defines" \
    " the kind of embedding as a"                                               \
    " pychrysalide.analysis.db.items.DbComment.CommentEmbeddingType value,"     \
    " *flags* states for the pychrysalide.glibext.BufferLine.BufferLineFlags"   \
    " property of the line to attach and *text* is an optional string for the"  \
    " comment.\n"                                                               \
    "\n"                                                                        \
    "An empty comment is not enough to delete a comment for a given address;"   \
    " the *ERASER* flag from the pychrysalide.analysis.db.DbItem.DbItemFlags"   \
    " enumeration must be explicitly add to the item by a call to the"          \
    " pychrysalide.analysis.db.DbItem.add_flag() function."

    result = -1;

    /* Récupération des paramètres */

    text = NULL;

    ret = PyArg_ParseTuple(args, "O&O&O&|s",
                           convert_any_to_vmpa, &addr,
                           convert_to_comment_embedding_type, &type,
                           convert_to_buffer_line_flags, &flags,
                           &text);
    if (!ret) goto exit;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1)
    {
        clean_vmpa_arg(addr);
        goto exit;
    }

    /* Eléments de base */

    comment = G_DB_COMMENT(pygobject_get(self));

    status = g_db_comment_fill(comment, addr, type, flags, text);
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
*  Description : Fournit l'adresse associée à un commentaire.                 *
*                                                                             *
*  Retour      : Adresse mémoire.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_comment_get_address(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbComment *comment;                    /* Commentaire à consulter     */
    const vmpa2t *addr;                     /* Localisation du commentaire */

#define DB_COMMENT_ADDRESS_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                       \
    address, py_db_comment,                             \
    "Location of the comment, provided as a"            \
    " pychrysalide.arch.vmpa instance."                 \
)

    comment = G_DB_COMMENT(pygobject_get(self));

    addr = g_db_comment_get_address(comment);

    result = build_from_internal_vmpa(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le type d'incrustation prévue pour un commentaire.   *
*                                                                             *
*  Retour      : Incrustation associée au commentaire.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_comment_get_embedding_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbComment *comment;                    /* Commentaire à consulter     */
    CommentEmbeddingType type;              /* Type d'incrustation         */

#define DB_COMMENT_EMBEDDING_TYPE_ATTRIB PYTHON_GET_DEF_FULL                \
(                                                                           \
    embedding_type, py_db_comment,                                          \
    "Type of embedding required for the comment, as a"                      \
    " pychrysalide.analysis.db.items.DbComment.CommentEmbeddingType value." \
)

    comment = G_DB_COMMENT(pygobject_get(self));

    type = g_db_comment_get_embedding_type(comment);

    result = cast_with_constants_group_from_type(get_python_db_comment_type(), "CommentEmbeddingType", type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les particularités d'accroche liées à un commentaire.*
*                                                                             *
*  Retour      : Particularités éventuelles pour l'accroche.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_comment_get_flags(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbComment *comment;                    /* Commentaire à consulter     */
    BufferLineFlags flags;                  /* Fanions à rechercher        */

#define DB_COMMENT_FLAGS_ATTRIB PYTHON_GET_DEF_FULL             \
(                                                               \
    flags, py_db_comment,                                       \
    "Flags of the line where to attach the comment, as a"       \
    " pychrysalide.glibext.BufferLine.BufferLineFlags value."   \
)

    comment = G_DB_COMMENT(pygobject_get(self));

    flags = g_db_comment_get_flags(comment);

    result = cast_with_constants_group_from_type(get_python_buffer_line_type(), "BufferLineFlags", flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le commentaire associé à un commentaire.             *
*                                                                             *
*  Retour      : Texte manipulable en Python.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_comment_get_text(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbComment *comment;                    /* Commentaire à consulter     */
    char *text;                             /* Contenu textuel associé     */

#define DB_COMMENT_TEXT_ATTRIB PYTHON_GET_DEF_FULL                          \
(                                                                           \
    text, py_db_comment,                                                    \
    "Content of the comment, as a string which may contain several lines,"  \
    " or None of no text is linked to the comment."                         \
)

    comment = G_DB_COMMENT(pygobject_get(self));
    text = g_db_comment_get_text(comment);

    if (text == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = PyUnicode_FromString(text);
        free(text);
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

PyTypeObject *get_python_db_comment_type(void)
{
    static PyMethodDef py_db_comment_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_db_comment_getseters[] = {
        DB_COMMENT_ADDRESS_ATTRIB,
        DB_COMMENT_EMBEDDING_TYPE_ATTRIB,
        DB_COMMENT_FLAGS_ATTRIB,
        DB_COMMENT_TEXT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_db_comment_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.items.DbComment",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DB_COMMENT_DOC,

        .tp_methods     = py_db_comment_methods,
        .tp_getset      = py_db_comment_getseters,

        .tp_init        = py_db_comment_init,
        .tp_new         = py_db_comment_new,

    };

    return &py_db_comment_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.items.DbComment'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_db_comment_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbComment'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_db_comment_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db.items");

        dict = PyModule_GetDict(module);

        if (!ensure_python_db_item_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_DB_COMMENT, type))
            return false;

        if (!define_db_comment_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en commentaire de base.                   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_db_comment(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_db_comment_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to database comment");
            break;

        case 1:
            *((GDbComment **)dst) = G_DB_COMMENT(pygobject_get(arg));
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
*  Description : Crée un nouvel objet Python de type 'CommentCollection'.    *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_comment_collection_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

#define COMMENT_COLLECTION_DOC                                          \
    "CommentCollection remembers all comment definitions.\n"            \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    CommentCollection()\n"                                         \
    "\n"                                                                \
    "There should be no need for creating such instances manually."

    /* Validations diverses */

    base = get_python_db_comment_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DB_COMMENT, type->tp_name, NULL, NULL, NULL);

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

PyTypeObject *get_python_comment_collection_type(void)
{
    static PyMethodDef py_comment_collection_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_comment_collection_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_comment_collection_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.items.CommentCollection",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = COMMENT_COLLECTION_DOC,

        .tp_methods     = py_comment_collection_methods,
        .tp_getset      = py_comment_collection_getseters,

        .tp_new         = py_comment_collection_new,

    };

    return &py_comment_collection_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....CommentCollection'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_comment_collection_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbComment'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_comment_collection_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db.items");

        dict = PyModule_GetDict(module);

        if (!ensure_python_db_collection_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_COMMENT_COLLECTION, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en collection de commentaires.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_comment_collection(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_comment_collection_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to comment collection");
            break;

        case 1:
            *((GCommentCollection **)dst) = G_COMMENT_COLLECTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
