
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope.c - équivalent Python du fichier "plugins/kaitai/scope.c"
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


#include "scope.h"


#include <assert.h>
#include <pygobject.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "record.h"
#include "parsers/meta.h"
#include "../record.h"
#include "../parsers/meta.h"



/* Rassemblement de données d'un paquet */
typedef struct _py_kaitai_scope_t
{
    PyObject_HEAD                           /* A laisser en premier        */

    kaitai_scope_t *native;                /* Tampon de données lié       */

} py_kaitai_scope_t;


/* Libère de la mémoire un objet Python 'py_kaitai_scope_t'. */
static void py_kaitai_scope_dealloc(py_kaitai_scope_t *);

/* Initialise un objet Python de type 'py_kaitai_scope_t'. */
static int py_kaitai_scope_init(py_kaitai_scope_t *, PyObject *, PyObject *);

/* Conserve le souvenir de la dernière correspondance effectuée. */
static PyObject *py_kaitai_scope_remember_last_record(PyObject *, PyObject *);

/* Recherche la définition d'un type nouveau pour Kaitai. */
static PyObject *py_kaitai_scope_find_sub_type(PyObject *, PyObject *);

/* Retourne le souvenir d'une correspondance racine. */
static PyObject *py_kaitai_scope_get_root_record(PyObject *, void *);

/* Retourne le souvenir de la correspondance parente effectuée. */
static PyObject *py_kaitai_scope_get_parent_record(PyObject *, void *);

