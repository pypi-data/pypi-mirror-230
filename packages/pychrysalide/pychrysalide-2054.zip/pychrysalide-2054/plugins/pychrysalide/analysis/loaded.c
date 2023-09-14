
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loaded.c - prototypes pour l'équivalent Python du fichier "analysis/loaded.c"
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


#include "loaded.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>


#include <analysis/loaded-int.h>
#include <core/global.h>
#include <plugins/dt.h>


#include "content.h"
#include "../access.h"
#include "../helpers.h"
#include "../glibext/named.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_loaded_content_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe générique des contenus chargés. */
static void py_loaded_content_init_gclass(GLoadedContentClass *, gpointer);

/* Fournit le contenu représenté de l'élément chargé. */
static GBinContent *py_loaded_content_get_content_wrapper(const GLoadedContent *);

/* Décrit la nature du contenu reconnu pour l'élément chargé. */
static char *py_loaded_content_get_content_class_wrapper(const GLoadedContent *, bool);

/* Lance l'analyse propre à l'élément chargé. */
static bool py_loaded_content_analyze_wrapper(GLoadedContent *, bool, bool, wgroup_id_t, GtkStatusStack *);

/* Fournit le désignation associée à l'élément chargé. */
static char *py_loaded_content_describe_wrapper(const GLoadedContent *, bool);

#ifdef INCLUDE_GTK_SUPPORT

/* Détermine le nombre de vues disponibles pour un contenu. */
static unsigned int py_loaded_content_count_views_wrapper(const GLoadedContent *);

/* Fournit le nom d'une vue donnée d'un contenu chargé. */
static char *py_loaded_content_get_view_name_wrapper(const GLoadedContent *, unsigned int);

/* Met en place la vue initiale pour un contenu chargé. */
static GtkWidget *py_loaded_content_build_default_view_wrapper(GLoadedContent *);

/* Met en place la vue demandée pour un contenu chargé. */
static GtkWidget *py_loaded_content_build_view_wrapper(GLoadedContent *, unsigned int);

/* Retrouve l'indice correspondant à la vue donnée d'un contenu. */
static unsigned int py_loaded_content_get_view_index_wrapper(GLoadedContent *, GtkWidget *);

#endif



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Lance l'analyse propre à l'élément chargé. */
static PyObject *py_loaded_content_analyze(PyObject *, PyObject *, PyObject *);

/* Lance l'analyse de l'élément chargé et attend sa conclusion. */
static PyObject *py_loaded_content_analyze_and_wait(PyObject *, PyObject *, PyObject *);

/* Fournit le désignation associée à l'élément chargé. */
static PyObject *py_loaded_content_describe(PyObject *, PyObject *);

/* Etablit une liste d'obscurcissements présents. */
static PyObject *py_loaded_content_detect_obfuscators(PyObject *, PyObject *);

#ifdef INCLUDE_GTK_SUPPORT

/* Détermine le nombre de vues disponibles pour un contenu. */
static PyObject *py_loaded_content_count_views(PyObject *, PyObject *);

/* Fournit le nom d'une vue donnée d'un contenu chargé. */
static PyObject *py_loaded_content_get_view_name(PyObject *, PyObject *);

/* Met en place la vue initiale pour un contenu chargé. */
static PyObject *py_loaded_content_build_default_view(PyObject *, PyObject *);

/* Met en place la vue initiale pour un contenu chargé. */
static PyObject *py_loaded_content_build_view(PyObject *, PyObject *);

#endif

/* Fournit le contenu représenté de l'élément chargé. */
static PyObject *py_loaded_content_get_content(PyObject *, void *);

/* Décrit la nature du contenu reconnu pour l'élément chargé. */
static PyObject *py_loaded_content_get_content_class(PyObject *, void *);

/* Décrit la nature du contenu reconnu pour l'élément chargé. */
static PyObject *py_loaded_content_get_content_class_for_human(PyObject *, void *);



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

static PyObject *py_loaded_content_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

