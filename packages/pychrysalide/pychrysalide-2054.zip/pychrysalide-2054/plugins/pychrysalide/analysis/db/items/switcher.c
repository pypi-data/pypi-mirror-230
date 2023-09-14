
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switcher.c - équivalent Python du fichier "analysis/db/items/switcher.c"
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


#include "switcher.h"


#include <malloc.h>
#include <pygobject.h>


#include <analysis/db/items/switcher.h>
#include <plugins/dt.h>


#include "../collection.h"
#include "../item.h"
#include "../../../access.h"
#include "../../../helpers.h"
#include "../../../arch/instruction.h"
#include "../../../arch/vmpa.h"
#include "../../../arch/operands/constants.h"
#include "../../../arch/operands/immediate.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Crée un nouvel objet Python de type 'DbSwitcher'. */
static PyObject *py_db_switcher_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_db_switcher_init(PyObject *, PyObject *, PyObject *);

/* Fournit l'adresse associée à une bascule. */
static PyObject *py_db_switcher_get_address(PyObject *, void *);

/* Fournit le chemin menant vers l'opérande basculé. */
static PyObject *py_db_switcher_get_path(PyObject *, void *);

/*  Indique l'affichage vers lequel un opérande a basculé. */
static PyObject *py_db_switcher_get_display(PyObject *, void *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Crée un nouvel objet Python de type 'SwitcherCollection'. */
static PyObject *py_switcher_collection_new(PyTypeObject *, PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'DbSwitcher'.            *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_switcher_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_db_switcher_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DB_SWITCHER, type->tp_name, NULL, NULL, NULL);

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
*  Paramètres  : self = objet à initialiser (théoriquement).                  *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Initialise une instance sur la base du dérivé de GObject.    *
*                                                                             *
*  Retour      : 0 en cas de succès, -1 sinon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_db_switcher_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à renvoyer            */
    GArchInstruction *instr;                /* Instruction propriétaire    */
    GImmOperand *imm;                       /* Opérande concerné           */
    ImmOperandDisplay display;              /* Type d'affichage forcé      */
    int ret;                                /* Bilan de lecture des args.  */
    GDbSwitcher *switcher;                  /* Version GLib de la bascule  */
    bool status;                            /* Bilan de l'initialisation   */

#define DB_SWITCHER_DOC                                                         \
    "DbSwitcher allows to switch display for immediate operands.\n"             \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    DbSwitcher(instr, imm, display)\n"                                     \
    "\n"                                                                        \
    "Where *instr* is an pychrysalide.arch.ArchInstruction instance containing" \
    " the target *imm* operand, which must be an pychrysalide.arch.ImmOperand"  \
    " object. The *display* argument defines the kind of display to apply, as"  \
    " a pychrysalide.arch.operands.ImmOperand.ImmOperandDisplay value."         \
    "\n"                                                                        \
    "ImmOperandDisplay.COUNT can be used to reset the display to its default"   \
    " state."

    result = -1;

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&O&",
                           convert_to_arch_instruction, &instr,
                           convert_to_imm_operand, &imm,
                           convert_to_imm_operand_display, &display);
    if (!ret) goto exit;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) goto exit;

    /* Eléments de base */

    switcher = G_DB_SWITCHER(pygobject_get(self));

    status = g_db_switcher_fill(switcher, instr, imm, display);
    if (!status) goto exit;

    result = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'adresse associée à une bascule.                    *
