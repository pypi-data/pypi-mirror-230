
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin.c - interactions avec un greffon Python
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


#include "plugin.h"


#include <assert.h>
#include <libgen.h>
#include <malloc.h>
#include <pygobject.h>
#include <string.h>


#include <common/extstr.h>
#include <plugins/dt.h>
#include <plugins/plugin-int.h>
#include <plugins/pglist.h>
#include <plugins/self.h>


#include "constants.h"
#include "translate.h"
#include "../access.h"
#include "../core.h"
#include "../helpers.h"
#include "../core/constants.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Initialise la classe des greffons d'extension. */
static void py_plugin_module_init_gclass(GPluginModuleClass *, gpointer);

CREATE_DYN_ABSTRACT_CONSTRUCTOR(plugin_module, G_TYPE_PLUGIN_MODULE, py_plugin_module_init_gclass);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_plugin_module_init(PyObject *self, PyObject *args, PyObject *kwds);

/* Encadre une étape de la vie d'un greffon. */
static bool py_plugin_module_manage_wrapper(GPluginModule *);

/* Assiste la désactivation d'un greffon. */
static bool py_plugin_module_exit(GPluginModule *);

/* Accompagne la fin du chargement des modules natifs. */
static void py_plugin_module_notify_plugins_loaded_wrapper(GPluginModule *, PluginAction);

/* Fournit le nom brut associé au greffon par défaut. */
static PyObject *py_plugin_module_get_modname_by_default(PyObject *, PyObject *);

/* Fournit le nom brut associé au greffon. */
static char *py_plugin_module_get_modname_wrapper(const GPluginModule *);

#ifdef INCLUDE_GTK_SUPPORT

/* Complète une liste de resources pour thème. */
static void py_plugin_module_include_theme_wrapper(const GPluginModule *, PluginAction, gboolean, char ***, size_t *);

/* Rend compte de la création d'un panneau. */
static void py_plugin_module_notify_panel_creation_wrapper(const GPluginModule *, PluginAction, GPanelItem *);

/* Rend compte d'un affichage ou d'un retrait de panneau. */
static void py_plugin_module_notify_panel_docking_wrapper(const GPluginModule *, PluginAction, GPanelItem *, bool);

#endif

/* Procède à une opération liée à un contenu binaire. */
static void py_plugin_module_handle_binary_content_wrapper(const GPluginModule *, PluginAction, GBinContent *, wgroup_id_t, GtkStatusStack *);

/* Procède à une opération liée à un contenu chargé. */
static void py_plugin_module_handle_loaded_content_wrapper(const GPluginModule *, PluginAction, GLoadedContent *, wgroup_id_t, GtkStatusStack *);

