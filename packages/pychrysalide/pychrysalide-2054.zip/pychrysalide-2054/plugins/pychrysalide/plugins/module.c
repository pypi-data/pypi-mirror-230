
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire plugins en tant que module
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "module.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <plugins/pglist.h>


#include "constants.h"
#include "plugin.h"
#include "../helpers.h"



/* Fournit le greffon répondant à un nom donné. */
static PyObject *py_plugins_get_plugin_by_name(PyObject *, PyObject *);

/* Fournit la liste de l'ensemble des greffons. */
static PyObject *py_plugins_get_all_plugins(PyObject *, PyObject *);

/* Fournit les greffons offrant le service demandé. */
static PyObject *py_plugins_get_all_plugins_for_action(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = désignation du greffon recherché.                     *
*                                                                             *
*  Description : Fournit le greffon répondant à un nom donné.                 *
*                                                                             *
*  Retour      : Instance du greffon trouvé avec son indice, ou None si aucun.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugins_get_plugin_by_name(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    const char *name;                       /* Désignation de greffon      */
    int ret;                                /* Bilan de lecture des args.  */
    size_t index;                           /* Indice de la trouvaille     */
    GPluginModule *plugin;                  /* Greffon retrouvé ou NULL    */

#define PY_PLUGINS_GET_PLUGIN_BY_NAME_METHOD PYTHON_METHOD_DEF  \
(                                                               \
     get_plugin_by_name, "name",                                \
     METH_VARARGS, py_plugins,                                  \
     "Find a given plugin from the list of loaded plugins.\n"   \
     "\n"                                                       \
     "The *name* string define the target to find.\n"           \
     "\n"                                                       \
     "The returned value is a tuple of the found"               \
     " pychrysalide.plugins.PluginModule instance and its"      \
     " value, or None in case of search failure."               \
)

    ret = PyArg_ParseTuple(args, "s", &name);
    if (!ret) return NULL;

    lock_plugin_list_for_reading();

    plugin = get_plugin_by_name(name, &index);

    unlock_plugin_list_for_reading();

    if (plugin != NULL)
    {
        result = PyTuple_New(2);

        PyTuple_SetItem(result, 0, pygobject_new(G_OBJECT(plugin)));
        PyTuple_SetItem(result, 1, PyLong_FromSize_t(index));

        g_object_unref(G_OBJECT(plugin));

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
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit la liste de l'ensemble des greffons.                 *
*                                                                             *
*  Retour      : Liste de tous les greffons chargés.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugins_get_all_plugins(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    size_t count;                           /* Taille de la liste finale   */
    GPluginModule **plugins;                /* Liste de greffons chargés   */
    size_t i;                               /* Boucle de parcours          */

#define PY_PLUGINS_GET_ALL_PLUGINS_METHOD PYTHON_METHOD_DEF     \
(                                                               \
     get_all_plugins, "/",                                      \
     METH_NOARGS, py_plugins,                                   \
     "Provide the list of all loaded plugins.\n"                \
     "\n"                                                       \
     "The returned value is a tuple of"                         \
     " pychrysalide.plugins.PluginModule instances."            \
)

    plugins = get_all_plugins(&count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(plugins[i])));
        g_object_unref(G_OBJECT(plugins[i]));
    }

    if (plugins != NULL)
        free(plugins);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = fonctionnalité recherchée.                            *
*                                                                             *
*  Description : Fournit les greffons offrant le service demandé.             *
*                                                                             *
*  Retour      : Liste de greffons correspondants issue d'un tri interne.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_plugins_get_all_plugins_for_action(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    PluginAction action;                    /* Fonctionnalité recherchée   */
    int ret;                                /* Bilan de lecture des args.  */

    size_t count;                           /* Taille de la liste finale   */
    GPluginModule **plugins;                /* Liste de greffons chargés   */
    size_t i;                               /* Boucle de parcours          */

#define PY_PLUGINS_GET_ALL_PLUGINS_FOR_ACTION_METHOD PYTHON_METHOD_DEF  \
(                                                                       \
     get_all_plugins_for_action, "action",                              \
     METH_VARARGS, py_plugins,                                          \
     "Provide the list of all loaded plugins suitable for a given"      \
     " action.\n"                                                       \
     "\n"                                                               \
     "The *action* has to be one of the"                                \
     " pychrysalide.plugins.PluginModule.PluginAction values.\n"        \
     "\n"                                                               \
     "The returned value is a tuple of"                                 \
     " matching pychrysalide.plugins.PluginModule instances."           \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_plugin_action, &action);
    if (!ret) return NULL;

    plugins = get_all_plugins_for_action(action, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(plugins[i])));
        g_object_unref(G_OBJECT(plugins[i]));
    }

    if (plugins != NULL)
        free(plugins);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'plugins' à un module Python.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_plugins_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_PLUGINS_DOC                                            \
    "This module provides features to deal with plugins: the definitions"   \
    " required to build new Python plugins as well as the functions"        \
    " suitable to interact with existing plugins.\n"                        \
    "\n"                                                                    \
    "The module is also the place for all plugins without another home."

    static PyMethodDef py_plugins_methods[] = {
        PY_PLUGINS_GET_PLUGIN_BY_NAME_METHOD,
        PY_PLUGINS_GET_ALL_PLUGINS_METHOD,
        PY_PLUGINS_GET_ALL_PLUGINS_FOR_ACTION_METHOD,
        { NULL }
    };

    static PyModuleDef py_chrysalide_plugins_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.plugins",
        .m_doc = PYCHRYSALIDE_PLUGINS_DOC,

        .m_size = -1,

        .m_methods = py_plugins_methods

    };

    module = build_python_module(super, &py_chrysalide_plugins_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'plugins'.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_plugins_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_plugin_module_is_registered();

    assert(result);

    return result;

}
