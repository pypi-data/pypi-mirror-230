
/* Chrysalide - Outil d'analyse de fichiers binaires
 * executable.c - équivalent Python du fichier "format/executable.c"
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


#include "executable.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <core/processors.h>


#include "format.h"
#include "../access.h"
#include "../helpers.h"
#include "../arch/processor.h"
#include "../arch/vmpa.h"
#include "../glibext/binportion.h"



/* ------------------------ DECLARATION DE FORMAT EXECUTABLE ------------------------ */


/* Enregistre une portion artificielle pour le format. */
static PyObject *py_exe_format_register_user_portion(PyObject *, PyObject *);

/* Fournit l'emplacement correspondant à une position physique. */
static PyObject *py_exe_format_translate_offset_into_vmpa(PyObject *, PyObject *);

/* Fournit l'emplacement correspondant à une adresse virtuelle. */
static PyObject *py_exe_format_translate_address_into_vmpa(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          DECLARATION DE FORMAT EXECUTABLE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = description de l'exécutable à consulter.              *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Enregistre une portion artificielle pour le format.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_exe_format_register_user_portion(PyObject *self, PyObject *args)
{
    GBinPortion *portion;                   /* Portion binaire à conserver */
    int ret;                                /* Bilan de lecture des args.  */
    GExeFormat *format;                     /* Version GLib du format      */

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_portion, &portion);
    if (!ret) return NULL;

    format = G_EXE_FORMAT(pygobject_get(self));

    g_object_ref(G_OBJECT(portion));
    g_exe_format_register_user_portion(format, portion);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = description de l'exécutable à consulter.              *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une position physique. *
*                                                                             *
*  Retour      : Position correspondante ou None.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_exe_format_translate_offset_into_vmpa(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GExeFormat *format;                     /* Version GLib du format      */
    unsigned long long off;                 /* Adresse en mémoire virtuelle*/
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t pos;                             /* Position complète déterminée*/
    bool status;                            /* Bilan de l'opération        */

    format = G_EXE_FORMAT(pygobject_get(self));
    assert(format != NULL);

    ret = PyArg_ParseTuple(args, "K", &off);
    if (!ret) return NULL;

    status = g_exe_format_translate_offset_into_vmpa(format, off, &pos);

    if (status)
        result = build_from_internal_vmpa(&pos);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = description de l'exécutable à consulter.              *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une adresse virtuelle. *
*                                                                             *
*  Retour      : Position correspondante ou None.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_exe_format_translate_address_into_vmpa(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GExeFormat *format;                     /* Version GLib du format      */
    unsigned long long addr;                /* Adresse en mémoire virtuelle*/
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t pos;                             /* Position complète déterminée*/
    bool status;                            /* Bilan de l'opération        */

    format = G_EXE_FORMAT(pygobject_get(self));
    assert(format != NULL);

    ret = PyArg_ParseTuple(args, "K", &addr);
    if (!ret) return NULL;

    status = g_exe_format_translate_address_into_vmpa(format, addr, &pos);

    if (status)
        result = build_from_internal_vmpa(&pos);

    else
    {
        result = Py_None;
        Py_INCREF(result);
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

PyTypeObject *get_python_executable_format_type(void)
{
    static PyMethodDef py_exe_format_methods[] = {
        {
            "register_user_portion", py_exe_format_register_user_portion,
            METH_VARARGS,
            "register_user_portion($self, portion, /)\n--\n\nRemember a given user-defined binary portion as part of the executable format content."
        },
        {
            "translate_offset_into_vmpa", py_exe_format_translate_offset_into_vmpa,
            METH_VARARGS,
            "translate_offset_into_vmpa($self, off, /)\n--\n\nTranslate a physical offset to a full location."
        },
        {
            "translate_address_into_vmpa", py_exe_format_translate_address_into_vmpa,
            METH_VARARGS,
            "translate_address_into_vmpa($self, addr, /)\n--\n\nTranslate a physical offset to a full location."
        },
        { NULL }
    };

    static PyGetSetDef py_exe_format_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_exe_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.ExeFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide executable format",

        .tp_methods     = py_exe_format_methods,
        .tp_getset      = py_exe_format_getseters,

    };

    return &py_exe_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.ExeFormat'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_executable_format_is_registered(void)
{
    PyTypeObject *type;       /* Type Python 'ExeFormat'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_executable_format_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!ensure_python_binary_format_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_EXE_FORMAT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en format exécutable.                     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_executable_format(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_executable_format_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to executable format");
            break;

        case 1:
            *((GExeFormat **)dst) = G_EXE_FORMAT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              TRADUCTION D'EMPLACEMENT                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : obj  = objet Python à convertir en emplacement.              *
*                info = informations utiles à l'opération.                    *
*                                                                             *
*  Description : Réalise une conversion d'un objet Python en localisation.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_vmpa_using_executable(PyObject *obj, exe_cv_info_t *info)
{
    int result;                             /* Bilan à retourner           */
    int ret;                                /* Bilan d'une consultation    */
    const char *arch;                       /* Architecture d'exécution    */
    proc_cv_info_t conv;                    /* Informations de conversion  */

    ret = PyObject_IsInstance(obj, (PyObject *)get_python_vmpa_type());

    if (ret)
    {
        info->vmpa = get_internal_vmpa(obj);
        result = 1;
    }

    else if (info->format != NULL)
    {
        arch = g_exe_format_get_target_machine(info->format);

        conv.proc = get_arch_processor_for_key(arch);

        if (conv.proc != NULL)
        {
            result = convert_to_vmpa_using_processor(obj, &conv);

            if (result == 1)
            {
                info->vmpa = conv.vmpa;
                copy_vmpa(&info->tmp, &conv.tmp);
            }

            g_object_unref(G_OBJECT(conv.proc));

        }

        else
            result = 0;

    }

    else
        result = 0;

    if (result == 0)
        PyErr_Format(PyExc_TypeError, _("unable to convert object to VMPA location"));

    return result;

}