*                                                                             *
*  Retour      : Adresse mémoire.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_switcher_get_address(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbSwitcher *switcher;                  /* Bascule à consulter         */
    const vmpa2t *addr;                     /* Localisation de la bascule  */

#define DB_SWITCHER_ADDRESS_ATTRIB PYTHON_GET_DEF_FULL              \
(                                                                   \
    address, py_db_switcher,                                        \
    "Location of the instruction containing the switched operand,"  \
    " as a pychrysalide.arch.vmpa instance."                        \
)

    switcher = G_DB_SWITCHER(pygobject_get(self));

    addr = g_db_switcher_get_address(switcher);

    result = build_from_internal_vmpa(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le chemin menant vers l'opérande basculé.            *
*                                                                             *
*  Retour      : Chemin de type "n[:n:n:n]".                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_switcher_get_path(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbSwitcher *switcher;                  /* Bascule à consulter         */
    const char *path;                       /* Chemin d'accès associé      */

#define DB_SWITCHER_PATH_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                   \
    path, py_db_switcher,                                           \
    "Path used to retrieved internally the operand to switch.\n"    \
    "\n"                                                            \
    "This path is a string of the form 'n[:n:n:n]', where n is"     \
    " an internal index."                                           \
)

    switcher = G_DB_SWITCHER(pygobject_get(self));

    path = g_db_switcher_get_path(switcher);

    result = PyUnicode_FromString(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique l'affichage vers lequel un opérande a basculé.       *
*                                                                             *
*  Retour      : Type d'affichage forcé pour un opérande.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_switcher_get_display(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GDbSwitcher *switcher;                  /* Bascule à consulter         */
    ImmOperandDisplay display;              /* Type d'affichage associé    */

#define DB_SWITCHER_DISPLAY_ATTRIB PYTHON_GET_DEF_FULL                  \
(                                                                       \
    display, py_db_switcher,                                            \
    "Kind of display forced for the target operand, as an"              \
    " pychrysalide.arch.operands.ImmOperand.ImmOperandDisplay value."   \
)

    switcher = G_DB_SWITCHER(pygobject_get(self));

    display = g_db_switcher_get_display(switcher);

    result = cast_with_constants_group_from_type(get_python_imm_operand_type(), "ImmOperandDisplay", display);

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

PyTypeObject *get_python_db_switcher_type(void)
{
    static PyMethodDef py_db_switcher_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_db_switcher_getseters[] = {
        DB_SWITCHER_ADDRESS_ATTRIB,
        DB_SWITCHER_PATH_ATTRIB,
        DB_SWITCHER_DISPLAY_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_db_switcher_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.items.DbSwitcher",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = DB_SWITCHER_DOC,

        .tp_methods     = py_db_switcher_methods,
        .tp_getset      = py_db_switcher_getseters,

        .tp_init        = py_db_switcher_init,
        .tp_new         = py_db_switcher_new,

    };

    return &py_db_switcher_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...db.items.DbSwitcher'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_db_switcher_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbSwitcher'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_db_switcher_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db.items");

        dict = PyModule_GetDict(module);

        if (!ensure_python_db_item_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_DB_SWITCHER, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en bascule d'affichage de collection.     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_db_switcher(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_db_switcher_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to collection switcher");
            break;

        case 1:
            *((GDbSwitcher **)dst) = G_DB_SWITCHER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA COLLECTION ASSOCIEE                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'SwitcherCollection'.    *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_switcher_collection_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

#define SWITCHER_COLLECTION_DOC                                         \
    "SwitcherCollection remembers all switch definitions for immediate" \
    " operand display.\n"                                               \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    SwitcherCollection()\n"                                        \
    "\n"                                                                \
    "There should be no need for creating such instances manually."

    /* Validations diverses */

    base = get_python_db_switcher_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DB_SWITCHER, type->tp_name, NULL, NULL, NULL);

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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_switcher_collection_type(void)
{
    static PyMethodDef py_switcher_collection_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_switcher_collection_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_switcher_collection_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.items.SwitcherCollection",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SWITCHER_COLLECTION_DOC,

        .tp_methods     = py_switcher_collection_methods,
        .tp_getset      = py_switcher_collection_getseters,

        .tp_new         = py_switcher_collection_new,

    };

    return &py_switcher_collection_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....SwitcherCollection'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_switcher_collection_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbSwitcher'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_switcher_collection_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db.items");

        dict = PyModule_GetDict(module);

        if (!ensure_python_db_collection_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_SWITCHER_COLLECTION, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en collection de bascules.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_switcher_collection(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_switcher_collection_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to switcher collection");
            break;

        case 1:
            *((GSwitcherCollection **)dst) = G_SWITCHER_COLLECTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
