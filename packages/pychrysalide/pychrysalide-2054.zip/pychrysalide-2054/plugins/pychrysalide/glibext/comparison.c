
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comparison.c - équivalent Python du fichier "glibext/comparison.h"
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


#include "comparison.h"


#include <pygobject.h>


#include <glibext/comparison-int.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/content.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de comparaison. */
static void py_comparable_item_interface_init(GComparableItemIface *, gpointer *);

/* Réalise une comparaison entre objets selon un critère précis. */
static bool py_comparable_item_compare_rich(const GComparableItem *, const GComparableItem *, RichCmpOperation, bool *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Effectue une comparaison avec un objet 'ComparableItem'. */
static PyObject *py_comparable_item_richcompare(PyObject *, PyObject *, int);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de comparaison.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_comparable_item_interface_init(GComparableItemIface *iface, gpointer *unused)
{

#define COMPARABLE_ITEM_DOC                                                 \
    "ComparableItem provides an interface to compare objects.\n"            \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, ComparableItem):\n"                \
    "        ...\n"                                                         \
    "\n"

    iface->cmp_rich = py_comparable_item_compare_rich;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = premier objet à cnsulter pour une comparaison.      *
*                other  = second objet à cnsulter pour une comparaison.       *
*                op     = opération de comparaison à réaliser.                *
*                status = bilan des opérations de comparaison. [OUT]          *
*                                                                             *
*  Description : Réalise une comparaison entre objets selon un critère précis.*
*                                                                             *
*  Retour      : true si la comparaison a pu être effectuée, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_comparable_item_compare_rich(const GComparableItem *item, const GComparableItem *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyitem;                       /* Objet Python concerné #1    */
    PyObject *pyother;                      /* Objet Python concerné #2    */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

    result = false;

    gstate = PyGILState_Ensure();

    pyitem = pygobject_new(G_OBJECT(item));
    pyother = pygobject_new(G_OBJECT(other));

    pyret = PyObject_RichCompare(pyitem, pyother, op);

    if (pyret != NULL)
    {
        ret = PyBool_Check(pyret);

        if (ret)
        {
            *status = (pyret == Py_True);
            result = true;
        }

        Py_DECREF(pyret);

    }

    Py_DECREF(pyother);
    Py_DECREF(pyitem);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet 'ComparableItem'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_comparable_item_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    GComparableItem *item_a;                /* Instance à manipuler #1     */
    GComparableItem *item_b;                /* Instance à manipuler #2     */
    bool valid;                             /* Indication de validité      */
    bool status;                            /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_comparable_item_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    item_a = G_COMPARABLE_ITEM(pygobject_get(a));
    item_b = G_COMPARABLE_ITEM(pygobject_get(b));

    valid = g_comparable_item_compare_rich(item_a, item_b, op, &status);

    if (valid)
        result = status ? Py_True : Py_False;
    else
        result = Py_NotImplemented;

 cmp_done:

    Py_INCREF(result);

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

PyTypeObject *get_python_comparable_item_type(void)
{
    static PyMethodDef py_comparable_item_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_comparable_item_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_comparable_item_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.ComparableItem",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = COMPARABLE_ITEM_DOC,

        .tp_richcompare = py_comparable_item_richcompare,

        .tp_methods     = py_comparable_item_methods,
        .tp_getset      = py_comparable_item_getseters,

    };

    return &py_comparable_item_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....ComparableItem'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_comparable_item_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ComparableItem' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_comparable_item_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_comparable_item_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_COMPARABLE_ITEM, type, &info))
            return false;

        if (!define_comparable_item_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en élément comparable.                    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_comparable_item(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_comparable_item_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to comparable item");
            break;

        case 1:
            *((GComparableItem **)dst) = G_COMPARABLE_ITEM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
