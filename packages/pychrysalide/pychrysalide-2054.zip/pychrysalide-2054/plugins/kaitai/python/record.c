
/* Chrysalide - Outil d'analyse de fichiers binaires
 * record.h - équivalent Python du fichier "plugins/kaitai/record.h"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "record.h"


#include <pygobject.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/arch/vmpa.h>


#include "parser.h"
#include "../record.h"



CREATE_DYN_ABSTRACT_CONSTRUCTOR(match_record, G_TYPE_MATCH_RECORD, NULL);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_match_record_init(PyObject *, PyObject *, PyObject *);

/* Modifie la référence au créateur de la correspondance. */
static int py_match_record_set_creator(PyObject *, PyObject *, void *);

/* Renvoie vers le lecteur à l'origine de la correspondance. */
static PyObject *py_match_record_get_creator(PyObject *, void *);

/* Fournit le contenu lié à une correspondance établie. */
static PyObject *py_match_record_get_content(PyObject *, void *);

/* Calcule ou fournit la zone couverte par une correspondance. */
static PyObject *py_match_record_get_range(PyObject *, void *);

/* Lit les octets bruts couverts par une correspondance. */
static PyObject *py_match_record_get_raw_bytes(PyObject *, void *);



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

static int py_match_record_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define MATCH_RECORD_DOC                                                    \
    "MatchRecord is an abstract class providing mainly location and raw"    \
    " data of an area which has matched a part of a binary content."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = correspondance à manipuler.                        *
*                value   = lecteur à l'origine de la correspondance.          *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Modifie la référence au créateur de la correspondance.       *
*                                                                             *
*  Retour      : Bilan de la définition.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_match_record_set_creator(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Bilan à renvoyer            */
    GMatchRecord *record;                   /* Version GLib de l'objet     */
    GKaitaiParser *parser;                  /* Lecteur à l'origine         */

    record = G_MATCH_RECORD(pygobject_get(self));

    if (!convert_to_kaitai_parser(value, &parser))
        result = -1;

    else
    {
        g_match_record_fix_creator(record, parser);
        result = 0;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = correspondance à manipuler.                        *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Renvoie vers le lecteur à l'origine de la correspondance.    *
*                                                                             *
*  Retour      : Lecteur à l'origine de la création.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_match_record_get_creator(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GMatchRecord *record;                   /* Version GLib de l'objet     */
    GKaitaiParser *parser;                  /* Lecteur à l'origine         */

#define MATCH_RECORD_CREATOR_ATTRIB PYTHON_GETSET_DEF_FULL                      \
(                                                                               \
    creator, py_match_record,                                                   \
    "Provide or define the pychrysalide.plugins.kaitai.KaitaiParser instance"   \
    " which has created the record.\n"                                          \
    "\n"                                                                        \
    "This field should not be defined after the record creation in most cases." \
)

    record = G_MATCH_RECORD(pygobject_get(self));

    parser = g_match_record_get_creator(record);

    result = pygobject_new(G_OBJECT(parser));
    g_object_unref(parser);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le contenu lié à une correspondance établie.         *
*                                                                             *
*  Retour      : Contenu binaire associé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_match_record_get_content(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GMatchRecord *record;                   /* Conservation à consulter    */
    GBinContent *content;                   /* Contenu associé             */

#define MATCH_RECORD_CONTENT_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                           \
    content, py_match_record,                               \
    "pychrysalide.analysis.BinContent instance linked to"   \
    " the match record."                                    \
)

    record = G_MATCH_RECORD(pygobject_get(self));
    content = g_match_record_get_content(record);

    if (content != NULL)
    {
        result = pygobject_new(G_OBJECT(content));
        g_object_unref(G_OBJECT(content));
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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : Zone de couverture déterminée.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_match_record_get_range(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GMatchRecord *record;                   /* Conservation à consulter    */
    mrange_t range;                         /* Couverture courante         */

#define MATCH_RECORD_RANGE_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                           \
    range, py_match_record,                                 \
    "Area of the matched data for the parsed attribute"     \
    " against a given binary content.\n"                    \
    "\n"                                                    \
    "This property is a pychrysalide.arch.mrange instance." \
)

    record = G_MATCH_RECORD(pygobject_get(self));
    g_match_record_get_range(record, &range);

    result = build_from_internal_mrange(&range);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Lit les octets bruts couverts par une correspondance.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_match_record_get_raw_bytes(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GMatchRecord *record;                   /* Conservation à consulter    */
    bin_t *out;                             /* Données brutes à transmettre*/
    size_t len;                             /* Quantité de ces données     */

#define MATCH_RECORD_RAW_BYTES_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                           \
    raw_bytes, py_match_record,                             \
    "Raw bytes from the area covered by the record."        \
)

    record = G_MATCH_RECORD(pygobject_get(self));

    g_match_record_read_raw_bytes(record, &out, &len);

    result = PyBytes_FromStringAndSize((char *)out, len);
    free(out);

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

PyTypeObject *get_python_match_record_type(void)
{
    static PyMethodDef py_match_record_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_match_record_getseters[] = {
        MATCH_RECORD_CREATOR_ATTRIB,
        MATCH_RECORD_CONTENT_ATTRIB,
        MATCH_RECORD_RANGE_ATTRIB,
        MATCH_RECORD_RAW_BYTES_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_match_record_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.MatchRecord",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = MATCH_RECORD_DOC,

        .tp_methods     = py_match_record_methods,
        .tp_getset      = py_match_record_getseters,

        .tp_init        = py_match_record_init,
        .tp_new         = py_match_record_new,

    };

    return &py_match_record_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...MatchRecord. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_match_record_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'MatchRecord'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_match_record_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_MATCH_RECORD, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en conservation de correspondance.        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_match_record(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_match_record_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to match record");
            break;

        case 1:
            *((GMatchRecord **)dst) = G_MATCH_RECORD(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
