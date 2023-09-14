
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list.c - équivalent Python du fichier "analysis/scan/patterns/modifiers/list.c"
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


#include "list.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/scan/patterns/modifiers/list.h>


#include "../modifier.h"
#include "../../../../access.h"
#include "../../../../helpers.h"



CREATE_DYN_CONSTRUCTOR(scan_modifier_list, G_TYPE_SCAN_MODIFIER_LIST);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_scan_modifier_list_init(PyObject *, PyObject *, PyObject *);

/* Intègre un nouveau transformateur dans une liste. */
static PyObject *py_scan_modifier_list_add(PyObject *, PyObject *);

/* Fournit les transformateurs associés à la liste. */
static PyObject *py_scan_modifier_list_get_modifiers(PyObject *, void *);



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

static int py_scan_modifier_list_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define SCAN_MODIFIER_LIST_DOC                                              \
    "The *ModifierList* class is a special modifier which groups a list of" \
    " modifiers for byte patterns."                                         \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    ModifierList()"                                                    \
    "\n"                                                                    \
    "The keyword for such a modifier is *(list)*."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = projet d'étude à manipuler.                           *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Intègre un nouveau transformateur dans une liste.            *
*                                                                             *
*  Retour      : Bilan de l'ajout : False si un élément similaire est déjà là.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_modifier_list_add(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Absence de retour Python    */
    GScanTokenModifier *modifier;           /* Modificateur à intégrer     */
    int ret;                                /* Bilan de lecture des args.  */
    GScanModifierList *list;                /* Version GLib du type        */
    bool status;                            /* Bilan de l'opération        */

#define SCAN_MODIFIER_LIST_ADD_METHOD PYTHON_METHOD_DEF                     \
(                                                                           \
    add, "$self, modifier, /",                                              \
    METH_VARARGS, py_scan_modifier_list,                                    \
    "Add an extra modifier to the list.\n"                                  \
    "\n"                                                                    \
    "This *modifier* parameter has to be a"                                 \
    " pychrysalide.analysis.scan.patterns.TokenModifier instance."          \
    "\n"                                                                    \
    "The function returns *True* if the provided modifier did not already"  \
    " exist in the list, *False* otherwise."                                \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_scan_token_modifier, &modifier);
    if (!ret) return NULL;

    list = G_SCAN_MODIFIER_LIST(pygobject_get(self));

    status = g_scan_modifier_list_add(list, modifier);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les transformateurs associés à la liste.             *
*                                                                             *
*  Retour      : Liste de modificateurs de séquence d'octets.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_modifier_list_get_modifiers(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GScanModifierList *list;                /* Version GLib du type        */
    size_t count;                           /* Nombre de transformateurs   */
    size_t i;                               /* Boucle de parcours          */
    GScanTokenModifier *modifier;           /* Modificateur de la liste    */

#define SCAN_MODIFIER_LIST_MODIFIERS_ATTRIB PYTHON_GET_DEF_FULL                             \
(                                                                                           \
    modifiers, py_scan_modifier_list,                                                       \
    "List of all modifiers contained in a list.\n"                                          \
    "\n"                                                                                    \
    "The returned value is a tuple of pychrysalide.analysis.scan.patterns.TokenModifier"    \
    " instances."                                                                           \
)

    list = G_SCAN_MODIFIER_LIST(pygobject_get(self));

    count = g_scan_modifier_list_count(list);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        modifier = g_scan_modifier_list_get(list, i);

        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(modifier)));

        g_object_unref(modifier);

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

PyTypeObject *get_python_scan_modifier_list_type(void)
{
    static PyMethodDef py_scan_modifier_list_methods[] = {
        SCAN_MODIFIER_LIST_ADD_METHOD,
        { NULL }
    };

    static PyGetSetDef py_scan_modifier_list_getseters[] = {
        SCAN_MODIFIER_LIST_MODIFIERS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_scan_modifier_list_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.patterns.modifiers.ModifierList",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SCAN_MODIFIER_LIST_DOC,

        .tp_methods     = py_scan_modifier_list_methods,
        .tp_getset      = py_scan_modifier_list_getseters,

        .tp_init        = py_scan_modifier_list_init,
        .tp_new         = py_scan_modifier_list_new,

    };

    return &py_scan_modifier_list_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....ModifierList'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_scan_modifier_list_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ModifierList'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_scan_modifier_list_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan.patterns.modifiers");

        dict = PyModule_GetDict(module);

        if (!ensure_python_scan_token_modifier_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_SCAN_MODIFIER_LIST, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en liste de transormations d'octets.      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_scan_modifier_list(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_scan_modifier_list_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to modifier list");
            break;

        case 1:
            *((GScanModifierList **)dst) = G_SCAN_MODIFIER_LIST(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
