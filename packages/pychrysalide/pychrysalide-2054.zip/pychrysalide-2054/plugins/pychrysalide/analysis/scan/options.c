
/* Chrysalide - Outil d'analyse de fichiers binaires
 * options.c - équivalent Python du fichier "analysis/scan/options.c"
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


#include "options.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/scan/options-int.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>



CREATE_DYN_CONSTRUCTOR(scan_options, G_TYPE_SCAN_OPTIONS);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_scan_options_init(PyObject *, PyObject *, PyObject *);

/* Indique le type d'un moteur d'analyse de données sélectionné. */
static PyObject *py_scan_options_get_backend_for_data(PyObject *, void *);

/* Sélectionne un type de moteur d'analyse pour données brutes. */
static int py_scan_options_set_backend_for_data(PyObject *, PyObject *, void *);

/* Impose le format JSON comme type de sortie. */
static PyObject *py_scan_options_get_print_json(PyObject *, void *);

/* Mémorise le format JSON comme type de sortie. */
static int py_scan_options_set_print_json(PyObject *, PyObject *, void *);

/* Indique un besoin d'affichage des correspondances finales. */
static PyObject *py_scan_options_get_print_strings(PyObject *, void *);

/* Mémorise un besoin d'affichage des correspondances finales. */
static int py_scan_options_set_print_strings(PyObject *, PyObject *, void *);

/* Indique un besoin de statistiques en fin de compilation. */
static PyObject *py_scan_options_get_print_stats(PyObject *, void *);

/* Mémorise un besoin de statistiques en fin de compilation. */
static int py_scan_options_set_print_stats(PyObject *, PyObject *, void *);



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

static int py_scan_options_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define SCAN_OPTIONS_DOC                                            \
    "The *ScanOptions* class stores all parameters used to tune"    \
    " a scanning process.\n"                                        \
    "\n"                                                            \
    "Instances can be created using the following constructor:\n"   \
    "\n"                                                            \
    "    ScanOptions()"

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format Axml.                *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique le type d'un moteur d'analyse de données sélectionné.*
*                                                                             *
*  Retour      : Type d'objet, idéalement valide.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_options_get_backend_for_data(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GScanOptions *options;                  /* Version native              */
    GType type;                             /* Type à transcrire           */

#define SCAN_OPTIONS_BACKEND_FOR_DATA_ATTRIB PYTHON_GETSET_DEF_FULL \
(                                                                   \
    backend_for_data, py_scan_options,                              \
    "Type of the selected scan algorithm."                          \
)

    options = G_SCAN_OPTIONS(pygobject_get(self));

    type = g_scan_options_get_backend_for_data(options);

    result = pyg_type_wrapper_new(type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Sélectionne un type de moteur d'analyse pour données brutes. *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_scan_options_set_backend_for_data(PyObject *self, PyObject *value, void *closure)
{
    GType type;                             /* Type à transcrit            */
    GScanOptions *options;                  /* Version native              */

    type = pyg_type_from_object(value);

    options = G_SCAN_OPTIONS(pygobject_get(self));

    g_scan_options_set_backend_for_data(options, type);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format Axml.                *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Impose le format JSON comme type de sortie.                  *
*                                                                             *
*  Retour      : Etat de l'option visée à conservé.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_options_get_print_json(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GScanOptions *options;                  /* Version native              */
    bool state;                             /* Etat courant à consulter    */

#define SCAN_OPTIONS_PRINT_JSON_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                               \
    print_json, py_scan_options,                                \
    "Define if the process summary is output into a JSON"       \
    " format at the end of the scan or not."                    \
)

    options = G_SCAN_OPTIONS(pygobject_get(self));

    state = g_scan_options_get_print_json(options);

    result = state ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Mémorise le format JSON comme type de sortie.                *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_scan_options_set_print_json(PyObject *self, PyObject *value, void *closure)
{
    bool state;                             /* Nouvel état à définir       */
    GScanOptions *options;                  /* Version native              */

    if (value != Py_True && value != Py_False)
        return -1;

    state = (value == Py_True);

    options = G_SCAN_OPTIONS(pygobject_get(self));

    g_scan_options_set_print_json(options, state);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format Axml.                *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique un besoin d'affichage des correspondances finales.   *
*                                                                             *
*  Retour      : Etat de l'option visée à conservé.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_options_get_print_strings(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GScanOptions *options;                  /* Version native              */
    bool state;                             /* Etat courant à consulter    */

#define SCAN_OPTIONS_PRINT_STRINGS_ATTRIB PYTHON_GETSET_DEF_FULL    \
(                                                                   \
    print_strings, py_scan_options,                                 \
    "Define if the matching patterns are printed with found"        \
    " offset at the end of the scan or not."                        \
)

    options = G_SCAN_OPTIONS(pygobject_get(self));

    state = g_scan_options_get_print_strings(options);

    result = state ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Mémorise un besoin d'affichage des correspondances finales.  *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_scan_options_set_print_strings(PyObject *self, PyObject *value, void *closure)
{
    bool state;                             /* Nouvel état à définir       */
    GScanOptions *options;                  /* Version native              */

    if (value != Py_True && value != Py_False)
        return -1;

    state = (value == Py_True);

    options = G_SCAN_OPTIONS(pygobject_get(self));

    g_scan_options_set_print_strings(options, state);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format Axml.                *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique un besoin de statistiques en fin de compilation.     *
*                                                                             *
*  Retour      : Etat de l'option visée à conservé.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_options_get_print_stats(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GScanOptions *options;                  /* Version native              */
    bool state;                             /* Etat courant à consulter    */

#define SCAN_OPTIONS_PRINT_STATS_ATTRIB PYTHON_GETSET_DEF_FULL  \
(                                                               \
    print_stats, py_scan_options,                               \
    "Control the output of final statistics afer a scan."       \
)

    options = G_SCAN_OPTIONS(pygobject_get(self));

    state = g_scan_options_get_print_stats(options);

    result = state ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Mémorise un besoin de statistiques en fin de compilation.    *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_scan_options_set_print_stats(PyObject *self, PyObject *value, void *closure)
{
    bool state;                             /* Nouvel état à définir       */
    GScanOptions *options;                  /* Version native              */

    if (value != Py_True && value != Py_False)
        return -1;

    state = (value == Py_True);

    options = G_SCAN_OPTIONS(pygobject_get(self));

    g_scan_options_set_print_stats(options, state);

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

PyTypeObject *get_python_scan_options_type(void)
{
    static PyMethodDef py_scan_options_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_scan_options_getseters[] = {
        SCAN_OPTIONS_BACKEND_FOR_DATA_ATTRIB,
        SCAN_OPTIONS_PRINT_JSON_ATTRIB,
        SCAN_OPTIONS_PRINT_STRINGS_ATTRIB,
        SCAN_OPTIONS_PRINT_STATS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_scan_options_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.ScanOptions",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = SCAN_OPTIONS_DOC,

        .tp_methods     = py_scan_options_methods,
        .tp_getset      = py_scan_options_getseters,

        .tp_init        = py_scan_options_init,
        .tp_new         = py_scan_options_new,

    };

    return &py_scan_options_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...scan.ScanOptions'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_scan_options_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ScanOptions' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_scan_options_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_SCAN_OPTIONS, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en ensemble d'options d'analyses.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_scan_options(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_scan_options_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to scan options");
            break;

        case 1:
            *((GScanOptions **)dst) = G_SCAN_OPTIONS(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
