
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.c - équivalent Python du fichier "plugins/pe/routine.c"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "routine.h"


#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/routine.h>


#include "constants.h"
#include "../routine.h"



/* ------------------------ SYMBOLES D'UN FORMAT PE EXPORTES ------------------------ */


#define PE_EXPORTED_ROUTINE_DOC                                     \
    "The PeExportedRoutine is a definition of a binary routine"     \
    " exported for other PE file."


/* Fournit l'indice de la routine dans un fichier PE. */
static PyObject *py_pe_exported_routine_get_ordinal(PyObject *, void *);

/* Définit l'indice de la routine dans un fichier PE. */
static int py_pe_exported_routine_set_ordinal(PyObject *, PyObject *, void *);



/* ------------------------ SYMBOLES D'UN FORMAT PE IMPORTES ------------------------ */


#define PE_IMPORTED_ROUTINE_DOC                                     \
    "The PeImportedRoutine is a definition of a binary routine"     \
    " imported from other PE file symbol."


/* Fournit la position du symbole dans les importations. */
static PyObject *py_pe_imported_routine_get_index(PyObject *, void *);

/* Fournit le fichier DLL visé par une importation de format PE. */
static PyObject *py_pe_imported_routine_get_library(PyObject *, void *);

/* Définit le fichier DLL visé par une importation de format PE. */
static int py_pe_imported_routine_set_library(PyObject *, PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          SYMBOLES D'UN FORMAT PE EXPORTES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'indice de la routine dans un fichier PE.           *
*                                                                             *
*  Retour      : Numéro de la routine.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_exported_routine_get_ordinal(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPeExportedRoutine *routine;            /* Version native              */
    uint16_t ordinal;                       /* Valeur native de l'ordinal  */

#define PE_EXPORTED_ROUTINE_ORDINAL_ATTRIB PYTHON_GETSET_DEF_FULL       \
(                                                                       \
    ordinal, py_pe_exported_routine,                                    \
    "Ordinal number linked to the symbol.\n"                            \
    "\n"                                                                \
    "The returned integer value is valid only if"                       \
    " the pychrysalide.format.pe.PeRoutine.PeSymbolFlag.HAS_ORDINAL"    \
    " bit is set in the symbol flags.\n"                                \
    "\n"                                                                \
    "This bit is automatically set when the value is defined."          \
)

    routine = G_PE_EXPORTED_ROUTINE(pygobject_get(self));

    ordinal = g_pe_exported_routine_get_ordinal(routine);

    //result = cast_with_constants_group_from_type(get_python_pe_exported_routine_type(), "OrdinalValue", ordinal);

    result = PyLong_FromUnsignedLong(ordinal);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit l'indice de la routine dans un fichier PE.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_pe_exported_routine_set_ordinal(PyObject *self, PyObject *value, void *closure)
{
    int ret;                                /* Bilan d'analyse             */
    GPeExportedRoutine *routine;            /* Version native              */
    uint16_t ordinal;                       /* Valeur native de l'ordinal  */

    ret = PyObject_IsInstance(value, (PyObject *)&PyLong_Type);
    if (!ret) return -1;

    routine = G_PE_EXPORTED_ROUTINE(pygobject_get(self));

    ordinal = PyLong_AsUnsignedLong(value);

    g_pe_exported_routine_set_ordinal(routine, ordinal);

    return 0;

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

PyTypeObject *get_python_pe_exported_routine_type(void)
{
    static PyMethodDef py_pe_exported_routine_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_pe_exported_routine_getseters[] = {
        PE_EXPORTED_ROUTINE_ORDINAL_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_pe_exported_routine_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.pe.PeExportedRoutine",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = PE_EXPORTED_ROUTINE_DOC,

        .tp_methods     = py_pe_exported_routine_methods,
        .tp_getset      = py_pe_exported_routine_getseters

    };

    return &py_pe_exported_routine_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.pe.PeRoutine'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_pe_exported_routine(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'PeRoutine'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_pe_exported_routine_type();

    dict = PyModule_GetDict(module);

    /* TODO : ensure get_python_binary_routine_type() */

    if (!register_class_for_pygobject(dict, G_TYPE_PE_EXPORTED_ROUTINE, type))
        return false;

    if (!define_python_pe_exported_routine_constants(type))
        return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en routine de fichier PE.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_pe_exported_routine(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_pe_exported_routine_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PE exported routine");
            break;

        case 1:
            *((GPeExportedRoutine **)dst) = G_PE_EXPORTED_ROUTINE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          SYMBOLES D'UN FORMAT PE IMPORTES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la position du symbole dans les importations.        *
*                                                                             *
*  Retour      : Indice positif ou nul.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_imported_routine_get_index(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPeImportedRoutine *routine;            /* Version native              */
    size_t index;                           /* Position dans les imports   */

#define PE_IMPORTED_ROUTINE_INDEX_ATTRIB PYTHON_GET_DEF_FULL        \
(                                                                   \
    index, py_pe_imported_routine,                                  \
    "Position of the symbol inside the importations table.\n"       \
    "\n"                                                            \
    "The returned value is an integer."                             \
)

    routine = G_PE_IMPORTED_ROUTINE(pygobject_get(self));

    index = g_pe_imported_routine_get_index(routine);

    result = PyLong_FromSize_t(index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le fichier DLL visé par une importation de format PE.*
*                                                                             *
*  Retour      : Désignation d'une bibliothèque Windows.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_imported_routine_get_library(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPeImportedRoutine *routine;            /* Version native              */
    const char *library;                    /* Nom de bibliothèque         */

#define PE_IMPORTED_ROUTINE_LIBRARY_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                                   \
    library, py_pe_imported_routine,                                \
    "Imported DLL's name for the symbol.\n"                         \
    "\n"                                                            \
    "The returned value is a string."                               \
)

    routine = G_PE_IMPORTED_ROUTINE(pygobject_get(self));

    library = g_pe_imported_routine_get_library(routine);

    result = PyUnicode_FromString(library);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit le fichier DLL visé par une importation de format PE.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_pe_imported_routine_set_library(PyObject *self, PyObject *value, void *closure)
{
    GPeImportedRoutine *routine;            /* Version native              */

    if (!PyUnicode_Check(value) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a string or None."));
        return -1;
    }

    routine = G_PE_IMPORTED_ROUTINE(pygobject_get(self));

    if (value == Py_None)
        g_pe_imported_routine_set_library(routine, NULL);
    else
        g_pe_imported_routine_set_library(routine, strdup(PyUnicode_DATA(value)));

    return 0;

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

PyTypeObject *get_python_pe_imported_routine_type(void)
{
    static PyMethodDef py_pe_imported_routine_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_pe_imported_routine_getseters[] = {
        PE_IMPORTED_ROUTINE_INDEX_ATTRIB,
        PE_IMPORTED_ROUTINE_LIBRARY_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_pe_imported_routine_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.pe.PeImportedRoutine",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = PE_IMPORTED_ROUTINE_DOC,

        .tp_methods     = py_pe_imported_routine_methods,
        .tp_getset      = py_pe_imported_routine_getseters

    };

    return &py_pe_imported_routine_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.pe.PeRoutine'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_pe_imported_routine(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'PeRoutine'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_pe_imported_routine_type();

    dict = PyModule_GetDict(module);

    /* TODO : ensure get_python_pe_exported_routine_type() */

    if (!register_class_for_pygobject(dict, G_TYPE_PE_IMPORTED_ROUTINE, type))
        return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en routine de fichier PE.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_pe_imported_routine(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_pe_imported_routine_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PE imported routine");
            break;

        case 1:
            *((GPeImportedRoutine **)dst) = G_PE_IMPORTED_ROUTINE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