/* Retourne le souvenir de la dernière correspondance effectuée. */
static PyObject *py_kaitai_scope_get_last_record(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à supprimer.                        *
*                                                                             *
*  Description : Libère de la mémoire un objet Python 'py_kaitai_scope_t'.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_kaitai_scope_dealloc(py_kaitai_scope_t *self)
{
    reset_record_scope(self->native);

    Py_TYPE(self)->tp_free((PyObject *)self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un objet Python de type 'py_kaitai_scope_t'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_kaitai_scope_init(py_kaitai_scope_t *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    GKaitaiMeta *meta;                      /* Informations globale        */
    int ret;                                /* Bilan de lecture des args.  */

#define KAITAI_SCOPE_DOC                                                \
    "The KaitaiScope object stores a local environment which freezes"   \
    " a particular state of the Kaitai parser. It allows the dynamic"   \
    " resolving of values contained in a Kaitai expression.\n"          \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    KaitaiScope(meta)"                                             \
    "\n"                                                                \
    "Where *meta* is a pychrysalide.plugins.kaitai.parsers.KaitaiMeta"  \
    " instance pointing to global information about the Kaitai"         \
    " definition."

    ret = PyArg_ParseTuple(args, "O&", convert_to_kaitai_meta, &meta);
    if (!ret) return -1;

    self->native = malloc(sizeof(kaitai_scope_t));

    init_record_scope(self->native, meta);

    result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = environnement local à manipuler.                      *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Conserve le souvenir de la dernière correspondance effectuée.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_scope_remember_last_record(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    GMatchRecord *record;                   /* Correspondance à utiliser   */
    int ret;                                /* Bilan de lecture des args.  */
    py_kaitai_scope_t *locals;              /* Instance à manipuler        */

#define KAITAI_SCOPE_REMEMBER_LAST_RECORD_METHOD PYTHON_METHOD_DEF  \
(                                                                   \
    remember_last_record, "$self, record, /",                       \
    METH_VARARGS, py_kaitai_scope,                                  \
    "Store a record as the last parsed record.\n"                   \
    "\n"                                                            \
    "This *record* is expected to be a"                             \
    " pychrysalide.plugins.kaitai.MatchRecord instance."            \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_match_record, &record);
    if (!ret) return NULL;

    locals = (py_kaitai_scope_t *)self;

    remember_last_record(locals->native, record);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = environnement local à manipuler.                      *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Recherche la définition d'un type nouveau pour Kaitai.       *
*                                                                             *
*  Retour      : Type prêt à emploi ou NULL si non trouvé.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_scope_find_sub_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    const char *name;                       /* Désignation à retrouver     */
    int ret;                                /* Bilan de lecture des args.  */
    py_kaitai_scope_t *locals;              /* Instance à manipuler        */
    GKaitaiType *type;                      /* Définition à identifier     */

#define KAITAI_SCOPE_FIND_SUB_TYPE_METHOD PYTHON_METHOD_DEF     \
(                                                               \
    find_sub_type, "$self, name, /",                            \
    METH_VARARGS, py_kaitai_scope,                              \
    "Retrieve the type structure linked to a given name.\n"     \
    "\n"                                                        \
    "This *name* has to be a string.\n"                         \
    "\n"                                                        \
    "The result is a known"                                     \
    " pychrysalide.plugins.kaitai.parsers.KaitaiType instance"  \
    " or *None* if the name has not been registered during"     \
    " the parsing."                                             \
)

    ret = PyArg_ParseTuple(args, "s", &name);
    if (!ret) return NULL;

    locals = (py_kaitai_scope_t *)self;

    type = find_sub_type(locals->native, name);

    result = pygobject_new(G_OBJECT(type));
    g_object_unref(G_OBJECT(type));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = environnement local à consulter.                      *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Retourne le souvenir d'une correspondance racine.            *
*                                                                             *
*  Retour      : Dernière correspondance établie ou None.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_scope_get_root_record(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_kaitai_scope_t *locals;              /* Instance à manipuler        */
    GMatchRecord *record;                   /* Correspondance à convertir  */

#define KAITAI_SCOPE_ROOT_RECORD_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    root_record, py_kaitai_scope,                               \
    "Provide the first record for a parsed content.\n"          \
    "\n"                                                        \
    "The result is a pychrysalide.plugins.kaitai.MatchRecord"   \
    " instance or *None*."                                      \
)

    locals = (py_kaitai_scope_t *)self;

    record = get_root_record(locals->native);

    if (record != NULL)
    {
        result = pygobject_new(G_OBJECT(record));
        g_object_unref(G_OBJECT(record));
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
*  Paramètres  : self = environnement local à consulter.                      *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Retourne le souvenir de la correspondance parente effectuée. *
*                                                                             *
*  Retour      : Dernière correspondance établie ou None.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_scope_get_parent_record(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_kaitai_scope_t *locals;              /* Instance à manipuler        */
    GMatchRecord *record;                   /* Correspondance à convertir  */

#define KAITAI_SCOPE_PARENT_RECORD_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                               \
    parent_record, py_kaitai_scope,                             \
    "Provide the current parent record for a parsed content.\n" \
    "\n"                                                        \
    "The result is a pychrysalide.plugins.kaitai.MatchRecord"   \
    " instance or *None*."                                      \
)

    locals = (py_kaitai_scope_t *)self;

    record = get_parent_record(locals->native);

    if (record != NULL)
    {
        result = pygobject_new(G_OBJECT(record));
        g_object_unref(G_OBJECT(record));
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
*  Paramètres  : self = environnement local à consulter.                      *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Retourne le souvenir de la dernière correspondance effectuée.*
*                                                                             *
*  Retour      : Dernière correspondance établie ou None.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_scope_get_last_record(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_kaitai_scope_t *locals;              /* Instance à manipuler        */
    GMatchRecord *record;                   /* Correspondance à convertir  */

#define KAITAI_SCOPE_LAST_RECORD_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    last_record, py_kaitai_scope,                               \
    "Provide the last createdrecord for a parsed content.\n"    \
    "\n"                                                        \
    "The result is a pychrysalide.plugins.kaitai.MatchRecord"   \
    " instance or *None*."                                      \
)

    locals = (py_kaitai_scope_t *)self;

    record = get_last_record(locals->native);

    if (record != NULL)
    {
        result = pygobject_new(G_OBJECT(record));
        g_object_unref(G_OBJECT(record));
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

PyTypeObject *get_python_kaitai_scope_type(void)
{
    static PyMethodDef py_kaitai_scope_methods[] = {
        KAITAI_SCOPE_REMEMBER_LAST_RECORD_METHOD,
        KAITAI_SCOPE_FIND_SUB_TYPE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_kaitai_scope_getseters[] = {
        KAITAI_SCOPE_ROOT_RECORD_ATTRIB,
        KAITAI_SCOPE_PARENT_RECORD_ATTRIB,
        KAITAI_SCOPE_LAST_RECORD_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_scope_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.KaitaiScope",
        .tp_basicsize   = sizeof(py_kaitai_scope_t),

        .tp_dealloc     = (destructor)py_kaitai_scope_dealloc,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = KAITAI_SCOPE_DOC,

        .tp_methods     = py_kaitai_scope_methods,
        .tp_getset      = py_kaitai_scope_getseters,

        .tp_init        = (initproc)py_kaitai_scope_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_kaitai_scope_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.common.PackedBuffer'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_scope_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'PackedBuffer'  */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_kaitai_scope_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.plugins.kaitai");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = structure interne à copier en objet Python.         *
*                                                                             *
*  Description : Convertit une structure 'kaitai_scope_t' en objet Python.    *
*                                                                             *
*  Retour      : Object Python résultant de la conversion opérée.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *build_from_internal_kaitai_scope(const kaitai_scope_t *locals)
{
    PyObject *result;                       /* Instance à retourner        */
    PyTypeObject *type;                     /* Type à instancier           */

    type = get_python_kaitai_scope_type();

    result = PyObject_CallObject((PyObject *)type, NULL);

    copy_record_scope(((py_kaitai_scope_t *)result)->native, locals);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en environnement local pour Kaitai.       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_scope(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_scope_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai scope");
            break;

        case 1:
            *((kaitai_scope_t **)dst) = ((py_kaitai_scope_t *)arg)->native;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