#define LOADED_CONTENT_DOC                                                  \
    "The LoadedContent object is an intermediary level of abstraction"      \
    " for all loaded binary contents to analyze."                           \
    "\n"                                                                    \
    "No matter if the loaded content comes from an ELF file or XML data,"   \
    " some basic features are available here."                              \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, LoadedContent):\n"                 \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.analysis.storage.LoadedContent._get_content();\n"       \
    "* pychrysalide.analysis.storage.LoadedContent._get_content_class();\n" \
    "* pychrysalide.analysis.storage.LoadedContent._analyze();\n"           \
    "* pychrysalide.analysis.storage.LoadedContent._describe();\n"          \
    "* pychrysalide.analysis.storage.LoadedContent._count_views();\n"       \
    "* pychrysalide.analysis.storage.LoadedContent._get_view_name();\n"     \
    "* pychrysalide.analysis.storage.LoadedContent._build_default_view();\n"\
    "* pychrysalide.analysis.storage.LoadedContent._build_view();\n"        \
    "* pychrysalide.analysis.storage.LoadedContent._get_view_index();\n"

    /* Validations diverses */

    base = get_python_loaded_content_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_LOADED_CONTENT, type->tp_name,
                               (GClassInitFunc)py_loaded_content_init_gclass, NULL, NULL);

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
*  Description : Initialise la classe générique des contenus chargés.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_loaded_content_init_gclass(GLoadedContentClass *class, gpointer unused)
{
    class->get_content = py_loaded_content_get_content_wrapper;
    class->get_content_class = py_loaded_content_get_content_class_wrapper;

    class->analyze = py_loaded_content_analyze_wrapper;

    class->describe = py_loaded_content_describe_wrapper;

#ifdef INCLUDE_GTK_SUPPORT
    class->count_views = py_loaded_content_count_views_wrapper;
    class->get_view_name = py_loaded_content_get_view_name_wrapper;
    class->build_def_view = py_loaded_content_build_default_view_wrapper;
    class->build_view = py_loaded_content_build_view_wrapper;
    class->get_view_index = py_loaded_content_get_view_index_wrapper;
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à manipuler.                        *
*                                                                             *
*  Description : Fournit le contenu représenté de l'élément chargé.           *
*                                                                             *
*  Retour      : Contenu représenté.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinContent *py_loaded_content_get_content_wrapper(const GLoadedContent *content)
{
    GBinContent *result;                    /* Contenu interne à renvoyer  */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define LOADED_CONTENT_GET_CONTENT_WRAPPER PYTHON_WRAPPER_DEF       \
(                                                                   \
    _get_content, "$self",                                          \
    METH_VARARGS,                                                   \
    "Abstract method used to get the binary content linked to the"  \
    " loaded content. The result is provided as a"                  \
    " pychrysalide.analysis.BinContent instance."                   \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_get_content"))
    {
        pyret = run_python_method(pyobj, "_get_content", NULL);

        if (pyret != NULL)
        {
            if (convert_to_binary_content(pyret, &result) != 1)
                PyErr_Clear();

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à manipuler.                        *
*                human   = description humaine attendue ?                     *
*                                                                             *
*  Description : Décrit la nature du contenu reconnu pour l'élément chargé.   *
*                                                                             *
*  Retour      : Classe de contenu associée à l'élément chargé.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_loaded_content_get_content_class_wrapper(const GLoadedContent *content, bool human)
{
    char *result;                           /* Contenu interne à renvoyer  */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *hobj;                         /* Argument pour Python        */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_GET_CONTENT_CLASS_WRAPPER PYTHON_WRAPPER_DEF         \
(                                                                           \
    _get_content_class, "$self, human",                                     \
    METH_VARARGS,                                                           \
    "Abstract method used to provide the nature of the loaded content.\n"   \
    "\n"                                                                    \
    "The description associated to a loaded ARM Elf binary is for instance" \
    " 'elf-armv7', or 'Elf, ARMv7' for the human version."                  \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_get_content_class"))
    {
        args = PyTuple_New(1);

        hobj = (human ? Py_True : Py_False);
        Py_INCREF(hobj);

        PyTuple_SetItem(args, 0, hobj);

        pyret = run_python_method(pyobj, "_get_content_class", args);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyret));

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
*  Paramètres  : content = élément chargé à manipuler.                        *
*                connect = organise le lancement des connexions aux serveurs. *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                gid     = groupe de travail dédié.                           *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Lance l'analyse propre à l'élément chargé.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_loaded_content_analyze_wrapper(GLoadedContent *content, bool connect, bool cache, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *connect_obj;                  /* Ordre de connexion          */
    PyObject *cache_obj;                    /* Usage du cache              */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define LOADED_CONTENT_ANALYZE_WRAPPER PYTHON_WRAPPER_DEF                   \
(                                                                           \
    _analyze, "$self, connect, cache, gid, status",                         \
    METH_VARARGS,                                                           \
    "Abstract method used to start the analysis of the loaded binary."      \
    "\n"                                                                    \
    "The *connect* parameter defines if connections to database servers"    \
    " (internal and/or remote) will be established. The default value"      \
    " depends on the running mode: if the analysis is run from the GUI,"    \
    " the binary will get connected to servers; in batch mode, no"          \
    " connection will be made."                                             \
    "\n"                                                                    \
    "The *cache* parameter rules the build of the cache for rendering"      \
    " lines. The same behavior relative to the running mode applies."       \
    "\n"                                                                    \
    "The identifier refers to the working queue used to process the"        \
    " analysis. A reference to the main status bar may also be provided,"   \
    " as a pychrysalide.gtkext.StatusStack instance if running in"          \
    " graphical mode or None otherwise."                                    \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_analyze"))
    {
        connect_obj = connect ? Py_True : Py_False;
        Py_INCREF(connect_obj);

        cache_obj = cache ? Py_True : Py_False;
        Py_INCREF(cache_obj);

        args = PyTuple_New(4);
        PyTuple_SetItem(args, 0, connect_obj);
        PyTuple_SetItem(args, 1, cache_obj);
        PyTuple_SetItem(args, 2, PyLong_FromUnsignedLong(gid));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_analyze", args);

        if (pyret != NULL)
        {
            result = (pyret == Py_True);
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
*  Paramètres  : content = élément chargé à consulter.                        *
*                full    = précise s'il s'agit d'une version longue ou non.   *
*                                                                             *
*  Description : Fournit le désignation associée à l'élément chargé.          *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_loaded_content_describe_wrapper(const GLoadedContent *content, bool full)
{
    char *result;                           /* Description à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *full_obj;                     /* Précision sur la longueur   */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_DESCRIBE_WRAPPER PYTHON_WRAPPER_DEF                      \
(                                                                               \
    _describe, "$self, full",                                                   \
    METH_VARARGS,                                                               \
    "Abstract method used to describe the loaded content.\n"                    \
    "\n"                                                                        \
    "The boolean *full* parameter shapes the size of the returned string.\n"    \
    "\n"                                                                        \
    "This method is mainly used to provide a label (or a tooltip text)"         \
    " for tabs in the graphical main window."                                   \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_describe"))
    {
        full_obj = full ? Py_True : Py_False;
        Py_INCREF(full_obj);

        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, full_obj);

        pyret = run_python_method(pyobj, "_describe", args);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyret));

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                                                                             *
*  Description : Détermine le nombre de vues disponibles pour un contenu.     *
*                                                                             *
*  Retour      : Quantité strictement positive.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static unsigned int py_loaded_content_count_views_wrapper(const GLoadedContent *content)
{
    unsigned int result;                    /* Quantité de vues à renvoyer */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_COUNT_VIEWS_WRAPPER PYTHON_WRAPPER_DEF   \
(                                                               \
    _count_views, "$self",                                      \
    METH_VARARGS,                                               \
    "Abstract method used to compute the quantity of available" \
    " views for the loaded binary."                             \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_count_views"))
    {
        pyret = run_python_method(pyobj, "_count_views", NULL);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
                result = PyLong_AsUnsignedLong(pyret);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = indice de la vue ciblée.                           *
*                                                                             *
*  Description : Fournit le nom d'une vue donnée d'un contenu chargé.         *
*                                                                             *
*  Retour      : Désignation humainement lisible.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_loaded_content_get_view_name_wrapper(const GLoadedContent *content, unsigned int index)
{
    char *result;                           /* Désignation à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_GET_VIEW_NAME_WRAPPER PYTHON_WRAPPER_DEF     \
(                                                                   \
    _get_view_name, "$self, index",                                 \
    METH_VARARGS,                                                   \
    "Abstract method used to provide the human readable name for"   \
    " a given view of a loaded binary.\n"                           \
    "\n"                                                            \
    "Such a method is used in the graphical main window for"        \
    " building menu labels."                                        \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_get_view_name"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(index));

        pyret = run_python_method(pyobj, "_get_view_name", args);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyret));

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
*  Paramètres  : content = contenu chargé à consulter.                        *
*                                                                             *
*  Description : Met en place la vue initiale pour un contenu chargé.         *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *py_loaded_content_build_default_view_wrapper(GLoadedContent *content)
{
    GtkWidget *result;                      /* Support à retourner         */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_BUILD_DEFAULT_VIEW_WRAPPER PYTHON_WRAPPER_DEF        \
(                                                                           \
    _build_default_view, "$self",                                           \
    METH_VARARGS,                                                           \
    "Abstract method used to build a new widget for the default graphical"  \
    " view of the loaded content."                                          \
    "\n"                                                                    \
    "This method is aimed to only be called from the GUI internals."        \
    " It provides the first view displayed in the main Chrysalide window"   \
    " after a binary loading."                                              \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_build_default_view"))
    {
        pyret = run_python_method(pyobj, "_build_default_view", NULL);

        if (pyret != NULL)
        {
            ret = convert_to_gtk_widget(pyret, &result);

            if (ret == 1)
                g_object_ref(G_OBJECT(result));

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = indice de la vue ciblée.                           *
*                                                                             *
*  Description : Met en place la vue demandée pour un contenu chargé.         *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *py_loaded_content_build_view_wrapper(GLoadedContent *content, unsigned int index)
{
    GtkWidget *result;                      /* Support à retourner         */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_BUILD_VIEW_WRAPPER PYTHON_WRAPPER_DEF                \
(                                                                           \
    _build_view, "$self, index",                                            \
    METH_VARARGS,                                                           \
    "Abstract method used to build a new widget for a given graphical view" \
    " of the loaded content.\n"                                             \
    "\n"                                                                    \
    "This method is aimed to only be called from the GUI internals."        \
    " It provides a view displayed in the main Chrysalide window"           \
    " once the binary is loaded."                                           \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_build_view"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(index));

        pyret = run_python_method(pyobj, "_build_view", args);

        if (pyret != NULL)
        {
            ret = convert_to_gtk_widget(pyret, &result);

            if (ret == 1)
                g_object_ref(G_OBJECT(result));

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
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = composant graphique en place.                      *
*                                                                             *
*  Description : Retrouve l'indice correspondant à la vue donnée d'un contenu.*
*                                                                             *
*  Retour      : Indice de la vue représentée, ou -1 en cas d'erreur.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static unsigned int py_loaded_content_get_view_index_wrapper(GLoadedContent *content, GtkWidget *view)
{
    unsigned int result;                    /* Indice à retourner          */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define LOADED_CONTENT_GET_VIEW_INDEX_WRAPPER PYTHON_WRAPPER_DEF            \
(                                                                           \
    _get_view_index, "$self, view",                                         \
    METH_VARARGS,                                                           \
    "Abstract method used to define the index of a given view for the"      \
    " loaded binary.\n"                                                     \
    "\n"                                                                    \
    "The view is provided as a GTK *widget*.\n"                             \
    "\n"                                                                    \
    "The result is the index of the type of view, or -1 in case of error."  \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_get_view_index"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(view)));

        pyret = run_python_method(pyobj, "_get_view_index", args);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
                result = PyLong_AsUnsignedLong(pyret);

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


#endif



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Lance l'analyse propre à l'élément chargé.                   *
*                                                                             *
*  Retour      : Rien (None).                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_analyze(PyObject *self, PyObject *args, PyObject *kwds)
{
    int connect;                            /* Connexion à la base ?       */
    int cache;                              /* Préparation de rendu ?      */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */

    static char *kwlist[] = { "connect", "cache", NULL };

#define LOADED_CONTENT_ANALYZE_METHOD PYTHON_METHOD_DEF                     \
(                                                                           \
    analyze, "$self, /, connect='?', cache='?'",                            \
    METH_VARARGS | METH_KEYWORDS, py_loaded_content,                        \
    "Start the analysis of the loaded binary and send an *analyzed* signal" \
    " when done."                                                           \
    "\n"                                                                    \
    "The *connect* parameter defines if connections to database servers"    \
    " (internal and/or remote) will be established. The default value"      \
    " depends on the running mode: if the analysis is run from the GUI,"    \
    " the binary will get connected to servers; in batch mode, no"          \
    " connection will be made."                                             \
    "\n"                                                                    \
    "The *cache* parameter rules the build of the cache for rendering"      \
    " lines. The same behavior relative to the running mode applies."       \
    "\n"                                                                    \
    "All theses operations can be forced by providing True values as"       \
    " parameters."                                                          \
)

    connect = is_batch_mode() ? 0 : 1;
    cache = is_batch_mode() ? 0 : 1;

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "|pp", kwlist, &connect, &cache);
    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    g_loaded_content_analyze(content, connect, cache);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Lance l'analyse de l'élément chargé et attend sa conclusion. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_analyze_and_wait(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Bilan à retourner           */
    int connect;                            /* Connexion à la base ?       */
    int cache;                              /* Préparation de rendu ?      */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    bool status;                            /* Bilan de l'opération        */

    static char *kwlist[] = { "connect", "cache", NULL };

#define LOADED_CONTENT_ANALYZE_AND_WAIT_METHOD PYTHON_METHOD_DEF            \
(                                                                           \
    analyze_and_wait, "$self, /, connect='?', cache='?'",                   \
    METH_VARARGS | METH_KEYWORDS, py_loaded_content,                        \
    "Run the analysis of the loaded binary and wait for its completion."    \
    "\n"                                                                    \
    "The final analysis status is returned as boolean."                     \
    "\n"                                                                    \
    "The *connect* parameter defines if connections to database servers"    \
    " (internal and/or remote) will be established. The default value"      \
    " depends on the running mode: if the analysis is run from the GUI,"    \
    " the binary will get connected to servers; in batch mode, no"          \
    " connection will be made."                                             \
    "\n"                                                                    \
    "The *cache* parameter rules the build of the cache for rendering"      \
    " lines. The same behavior relative to the running mode applies."       \
    "\n"                                                                    \
    "All theses operations can be forced by providing True values as"       \
    " parameters."                                                          \
)

    connect = is_batch_mode() ? 0 : 1;
    cache = is_batch_mode() ? 0 : 1;

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "|pp", kwlist, &connect, &cache);
    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    status = g_loaded_content_analyze_and_wait(content, connect, cache);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Fournit le désignation associée à l'élément chargé.          *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_describe(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    int full;                               /* Précision quant aux attentes*/
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    const char *desc;                       /* Description associée        */

#define LOADED_CONTENT_DESCRIBE_METHOD PYTHON_METHOD_DEF                        \
(                                                                               \
    describe, "$self, full",                                                    \
    METH_VARARGS, py_loaded_content,                                            \
    "Describe the loaded content.\n"                                            \
    "\n"                                                                        \
    "The boolean *full* parameter shapes the size of the returned string.\n"    \
    "\n"                                                                        \
    "This method is mainly used to provide a label (or a tooltip text)"         \
    " for tabs in the graphical main window."                                   \
)

    ret = PyArg_ParseTuple(args, "p", &full);
    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    desc = g_loaded_content_describe(content, full);

    result = PyUnicode_FromString(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Etablit une liste d'obscurcissements présents.               *
*                                                                             *
*  Retour      : Désignations humaines correspondantes.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_detect_obfuscators(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    int version;                            /* Avec la version si possible */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    size_t count;                           /* Nombre de détections        */
    char **detections;                      /* Liste d'obscurcissements    */
    size_t i;                               /* Boucle de parcours          */

#define LOADED_CONTENT_DETECT_OBFUSCATORS_METHOD PYTHON_METHOD_DEF          \
(                                                                           \
    detect_obfuscators, "$self, version",                                   \
    METH_VARARGS, py_loaded_content,                                        \
    "List all detected obfuscators.\n"                                      \
    "\n"                                                                    \
    "If the *version* parameter is equal to True, the operation tries to"   \
    " resolve obfuscators versions too.\n"                                  \
    "\n"                                                                    \
    "The result is a tuple of strings or an empty tuple."                   \
)

    ret = PyArg_ParseTuple(args, "p", &version);
    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    detections = g_loaded_content_detect_obfuscators(content, version, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, PyUnicode_FromString(detections[i]));
        free(detections[i]);
    }

    if (detections != NULL)
        free(detections);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu chargé à manipuler.                           *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Détermine le nombre de vues disponibles pour un contenu.     *
*                                                                             *
*  Retour      : Quantité strictement positive.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_count_views(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    size_t count;                           /* Quantité à retourner        */

#define LOADED_CONTENT_COUNT_VIEWS_METHOD PYTHON_METHOD_DEF             \
(                                                                       \
    count_views, "$self",                                               \
    METH_NOARGS, py_loaded_content,                                     \
    "Compute the quantity of available views for the loaded binary."    \
)

    content = G_LOADED_CONTENT(pygobject_get(self));

    count = g_loaded_content_count_views(content);

    result = PyLong_FromUnsignedLongLong(count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu chargé à manipuler.                           *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Fournit le nom d'une vue donnée d'un contenu chargé.         *
*                                                                             *
*  Retour      : Désignation humainement lisible.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_get_view_name(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    unsigned int index;                     /* Indice de la vue ciblée     */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    const char *name;                       /* Dénomination récupérée      */

#define LOADED_CONTENT_GET_VIEW_NAME_METHOD PYTHON_METHOD_DEF                   \
(                                                                               \
    get_view_name, "$self, index",                                              \
    METH_VARARGS, py_loaded_content,                                            \
    "Provide the human readable name for a given view of a loaded binary.\n"    \
    "\n"                                                                        \
    "Such a method is used in the graphical main window for building menu"      \
    " labels."                                                                  \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    name = g_loaded_content_get_view_name(content, index);

    result = PyUnicode_FromString(name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu chargé à manipuler.                           *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Met en place la vue initiale pour un contenu chargé.         *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_build_default_view(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    GtkWidget *view;                        /* Composant GTK à transposer  */

#define LOADED_CONTENT_BUILD_DEFAULT_VIEW_METHOD PYTHON_METHOD_DEF          \
(                                                                           \
    build_default_view, "$self",                                            \
    METH_NOARGS, py_loaded_content,                                         \
    "Build a new widget for the default graphical view of the loaded"       \
    " content.\n"                                                           \
    "\n"                                                                    \
    "This method is aimed to only be called from the GUI internals."        \
    " It provides the first view displayed in the main Chrysalide window"   \
    " after a binary loading."                                              \
)

    content = G_LOADED_CONTENT(pygobject_get(self));

    view = g_loaded_content_build_default_view(content);

    result = new_pygobject_widget(view);

    g_object_unref(G_OBJECT(view));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu chargé à manipuler.                           *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Met en place la vue initiale pour un contenu chargé.         *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_build_view(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    unsigned int index;                     /* Indice de la vue ciblée     */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    GtkWidget *view;                        /* Composant GTK à transposer  */

#define LOADED_CONTENT_BUILD_VIEW_METHOD PYTHON_METHOD_DEF              \
(                                                                       \
    build_view, "$self, index",                                         \
    METH_VARARGS, py_loaded_content,                                    \
    "Build a new widget for a given graphical view of the loaded"       \
    " content.\n"                                                       \
    "\n"                                                                \
    "This method is aimed to only be called from the GUI internals."    \
    " It provides a view displayed in the main Chrysalide window"       \
    " once the binary is loaded."                                       \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    view = g_loaded_content_build_default_view(content);

    result = new_pygobject_widget(view);

    g_object_unref(G_OBJECT(view));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu chargé à manipuler.                           *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Retrouve l'indice correspondant à la vue donnée d'un contenu.*
*                                                                             *
*  Retour      : Indice de la vue représentée, ou -1 en cas d'erreur.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_get_view_index(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    PyObject *gtk_mod;                      /* Module Python Gtk           */
    PyObject *type;                         /* Module "GtkWidget"          */
    PyObject *widget_obj;                   /* Composant GTK en Python     */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    GtkWidget *widget;                      /* Composant GTK à retrouver   */
    unsigned int index;                     /* Indice de la vue fournie    */

#define LOADED_CONTENT_GET_VIEW_INDEX_METHOD PYTHON_METHOD_DEF              \
(                                                                           \
    get_view_index, "$self, widget",                                        \
    METH_VARARGS, py_loaded_content,                                        \
    "Define the index of a given view for the loaded binary.\n"             \
    "\n"                                                                    \
    "The view is provided as a GTK *widget*.\n"                             \
    "\n"                                                                    \
    "The result is the index of the type of view, or -1 in case of error."  \
)

    gtk_mod = PyImport_ImportModule("gi.repository.Gtk");

    if (gtk_mod == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "unable to find the Gtk Python module");
        return NULL;
    }

    type = PyObject_GetAttrString(gtk_mod, "Widget");

    Py_DECREF(gtk_mod);

    ret = PyArg_ParseTuple(args, "O!", type, &widget_obj);

    Py_DECREF(type);

    if (!ret) return NULL;

    content = G_LOADED_CONTENT(pygobject_get(self));

    widget = GTK_WIDGET(pygobject_get(widget_obj));

    index = g_loaded_content_get_view_index(content, widget);

    result = PyLong_FromUnsignedLong(index);

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le contenu représenté de l'élément chargé.           *
*                                                                             *
*  Retour      : Contenu représenté.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_get_content(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    GBinContent *bincnt;                    /* Contenu binaire associé     */

#define LOADED_CONTENT_CONTENT_ATTRIB PYTHON_GET_DEF_FULL                       \
(                                                                               \
    content, py_loaded_content,                                                 \
    "Binary content, provided as a pychrysalide.analysis.BinContent instance."  \
)

    content = G_LOADED_CONTENT(pygobject_get(self));

    bincnt = g_loaded_content_get_content(content);

    result = pygobject_new(G_OBJECT(bincnt));

    g_object_unref(G_OBJECT(bincnt));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Décrit la nature du contenu reconnu pour l'élément chargé.   *
*                                                                             *
*  Retour      : Classe de contenu associée à l'élément chargé.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_get_content_class(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    char *class;                            /* Nature du contenu binaire   */

#define LOADED_CONTENT_CONTENT_CLASS_ATTRIB PYTHON_GET_DEF_FULL             \
(                                                                           \
    content_class, py_loaded_content,                                       \
    "Nature of the loaded content.\n"                                       \
    "\n"                                                                    \
    "The description associated to a loaded ARM Elf binary is for instance" \
    " 'elf-armv7'."                                                         \
)

    content = G_LOADED_CONTENT(pygobject_get(self));

    class = g_loaded_content_get_content_class(content, false);

    result = PyUnicode_FromString(class);

    free(class);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Décrit la nature du contenu reconnu pour l'élément chargé.   *
*                                                                             *
*  Retour      : Classe de contenu associée à l'élément chargé.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_content_get_content_class_for_human(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GLoadedContent *content;                /* Version GLib de l'élément   */
    char *class;                            /* Nature du contenu binaire   */

#define LOADED_CONTENT_CONTENT_CLASS_FOR_HUMAN_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                                           \
    content_class_for_human, py_loaded_content,                             \
    "Humain version of the nature of the loaded content.\n"                 \
    "\n"                                                                    \
    "The description associated to a loaded ARM Elf binary is for instance" \
    " ''Elf, ARMv7'."                                                       \
)

    content = G_LOADED_CONTENT(pygobject_get(self));

    class = g_loaded_content_get_content_class(content, true);

    result = PyUnicode_FromString(class);

    free(class);

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

PyTypeObject *get_python_loaded_content_type(void)
{
    static PyMethodDef py_loaded_content_methods[] = {
        LOADED_CONTENT_GET_CONTENT_WRAPPER,
        LOADED_CONTENT_GET_CONTENT_CLASS_WRAPPER,
        LOADED_CONTENT_ANALYZE_WRAPPER,
        LOADED_CONTENT_DESCRIBE_WRAPPER,
#ifdef INCLUDE_GTK_SUPPORT
        LOADED_CONTENT_COUNT_VIEWS_WRAPPER,
        LOADED_CONTENT_GET_VIEW_NAME_WRAPPER,
        LOADED_CONTENT_BUILD_DEFAULT_VIEW_WRAPPER,
        LOADED_CONTENT_BUILD_VIEW_WRAPPER,
        LOADED_CONTENT_GET_VIEW_INDEX_WRAPPER,
#endif
        LOADED_CONTENT_ANALYZE_METHOD,
        LOADED_CONTENT_ANALYZE_AND_WAIT_METHOD,
        LOADED_CONTENT_DESCRIBE_METHOD,
        LOADED_CONTENT_DETECT_OBFUSCATORS_METHOD,
#ifdef INCLUDE_GTK_SUPPORT
        LOADED_CONTENT_COUNT_VIEWS_METHOD,
        LOADED_CONTENT_GET_VIEW_NAME_METHOD,
        LOADED_CONTENT_BUILD_DEFAULT_VIEW_METHOD,
        LOADED_CONTENT_BUILD_VIEW_METHOD,
        LOADED_CONTENT_GET_VIEW_INDEX_METHOD,
#endif
        { NULL }
    };

    static PyGetSetDef py_loaded_content_getseters[] = {
        LOADED_CONTENT_CONTENT_ATTRIB,
        LOADED_CONTENT_CONTENT_CLASS_ATTRIB,
        LOADED_CONTENT_CONTENT_CLASS_FOR_HUMAN_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_loaded_content_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.LoadedContent",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = LOADED_CONTENT_DOC,

        .tp_methods     = py_loaded_content_methods,
        .tp_getset      = py_loaded_content_getseters,

        .tp_new         = py_loaded_content_new,

    };

    return &py_loaded_content_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....LoadedContent'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_loaded_content_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LoadedContent' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_loaded_content_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

#ifdef INCLUDE_GTK_SUPPORT
        if (!ensure_python_named_widget_is_registered())
            return false;
#endif

        if (!register_class_for_pygobject(dict, G_TYPE_LOADED_CONTENT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en contenu chargé.                        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_loaded_content(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_loaded_content_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to loaded content");
            break;

        case 1:
            *((GLoadedContent **)dst) = G_LOADED_CONTENT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
