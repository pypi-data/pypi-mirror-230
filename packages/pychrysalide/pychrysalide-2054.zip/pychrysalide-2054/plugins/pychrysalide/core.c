
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - plugin permettant des extensions en Python
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#undef NO_IMPORT_PYGOBJECT
#include <pygobject.h>
#define NO_IMPORT_PYGOBJECT


#include "core.h"


#include <assert.h>
#include <errno.h>
#include <malloc.h>
#include <pygobject.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>


#include <i18n.h>
#include <gleak.h>
#include <common/cpp.h>
#include <common/environment.h>
#include <common/extstr.h>
#include <core/core.h>
#include <core/logs.h>
#include <core/paths.h>
#include <plugins/pglist.h>
#include <plugins/self.h>


#include "access.h"
#include "helpers.h"
#include "star.h"
#include "strenum.h"
#include "struct.h"
#include "analysis/module.h"
#include "arch/module.h"
#include "common/module.h"
#include "core/module.h"
#include "debug/module.h"
#include "format/module.h"
#include "glibext/module.h"
#include "gtkext/module.h"
#include "gui/module.h"
#include "mangling/module.h"
#include "plugins/module.h"
#include "plugins/plugin.h"



DEFINE_CHRYSALIDE_CONTAINER_PLUGIN("PyChrysalide", "Chrysalide bindings to Python",
                                   PACKAGE_VERSION, CHRYSALIDE_WEBSITE("api/python/pychrysalide"),
                                   NO_REQ, AL(PGA_PLUGIN_INIT, PGA_PLUGIN_EXIT,
                                              PGA_NATIVE_PLUGINS_LOADED, PGA_TYPE_BUILDING));


/* Note la nature du chargement */
static bool _standalone = true;

/* Réceptacle pour le chargement forcé */
static PyObject *_chrysalide_module = NULL;


/* Fournit la révision du programme global. */
static PyObject *py_chrysalide_revision(PyObject *, PyObject *);

/* Fournit la version du programme global. */
static PyObject *py_chrysalide_version(PyObject *, PyObject *);

/* Fournit la version du greffon pour Python. */
static PyObject *py_chrysalide_mod_version(PyObject *, PyObject *);

/* Détermine si l'interpréteur lancé est celui pris en compte. */
static bool is_current_abi_suitable(void);

/* Assure une pleine initialisation des objets de Python-GI. */
static bool install_metaclass_for_python_gobjects(void);

/* Définit la version attendue de GTK à charger dans Python. */
static bool set_version_for_gtk_namespace(const char *);

/* Point de sortie pour l'initialisation de Python. */
static void PyExit_pychrysalide(void);

/* Complète les chemins de recherches de Python. */
static void extend_python_path(const char *);

/* Charge autant de greffons composés en Python que possible. */
static void load_python_plugins(GPluginModule *);

