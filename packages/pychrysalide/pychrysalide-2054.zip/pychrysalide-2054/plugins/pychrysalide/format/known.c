
/* Chrysalide - Outil d'analyse de fichiers binaires
 * known.c - équivalent Python du fichier "format/known.c"
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


#include "known.h"


#include <pygobject.h>


#include <i18n.h>
#include <format/known-int.h>
#include <plugins/dt.h>


#include "../access.h"
#include "../helpers.h"
#include "../analysis/content.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_known_format_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des descriptions de fichier binaire. */
static void py_known_format_init_gclass(GKnownFormatClass *, gpointer);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_known_format_init(PyObject *, PyObject *, PyObject *);

/* Indique la désignation interne du format. */
static char *py_known_format_get_key_wrapper(const GKnownFormat *);

/* Fournit une description humaine du format. */
static char *py_known_format_get_description_wrapper(const GKnownFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool py_known_format_analyze_wrapper(GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Réalise un traitement post-désassemblage. */
static void py_known_format_complete_analysis_wrapper(GKnownFormat *, wgroup_id_t, GtkStatusStack *);



/* --------------------------- DEFINITION DU FORMAT CONNU --------------------------- */


/* Assure l'interprétation d'un format en différé. */
static PyObject *py_known_format_analyze(PyObject *, PyObject *);

/* Réalise un traitement post-désassemblage. */
static PyObject *py_known_format_complete_analysis(PyObject *, PyObject *);

/* Indique la désignation interne du format. */
static PyObject *py_known_format_get_key(PyObject *, void *);

/* Indique la désignation humaine du format. */
static PyObject *py_known_format_get_description(PyObject *, void *);

/* Fournit une référence vers le contenu binaire analysé. */
static PyObject *py_known_format_get_content(PyObject *, void *);



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

static PyObject *py_known_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_known_format_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_KNOWN_FORMAT, type->tp_name,
                               (GClassInitFunc)py_known_format_init_gclass, NULL, NULL);

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

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe générique des processeurs.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_known_format_init_gclass(GKnownFormatClass *class, gpointer unused)
{
    class->get_key = py_known_format_get_key_wrapper;
    class->get_desc = py_known_format_get_description_wrapper;

    class->analyze = py_known_format_analyze_wrapper;
    class->complete = py_known_format_complete_analysis_wrapper;

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

static int py_known_format_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GBinContent *content;                   /* Contenu à intégrer au format*/
    int ret;                                /* Bilan de lecture des args.  */
    GKnownFormat *format;                   /* Format à manipuler          */

#define KNOWN_FORMAT_DOC                                                \
    "KnownFormat is a small class providing basic features for"         \
    " recognized formats.\n"                                            \
    "\n"                                                                \
    "One item has to be defined as class attribute in the final"        \
    " class:\n"                                                         \
    "* *_key*: a string providing a small name used to identify the"    \
    " format.\n"                                                        \
    "\n"                                                                \
    "The following methods have to be defined for new classes:\n"       \
    "* pychrysalide.format.KnownFormat._get_description();\n"           \
    "* pychrysalide.format.KnownFormat._analyze().\n"                   \
    "\n"                                                                \
    "The following method may also be defined for new classes too:\n"   \
    "* pychrysalide.format.KnownFormat._complete_analysis().\n"         \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " only one argument: a binary content, provided as a"               \
    " pychrysalide.analysis.BinContent instance."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    format = G_KNOWN_FORMAT(pygobject_get(self));

    g_known_format_set_content(format, content);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                                                                             *
*  Description : Indique la désignation interne du format.                    *
*                                                                             *
*  Retour      : Désignation du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_known_format_get_key_wrapper(const GKnownFormat *format)
{
    char *result;                           /* Désignation à renvoyer      */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pykey;                        /* Clef en objet Python        */
    int ret;                                /* Bilan d'une conversion      */

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(format));

    if (PyObject_HasAttrString(pyobj, "_key"))
    {
        pykey = PyObject_GetAttrString(pyobj, "_key");

        if (pykey != NULL)
        {
            ret = PyUnicode_Check(pykey);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pykey));

            Py_DECREF(pykey);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                                                                             *
*  Description : Fournit une description humaine du format.                   *
*                                                                             *
*  Retour      : Description du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_known_format_get_description_wrapper(const GKnownFormat *format)
{
    char *result;                           /* Description à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define KNOWN_FORMAT_GET_DESCRIPTION_WRAPPER PYTHON_WRAPPER_DEF     \
(                                                                   \
    _get_description, "$self, /",                                   \
    METH_NOARGS,                                                    \
    "Abstract method used to build a description of the format.\n"  \
    "\n"                                                            \
    "The result is expected to be a string."                        \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(format));

    if (has_python_method(pyobj, "_get_description"))
    {
        pyret = run_python_method(pyobj, "_get_description", NULL);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyret));

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure l'interprétation d'un format en différé.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_known_format_analyze_wrapper(GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define KNOWN_FORMAT_ANALYZE_WRAPPER PYTHON_WRAPPER_DEF             \
(                                                                   \
    _analyze, "$self, gid, status, /",                              \
    METH_VARARGS,                                                   \
    "Abstract method used to start the analysis of the known"       \
    " format and return its status.\n"                              \
    "\n"                                                            \
    "The identifier refers to the working queue used to process"    \
    " the analysis. A reference to the main status bar may also be" \
    " provided, as a pychrysalide.gtkext.StatusStack instance if"   \
    " running in graphical mode or None otherwise.\n"               \
    "\n"                                                            \
    "The expected result of the call is a boolean."                 \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(format));

    if (has_python_method(pyobj, "_analyze"))
    {
        args = PyTuple_New(2);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(gid));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_analyze", args);

        result = (pyret == Py_True);

        Py_DECREF(args);
        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Réalise un traitement post-désassemblage.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_known_format_complete_analysis_wrapper(GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define KNOWN_FORMAT_COMPLETE_ANALYSIS_WRAPPER PYTHON_VOID_WRAPPER_DEF  \
(                                                                       \
    _complete_analysis, "$self, gid, status, /",                        \
    METH_VARARGS,                                                       \
    "Abstract method used to complete an analysis of a known format.\n" \
    "\n"                                                                \
    "The identifier refers to the working queue used to process the"    \
    " analysis. A reference to the main status bar may also be"         \
    " provided, as a pychrysalide.gtkext.StatusStack instance if"       \
    " running in graphical mode or None otherwise.\n"                   \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(format));

    if (has_python_method(pyobj, "_complete_analysis"))
    {
        args = PyTuple_New(2);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(gid));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_complete_analysis", args);

        Py_DECREF(args);
        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                             DEFINITION DU FORMAT CONNU                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un format connu.                   *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Assure l'interprétation d'un format en différé.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_known_format_analyze(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    GKnownFormat *format;                   /* Format connu manipulé       */
    bool status;                            /* Bilan de l'opération        */

#define KNOWN_FORMAT_ANALYZE_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    analyze, "$self, gid, status, /",                               \
    METH_VARARGS, py_known_format,                                  \
    "Start the analysis of the known format and return its status." \
    "\n"                                                            \
    "Once this analysis is done, a few early symbols and the"       \
    " mapped sections are expected to be defined, if any.\n"        \
    "\n"                                                            \
    "The identifier refers to the working queue used to process"    \
    " the analysis. A reference to the main status bar may also be" \
    " provided, as a pychrysalide.gtkext.StatusStack instance if"   \
    " running in graphical mode or None otherwise.\n"               \
    "\n"                                                            \
    "The return value is a boolean status of the operation."        \
)

    ret = PyArg_ParseTuple(args, "");//|KO!", &gid, &status);
    if (!ret) return NULL;

    format = G_KNOWN_FORMAT(pygobject_get(self));

    status = g_known_format_analyze(format, 0, NULL);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un format connu.                   *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Réalise un traitement post-désassemblage.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_known_format_complete_analysis(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    GKnownFormat *format;                   /* Format connu manipulé       */

#define KNOWN_FORMAT_COMPLETE_ANALYSIS_METHOD PYTHON_METHOD_DEF     \
(                                                                   \
    complete_analysis, "$self, gid, status, /",                     \
    METH_VARARGS, py_known_format,                                  \
    "Complete an analysis of a known format.\n"                     \
    "\n"                                                            \
    "This process is usually done once the disassembling process"   \
    " is completed.\n"                                              \
    "\n"                                                            \
    "The identifier refers to the working queue used to process"    \
    " the analysis. A reference to the main status bar may also be" \
    " provided, as a pychrysalide.gtkext.StatusStack instance if"   \
    " running in graphical mode or None otherwise.\n"               \
    "\n"                                                            \
    "The return value is a boolean status of the operation."        \
)

    ret = PyArg_ParseTuple(args, "");//|KO!", &gid, &status);
    if (!ret) return NULL;

    format = G_KNOWN_FORMAT(pygobject_get(self));

    g_known_format_complete_analysis(format, 0, NULL);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la désignation interne du format.                    *
*                                                                             *
*  Retour      : Désignation du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_known_format_get_key(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GKnownFormat *format;                   /* Format de binaire manipulé  */
    char *key;                              /* Désignation interne         */

#define KNOWN_FORMAT_KEY_ATTRIB PYTHON_GET_DEF_FULL                     \
(                                                                       \
    key, py_known_format,                                               \
    "Internal name of the known format, provided as a (tiny) string."   \
)

    format = G_KNOWN_FORMAT(pygobject_get(self));

    key = g_known_format_get_key(format);

    result = PyUnicode_FromString(key);

    free(key);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la désignation humaine du format.                    *
*                                                                             *
*  Retour      : Description du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_known_format_get_description(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GKnownFormat *format;                   /* Format de binaire manipulé  */
    char *desc;                             /* Description humaine         */

#define KNOWN_FORMAT_DESCRIPTION_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    description, py_known_format,                               \
    "Human description of the known format, as a string."       \
)

    format = G_KNOWN_FORMAT(pygobject_get(self));

    desc = g_known_format_get_description(format);

    result = PyUnicode_FromString(desc);

    free(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit une référence vers le contenu binaire analysé.       *
*                                                                             *
*  Retour      : Gestionnaire de contenu binaire en place.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_known_format_get_content(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GKnownFormat *format;                   /* Format de binaire manipulé  */
    GBinContent *content;                   /* Instance GLib correspondante*/

#define KNOWN_FORMAT_CONTENT_ATTRIB PYTHON_GET_DEF_FULL             \
(                                                                   \
    content, py_known_format,                                       \
    "Binary content linked to the known format."                    \
    "\n"                                                            \
    "The result is a pychrysalide.analysis.BinContent instance."    \
)

    format = G_KNOWN_FORMAT(pygobject_get(self));

    content = g_known_format_get_content(format);

    if (content != NULL)
    {
        result = pygobject_new(G_OBJECT(content));
        g_object_unref(content);
    }
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

PyTypeObject *get_python_known_format_type(void)
{
    static PyMethodDef py_known_format_methods[] = {
        KNOWN_FORMAT_GET_DESCRIPTION_WRAPPER,
        KNOWN_FORMAT_ANALYZE_WRAPPER,
        KNOWN_FORMAT_COMPLETE_ANALYSIS_WRAPPER,
        KNOWN_FORMAT_ANALYZE_METHOD,
        KNOWN_FORMAT_COMPLETE_ANALYSIS_METHOD,
        { NULL }
    };

    static PyGetSetDef py_known_format_getseters[] = {
        KNOWN_FORMAT_KEY_ATTRIB,
        KNOWN_FORMAT_DESCRIPTION_ATTRIB,
        KNOWN_FORMAT_CONTENT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_known_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.KnownFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KNOWN_FORMAT_DOC,

        .tp_methods     = py_known_format_methods,
        .tp_getset      = py_known_format_getseters,

        .tp_init        = py_known_format_init,
        .tp_new         = py_known_format_new,

    };

    return &py_known_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.BinFormat'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_known_format_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinFormat'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_known_format_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_KNOWN_FORMAT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en format connu.                          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_known_format(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_known_format_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to known format");
            break;

        case 1:
            *((GKnownFormat **)dst) = G_KNOWN_FORMAT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
