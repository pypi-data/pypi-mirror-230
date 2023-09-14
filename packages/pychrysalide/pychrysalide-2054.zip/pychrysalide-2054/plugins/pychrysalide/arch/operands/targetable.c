
/* Chrysalide - Outil d'analyse de fichiers binaires
 * targetable.c - prototypes pour l'équivalent Python du fichier "arch/operands/targetable.c"
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


#include "targetable.h"


#include <pygobject.h>


#include <arch/operands/targetable-int.h>


#include "../processor.h"
#include "../vmpa.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../format/format.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface pour ciblage. */
static void py_targetable_operand_init(GTargetableOperandIface *, gpointer *);

/* Obtient l'adresse de la cible visée par un opérande. */
static bool py_targetable_operand_get_addr_wrapper(const GTargetableOperand *, const vmpa2t *, GBinFormat *, GArchProcessor *, vmpa2t *);



/* ------------------------ INTERFACE POUR OPERANDE CIBLABLE ------------------------ */


/* Obtient l'adresse de la cible visée par un opérande. */
static PyObject *py_targetable_operand_get_addr(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface pour ciblage.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_targetable_operand_init(GTargetableOperandIface *iface, gpointer *unused)
{

#define TARGETABLE_OPERAND_DOC                                              \
    "The TargetableOperand interface depicts operands which can drive to"   \
    " another location.\n"                                                  \
    "\n"                                                                    \
    "By instance, an immediate value can target a given address into"       \
    " some function code."                                                  \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, TargetableOperand):\n"             \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following method has to be defined for new implementations:\n"     \
    "* pychrysalide.arch.operands.RenamedOperand._get_addr();\n"            \

    iface->get_addr = py_targetable_operand_get_addr_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                src     = localisation de l'instruction mère.                *
*                format  = format reconnu pour le binaire chargé.             *
*                proc    = architecture associée à ce même binaire.           *
*                addr    = localisation de la cible. [OUT]                    *
*                                                                             *
*  Description : Obtient l'adresse de la cible visée par un opérande.         *
*                                                                             *
*  Retour      : true si la cible est valide, false sinon.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_targetable_operand_get_addr_wrapper(const GTargetableOperand *operand, const vmpa2t *src, GBinFormat *format, GArchProcessor *proc, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define TARGETABLE_OPERAND_GET_ADDR_WRAPPER PYTHON_WRAPPER_DEF          \
(                                                                       \
    _get_addr, "$self, src, format, proc",                              \
    METH_VARARGS,                                                       \
    "Abstract method used to compute a target address from an operand." \
    "\n"                                                                \
    "The *src* argument is the location of the instruction owning the"  \
    " operand, as a pychrysalide.arch.vmpa instance. The format is a"   \
    " pychrysalide.format.BinFormat instance, providing all needed"     \
    " information and the processor is a"                               \
    " pychrysalide.arch.ArchProcessor instance, providing all needed"   \
    " information too.\n"                                               \
    "\n"                                                                \
    "The result has to be a pychrysalide.arch.vmpa address or None."    \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_get_addr"))
    {
        args = PyTuple_New(3);
        PyTuple_SetItem(args, 0, build_from_internal_vmpa(src));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(format)));
        PyTuple_SetItem(args, 2, pygobject_new(G_OBJECT(proc)));

        pyret = run_python_method(pyobj, "_get_addr", NULL);

        if (pyret != NULL)
        {
            ret = convert_any_to_vmpa(pyret, addr);

            result = (ret == 1);

            PyErr_Clear();

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          INTERFACE POUR OPERANDE CIBLABLE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Obtient l'adresse de la cible visée par un opérande.         *
*                                                                             *
*  Retour      : Localisation de la cible ou None.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_targetable_operand_get_addr(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *src;                            /* Version native d'adresse    */
    GBinFormat *format;                     /* Instance GLib du format     */
    GArchProcessor *proc;                   /* Instance GLib de l'archi.   */
    int ret;                                /* Bilan de lecture des args.  */
    GTargetableOperand *operand;            /* Instance à manipuler        */
    vmpa2t addr;                            /* Localisation à cibler       */
    bool defined;                           /* Cible définie ?             */

#define TARGETABLE_OPERAND_GET_ADDR_METHOD PYTHON_METHOD_DEF            \
(                                                                       \
    get_addr, "$self, src, format, proc",                               \
    METH_VARARGS, py_targetable_operand,                                \
    "Compute a target address from an operand."                         \
    "\n"                                                                \
    "The following arguments are required:\n"                           \
    "* src is the location of the instruction owning the operand, as a" \
    " pychrysalide.arch.vmpa instance.\n"                               \
    "* format is a pychrysalide.format.BinFormat instance, providing"   \
    " all needed information.\n"                                        \
    "* proc is a pychrysalide.arch.ArchProcessor instance, providing"   \
    " all needed information too.\n"                                    \
    "\n"                                                                \
    "The result is a pychrysalide.arch.vmpa address or None."           \
)

    ret = PyArg_ParseTuple(args, "O&O&O&",
                           convert_any_to_vmpa, &src,
                           convert_to_binary_format, &format,
                           convert_to_arch_processor, &proc);
    if (!ret) return NULL;

    operand = G_TARGETABLE_OPERAND(pygobject_get(self));

    defined = g_targetable_operand_get_addr(operand, src, format, proc, &addr);

    if (defined)
        result = build_from_internal_vmpa(&addr);
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    clean_vmpa_arg(src);

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

PyTypeObject *get_python_targetable_operand_type(void)
{
    static PyMethodDef py_targetable_operand_methods[] = {
        TARGETABLE_OPERAND_GET_ADDR_WRAPPER,
        TARGETABLE_OPERAND_GET_ADDR_METHOD,
        { NULL }
    };

    static PyGetSetDef py_targetable_operand_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_targetable_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.TargetableOperand",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = TARGETABLE_OPERAND_DOC,

        .tp_methods     = py_targetable_operand_methods,
        .tp_getset      = py_targetable_operand_getseters

    };

    return &py_targetable_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....TargetableOperand'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_targetable_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'TargetableOperand'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_targetable_operand_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_targetable_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_TARGETABLE_OPERAND, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande ciblable.                     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_targetable_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_targetable_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to targetable operand");
            break;

        case 1:
            *((GTargetableOperand **)dst) = G_TARGETABLE_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
