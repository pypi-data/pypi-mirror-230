
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proxy.c - équivalent Python du fichier "arch/operands/proxy.c"
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


#include "proxy.h"


#include <pygobject.h>


#include <i18n.h>
#include <arch/operands/proxy-int.h>
#include <plugins/dt.h>


#include "feeder.h"
#include "../operand.h"
#include "../../access.h"
#include "../../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_proxy_operand_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des descriptions de fichier binaire. */
static void py_proxy_operand_init_gclass(GProxyOperandClass *, gpointer);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_proxy_operand_init(PyObject *, PyObject *, PyObject *);



/* ------------------ OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES ------------------ */


/* Fournit le fournisseur représenté par l'opérande. */
static PyObject *py_proxy_operand_get_feeder(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du nouvel objet à mettre en place.               *
*                args = éventuelle liste d'arguments.                         *
*                kwds = éventuel dictionnaire de valeurs mises à disposition. *
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proxy_operand_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_proxy_operand_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_PROXY_OPERAND, type->tp_name,
                               (GClassInitFunc)py_proxy_operand_init_gclass, NULL, NULL);

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
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe des descriptions de fichier binaire.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_proxy_operand_init_gclass(GProxyOperandClass *class, gpointer unused)
{

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

static int py_proxy_operand_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GProxyFeeder *feeder;                   /* Fournisseur transmis        */
    int ret;                                /* Bilan de lecture des args.  */
    GProxyOperand *operand;                 /* Opérande à manipuler        */

#define PROXY_OPERAND_DOC                                                   \
    "The ProxyOperand object behaves like a proxy operand for an object"    \
    " which can feed the operand with content.\n"                           \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    ProxyOperand(feeder)"                                              \
    "\n"                                                                    \
    "Where feeder is an instance implementing the"                          \
    " pychrysalide.arch.operands.ProxyFeeder interface."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_proxy_feeder, &feeder);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    operand = G_PROXY_OPERAND(pygobject_get(self));

    g_object_ref(G_OBJECT(feeder));
    operand->feeder = feeder;

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                    OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le fournisseur représenté par l'opérande.            *
*                                                                             *
*  Retour      : Fournisseur associé à l'opérande.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proxy_operand_get_feeder(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GProxyOperand *operand;                 /* Version GLib de l'opérande  */
    GProxyFeeder *feeder;                   /* Fournisseur lié à l'opérande*/

#define PROXY_OPERAND_FEEDER_ATTRIB PYTHON_GET_DEF_FULL         \
(                                                               \
    feeder, py_proxy_operand,                                   \
    "Give the proxy feeder linked to the operand.\n"            \
    "\n"                                                        \
    "This feeder is a pychrysalide.arch.operands.ProxyFeeder"   \
    " providing content for the operand."                       \
)

    operand = G_PROXY_OPERAND(pygobject_get(self));

    feeder = g_proxy_operand_get_feeder(operand);

    result = pygobject_new(G_OBJECT(feeder));
    g_object_unref(feeder);

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

PyTypeObject *get_python_proxy_operand_type(void)
{
    static PyMethodDef py_proxy_operand_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_proxy_operand_getseters[] = {
        PROXY_OPERAND_FEEDER_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_proxy_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.ProxyOperand",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = PROXY_OPERAND_DOC,

        .tp_methods     = py_proxy_operand_methods,
        .tp_getset      = py_proxy_operand_getseters,

        .tp_init        = py_proxy_operand_init,
        .tp_new         = py_proxy_operand_new,

    };

    return &py_proxy_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ArchOperand'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_proxy_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchOperand'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_proxy_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!ensure_python_arch_operand_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_PROXY_OPERAND, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande renvoyant vers un élément.    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_proxy_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_proxy_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to proxy operand");
            break;

        case 1:
            *((GProxyOperand **)dst) = G_PROXY_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
