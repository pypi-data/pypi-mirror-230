
/* Chrysalide - Outil d'analyse de fichiers binaires
 * group.h - équivalent Python du fichier "plugins/kaitai/parsers/group.h"
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "group.h"


#include <pygobject.h>
#include <string.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/arch/vmpa.h>
#include <plugins/yaml/python/node.h>


#include "../record.h"
#include "../parsers/struct.h"
#include "../../records/group-int.h"



CREATE_DYN_CONSTRUCTOR(record_group, G_TYPE_RECORD_GROUP);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_record_group_init(PyObject *, PyObject *, PyObject *);

/* Assure l'encadrement des accès aux champs d'une séquence. */
static PyObject *py_record_group_getattr(PyObject *, char *);



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

static int py_record_group_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GKaitaiStruct *kstruct;                 /* Séquence définie créatrice  */
    GBinContent *content;                   /* Contenu binaire analysé     */
    int ret;                                /* Bilan de lecture des args.  */
    GRecordGroup *group;                    /* Création GLib à transmettre */

#define RECORD_GROUP_DOC                                                        \
    "The RecordGroup class stores a map of parsed attributes with their"        \
    " relative values. Each of theses Kaitai attributes can be accessed as"     \
    " usual Python attribute.\n"                                                \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    RecordGroup(kstruct, content)"                                         \
    "\n"                                                                        \
    "Where the *kstruct* refers to a"                                           \
    " pychrysalide.plugins.kaitai.parsers.KaitaiStructure instance as the"      \
    " creator of the newly created object, and *content* points to a"           \
    " pychrysalide.analysis.BinContent instance."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&",
                           convert_to_kaitai_structure, &kstruct,
                           convert_to_binary_content, &content);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    group = G_RECORD_GROUP(pygobject_get(self));

    if (!g_record_group_create(group, kstruct, content))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create record group."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = structure C convertie en Python.                      *
*                name = nom du champ auquel un accès est demandé.             *
*                                                                             *
*  Description : Assure l'encadrement des accès aux champs d'une séquence.    *
*                                                                             *
*  Retour      : Valeur du champ demandé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_record_group_getattr(PyObject *self, char *name)
{
    PyObject *result;                       /* Elément à retourner         */
    GRecordGroup *group;                    /* Version native de l'objet   */
    GMatchRecord *found;                    /* Sous-élément identifié      */
    PyObject *w;                            /* Conversion du nom de champ  */
    PyTypeObject *tp;                       /* Type de l'objet manipulé    */

    group = G_RECORD_GROUP(pygobject_get(self));

    found = g_match_record_find_by_name(G_MATCH_RECORD(group), name, strlen(name), DIRECT_SEARCH_DEEP_LEVEL);

    if (found != NULL)
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_unref(G_OBJECT(found));
    }

    else
    {
        w = PyUnicode_InternFromString(name);
        if (w == NULL) return NULL;

        tp = Py_TYPE(self);

        if (tp->tp_base->tp_getattro != NULL)
            result = tp->tp_base->tp_getattro(self, w);

        else
        {
            PyErr_Format(PyExc_AttributeError,
                         "type object '%.50s' has no attribute '%U'",
                         tp->tp_name, name);
            result = NULL;
        }

        Py_DECREF(w);

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

PyTypeObject *get_python_record_group_type(void)
{
    static PyMethodDef py_record_group_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_record_group_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_record_group_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.records.RecordGroup",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_getattr     = py_record_group_getattr,

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RECORD_GROUP_DOC,

        .tp_methods     = py_record_group_methods,
        .tp_getset      = py_record_group_getseters,

        .tp_init        = py_record_group_init,
        .tp_new         = py_record_group_new,

    };

    return &py_record_group_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...records.RecordGroup. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_record_group_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'RecordGroup'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_record_group_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.records");

        dict = PyModule_GetDict(module);

        if (!ensure_python_match_record_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_RECORD_GROUP, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en correspondances attribut/binaire.      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_record_group(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_record_group_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to record group");
            break;

        case 1:
            *((GRecordGroup **)dst) = G_RECORD_GROUP(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
