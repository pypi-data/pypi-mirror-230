
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pglist.c - gestion de l'ensemble des greffons
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#include "pglist.h"


#include <assert.h>
#include <dirent.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include "plugin-int.h"
#include "../common/extstr.h"
#include "../core/logs.h"
#include "../core/paths.h"



/* Liste de l'ensemble des greffons */
static GPluginModule **_pg_list = NULL;
static size_t _pg_count = 0;

/* Accès à cette liste */
static GRWLock _pg_lock;


/* Filtre les répertoire et les modules de greffons pootentels. */
static int filter_dirs_or_mods(const struct dirent *);

/* Part à la recherche de greffons sous forme de modules. */
static void browse_directory_for_plugins(const char *);

/* Suit les variations du compteur de références d'un greffon. */
static void on_plugin_ref_toggle(gpointer, GPluginModule *, gboolean);



/******************************************************************************
*                                                                             *
*  Paramètres  : load = procéde à un chargement dans la foulée ?              *
*                                                                             *
*  Description : Procède au chargement des différents greffons trouvés.       *
*                                                                             *
*  Retour      : Toujours true (même s'il y a des erreurs de chargement).     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_all_plugins(bool load)
{
    char *edir;                             /* Répertoire de base effectif */
    char *env;                              /* Contenu environnemental     */
    char *saveptr;                          /* Sauvegarde pour parcours    */
    char *udir;                             /* Répertoire supplémentaire ? */

    g_rw_lock_init(&_pg_lock);

    edir = get_effective_directory_new(TDT_PLUGINS_LIB);
    browse_directory_for_plugins(edir);
    free(edir);

    env = getenv("CHRYSALIDE_PLUGINS_PATH");

    if (env != NULL)
    {
        env = strdup(env);

        for (udir = strtok_r(env, ":", &saveptr); udir != NULL; udir = strtok_r(NULL, ":", &saveptr))
            browse_directory_for_plugins(udir);

        free(env);

    }

    if (load)
        load_remaning_plugins();

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Procède au déchargement des différents greffons présents.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_all_plugins(void)
{
    size_t i;                               /* Boucle de parcours          */
    const plugin_interface *pg_iface;       /* Définition du greffon       */

    lock_plugin_list_for_reading();

    if (_pg_list != NULL)
    {
        for (i = 0; i < _pg_count; i++)
        {
            assert(_pg_list[i] != NULL);

            /**
             * Si le greffon a conduit à la mise en place d'autres greffons, le
             * système de dépendances ne suffit pas pour le décompte des références :
             * le greffon voit à un instant T son compteur décroître ici ; à un
             * instant T+1, un greffon fils décrémente à son tour le compteur vers
             * le greffon principal.
             *
             * Le compteur du conteneur tombe alors à 0, et le code correspondant
             * est retiré. Lorsque que le flot d'exécution revient à la procédure
             * de sortie du second greffon, son code n'est plus en mémoire.
             *
             * On s'assure donc que les greffons qui génèrent d'autres greffons
             * sont bien traités en dernier.
             */

            pg_iface = g_plugin_module_get_interface(_pg_list[i]);

            if (pg_iface != NULL && pg_iface->container)
                g_object_ref(_pg_list[i]);

            g_object_unref(_pg_list[i]);

        }

        for (i = 0; i < _pg_count; i++)
        {
            if (_pg_list[i] == NULL)
                continue;

            pg_iface = g_plugin_module_get_interface(_pg_list[i]);

            if (pg_iface == NULL || !pg_iface->container)
                continue;

            g_object_unref(_pg_list[i]);

        }

        free(_pg_list);

    }

    unlock_plugin_list_for_reading();

    g_rw_lock_clear(&_pg_lock);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lock = type d'action à mener.                                *
*                                                                             *
*  Description : Verrouille ou déverrouille l'accès en lecture à la liste.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _lock_unlock_plugin_list_for_reading(bool lock)
{
    if (lock)
        g_rw_lock_reader_lock(&_pg_lock);
    else
        g_rw_lock_reader_unlock(&_pg_lock);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry = entrée de répertoire à analyser.                     *
*                                                                             *
*  Description : Filtre les répertoire et les modules de greffons pootentels. *
*                                                                             *
*  Retour      : Valeur non nulle pour garder l'élément.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int filter_dirs_or_mods(const struct dirent *entry)
{
    int result;                             /* Conclusion à remonter       */

    if (entry->d_type == DT_DIR)
        result = strcmp(entry->d_name, ".") * strcmp(entry->d_name, "..");

    else
        result = (strrcmp(entry->d_name, "." G_MODULE_SUFFIX) == 0 ? 1 : 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dir = répertoire à parcourir en quête de greffons (sans /).  *
*                                                                             *
*  Description : Part à la recherche de greffons sous forme de modules.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void browse_directory_for_plugins(const char *dir)
{
    struct dirent **namelist;               /* Eléments trouvés            */
    int ret;                                /* Bilan du parcours           */
    char *filename;                         /* Elément à ausculter         */
    GPluginModule *plugin;                  /* Greffon à intégrer ou pas   */

    ret = scandir(dir, &namelist, filter_dirs_or_mods, alphasort);
    if (ret < 0)
    {
        LOG_ERROR_N("scandir");
        return;
    }

    while (ret--)
    {
        filename = (char *)calloc(strlen(dir) + 1 + strlen(namelist[ret]->d_name) + 1, sizeof(char));

        strcpy(filename, dir);
        strcat(filename, G_DIR_SEPARATOR_S);
        strcat(filename, namelist[ret]->d_name);

        if (namelist[ret]->d_type == DT_DIR)
            browse_directory_for_plugins(filename);

        else
        {
            plugin = g_plugin_module_new(filename);

            if (plugin != NULL)
                register_plugin(plugin);

        }

        free(filename);
        free(namelist[ret]);

    }

    free(namelist);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à ajouter aux autres disponibles.           *
*                                                                             *
*  Description : Ajoute un greffon à la liste principale de greffons.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _register_plugin(GPluginModule *plugin)
{
    size_t i;                               /* Boucle de parcours          */
    const plugin_interface *pg_iface;       /* Informations à consulter    */
    const char *name;                       /* Désignation du greffon      */

    /**
     * L'appel sans verrou n'est fourni que pour les greffons
     * mettant en place des greffons en interne !
     */

    /* Recherche d'un éventuel doublon */

    pg_iface = g_plugin_module_get_interface(plugin);

    name = pg_iface->name;

    for (i = 0; i < _pg_count; i++)
    {
        pg_iface = g_plugin_module_get_interface(_pg_list[i]);

        if (strcmp(name, pg_iface->name) == 0)
        {
            log_variadic_message(LMT_ERROR,
                                 _("Plugin '%s' already registered!"), name);

            break;

        }

    }

    /* Ajout du greffon à la liste */

    if (i == _pg_count)
    {
        _pg_list = (GPluginModule **)realloc(_pg_list, ++_pg_count * sizeof(GPluginModule));

        _pg_list[_pg_count - 1] = plugin;

        g_object_add_toggle_ref(G_OBJECT(plugin), (GToggleNotify)on_plugin_ref_toggle, NULL);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : unused = adresse non utilisée ici.                           *
*                plugin = greffon àà venir effacer de la liste au besoin.     *
*                last   = indication sur la valeur du compteur de références. *
*                                                                             *
*  Description : Suit les variations du compteur de références d'un greffon.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_plugin_ref_toggle(gpointer unused, GPluginModule *plugin, gboolean last)
{
    const plugin_interface *pg_iface;       /* Vitrine d'un greffon        */
    size_t index;                           /* Indice du greffon           */
    GPluginModule *same;                    /* Juste pour la récupération  */

    if (last)
    {
        assert(g_rw_lock_writer_trylock(&_pg_lock) == FALSE);

        pg_iface = g_plugin_module_get_interface(plugin);

        same = get_plugin_by_name(pg_iface->name, &index);
        assert(same != NULL);

        _pg_list[index] = NULL;

        g_object_remove_toggle_ref(G_OBJECT(plugin), (GToggleNotify)on_plugin_ref_toggle, NULL);

        g_object_unref(G_OBJECT(same));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à ajouter aux autres disponibles.           *
*                                                                             *
*  Description : Ajoute un greffon à la liste principale de greffons.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_plugin(GPluginModule *plugin)
{
    g_rw_lock_writer_lock(&_pg_lock);

    _register_plugin(plugin);

    g_rw_lock_writer_unlock(&_pg_lock);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Charge tous les greffons restant à charger.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_remaning_plugins(void)
{
    bool changed;                           /* Variation de dépendances    */
    size_t i;                               /* Boucle de parcours          */
    PluginStatusFlags flags;                /* Fanions de greffon          */

    g_rw_lock_reader_lock(&_pg_lock);

    /* Etablit la liste de toutes les dépendances */

    do
    {
        changed = false;

        for (i = 0; i < _pg_count; i++)
            changed |= g_plugin_module_resolve_dependencies(_pg_list[i], _pg_list, _pg_count);

    }
    while (changed);

    for (i = 0; i < _pg_count; i++)
    {
        flags = g_plugin_module_get_flags(_pg_list[i]);

        if (flags & PSF_UNKNOW_DEP)
            log_variadic_message(LMT_ERROR,
                                 _("There is (at least) one unknown dependency in the plugin '%s'"),
                                 g_plugin_module_get_filename(_pg_list[i]));

        else if (flags & PSF_DEP_LOOP)
            log_variadic_message(LMT_ERROR,
                                 _("There is a dependency loop in the plugin '%s'"),
                                 g_plugin_module_get_filename(_pg_list[i]));

    }

    /* Effectue les chargements possibles */

    for (i = 0; i < _pg_count; i++)
    {
        flags = g_plugin_module_get_flags(_pg_list[i]);

        if ((flags & (BROKEN_PLUGIN_STATUS | PSF_LOADED)) == 0)
            g_plugin_module_load(_pg_list[i], _pg_list, _pg_count);

    }

    /* Supprime les greffons non chargés */

    for (i = 0; i < _pg_count; i++)
    {
        flags = g_plugin_module_get_flags(_pg_list[i]);

        if ((flags & PSF_LOADED) == 0)
        {
            g_object_unref(G_OBJECT(_pg_list[i]));

            memmove(&_pg_list[i], &_pg_list[i + 1], (_pg_count - i - 1) * sizeof(GPluginModule *));
            _pg_count--;

        }

    }

    g_rw_lock_reader_unlock(&_pg_lock);

    notify_native_plugins_loaded();

    notify_all_plugins_loaded();

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name  = désignation du greffon recherché.                    *
*                index = indice du greffon trouvé. [OUT]                      *
*                                                                             *
*  Description : Fournit le greffon répondant à un nom donné.                 *
*                                                                             *
*  Retour      : Instance du greffon trouvé ou NULL si aucun.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPluginModule *get_plugin_by_name(const char *name, size_t *index)
{
    GPluginModule *result;                  /* Greffon trouvé à renvoyer   */
    size_t i;                               /* Boucle de parcours          */
    const plugin_interface *pg_iface;       /* Vitrine d'un greffon        */

    result = NULL;

    /**
     * L'accès à la liste doit être encadré.
     */
    assert(g_rw_lock_writer_trylock(&_pg_lock) == FALSE);

    for (i = 0; i < _pg_count && result == NULL; i++)
    {
        /* Si on est en train de procéder à un nettoyage... */
        if (_pg_list[i] == NULL) continue;

        pg_iface = g_plugin_module_get_interface(_pg_list[i]);

        if (strcmp(pg_iface->name, name) == 0)
        {
            result = _pg_list[i];

            if (index != NULL)
                *index = i;

        }

    }

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : count = nombre de greffons trouvés. [OUT]                    *
*                                                                             *
*  Description : Fournit la liste de l'ensemble des greffons.                 *
*                                                                             *
*  Retour      : Liste de tous les greffons chargés.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPluginModule **get_all_plugins(size_t *count)
{
    GPluginModule **result;                 /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours          */

    g_rw_lock_reader_lock(&_pg_lock);

    result = malloc(_pg_count * sizeof(GPluginModule *));
    *count = _pg_count;

    for (i = 0; i < _pg_count; i++)
    {
        result[i] = _pg_list[i];
        g_object_ref(G_OBJECT(_pg_list[i]));
    }

    g_rw_lock_reader_unlock(&_pg_lock);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : action = fonctionnalité recherchée.                          *
*                count  = nombre de greffons trouvés. [OUT]                   *
*                                                                             *
*  Description : Fournit les greffons offrant le service demandé.             *
*                                                                             *
*  Retour      : Liste de greffons correspondants issue d'un tri interne.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPluginModule **get_all_plugins_for_action(PluginAction action, size_t *count)
{
    GPluginModule **result;                 /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    const plugin_interface *pg_iface;       /* Informations à consulter    */
    size_t j;                               /* Boucle de parcours #2       */

    result = NULL;
    *count = 0;

    g_rw_lock_reader_lock(&_pg_lock);

    for (i = 0; i < _pg_count; i++)
    {
        pg_iface = g_plugin_module_get_interface(_pg_list[i]);

        for (j = 0; j < pg_iface->actions_count; j++)
        {
            if (pg_iface->actions[j] == action)
            {
                result = realloc(result, ++(*count) * sizeof(GPluginModule *));

                result[*count - 1] = _pg_list[i];
                g_object_ref(G_OBJECT(_pg_list[i]));

                break;

            }

        }

    }

    g_rw_lock_reader_unlock(&_pg_lock);

    return result;

}
