
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - équivalent Python du fichier "analysis/scan/item.c"
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "item.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/scan/item-int.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "context.h"



CREATE_DYN_CONSTRUCTOR(registered_item, G_TYPE_REGISTERED_ITEM);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_registered_item_init(PyObject *, PyObject *, PyObject *);

/* Lance une résolution d'élément à appeler. */
static PyObject *py_registered_item_resolve(PyObject *, PyObject *);



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

static int py_registered_item_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define REGISTERED_ITEM_DOC                                            \
    "The *RegisteredItem* class defines the basics for evaluation"  \
    " items involved into content scanning.\n"                      \
    "\n"                                                            \
    "Instances can be created using the following constructor:\n"   \
    "\n"                                                            \
    "    RegisteredItem()"

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = élément d'appel à consulter.                          *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Lance une résolution d'élément à appeler.                    *
*                                                                             *
*  Retour      : Nouvel élément d'appel identifié ou None.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_registered_item_resolve(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *target;                     /* Désignation de la cible     */
    GScanContext *ctx;                      /* Contexte d'analyse          */
    GScanScope *scope;                      /* Portée de variables locales */
    int ret;                                /* Bilan de lecture des args.  */
    GRegisteredItem *item;                  /* Version native              */
    bool status;                            /* Bilan d'exécution           */
    GRegisteredItem *resolved;              /* Elément trouvé              */

#define REGISTERED_ITEM_RESOLVE_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    resolve, "$self, target, /, ctx=None, scope=None",                  \
    METH_VARARGS, py_registered_item,                                   \
    "Resolve a name into a scan item."                                  \
    "\n"                                                                \
    "The *target* name is the only mandatory parameter and has to point"\
    " to only one item. The *ctx* argument points to an optional useful"\
    " storage for resolution lookup, as a"                              \
    " pychrysalide.analysis.scan.ScanContext instance. The *args* list" \
    " defines an optional list of arguments, as"                        \
    " pychrysalide.analysis.scan.ScanExpression instances, to use for"  \
    " building the resolved item. The *final* flag states if the"       \
    " scanning process is about to conclude or not."                    \
    "\n"                                                                \
    "The result is an object inheriting from"                           \
    " pychrysalide.analysis.scan.RegisteredItem or *None* if the"       \
    " resolution operation failed."                                     \
)

    ctx = NULL;
    scope = NULL;

    ret = PyArg_ParseTuple(args, "s|O&", &target,
                           convert_to_scan_context, &ctx);
    if (!ret) return NULL;

    item = G_REGISTERED_ITEM(pygobject_get(self));

    status = g_registered_item_resolve(item, target, ctx, scope, &resolved);

    if (!status)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("Unable to resolve any target from the item"));
    }
    else
    {
        if (resolved != NULL)
        {
            result = pygobject_new(G_OBJECT(resolved));
            g_object_unref(G_OBJECT(resolved));
        }
        else
        {
            result = Py_None;
            Py_INCREF(result);
        }
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un composant nommé à manipuler.*
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_registered_item_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Décompte à retourner        */
    GRegisteredItem *item;                  /* Version native              */
    char *name;                             /* Désignation à convertir     */

#define REGISTERED_ITEM_NAME_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                       \
    name, py_registered_item,                                           \
    "Name linked to the registered item.\n"                             \
    "\n"                                                                \
    "The result should be a string, or *None* for the root namespace."  \
)

    item = G_REGISTERED_ITEM(pygobject_get(self));

    name = g_registered_item_get_name(item);

    if (name == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = PyUnicode_FromString(name);
        free(name);
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

PyTypeObject *get_python_registered_item_type(void)
{
    static PyMethodDef py_registered_item_methods[] = {
        REGISTERED_ITEM_RESOLVE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_registered_item_getseters[] = {
        REGISTERED_ITEM_NAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_registered_item_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.RegisteredItem",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = REGISTERED_ITEM_DOC,

        .tp_methods     = py_registered_item_methods,
        .tp_getset      = py_registered_item_getseters,

        .tp_init        = py_registered_item_init,
        .tp_new         = py_registered_item_new,

    };

    return &py_registered_item_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...scan.RegisteredItem'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_registered_item_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'RegisteredItem' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_registered_item_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_REGISTERED_ITEM, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en expression d'évaluation généraliste.   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_registered_item(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_registered_item_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to generic scan expression");
            break;

        case 1:
            *((GRegisteredItem **)dst) = G_REGISTERED_ITEM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
