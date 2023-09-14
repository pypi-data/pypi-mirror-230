
/* Chrysalide - Outil d'analyse de fichiers binaires
 * feeder.c - prototypes pour l'équivalent Python du fichier "arch/operands/feeder.c"
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


#include "feeder.h"


#include <assert.h>
#include <pygobject.h>


#include <arch/operands/feeder-int.h>


#include "../../access.h"
#include "../../helpers.h"
#include "../../glibext/bufferline.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_proxy_feeder_interface_init(GProxyFeederIface *, gpointer *);

/* Compare un fournisseur avec un autre. */
static int py_proxy_feeder___cmp___wrapper(const GProxyFeeder *, const GProxyFeeder *);

/* Traduit un fournisseur en version humainement lisible. */
static void py_proxy_feeder_print_wrapper(const GProxyFeeder *, GBufferLine *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Effectue une comparaison avec un objet Python 'ProxyFeeder'. */
static PyObject *py_proxy_feeder_richcompare(PyObject *, PyObject *, int);

/* Traduit un fournisseur en version humainement lisible. */
static PyObject *py_proxy_feeder_print(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_proxy_feeder_interface_init(GProxyFeederIface *iface, gpointer *unused)
{

#define PROXY_FEEDER_DOC                                                    \
    "ProxyFeeder gives an interface for operands which aim to provide"      \
    " a dynamic content.\n"                                                 \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, ProxyFeeder):\n"                   \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.arch.operands.ProxyFeeder._compare();\n"                \
    "* pychrysalide.arch.operands.ProxyFeeder._print();\n"                  \

    iface->compare = py_proxy_feeder___cmp___wrapper;
    iface->print = py_proxy_feeder_print_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier opérande à consulter.                            *
*                b = second opérande à consulter.                             *
*                                                                             *
*  Description : Compare un fournisseur avec un autre.                        *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_proxy_feeder___cmp___wrapper(const GProxyFeeder *a, const GProxyFeeder *b)
{
    int result;                             /* Empreinte à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define PROXY_FEEDER_CMP_WRAPPER PYTHON_WRAPPER_DEF             \
(                                                               \
    __cmp__, "$self, other, /",                                 \
    METH_VARARGS,                                               \
    "Abstract method used to compare the proxy feeder with"     \
    " another one. This second object is always an"             \
    " pychrysalide.arch.operands.ProxyFeeder instance.\n"       \
    "\n"                                                        \
    " This is the Python old-style comparison method, but"      \
    " Chrysalide provides a glue to automatically build a rich" \
    " version of this function."                                \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(a));

    if (has_python_method(pyobj, "__cmp__"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(b)));

        pyret = run_python_method(pyobj, "__cmp__", args);

        if (pyret != NULL)
        {
            if (PyLong_Check(pyret))
                result = PyLong_AsLong(pyret);
        }

        Py_DECREF(args);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : feeder = fournisseur à traiter.                              *
*                line   = ligne tampon où imprimer l'élément donné.           *
*                                                                             *
*  Description : Traduit un fournisseur en version humainement lisible.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_proxy_feeder_print_wrapper(const GProxyFeeder *feeder, GBufferLine *line)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define PROXY_FEEDER_PRINT_WRAPPER PYTHON_WRAPPER_DEF               \
(                                                                   \
    _print, "$self, line, /",                                       \
    METH_VARARGS,                                                   \
    "Abstract method used to generate content into a rendering"     \
    " line, which is a provided pychrysalide.glibext.BufferLine"    \
    " instance."                                                    \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(feeder));

    if (has_python_method(pyobj, "_print"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(line)));

        pyret = run_python_method(pyobj, "_print", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

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
*  Description : Effectue une comparaison avec un objet Python 'ProxyFeeder'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proxy_feeder_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    const GProxyFeeder *feeder_a;           /* Premier élément à traiter   */
    const GProxyFeeder *feeder_b;           /* Second élément à traiter    */
    int status;                             /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_proxy_feeder_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    feeder_a = G_PROXY_FEEDER(pygobject_get(a));
    feeder_b = G_PROXY_FEEDER(pygobject_get(b));

    status = py_proxy_feeder___cmp___wrapper(feeder_a, feeder_b);

    result = status_to_rich_cmp_state(status, op);

 cmp_done:

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Traduit un fournisseur en version humainement lisible.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proxy_feeder_print(PyObject *self, PyObject *args)
{
    GBufferLine *line;                      /* Ligne de rendu à compléter  */
    GProxyFeeder *feeder;                   /* Version native              */
    int ret;                                /* Bilan de lecture des args.  */

#define PROXY_FEEDER_PRINT_METHOD PYTHON_METHOD_DEF                     \
(                                                                       \
    print, "$self, line, /",                                            \
    METH_VARARGS, py_proxy_feeder,                                      \
    "Produce output into a rendering line.\n"                           \
    "\n"                                                                \
    "The provided line is a pychrysalide.glibext.BufferLine instance."  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_buffer_line, &line);
    if (!ret) return NULL;

    feeder = G_PROXY_FEEDER(pygobject_get(self));

    g_proxy_feeder_print(feeder, line);

    Py_RETURN_NONE;

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

PyTypeObject *get_python_proxy_feeder_type(void)
{
    static PyMethodDef py_proxy_feeder_methods[] = {
        PROXY_FEEDER_CMP_WRAPPER,
        PROXY_FEEDER_PRINT_WRAPPER,
        PROXY_FEEDER_PRINT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_proxy_feeder_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_proxy_feeder_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.ProxyFeeder",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = PROXY_FEEDER_DOC,

        .tp_richcompare = py_proxy_feeder_richcompare,

        .tp_methods     = py_proxy_feeder_methods,
        .tp_getset      = py_proxy_feeder_getseters

    };

    return &py_proxy_feeder_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ProxyFeeder'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_proxy_feeder_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ProxyFeeder'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_proxy_feeder_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_proxy_feeder_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_PROXY_FEEDER, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en fournisseur intermédiaire.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_proxy_feeder(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_proxy_feeder_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to proxy feeder");
            break;

        case 1:
            *((GProxyFeeder **)dst) = G_PROXY_FEEDER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