/* Efface un type Python pour greffon de la mémoire. */
static void free_native_plugin_type(PyTypeObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit la révision du programme global.                     *
*                                                                             *
*  Retour      : Numéro de révision.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_chrysalide_revision(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */

#define PY_CHRYSALIDE_REVISION_METHOD PYTHON_METHOD_DEF                     \
(                                                                           \
     revision, "/",                                                         \
     METH_NOARGS, py_chrysalide,                                            \
     "Provide the revision number of Chrysalide.\n"                         \
     "\n"                                                                   \
     "The returned value is provided as a string, for instance: 'r1665'."   \
)

    result = PyUnicode_FromString("r" XSTR(REVISION));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit la version du programme global.                      *
*                                                                             *
*  Retour      : Numéro de version.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_chrysalide_version(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    int major;                              /* Numéro de version majeur    */
    int minor;                              /* Numéro de version mineur    */
    int revision;                           /* Numéro de révision          */
    char version[16];                       /* Conservation temporaire     */

#define PY_CHRYSALIDE_VERSION_METHOD PYTHON_METHOD_DEF                      \
(                                                                           \
     version, "/",                                                          \
     METH_NOARGS, py_chrysalide,                                            \
     "Provide the version number of Chrysalide.\n"                          \
     "\n"                                                                   \
     "The returned value is provided as a string, for instance: '1.6.65'."  \
)

    major = REVISION / 1000;
    minor = (REVISION - (major * 1000)) / 100;
    revision = REVISION % 100;

    snprintf(version, sizeof(version), "%d.%d.%d", major, minor, revision);

    result = PyUnicode_FromString(version);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit la version du greffon pour Python.                   *
*                                                                             *
*  Retour      : Numéro de version.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_chrysalide_mod_version(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    char version[16];                       /* Conservation temporaire     */

#define PY_CHRYSALIDE_MOD_VERSION_METHOD PYTHON_METHOD_DEF                  \
(                                                                           \
     mod_version, "/",                                                      \
     METH_NOARGS, py_chrysalide,                                            \
     "Provide the version number of Chrysalide module for Python.\n"        \
     "\n"                                                                   \
     "The returned value is provided as a string, for instance: '0.1.0'."   \
)

    snprintf(version, sizeof(version), "%s", _chrysalide_plugin.version);

    result = PyUnicode_FromString(version);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Détermine si l'interpréteur lancé est celui pris en compte.  *
*                                                                             *
*  Retour      : true si l'exécution peut se poursuivre, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_current_abi_suitable(void)
{
    bool result;
    int fds[2];
    int ret;
    char cmds[128];
    char content[64];
    ssize_t got;

#define GRAB_ABI_FLAGS_IN_PYTHON                        \
    "import sys" "\n"                                   \
    "import os" "\n"                                    \
    "data = bytes(sys.abiflags, 'UTF-8') + b'\\0'" "\n" \
    "os.write(%d, data)" "\n"

    result = false;

    ret = pipe(fds);
    if (ret == -1)
    {
        perror("pipe()");
        return false;
    }

    snprintf(cmds, sizeof(cmds), GRAB_ABI_FLAGS_IN_PYTHON, fds[1]);

    ret = PyRun_SimpleString(cmds);
    if (ret != 0) goto icas_exit;

    got = read(fds[0], content, sizeof(content));
    if (got < 0)
    {
        perror("read()");
        goto icas_exit;
    }

    content[got] = '\0';

    result = (strcmp(content, LIBPYTHON_ABI_FLAGS) == 0);

 icas_exit:

    if (!result)
        PyErr_SetString(PyExc_SystemError, "the ABI flags of the current interpreter do not match " \
                        "the ones of the Python library used during the module compilation.");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Assure une pleine initialisation des objets de Python-GI.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool install_metaclass_for_python_gobjects(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *gi_types_mod;                 /* Module Python-GObject       */

    /**
     * Les extensions Python sont chargées à partir de la fonction load_python_plugins(),
     * qui fait appel à create_python_plugin(). Une instance y est construite via un
     * appel à PyObject_CallFunction() avec la classe spécifiée par l'alias AutoLoad
     * dans le fichier __init__.py présent dans chaque module d'extension.
     *
     * Le constructeur py_plugin_module_new() renvoie in fine à la fonction générique
     * python_abstract_constructor_with_dynamic_gtype(), laquelle conduit à la fonction
     * pygobject_register_class() définie dans <python3-gi>/gi/pygobject-object.c.
     * Le code de cette dernière comprend notamment la portion suivante :
     *
     *    [...]
     *    Py_SET_TYPE(type, PyGObject_MetaType);
     *    [...]
     *    if (PyType_Ready(type) < 0) {
     *        g_warning ("couldn't make the type `%s' ready", type->tp_name);
     *        return;
     *    }
     *    [...]
     *
     * La fonction PyType_Ready() est définie dans <python3>/Objects/typeobject.c
     * et commence par :
     *
     *    int PyType_Ready(PyTypeObject *type)
     *    {
     *        if (type->tp_flags & Py_TPFLAGS_READY) {
     *            assert(_PyType_CheckConsistency(type));
     *            return 0;
     *        }
     *        [...]
     *    }
     *
     * La vérification de cohérencce commence par analyser le type et son propre
     * type :
     *
     *  - cf. _PyType_CheckConsistency() dans <python3>/Objects/typeobject.c :
     *
     *    int _PyType_CheckConsistency(PyTypeObject *type)
     *    {
     *        [...]
     *        CHECK(!_PyObject_IsFreed((PyObject *)type));
     *        [...]
     *    }
     *
     *  - cf. _PyObject_IsFreed() dans <python3>/Objects/object.c :
     *
     *    int _PyObject_IsFreed(PyObject *op)
     *    {
     *        if (_PyMem_IsPtrFreed(op) || _PyMem_IsPtrFreed(Py_TYPE(op))) {
     *            return 1;
     *    }
     *
     * La fonction _PyMem_IsPtrFreed() recherche entre autres la valeur NULL.
     *
     * Or le type du type est écrasé dans la fonction pygobject_register_class()
     * avec la valeur de la variable PyGObject_MetaType. Cette variable n'est
     * définie qu'à un seul endroit, dans <python3-gi>/gi/gimodule.c :
     *
     *    static PyObject *
     *    pyg__install_metaclass(PyObject *dummy, PyTypeObject *metaclass)
     *    {
     *        Py_INCREF(metaclass);
     *        PyGObject_MetaType = metaclass;
     *        Py_INCREF(metaclass);
     *
     *        Py_SET_TYPE(&PyGObject_Type, metaclass);
     *
     *        Py_INCREF(Py_None);
     *        return Py_None;
     *    }
     *
     * Afin de valider la vérification de _PyType_CheckConsistency() pour les
     * modules externes qui entraînent un enregistrement tout en portant le drapeau
     * Py_TPFLAGS_READY (typiquement ceux du répertoire "plugins/python/", il faut
     * initialiser au besoin la variable PyGObject_MetaType.
     *
     * Une ligne suffit donc à enregistrer le type intermédiaire :
     *
     *    from _gi import types
     *
     * On simule ici une déclaration similaire si nécessaire
     */

    result = false;

    if (PyType_CheckExact(&PyGObject_Type))
    {
        gi_types_mod = PyImport_ImportModule("gi.types");

        result = (PyErr_Occurred() == NULL);

        if (result)
            result = (PyType_CheckExact(&PyGObject_Type) == 0);

        Py_XDECREF(gi_types_mod);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : version = idenfiant de la version de GTK à stipuler.         *
*                                                                             *
*  Description : Définit la version attendue de GTK à charger dans Python.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool set_version_for_gtk_namespace(const char *version)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *gi_mod;                       /* Module Python-GObject       */
    PyObject *args;                         /* Arguments à fournir         */

    result = false;

    /**
     * On cherche ici à éviter le message suivant si on charge 'gi.repository.Gtk' directement :
     *
     *
     *   PyGIWarning: Gtk was imported without specifying a version first. \
     *   Use gi.require_version('Gtk', '3.0') before import to ensure that the right version gets loaded.
     *
     */

    gi_mod = PyImport_ImportModule("gi");

    if (gi_mod != NULL)
    {
        args = Py_BuildValue("ss", "Gtk", version);

        run_python_method(gi_mod, "require_version", args);

        result = (PyErr_Occurred() == NULL);

        Py_DECREF(args);
        Py_DECREF(gi_mod);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Point de sortie pour l'initialisation de Python.             *
*                                                                             *
*  Retour      : ?                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void PyExit_pychrysalide(void)
{
    assert(_standalone);

    extern void set_current_project(void *project);

    set_current_project(NULL);

#ifdef TRACK_GOBJECT_LEAKS
    remember_gtypes_for_leaks();
#endif

    exit_all_plugins();

    unload_all_core_components(true);

#ifdef TRACK_GOBJECT_LEAKS
    dump_remaining_gtypes();
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Point d'entrée pour l'initialisation de Python.              *
*                                                                             *
*  Retour      : ?                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

#define PYCHRYSALIDE_DOC                                                                                        \
    "PyChrysalide is a module containing Chrysalide's features and designed for Python users.\n"                \
    "\n"                                                                                                        \
    "The whole API is defined in a single library named 'pychrysalide.so' and can be used in two ways:\n"       \
    "* either from the Chrysalide's GUI, by registering hooks or GLib signals;\n"                               \
    "* or from a shell command line, by setting PYTHONPATH to point to the directory containing the library.\n" \
    "\n"                                                                                                        \
    "In both cases, this is a good start point to have a look at already existing plugins to quickly learn "    \
    "how the API works.\n"                                                                                      \
    "\n"                                                                                                        \
    "These plugins are located in the 'plugins/python' directory."

PyMODINIT_FUNC PyInit_pychrysalide(void)
{
    PyObject *result;                       /* Module Python à retourner   */
    bool status;                            /* Bilan des inclusions        */
    int ret;                                /* Bilan de préparatifs        */
#ifdef PYTHON_PACKAGE
    Dl_info info;                           /* Informations dynamiques     */
#endif
    GPluginModule *self;                    /* Représentation interne      */
    PluginStatusFlags self_flags;           /* Fanions à mettre à jour     */

    static PyMethodDef py_chrysalide_methods[] = {
        PY_CHRYSALIDE_REVISION_METHOD,
        PY_CHRYSALIDE_VERSION_METHOD,
        PY_CHRYSALIDE_MOD_VERSION_METHOD,
        { NULL }
    };

    static PyModuleDef py_chrysalide_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide",
        .m_doc = PYCHRYSALIDE_DOC,

        .m_size = -1,

        .m_methods = py_chrysalide_methods

    };

    /**
     * Vérification préalable : dans le cas où on est embarqué directement dans
     * un interpréteur Python, le module se charge et termine par charger à leur
     * tour les différentes extensions trouvées, via load_remaning_plugins() puis
     * chrysalide_plugin_on_native_loaded().
     *
     * Lesquelles vont très probablement charger le module pychrysalide.
     *
     * Comme le chargement de ce dernier n'est alors pas encore terminé,
     * Python va relancer cette procédure, et register_access_to_python_module()
     * va détecter un doublon.
     */

    result = get_access_to_python_module(py_chrysalide_module.m_name);

    if (result != NULL)
    {
        Py_INCREF(result);
        return result;
    }

    if (!is_current_abi_suitable())
        goto exit;

    if (pygobject_init(-1, -1, -1) == NULL)
    {
        PyErr_SetString(PyExc_SystemError, "unable to init GObject in Python.");
        goto exit;
    }

    if (!install_metaclass_for_python_gobjects())
        goto exit;

    if (!set_version_for_gtk_namespace("3.0"))
        goto exit;

    if (!load_all_core_components(true))
    {
        PyErr_SetString(PyExc_SystemError, "unable to load all basic components.");
        goto exit;
    }

    /* Mise en place des fonctionnalités offertes */

    result = PyModule_Create(&py_chrysalide_module);

    register_access_to_python_module(py_chrysalide_module.m_name, result);

    status = true;

    if (status) status = add_features_module(result);

    if (status) status = add_analysis_module(result);
    if (status) status = add_arch_module(result);
    if (status) status = add_common_module(result);
    if (status) status = add_core_module(result);
    if (status) status = add_debug_module(result);
    if (status) status = add_format_module(result);
    if (status) status = add_glibext_module(result);
#ifdef INCLUDE_GTK_SUPPORT
    if (status) status = add_gtkext_module(result);
    if (status) status = add_gui_module(result);
#endif
    if (status) status = add_mangling_module(result);
    if (status) status = add_plugins_module(result);

    if (status) status = ensure_python_string_enum_is_registered();
    if (status) status = ensure_python_py_struct_is_registered();

    if (status) status = populate_analysis_module();
    if (status) status = populate_arch_module();
    if (status) status = populate_common_module();
    if (status) status = populate_core_module();
    if (status) status = populate_debug_module();
    if (status) status = populate_format_module();
    if (status) status = populate_glibext_module();
#ifdef INCLUDE_GTK_SUPPORT
    if (status) status = populate_gtkext_module();
    if (status) status = populate_gui_module();
#endif
    if (status) status = populate_mangling_module();
    if (status) status = populate_plugins_module();

    if (!status)
    {
        PyErr_SetString(PyExc_SystemError, "failed to load all PyChrysalide components.");
        Py_DECREF(result);
        result = NULL;
        goto exit;
    }

    if (_standalone)
    {
        ret = Py_AtExit(PyExit_pychrysalide);

        if (ret == -1)
        {
            PyErr_SetString(PyExc_SystemError, "failed to register a cleanup function.");
            Py_DECREF(result);
            result = NULL;
            goto exit;
        }

        /**
         * Comme les sources locales sont prioritaires, le fichier "core/global.h"
         * du greffon masque la fonction suivante, issue du corps principal du
         * programme.
         *
         * On la déclare donc à la main.
         */
        extern void set_batch_mode(void);

        set_batch_mode();

        /**
         * Si cette extension pour Python est chargée depuis un dépôt Python,
         * elle ne se trouve pas dans le répertoire classique des extensions et
         * n'est donc pas chargée et enregistrée comme attendu.
         *
         * Cet enregistrement est donc forcé ici.
         */

#ifdef PYTHON_PACKAGE

        ret = dladdr(__FUNCTION__, &info);
        if (ret == 0)
        {
            LOG_ERROR_DL_N("dladdr");
            Py_DECREF(result);
            result = NULL;
            goto exit;
        }

        self = g_plugin_module_new(info.dli_fname);
        assert(self != NULL);

        register_plugin(self);

#endif

        init_all_plugins(false);

        lock_plugin_list_for_reading();

        self = get_plugin_by_name("PyChrysalide", NULL);
        assert(self != NULL);

        self_flags = g_plugin_module_get_flags(self);
        self_flags &= ~(PSF_FAILURE | PSF_LOADED);
        self_flags |= (status ? PSF_LOADED : PSF_FAILURE);

        g_plugin_module_override_flags(self, self_flags);

        unlock_plugin_list_for_reading();

        load_remaning_plugins();

        /**
         * On laisse fuir ici la référence sur self afin d'avoir
         * l'assurance que le greffon se déchargera toujours en dernier.
         *
         * La fuite mémoire est au final évitée dans PyExit_pychrysalide().
         */

    }

 exit:

    if (result == NULL && !_standalone)
        log_pychrysalide_exception("Loading failed");

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin supplémentaire pour l'espace de recherche.     *
*                                                                             *
*  Description : Complète les chemins de recherches de Python.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void extend_python_path(const char *path)
{
    PyObject *list;                         /* Liste de chemins à compléter*/
    PyObject *new;                          /* Nouveau chemin à intégrer   */

    list = PySys_GetObject("path");
    assert(list != NULL);

    new = PyUnicode_FromString(path);
    assert(new != NULL);

    PyList_Append(list, new);

    Py_DECREF(new);

    add_to_env_var("PYTHONPATH", path, ":");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = instance représentant le greffon Python d'origine.  *
*                                                                             *
*  Description : Charge autant de greffons composés en Python que possible.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void load_python_plugins(GPluginModule *plugin)
{
#ifdef DISCARD_LOCAL
    char *edir;                             /* Répertoire de base effectif */
#endif
    DIR *dir;                               /* Répertoire à parcourir      */
    char *paths;                            /* Emplacements de greffons    */
    char *save;                             /* Sauvegarde pour ré-entrance */
    char *path;                             /* Chemin à fouiller           */
    struct dirent *entry;                   /* Elément trouvé              */
    char *modname;                          /* Nom du module pour Python   */
    char *filename;                         /* Chemin d'accès reconstruit  */
    GPluginModule *pyplugin;                /* Lien vers un grffon Python  */
    bool status;                            /* Bilan d'une opération       */
    GGenConfig *config;                     /* Configuration à charger     */

    /* Définition des zones d'influence */

#ifndef DISCARD_LOCAL

    extend_python_path(PACKAGE_SOURCE_DIR G_DIR_SEPARATOR_S "plugins" G_DIR_SEPARATOR_S "python");

#else

    edir = get_effective_directory(PLUGINS_DATA_DIR G_DIR_SEPARATOR_S "python");
    dir = opendir(edir);
    free(edir);

    if (dir != NULL)
    {
         closedir(dir);

         edir = get_effective_directory(PLUGINS_DATA_DIR G_DIR_SEPARATOR_S "python");
         extend_python_path(edir);
         free(edir);

    }

#endif

    g_plugin_module_log_variadic_message(plugin, LMT_INFO,
                                         _("PYTHONPATH environment variable set to '%s'"),
                                         getenv("PYTHONPATH"));

    /* Chargements des extensions Python */

    paths = get_env_var("PYTHONPATH");

    save = NULL;   /* gcc... */

    for (path = strtok_r(paths, ":", &save);
         path != NULL; 
         path = strtok_r(NULL, ":", &save))
    {
        dir = opendir(path);
        if (dir == NULL)
        {
            perror("opendir");
            continue;
        }

        g_plugin_module_log_variadic_message(plugin, LMT_INFO, 
                                             _("Looking for Python plugins in '%s'..."),
                                             path);

        while (1)
        {
            errno = 0;

            entry = readdir(dir);

            if (entry == NULL)
            {
                if (errno != 0)
                    perror("readdir");

                break;

            }

            if (entry->d_type != DT_DIR) continue;
            if (entry->d_name[0] == '.') continue;

            modname = strdup(entry->d_name);
            modname = stradd(modname, ".");
            modname = stradd(modname, "__init__");

            filename = strdup(path);
            filename = stradd(filename, G_DIR_SEPARATOR_S);
            filename = stradd(filename, entry->d_name);

            pyplugin = create_python_plugin(modname, filename);

            if (pyplugin == NULL)
            {
                g_plugin_module_log_variadic_message(plugin, LMT_ERROR, 
                                                     _("No suitable Python plugin found in '%s'"),
                                                     filename);
                goto done_with_plugin;
            }

            g_plugin_module_create_config(pyplugin);

            status = g_plugin_module_manage(pyplugin, PGA_PLUGIN_LOADED);

            if (!status)
            {
                g_plugin_module_log_variadic_message(plugin, LMT_ERROR,
                                                     _("Plugin '%s' failed to complete loading..."), filename);
                g_object_unref(G_OBJECT(pyplugin));
                goto done_with_plugin;
            }

            config = g_plugin_module_get_config(pyplugin);
            g_generic_config_read(config);
            g_object_unref(G_OBJECT(config));

            g_plugin_module_log_variadic_message(plugin, LMT_PROCESS,
                                                 _("Loaded the Python plugin found in the '<b>%s</b>' directory"),
                                                 filename);

            _register_plugin(pyplugin);

 done_with_plugin:

            free(filename);
            free(modname);

        }

         closedir(dir);

    }

    free(paths);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du chargement du greffon.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_init(GPluginModule *plugin)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    int ret;                                /* Bilan de préparatifs        */

    _standalone = false;

    /* Chargement du module pour Python */

    ret = PyImport_AppendInittab("pychrysalide", &PyInit_pychrysalide);

    if (ret == -1)
    {
        log_plugin_simple_message(LMT_ERROR, _("Can not extend the existing table of Python built-in modules."));
        result = false;
        goto cpi_done;
    }

    Py_Initialize();

    gstate = PyGILState_Ensure();

    PySys_SetArgv(0, (wchar_t *[]) { NULL });

    _chrysalide_module = PyImport_ImportModule("pychrysalide");

    /**
     * Pour mémoire, une situation concrête conduisant à un échec :
     * le paquet python3-gi-dbg n'est pas installé alors que le
     * programme est compilé en mode débogage.
     *
     * Dans ce cas, pygobject_init(-1, -1, -1) échoue, et Py_Initialize()
     * le laisse rien filtrer...
     *
     * En mode autonome, le shell Python remonte bien l'erreur par contre.
     */

    result = (_chrysalide_module != NULL);

    PyGILState_Release(gstate);

 cpi_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du déchargement du greffon.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT void chrysalide_plugin_exit(GPluginModule *plugin)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */

    gstate = PyGILState_Ensure();

    clear_all_accesses_to_python_modules();

    Py_XDECREF(_chrysalide_module);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = informations à libérer de la mémoire.                 *
*                                                                             *
*  Description : Efface un type Python pour greffon de la mémoire.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void free_native_plugin_type(PyTypeObject *type)
{
    free((char *)type->tp_name);
    free((char *)type->tp_doc);

    free(type);

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

G_MODULE_EXPORT void chrysalide_plugin_on_plugins_loaded(GPluginModule *plugin, PluginAction action)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    size_t count;                           /* Quantité de greffons chargés*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */
    GPluginModule **list;                   /* Ensemble de ces greffons    */
    size_t i;                               /* Boucle de parcours          */
    char *name;                             /* Désignation complète        */
    char *doc;                              /* Description adaptée         */
    int ret;                                /* Bilan d'un appel            */
    PyTypeObject *type;                     /* Nouveau type dynamique      */

    gstate = PyGILState_Ensure();

    if (action == PGA_NATIVE_PLUGINS_LOADED)
    {
        /* Intégration des greffons natifs en Python */

        if (ensure_python_plugin_module_is_registered())
        {
            module = get_access_to_python_module("pychrysalide.plugins");
            assert(module != NULL);

            dict = PyModule_GetDict(module);

            list = get_all_plugins(&count);

            for (i = 0; i < count; i++)
            {
                ret = asprintf(&name, "pychrysalide.plugins.%s", G_OBJECT_TYPE_NAME(list[i]) + 1);
                if (ret == -1)
                {
                    LOG_ERROR_N("asprintf");
                    continue;
                }

                ret = asprintf(&doc, "Place holder for the native plugin %s documentation",
                               G_OBJECT_TYPE_NAME(list[i]) + 1);
                if (ret == -1)
                {
                    LOG_ERROR_N("asprintf");
                    free(name);
                    continue;
                }

                type = calloc(1, sizeof(PyTypeObject));

                type->tp_name = name;
                type->tp_doc = doc;
                type->tp_flags = Py_TPFLAGS_DEFAULT;
                type->tp_new = no_python_constructor_allowed;

                if (register_class_for_pygobject(dict, G_OBJECT_TYPE(list[i]), type))
                    g_object_set_data_full(G_OBJECT(list[i]), "python_type", type,
                                           (GDestroyNotify)free_native_plugin_type);

                else
                    free_native_plugin_type(type);

            }

            if (list != NULL)
                free(list);

        }

        /* Chargement des extensions purement Python */

        load_python_plugins(plugin);

    }

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                type   = type d'objet à mettre en place.                     *
*                                                                             *
*  Description : Crée une instance à partir d'un type dynamique externe.      *
*                                                                             *
*  Retour      : Instance d'objet gérée par l'extension ou NULL.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT gpointer chrysalide_plugin_build_type_instance(GPluginModule *plugin, PluginAction action, GType type)
{
    gpointer result;                        /* Instance à retourner        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *instance;                     /* Initialisation forcée       */

    result = NULL;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(type);

    if (pytype != NULL)
    {
        instance = PyObject_CallObject((PyObject *)pytype, NULL);
        assert(instance != NULL);

        result = pygobject_get(instance);

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : prefix = message d'introduction à faire apparaître à l'écran.*
*                                                                             *
*  Description : Présente dans le journal une exception survenue.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void log_pychrysalide_exception(const char *prefix, ...)
{
    va_list ap;                             /* Compléments argumentaires   */
    char *msg;                              /* Message complet à imprimer  */
    PyObject *err_type;                     /* Type d'erreur Python        */
    PyObject *err_value;                    /* Instance Python d'erreur    */
    PyObject *err_traceback;                /* Trace Python associée       */
    PyObject *err_string;                   /* Description Python d'erreur */
    const char *err_msg;                    /* Représentation humaine      */

    assert(PyGILState_Check() == 1);

    if (PyErr_Occurred())
    {
        /* Base de la communication */

        va_start(ap, prefix);

        vasprintf(&msg, prefix, ap);

        va_end(ap);

        /* Détails complémentaires */

        PyErr_Fetch(&err_type, &err_value, &err_traceback);

        PyErr_NormalizeException(&err_type, &err_value, &err_traceback);

        if (err_traceback == NULL)
        {
            err_traceback = Py_None;
            Py_INCREF(err_traceback);
        }

        PyException_SetTraceback(err_value, err_traceback);

        if (err_value == NULL)
            msg = stradd(msg, _(": no extra information is provided..."));

        else
        {
            err_string = PyObject_Str(err_value);
            err_msg = PyUnicode_AsUTF8(err_string);

            msg = stradd(msg, ": ");
            msg = stradd(msg, err_msg);

            Py_DECREF(err_string);

        }

        /**
         * Bien que la documentation précise que la fonction PyErr_Fetch()
         * transfère la propritété des éléments retournés, la pratique
         * montre que le programme plante à la terminaison en cas d'exception.
         *
         * C'est par exemple le cas quand un greffon Python ne peut se lancer
         * correctement ; l'exception est alors levée à partir de la fonction
         * create_python_plugin() et le plantage intervient en sortie d'exécution,
         * au moment de la libération de l'extension Python :
         *
         *    ==14939== Jump to the invalid address stated on the next line
         *    ==14939==    at 0x1A8FCBC9: ???
         *    ==14939==    by 0x53DCDB2: g_object_unref (in /usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0.5800.3)
         *    ==14939==    by 0x610F834: on_plugin_ref_toggle (pglist.c:370)
         *    ==14939==    by 0x610F31A: exit_all_plugins (pglist.c:153)
         *    ==14939==    by 0x10AD19: main (main.c:440)
         *    ==14939==  Address 0x1a8fcbc9 is not stack'd, malloc'd or (recently) free'd
         *
         * Curieusement, un appel à PyErr_PrintEx(1) corrige l'effet, alors qu'un
         * appel à PyErr_PrintEx(0) ne change rien.
         *
         * La seule différence de l'instruction set_sys_last_vars réside en quelques
         * lignes dans le code de l'interpréteur Python :
         *
         *    if (set_sys_last_vars) {
         *        _PySys_SetObjectId(&PyId_last_type, exception);
         *        _PySys_SetObjectId(&PyId_last_value, v);
         *        _PySys_SetObjectId(&PyId_last_traceback, tb);
         *    }
         *
         * L'explication n'est pas encore déterminé : bogue dans Chrysalide ou dans Python ?
         * L'ajout des éléments dans le dictionnaire du module sys ajoute une référence
         * à ces éléments.
         *
         * On reproduit ici le comportement du code correcteur avec PySys_SetObject().
         */

        PySys_SetObject("last_type", err_type);
        PySys_SetObject("last_value", err_value);
        PySys_SetObject("last_traceback", err_traceback);

        Py_XDECREF(err_traceback);
        Py_XDECREF(err_value);
        Py_XDECREF(err_type);

        log_plugin_simple_message(LMT_ERROR, msg);

        free(msg);

    }

}
