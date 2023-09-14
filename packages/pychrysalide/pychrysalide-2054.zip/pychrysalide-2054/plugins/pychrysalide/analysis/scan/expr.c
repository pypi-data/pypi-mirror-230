
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr.c - équivalent Python du fichier "analysis/scan/expr.c"
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


#include "expr.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/content.h>
#include <analysis/scan/expr-int.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/glibext/comparison.h>


#include "constants.h"



/* Initialise la classe générique des expressions d'évaluation. */
static void py_scan_expression_init_gclass(GScanExpressionClass *, gpointer);

CREATE_DYN_ABSTRACT_CONSTRUCTOR(scan_expression, G_TYPE_SCAN_EXPRESSION, py_scan_expression_init_gclass);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_scan_expression_init(PyObject *, PyObject *, PyObject *);

/* Réalise une comparaison entre objets selon un critère précis. */
static bool py_scan_expression_compare_rich_wrapper(const GScanExpression *, const GScanExpression *, RichCmpOperation, bool *);

/* Indique l'état de réduction d'une expression. */
static PyObject *py_scan_expression_get_state(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe générique des expressions d'évaluation. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_scan_expression_init_gclass(GScanExpressionClass *class, gpointer unused)
{
    class->cmp_rich = py_scan_expression_compare_rich_wrapper;

}


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

static int py_scan_expression_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ScanReductionState state;               /* Etat de réduction initial   */
    int ret;                                /* Bilan de lecture des args.  */
    GScanExpression *expr;                  /* Création GLib à transmettre */

    static char *kwlist[] = { "state", NULL };

#define SCAN_EXPRESSION_DOC                                             \
    "A ScanExpression is an abstract object which defines an expression"\
    " involved in data matching when running a scan.\n"                 \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " the following arguments as keyword parameters:\n"                 \
    "* *state*: initial state of reduction for the expression, as a"    \
    " pychrysalide.analysis.scan.ScanExpression.ScanReductionState"     \
    " value."   \
    "\n"                                                                \
    "The following methods have to be defined for new classes:\n"       \
    "* pychrysalide.analysis.scan.ScanExpression._cmp_rich().\n"

    /* Récupération des paramètres */

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist, convert_to_scan_reduction_state, &state);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    expr = G_SCAN_EXPRESSION(pygobject_get(self));

    if (!g_scan_expression_create(expr, state))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create scan expression."));
        return -1;
    }

    return 0;

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

static bool py_scan_expression_compare_rich_wrapper(const GScanExpression *item, const GScanExpression *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define SCAN_EXPRESSION_CMP_RICH_WRAPPER PYTHON_WRAPPER_DEF             \
(                                                                       \
    _cmp_rich, "$self, other, op, /",                                   \
    METH_VARARGS,                                                       \
    "Abstract method used to compare the expression against another"    \
    " one.\n"                                                           \
    "\n"                                                                \
    "The second *other* instance is built from the same type as *self*."\
    " The *op* argument points to a"                                    \
    " pychrysalide.glibext.ComparableItem.RichCmpOperation mode"        \
    " describing the expected comparison.\n"                            \
    "\n"                                                                \
    "The result is a boolean status or *None* if the comparison"        \
    " process is undefined."                                            \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

    if (has_python_method(pyobj, "_cmp_rich"))
    {
        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(other)));
        PyTuple_SetItem(args, 1, cast_with_constants_group_from_type(get_python_comparable_item_type(),
                                                                     "RichCmpOperation", op));

        pyret = run_python_method(pyobj, "_cmp_rich", args);

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

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique l'état de réduction d'une expression.                *
*                                                                             *
*  Retour      : Etat courant associé à l'expression.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_expression_get_state(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GScanExpression *expr;                  /* Version GLib de l'opérande  */
    ScanReductionState state;               /* Etat courant de l'expression*/

#define SCAN_EXPRESSION_STATE_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                                   \
    state, py_scan_expression,                                      \
    "Current state of the expression, relative to the reduction"    \
    " process, as a"                                                \
    " pychrysalide.analysis.scan.ScanExpression.ScanReductionState" \
    " value."                                                       \
)

    expr = G_SCAN_EXPRESSION(pygobject_get(self));

    state = g_scan_expression_get_state(expr);

    result = cast_with_constants_group_from_type(get_python_scan_expression_type(), "ScanReductionState", state);

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

PyTypeObject *get_python_scan_expression_type(void)
{
    static PyMethodDef py_scan_expression_methods[] = {
        SCAN_EXPRESSION_CMP_RICH_WRAPPER,
        { NULL }
    };

    static PyGetSetDef py_scan_expression_getseters[] = {
        SCAN_EXPRESSION_STATE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_scan_expression_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.ScanExpression",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SCAN_EXPRESSION_DOC,

        .tp_methods     = py_scan_expression_methods,
        .tp_getset      = py_scan_expression_getseters,

        .tp_init        = py_scan_expression_init,
        .tp_new         = py_scan_expression_new,

    };

    return &py_scan_expression_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...scan.ScanExpression'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_scan_expression_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ScanExpression'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_scan_expression_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!ensure_python_comparable_item_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_SCAN_EXPRESSION, type))
            return false;

        if (!define_expression_value_type_constants(type))
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

int convert_to_scan_expression(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_scan_expression_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to match expression");
            break;

        case 1:
            *((GScanExpression **)dst) = G_SCAN_EXPRESSION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