/* Procède à une opération liée à l'analyse d'un format. */
static bool py_plugin_module_handle_known_format_analysis_wrapper(const GPluginModule *, PluginAction, GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Procède à un préchargement de format de fichier. */
static bool py_plugin_module_preload_binary_format_wrapper(const GPluginModule *, PluginAction, GBinFormat *, GPreloadInfo *, GtkStatusStack *);

/* Procède au rattachement d'éventuelles infos de débogage. */
static void py_plugin_module_attach_debug_format_wrapper(const GPluginModule *, PluginAction, GExeFormat *);

/* Exécute une action pendant un désassemblage de binaire. */
static void py_plugin_module_process_disassembly_event_wrapper(const GPluginModule *, PluginAction, GLoadedBinary *, GtkStatusStack *, GProcContext *);

/* Effectue la détection d'effets d'outils externes. */
static void py_plugin_module_detect_external_tools_wrapper(const GPluginModule *, PluginAction, const GLoadedContent *, bool, char ***, size_t *);



/* ------------------------- MODULE PYTHON POUR LES SCRIPTS ------------------------- */


/* Construit le nom d'un fichier de configuration du greffon. */
static PyObject *py_plugin_module_build_config_filename(PyObject *, PyObject *);

/* Affiche un message dans le journal des messages système. */
static PyObject *py_plugin_module_log_message(PyObject *, PyObject *);

/* Fournit le nom brut associé au greffon. */
static PyObject *py_plugin_module_get_modname(PyObject *, void *);

/* Indique le fichier contenant le greffon manipulé. */
static PyObject *py_plugin_module_get_filename(PyObject *, void *);

/* Fournit la description du greffon dans son intégralité. */
static PyObject *py_plugin_module_get_interface(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe des greffons d'extension.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_init_gclass(GPluginModuleClass *class, gpointer unused)
{
    class->init = NULL;
    class->manage = py_plugin_module_manage_wrapper;
    class->exit = py_plugin_module_exit;

    class->plugins_loaded = py_plugin_module_notify_plugins_loaded_wrapper;

    class->get_modname = py_plugin_module_get_modname_wrapper;

#ifdef INCLUDE_GTK_SUPPORT
    class->include_theme = py_plugin_module_include_theme_wrapper;
    class->notify_panel = py_plugin_module_notify_panel_creation_wrapper;
    class->notify_docking = py_plugin_module_notify_panel_docking_wrapper;
#endif

    class->handle_content = py_plugin_module_handle_binary_content_wrapper;
    class->handle_loaded = py_plugin_module_handle_loaded_content_wrapper;

    class->handle_fmt_analysis = py_plugin_module_handle_known_format_analysis_wrapper;
    class->preload_format = py_plugin_module_preload_binary_format_wrapper;
    class->attach_debug = py_plugin_module_attach_debug_format_wrapper;

    class->process_disass = py_plugin_module_process_disassembly_event_wrapper;

    class->detect = py_plugin_module_detect_external_tools_wrapper;

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

static int py_plugin_module_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan d'un appel            */
    GPluginModule *plugin;                  /* Greffon à manipuler         */
    plugin_interface *iface;                /* Interface à constituer      */
    GPluginModule *dependency;              /* Module nécessaire           */
    PyObject *value;                        /* Valeur à présence imposée   */
    size_t i;                               /* Boucle de parcours          */
    PyObject *action;                       /* Identifiant d'une action    */

#define PLUGIN_MODULE_DOC                                                   \
    "PythonModule is the class allowing the creation of Chrysalide plugins" \
    " for Python."                                                          \
    "\n"                                                                    \
    "Calls to the *__init__* constructor of this abstract object expect"    \
    " no particular argument.\n"                                            \
    "\n"                                                                    \
    "Several items have to be defined as class attributes in the final"     \
    " class:\n"                                                             \
    "* *_name*: a string providing a small name for the plugin;\n"          \
    "* *_desc*: a string for a human readable description of the plugin;\n" \
    "* *_version*: a string providing the version of the plugin;\n"         \
    "* *_url*: a string for the homepage describing the plugin;\n"          \
    "* *_actions*: a tuple of"                                              \
    " pychrysalide.plugins.PluginModule.PluginAction defining the features" \
    " the plugin is bringing; this list can be empty.\n"                    \
    "\n"                                                                    \
    "Depending on the implemented actions, some of the following methods"   \
    " have to be defined for new classes:\n"                                \
    "* pychrysalide.plugins.PluginModule._init_config();\n"                 \
    "* pychrysalide.plugins.PluginModule._notify_plugins_loaded();\n"       \
    "* pychrysalide.plugins.PluginModule._include_theme();\n"               \
    "* pychrysalide.plugins.PluginModule._on_panel_creation;\n"             \
    "* pychrysalide.plugins.PluginModule._on_panel_docking();\n"            \
    "* pychrysalide.plugins.PluginModule._handle_binary_content();\n"       \
    "* pychrysalide.plugins.PluginModule._handle_loaded_content();\n"       \
    "* pychrysalide.plugins.PluginModule._handle_format_analysis();\n"      \
    "* pychrysalide.plugins.PluginModule._preload_format();\n"              \
    "* pychrysalide.plugins.PluginModule._attach_debug_format();\n"         \
    "* pychrysalide.plugins.PluginModule._process_disassembly_event();\n"   \
    "* pychrysalide.plugins.PluginModule._detect_external_tools()."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    plugin = G_PLUGIN_MODULE(pygobject_get(self));

    iface = calloc(1, sizeof(plugin_interface));
    plugin->interface = iface;

#define LOAD_PYTHON_IFACE(attr)                                                                         \
    do                                                                                                  \
    {                                                                                                   \
        value = PyObject_GetAttrString(self, "_" #attr);                                                \
        if (value == NULL)                                                                              \
        {                                                                                               \
            PyErr_SetString(PyExc_TypeError, _("A '_" #attr "' class attributes is missing."));         \
            return -1;                                                                                  \
        }                                                                                               \
        if (PyUnicode_Check(value))                                                                     \
        {                                                                                               \
            iface->attr = strdup(PyUnicode_AsUTF8(value));                                              \
            Py_DECREF(value);                                                                           \
        }                                                                                               \
        else                                                                                            \
        {                                                                                               \
            Py_DECREF(value);                                                                           \
            PyErr_SetString(PyExc_TypeError, _("The '_" #attr "' class attributes must be a string.")); \
            return -1;                                                                                  \
        }                                                                                               \
        assert(iface->attr != NULL);                                                                    \
    }                                                                                                   \
    while (0);

    LOAD_PYTHON_IFACE(name);
    LOAD_PYTHON_IFACE(desc);
    LOAD_PYTHON_IFACE(version);
    LOAD_PYTHON_IFACE(url);

    iface->container = false;

    /**
     * Comme le greffon n'est pas passé par la résolution des dépendances,
     * orchestrée par la fonction g_plugin_module_resolve_dependencies(),
     * on simule l'effet attendu en obtenant une référence par un appel à
     * get_plugin_by_name().
     *
     * L'incrémentation des références doit coller au plus près de
     * l'inscription nominative du greffon : en cas de sortie impromptue
     * (lorsqu'une erreur intervient pendant un chargement par exemple),
     * l'état de l'ensemble est ainsi cohérent au moment du retrait du
     * greffon fautif via la fonction g_plugin_module_dispose().
     */

    lock_plugin_list_for_reading();
    dependency = get_plugin_by_name("PyChrysalide", NULL);
    unlock_plugin_list_for_reading();

    assert(dependency != NULL);

    if (dependency == NULL)
    {
        PyErr_SetString(PyExc_TypeError, _("The internal name of the Python plugin has changed!"));
        return -1;
    }

    iface->required = malloc(sizeof(char *));
    iface->required[0] = "PyChrysalide";
    iface->required_count = 1;

    /* Validation du reste de l'interface */

    value = PyObject_GetAttrString(self, "_actions");

    if (value == NULL)
    {
        PyErr_SetString(PyExc_TypeError, _("An '_actions' class attributes is missing."));
        return -1;
    }

    if (!PyTuple_Check(value))
    {
        Py_DECREF(value);
        PyErr_SetString(PyExc_TypeError, _("The '_actions' class attributes must be a tuple."));
        return -1;
    }

    iface->actions_count = PyTuple_Size(value);
    iface->actions = malloc(iface->actions_count * sizeof(plugin_action_t));

    for (i = 0; i < iface->actions_count; i++)
    {
        action = PyTuple_GetItem(value, i);

        if (!PyLong_Check(action))
        {
            Py_DECREF(value);
            PyErr_SetString(PyExc_TypeError, _("invalid type for plugin action."));
            return -1;
        }

        iface->actions[i] = PyLong_AsUnsignedLong(action);

    }

    Py_DECREF(value);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Encadre une étape de la vie d'un greffon.                    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_plugin_module_manage_wrapper(GPluginModule *plugin)
{
    bool result;                            /* Bilan à faire remonter      */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_MANAGE_WRAPPER PYTHON_WRAPPER_DEF                 \
(                                                                       \
    _manage, "$self, action, /",                                        \
    METH_VARARGS,                                                       \
    "Abstract method called to react to several steps of the plugin"    \
    " life.\n"                                                          \
    "\n"                                                                \
    "The expected action is a"                                          \
    " pychrysalide.plugins.PluginModule.PluginAction value.\n"          \
    "\n"                                                                \
    "This method has to be defined in order to handle actions such as"  \
    " *PLUGIN_LOADED*."                                                 \
)

    result = true;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_manage"))
    {
        args = PyTuple_New(1);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(PGA_PLUGIN_LOADED));

        pyret = run_python_method(pyobj, "_manage", args);

        result = (pyret == Py_True);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Assiste la désactivation d'un greffon.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_plugin_module_exit(GPluginModule *plugin)
{
    bool result;                            /* Bilan à faire remonter      */
    plugin_interface *final;                /* Interface finale conservée  */

    result = true;

    final = (plugin_interface *)G_PLUGIN_MODULE(plugin)->interface;

    if (final != NULL)
    {
        if (final->name != NULL) free(final->name);
        if (final->desc != NULL) free(final->desc);
        if (final->version != NULL) free(final->version);
        if (final->url != NULL) free(final->url);

        assert(final->required_count == 1);

        if (final->required != NULL)
            free(final->required);

        if (final->actions != NULL)
            free(final->actions);

        free(final);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                                                                             *
*  Description : Accompagne la fin du chargement des modules natifs.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_notify_plugins_loaded_wrapper(GPluginModule *plugin, PluginAction action)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_NOTIFY_PLUGINS_LOADED_WRAPPER PYTHON_WRAPPER_DEF  \
(                                                                       \
    _notify_plugins_loaded, "$self, action, /",                         \
    METH_VARARGS,                                                       \
    "Abstract method called once all the (native?) plugins are"         \
    " loaded.\n"                                                        \
    "\n"                                                                \
    "The expected action is a"                                          \
    " pychrysalide.plugins.PluginModule.PluginAction value.\n"          \
    "\n"                                                                \
    "This method has to be defined in order to handle actions such as"  \
    " *NATIVE_PLUGINS_LOADED* or *PLUGINS_LOADED*."                     \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_notify_plugins_loaded"))
    {
        args = PyTuple_New(1);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));

        pyret = run_python_method(pyobj, "_notify_plugins_loaded", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Fournit le nom brut associé au greffon par défaut.           *
*                                                                             *
*  Retour      : Désignation brute du greffon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_get_modname_by_default(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GPluginModule *plugin;                  /* Version native du greffon   */
    char *path;                             /* Chemin à traiter            */

    plugin = G_PLUGIN_MODULE(pygobject_get(self));

    path = strdup(g_plugin_module_get_filename(plugin));

    result = PyUnicode_FromString(basename(path));

    free(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à valider.                                  *
*                                                                             *
*  Description : Fournit le nom brut associé au greffon.                      *
*                                                                             *
*  Retour      : Désignation brute du greffon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_plugin_module_get_modname_wrapper(const GPluginModule *plugin)
{
    char *result;                           /* Désignation brute à renvoyer*/
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_GET_MODNAME_WRAPPER PYTHON_WRAPPER_DEF_WITH       \
(                                                                       \
    _get_modname, "$self, /",                                           \
    METH_VARARGS, py_plugin_module_get_modname_by_default,              \
    "(Abstract) method providing the raw module name of the plugin.\n"  \
    " loaded.\n"                                                        \
    "\n"                                                                \
    "The result should be a short string value.\n"                      \
    "\n"                                                                \
    "A default implementation builds the module name from the Python"   \
    " script filename."                                                 \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_get_modname"))
    {
        pyret = run_python_method(pyobj, "_get_modname", NULL);

        if (!PyUnicode_Check(pyret))
            g_plugin_module_log_variadic_message(plugin, LMT_ERROR,
                                                 _("The returned raw name must be a string"));

        else
            result = strdup(PyUnicode_DATA(pyret));

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin    = greffon à manipuler.                             *
*                action    = type d'action attendue.                          *
*                dark      = indique une préférence pour la variante foncée.  *
*                resources = liste de ressources à constituer. [OUT]          *
*                count     = taille de cette liste. [OUT]                     *
*                                                                             *
*  Description : Complète une liste de resources pour thème.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_include_theme_wrapper(const GPluginModule *plugin, PluginAction action, gboolean dark, char ***resources, size_t *count)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *darkness;                     /* Valeur booléenne à joindre  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */
    Py_ssize_t length;                      /* Nombre d'éléments collectés */
    Py_ssize_t i;                           /* Boucle de parcours          */
    PyObject *res;                          /* Ressource à ajouter         */

#define PLUGIN_MODULE_INCLUDE_THEME_WRAPPER PYTHON_WRAPPER_DEF          \
(                                                                       \
    _include_theme, "$self, action, dark, /",                           \
    METH_VARARGS,                                                       \
    "Abstract method called once all the native plugins are loaded.\n"  \
    "\n"                                                                \
    "The expected action is a"                                          \
    " pychrysalide.plugins.PluginModule.PluginAction value and the"     \
    " *dark* parameter indicates if a dark theme is being to get"       \
    " loaded.\n"                                                        \
    "\n"                                                                \
    "The expected result is a list of CSS definition resource URIs,"    \
    " provided as strings such as 'resource:///org/xxx/extra.css'"      \
    " for instance.\n"                                                  \
    "\n"                                                                \
    "This method has to be defined in order to handle action such as"   \
    " *GUI_THEME*."                                                     \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_include_theme"))
    {
        args = PyTuple_New(2);

        darkness = (dark ? Py_True : Py_False);
        Py_INCREF(darkness);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, darkness);

        pyret = run_python_method(pyobj, "_include_theme", args);

        if (!PySequence_Check(pyret))
            g_plugin_module_log_simple_message(plugin, LMT_ERROR, _("The returned value must be a string list"));

        else
        {
            length = PySequence_Length(pyret);

            for (i = 0; i < length; i++)
            {
                res = PySequence_GetItem(pyret, i);

                if (!PyUnicode_Check(res))
                    g_plugin_module_log_variadic_message(plugin, LMT_ERROR,
                                                         _("The returned #%zd value must be a string"));

                else
                {
                    *resources = realloc(*resources, ++(*count) * sizeof(char **));
                    *resources[*count - 1] = strdup(PyUnicode_DATA(res));
                }

                Py_DECREF(res);

            }

        }

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                item   = nouveau panneau créé.                               *
*                                                                             *
*  Description : Rend compte de la création d'un panneau.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_notify_panel_creation_wrapper(const GPluginModule *plugin, PluginAction action, GPanelItem *item)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_ON_PANEL_CREATION_WRAPPER PYTHON_WRAPPER_DEF      \
(                                                                       \
    _on_panel_creation, "$self, action, item, /",                       \
    METH_VARARGS,                                                       \
    "Abstract method called when a new instance of panel is created.\n" \
    "\n"                                                                \
    "The expected *action* is a"                                        \
    " pychrysalide.plugins.PluginModule.PluginAction value and the"     \
    " *item* is a pychrysalide.gui.PanelItem instance.\n"               \
    "\n"                                                                \
    "This method has to be defined in order to handle action such as"   \
    " *PANEL_CREATION*."                                                \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_on_panel_creation"))
    {
        args = PyTuple_New(2);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(item)));

        pyret = run_python_method(pyobj, "_on_panel_creation", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                item   = panneau marqué par un changement d'affichage.       *
*                dock   = indique une accroche et non un décrochage.          *
*                                                                             *
*  Description : Rend compte d'un affichage ou d'un retrait de panneau.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_notify_panel_docking_wrapper(const GPluginModule *plugin, PluginAction action, GPanelItem *item, bool dock)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydock;                       /* Valeur booléenne à joindre  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_ON_PANEL_DOCKING_WRAPPER PYTHON_WRAPPER_DEF       \
(                                                                       \
    _on_panel_docking, "$self, action, item, dock, /",                  \
    METH_VARARGS,                                                       \
    "Abstract method called when a panel is docked or undocked into"    \
    " the Chrysalide main graphical interface.\n"                       \
    "\n"                                                                \
    "The expected *action* is a"                                        \
    " pychrysalide.plugins.PluginModule.PluginAction value, the"        \
    " *item* is a pychrysalide.gui.PanelItem instance and the *dock*"   \
    " parameter indicates if the panel request a docking operation"     \
    " or an undocking one.\n"                                           \
    "\n"                                                                \
    "This method has to be defined in order to handle action such as"   \
    " *PANEL_DOCKING*."                                                 \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_on_panel_docking"))
    {
        args = PyTuple_New(3);

        pydock = (dock ? Py_True : Py_False);
        Py_INCREF(pydock);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(item)));
        PyTuple_SetItem(args, 2, pydock);

        pyret = run_python_method(pyobj, "_on_panel_docking", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = contenu binaire à traiter.                         *
*                wid     = identifiant du groupe de traitement.               *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Procède à une opération liée à un contenu binaire.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_handle_binary_content_wrapper(const GPluginModule *plugin, PluginAction action, GBinContent *content, wgroup_id_t wid, GtkStatusStack *status)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_HANDLE_BINARY_CONTENT_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                                   \
    _handle_binary_content, "$self, action, content, wid, status, /",               \
    METH_VARARGS,                                                                   \
    "Abstract method used to explore a binary content (and possibly to add new"     \
    " contents to explore) or to load a recognized binary content into a"           \
    " pychrysalide.analysis.LoadedContent instance.\n"                              \
    "\n"                                                                            \
    "The expected action is a pychrysalide.plugins.PluginModule.PluginAction"       \
    " value and the initial binary content is a pychrysalide.analysis.BinContent"   \
    " instance. A tracking identifier is provided and is aimed to be"               \
    " used with methods from pychrysalide.analysis.ContentExplorer and"             \
    " pychrysalide.analysis.ContentResolver. A reference to the main status bar"    \
    " may also be provided, as a pychrysalide.gtkext.StatusStack instance if"       \
    " running in graphical mode or None otherwise.\n"                               \
    "\n"                                                                            \
    "This method has to be defined in order to handle actions such as"              \
    " *CONTENT_EXPLORER* or *CONTENT_RESOLVER*."                                    \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_handle_binary_content"))
    {
        args = PyTuple_New(4);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(content)));
        PyTuple_SetItem(args, 2, PyLong_FromUnsignedLong(wid));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_handle_binary_content", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = contenu chargé à traiter.                          *
*                gid     = identifiant du groupe de traitement.               *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Procède à une opération liée à un contenu chargé.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_handle_loaded_content_wrapper(const GPluginModule *plugin, PluginAction action, GLoadedContent *content, wgroup_id_t gid, GtkStatusStack *status)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_HANDLE_LOADED_CONTENT_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                                   \
    _handle_loaded_content, "$self, action, content, gid, status, /",               \
    METH_VARARGS,                                                                   \
    "Abstract method run once a loaded binary has been analyzed with success.\n"    \
    "\n"                                                                            \
    "The expected action is a pychrysalide.plugins.PluginModule.PluginAction"       \
    " value and the analyzed content is a pychrysalide.analysis.LoadedContent"      \
    " instance. The identifier refers to the working queue used to process the"     \
    " analysis. A reference to the main status bar may also be provided, as a"      \
    " pychrysalide.gtkext.StatusStack instance if running in graphical mode or"     \
    " None otherwise.\n"                                                            \
    "\n"                                                                            \
    "This method has to be defined in order to handle action such as"               \
    " *CONTENT_ANALYZED*."                                                          \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_handle_loaded_content"))
    {
        args = PyTuple_New(4);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(content)));
        PyTuple_SetItem(args, 2, PyLong_FromUnsignedLong(gid));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_handle_loaded_content", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Procède à une opération liée à l'analyse d'un format.        *
*                                                                             *
*  Retour      : Bilan de l'exécution du traitement.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_plugin_module_handle_known_format_analysis_wrapper(const GPluginModule *plugin, PluginAction action, GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_HANDLE_BINARY_FORMAT_ANALYSIS_WRAPPER PYTHON_WRAPPER_DEF      \
(                                                                                   \
    _handle_binary_format_analysis, "$self, action, format, gid, status, /",        \
    METH_VARARGS,                                                                   \
    "Abstract method run at several different steps of a binary format analysis:\n" \
    "* at the beginning and at the end of the main analysis pass;\n"                \
    "* at the beginning and at the end of the extra final pass.\n"                  \
    "\n"                                                                            \
    "The expected action is a pychrysalide.plugins.PluginModule.PluginAction"       \
    " value and the provided format is a pychrysalide.format.KnownFormat"           \
    " instance. The identifier refers to the working queue used to process the"     \
    " analysis. A reference to the main status bar may also be provided, as a"      \
    " pychrysalide.gtkext.StatusStack instance if running in graphical mode or"     \
    " None otherwise.\n"                                                            \
    "\n"                                                                            \
    "This method has to be defined in order to handle actions such as"              \
    " *FORMAT_ANALYSIS_STARTED*, *FORMAT_ANALYSIS_ENDED*,"                          \
    " *FORMAT_POST_ANALYSIS_STARTED* or *FORMAT_POST_ANALYSIS_ENDED*."              \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_handle_format_analysis"))
    {
        args = PyTuple_New(4);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(format)));
        PyTuple_SetItem(args, 2, PyLong_FromUnsignedLong(gid));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_handle_format_analysis", args);

        result = (pyret == Py_True);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Procède à un préchargement de format de fichier.             *
*                                                                             *
*  Retour      : Bilan de l'exécution du traitement.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_plugin_module_preload_binary_format_wrapper(const GPluginModule *plugin, PluginAction action, GBinFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_PRELOAD_BINARY_FORMAT_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                                   \
    _preload_binary_format, "$self, action, format, info, status, /",               \
    METH_VARARGS,                                                                   \
    "Abstract method which is an opportunity to setup instructions or comments"     \
    " ahead of the disassembling process.\n"                                        \
    "\n"                                                                            \
    "Format fields do not need to get disassembled and may be annotated for"        \
    " instance.\n"                                                                  \
    "\n"                                                                            \
    "The expected action is a pychrysalide.plugins.PluginModule.PluginAction"       \
    " value and the provided format is a pychrysalide.format.BinFormat"             \
    " instance. The information holder to fill is a pychrysalide.format.PreloadInfo"\
    " instance. A reference to the main status bar may also be provided, as a"      \
    " pychrysalide.gtkext.StatusStack instance if running in graphical mode or"     \
    " None otherwise.\n"                                                            \
    "\n"                                                                            \
    "This method has to be defined in order to handle action such as"               \
    " *FORMAT_PRELOAD*."                                                            \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_preload_format"))
    {
        args = PyTuple_New(4);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(format)));
        PyTuple_SetItem(args, 2, pygobject_new(G_OBJECT(info)));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(status)));

        pyret = run_python_method(pyobj, "_preload_format", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                                                                             *
*  Description : Procède au rattachement d'éventuelles infos de débogage.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_attach_debug_format_wrapper(const GPluginModule *plugin, PluginAction action, GExeFormat *format)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_ATTACH_DEBUG_FORMAT_WRAPPER PYTHON_WRAPPER_DEF                \
(                                                                                   \
    _attach_debug_format, "$self, action, format, /",                               \
    METH_VARARGS,                                                                   \
    "Abstract method called when a debugger is attached to a binary format.\n"      \
    "\n"                                                                            \
    "The expected action is a pychrysalide.plugins.PluginModule.PluginAction"       \
    " value and the provided format is a pychrysalide.format.ExeFormat instance.\n" \
    "\n"                                                                            \
    "This method has to be defined in order to handle action such as"               \
    " *FORMAT_ATTACH_DEBUG*."                                                       \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_attach_debug_format"))
    {
        args = PyTuple_New(2);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(format)));

        pyret = run_python_method(pyobj, "_attach_debug_format", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                binary = binaire dont le contenu est en cours de traitement. *
*                status  = barre de statut à tenir informée.                  *
*                context = contexte de désassemblage.                         *
*                                                                             *
*  Description : Exécute une action pendant un désassemblage de binaire.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_process_disassembly_event_wrapper(const GPluginModule *plugin, PluginAction action, GLoadedBinary *binary, GtkStatusStack *status, GProcContext *context)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */

#define PLUGIN_MODULE_PROCESS_DISASSEMBLY_EVENT_WRAPPER PYTHON_WRAPPER_DEF          \
(                                                                                   \
    _process_disassembly_event, "$self, action, format, /",                         \
    METH_VARARGS,                                                                   \
    "Abstract method run at several different steps of a binary analysis.\n"        \
    "\n"                                                                            \
    "The expected action is a pychrysalide.plugins.PluginModule.PluginAction"       \
    " value and the provided format is a pychrysalide.format.ExeFormat instance.\n" \
    "\n"                                                                            \
    "This method has to be defined in order to handle actions such as"              \
    " *DISASSEMBLY_STARTED*, *DISASSEMBLY_RAW*, *DISASSEMBLY_HOOKED_LINK*,"         \
    " *DISASSEMBLY_HOOKED_POST*, *DISASSEMBLY_LIMITED*, *DISASSEMBLY_LOOPS*,"       \
    " *DISASSEMBLY_LINKED*, *DISASSEMBLY_GROUPED*, *DISASSEMBLY_RANKED*,"           \
    " *DISASSEMBLY_ENDED*."                                                         \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_process_disassembly_event"))
    {
        args = PyTuple_New(4);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(binary)));
        PyTuple_SetItem(args, 2, pygobject_new(G_OBJECT(status)));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(context)));

        pyret = run_python_method(pyobj, "_process_disassembly_event", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = élément chargé à consulter.                        *
*                version = précise si les versions doivent être recherchées.  *
*                names   = désignations humaines correspondantes, à libérer.  *
*                count   = nombre de types d'obscurcissement trouvés. [OUT]   *
*                                                                             *
*  Description : Effectue la détection d'effets d'outils externes.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_plugin_module_detect_external_tools_wrapper(const GPluginModule *plugin, PluginAction action, const GLoadedContent *content, bool version, char ***names, size_t *count)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *details;                      /* Valeur booléenne à joindre  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan d'exécution           */
    Py_ssize_t length;                      /* Nombre d'éléments collectés */
    Py_ssize_t i;                           /* Boucle de parcours          */
    PyObject *res;                          /* Ressource à ajouter         */

#define PLUGIN_MODULE_DETECT_EXTERNAL_TOOLS_WRAPPER PYTHON_WRAPPER_DEF  \
(                                                                       \
    _detect_external_tools, "$self, action, content, version, /",       \
    METH_VARARGS,                                                       \
    "Abstract method called when a detection of tools used the build"   \
    " the analyzed content is required.\n"                              \
    "\n"                                                                \
    "The expected action is a"                                          \
    " pychrysalide.plugins.PluginModule.PluginAction value and the"     \
    " content is a pychrysalide.analysis.LoadedContent instance. The"   \
    " *version* parameter is a boolean value indicating if some extra"  \
    " details about the tools version are wished.\n"                    \
    "\n"                                                                \
    "The expected result is a list of strings.\n"                       \
    "\n"                                                                \
    "This method has to be defined in order to handle action such as"   \
    " *DETECTION_OBFUSCATORS*."                                         \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(plugin));

    if (has_python_method(pyobj, "_detect_external_tools"))
    {
        args = PyTuple_New(3);

        details = (version ? Py_True : Py_False);
        Py_INCREF(details);

        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(action));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(content)));
        PyTuple_SetItem(args, 2, details);

        pyret = run_python_method(pyobj, "_detect_external_tools", args);

        if (!PySequence_Check(pyret))
            g_plugin_module_log_simple_message(plugin, LMT_ERROR, _("The returned value must be a string list"));

        else
        {
            length = PySequence_Length(pyret);

            for (i = 0; i < length; i++)
            {
                res = PySequence_GetItem(pyret, i);

                if (!PyUnicode_Check(res))
                    g_plugin_module_log_variadic_message(plugin, LMT_ERROR,
                                                         _("The returned #%zd value must be a string"));

                else
                {
                    *names = realloc(*names, ++(*count) * sizeof(char **));
                    *names[*count - 1] = strdup(PyUnicode_DATA(res));
                }

                Py_DECREF(res);

            }

        }

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                           MODULE PYTHON POUR LES SCRIPTS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Construit le nom d'un fichier de configuration du greffon.   *
*                                                                             *
*  Retour      : Chemin d'accès déterminé, ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_build_config_filename(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *final;                      /* Suffixe de fichier imposé   */
    int create;                             /* Volonté de création         */
    char *filename;                         /* Nom de fichier déterminé    */

#define PLUGIN_MODULE_BUILD_CONFIG_FILENAME_METHOD PYTHON_METHOD_DEF        \
(                                                                           \
    build_config_filename, "final, /, create=False",                        \
    METH_VARARGS, py_plugin_module,                                         \
    "Build a filename suitable for the plugin configuration, ending with"   \
    " the *final* suffix.\n"                                                \
    "\n"                                                                    \
    "If the *create* parameter is set, the path to this filename is"        \
    " created.\n"                                                           \
    "\n"                                                                    \
    "The result is a string or None on failure."                            \
)

    create = 0;

    if (!PyArg_ParseTuple(args, "s|p", &final, &create))
        return NULL;

    filename = g_plugin_module_build_config_filename(G_PLUGIN_MODULE(pygobject_get(self)), final, create);

    if (filename != NULL)
    {
        result = PyUnicode_FromString(filename);
        free(filename);
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
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Affiche un message dans le journal des messages système.     *
*                                                                             *
*  Retour      : Rien en équivalent Python.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_log_message(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    LogMessageType type;                    /* Espèce du message           */
    const char *msg;                        /* Contenu du message          */

#define PLUGIN_MODULE_LOG_MESSAGE_METHOD PYTHON_METHOD_DEF                  \
(                                                                           \
    log_message, "type, msg, /",                                            \
    METH_VARARGS, py_plugin_module,                                         \
    "Display a message in the log window, in graphical mode, or in the"     \
    " console output if none.\n"                                            \
    "\n"                                                                    \
    "The type of the message has to be a pychrysalide.core.LogMessageType"  \
    " value."                                                               \
    "\n"                                                                    \
    "The only difference with the main pychrysalide.core.log_message()"     \
    " function is that messages are automatically prefixed with the plugin" \
    " name here."                                                           \
)

    if (!PyArg_ParseTuple(args, "O&s", convert_to_log_message_type, &type, &msg))
        return NULL;

    g_plugin_module_log_simple_message(G_PLUGIN_MODULE(pygobject_get(self)), type, msg);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom brut associé au greffon.                      *
*                                                                             *
*  Retour      : Désignation brute du greffon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_get_modname(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPluginModule *plugin;                  /* Version native du greffon   */
    char *modname;                          /* Désignation brute           */

#define PLUGIN_MODULE_MODNAME_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                           \
    modname, py_plugin_module,                              \
    "Raw module name of the plugin."                        \
)

    plugin = G_PLUGIN_MODULE(pygobject_get(self));
    modname = g_plugin_module_get_modname(plugin);

    result = PyUnicode_FromString(modname);

    free(modname);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le fichier contenant le greffon manipulé.            *
*                                                                             *
*  Retour      : Chemin d'accès au greffon.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_get_filename(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPluginModule *plugin;                  /* Version native du greffon   */
    const char *filename;                   /* Chemin d'accès associé      */

#define PLUGIN_MODULE_FILENAME_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                           \
    filename, py_plugin_module,                             \
    "Filename of the plugin."                               \
)

    plugin = G_PLUGIN_MODULE(pygobject_get(self));
    filename = g_plugin_module_get_filename(plugin);

    result = PyUnicode_FromString(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la description du greffon dans son intégralité.      *
*                                                                             *
*  Retour      : Interfaçage renseigné.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_get_interface(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPluginModule *plugin;                  /* Version native du greffon   */
    const plugin_interface *iface;          /* Interface liée à traduire   */

#define PLUGIN_MODULE_INTERFACE_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                               \
    interface, py_plugin_module,                                \
    "Interface exported by the plugin..\n"                      \
    "\n"                                                        \
    "This property is a pychrysalide.StructObject instance."    \
    "\n"                                                        \
    "The provided information is composed of the following"     \
    " properties :\n"                                           \
    "\n"                                                        \
    "* gtp_name;\n"                                             \
    "* name;\n"                                                 \
    "* desc;\n"                                                 \
    "* version;\n"                                              \
    "* url;\n"                                                  \
    "* container;\n"                                            \
    "* required;\n"                                             \
    "* actions.\n"                                              \
    "\n"                                                        \
    "The *gtp_name* value may be *None* for non-native plugin." \
    " All other fields carry a string value except:\n"          \
    "* *container*: a boolean status indicating if the plugin"  \
    " can embed other plugins;\n"                               \
    "* *required*: a tuple of depedencies names;\n"             \
    "* *actions*: a tuple of available features from the plugin"\
    " coded as pychrysalide.plugins.PluginModule.PluginAction"  \
    " values."                                                  \
)

    plugin = G_PLUGIN_MODULE(pygobject_get(self));
    iface = g_plugin_module_get_interface(plugin);

    result = translate_plugin_interface_to_python(iface);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la configuration mise en place pour le greffon.      *
*                                                                             *
*  Retour      : Configuration dédiée à l'extension.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugin_module_get_config(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPluginModule *plugin;                  /* Version native du greffon   */
    GGenConfig *config;                     /* Configuration associée      */

#define PLUGIN_MODULE_CONFIG_ATTRIB PYTHON_GET_DEF_FULL         \
(                                                               \
    config, py_plugin_module,                                   \
    "Dedicated configuration for the plugin."                   \
    "\n"                                                        \
    "The value is a pychrysalide.glibext.GenConfig instance"    \
    " or None if the configuration is not yet created.\n"       \
    "\n"                                                        \
    "As configuration storage path depends on the plugin name," \
    " all plugin properties have to get fully loaded by the"    \
    " core before the configuration can be setup."              \
    "automatically"            \
)

    plugin = G_PLUGIN_MODULE(pygobject_get(self));
    config = g_plugin_module_get_config(plugin);

    if (config == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(config));

        g_object_unref(G_OBJECT(config));

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

PyTypeObject *get_python_plugin_module_type(void)
{
    static PyMethodDef py_plugin_module_methods[] = {
        PLUGIN_MODULE_MANAGE_WRAPPER,
        PLUGIN_MODULE_NOTIFY_PLUGINS_LOADED_WRAPPER,
        PLUGIN_MODULE_GET_MODNAME_WRAPPER,
#ifdef INCLUDE_GTK_SUPPORT
        PLUGIN_MODULE_INCLUDE_THEME_WRAPPER,
        PLUGIN_MODULE_ON_PANEL_CREATION_WRAPPER,
        PLUGIN_MODULE_ON_PANEL_DOCKING_WRAPPER,
#endif
        PLUGIN_MODULE_HANDLE_BINARY_CONTENT_WRAPPER,
        PLUGIN_MODULE_HANDLE_LOADED_CONTENT_WRAPPER,
        PLUGIN_MODULE_HANDLE_BINARY_FORMAT_ANALYSIS_WRAPPER,
        PLUGIN_MODULE_PRELOAD_BINARY_FORMAT_WRAPPER,
        PLUGIN_MODULE_ATTACH_DEBUG_FORMAT_WRAPPER,
        PLUGIN_MODULE_PROCESS_DISASSEMBLY_EVENT_WRAPPER,
        PLUGIN_MODULE_DETECT_EXTERNAL_TOOLS_WRAPPER,
        PLUGIN_MODULE_BUILD_CONFIG_FILENAME_METHOD,
        PLUGIN_MODULE_LOG_MESSAGE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_plugin_module_getseters[] = {
        PLUGIN_MODULE_MODNAME_ATTRIB,
        PLUGIN_MODULE_FILENAME_ATTRIB,
        PLUGIN_MODULE_INTERFACE_ATTRIB,
        PLUGIN_MODULE_CONFIG_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_plugin_module_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.PluginModule",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = PLUGIN_MODULE_DOC,

        .tp_methods     = py_plugin_module_methods,
        .tp_getset      = py_plugin_module_getseters,

        .tp_init        = py_plugin_module_init,
        .tp_new         = py_plugin_module_new,

    };

    return &py_plugin_module_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins.PluginModule'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_plugin_module_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'PluginModule'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_plugin_module_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_PLUGIN_MODULE, type))
            return false;

        if (!define_plugin_module_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : modname  = nom du module à charger.                          *
*                filename = chemin d'accès au code Python à charger.          *
*                                                                             *
*  Description : Crée un greffon à partir de code Python.                     *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL si erreur.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPluginModule *create_python_plugin(const char *modname, const char *filename)
{
    GPluginModule *result;                  /* Structure à retourner       */
    PyObject *name;                         /* Chemin d'accès pour Python  */
    PyObject *module;                       /* Script Python chargé        */
    PyObject *dict;                         /* Dictionnaire associé        */
    PyObject *class;                        /* Classe à instancier         */
    PyObject *instance;                     /* Instance Python du greffon  */

    name = PyUnicode_FromString(modname);
    if (name == NULL) goto bad_exit;

    module = PyImport_Import(name);
    Py_DECREF(name);

    if (module == NULL) goto no_import;

    dict = PyModule_GetDict(module);
    class = PyDict_GetItemString(dict, "AutoLoad");

    if (class == NULL) goto no_class;
    if (!PyType_Check(class->ob_type)) goto no_class;

    Py_INCREF(class);

    instance = PyObject_CallFunction(class, NULL);
    if (instance == NULL) goto no_instance;

    result = G_PLUGIN_MODULE(pygobject_get(instance));

    result->filename = strdup(filename);

    /**
     * L'instance Python et l'objet GLib résultante sont un même PyGObject.
     *
     * Donc pas besoin de toucher au comptage des références ici, la libération
     * se réalisera à la fin, quand l'objet GLib sera libéré.
     */

    Py_DECREF(module);

    return result;

 no_instance:

    log_pychrysalide_exception(_("An error occured when building the 'AutoLoad' instance"));

 no_class:

    if (class == NULL)
        log_plugin_simple_message(LMT_ERROR,
                                  _("An error occured when looking for the 'AutoLoad': item not found!"));

 no_import:

    Py_XDECREF(module);

    log_pychrysalide_exception(_("An error occured when importing '%s'"), modname);

 bad_exit:

    return NULL;

}
