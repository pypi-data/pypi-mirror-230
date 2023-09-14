
/* Chrysalide - Outil d'analyse de fichiers binaires
 * theme.c - prototypes pour l'ajout d'extensions au thème GTK
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "theme.h"


#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>


#include <config.h>
#include <i18n.h>


#include "../theme.h"
#include "../../common/extstr.h"
#include "../../common/xdg.h"
#include "../../core/logs.h"
#include "../../core/paths.h"



/* Parcourt un répertoire donné à la recherche de thèmes. */
static void look_for_editor_themes(const char *);


/* Liste de thèmes utilisables */
static GEditorTheme **_themes = NULL;
static size_t _theme_count = 0;



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Parcourt tous les répertoires connus pour trouver un thème.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_all_themes(void)
{
    char *suffix;                           /* Fin du répertoire personnel */
    char *owndir;                           /* Thèmes personnels ?         */
#ifdef DISCARD_LOCAL
    char *edir;                             /* Répertoire de base effectif */
#endif

    /* Répertoire de l'utilisateur en premier ! */

    suffix = strdup("chrysalide");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, "themes");

    owndir = get_xdg_config_dir(suffix);

    free(suffix);

    if (owndir != NULL)
    {
        look_for_editor_themes(owndir);
        free(owndir);
    }

    /* Parcours des autres répertoires classiques au besoin */

#ifndef DISCARD_LOCAL
    look_for_editor_themes(PACKAGE_SOURCE_DIR G_DIR_SEPARATOR_S "themes");
#else

    edir = get_effective_directory(THEMES_DIR);
    look_for_editor_themes(edir);
    free(edir);

#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dirname = chemin du répertoire où effectuer des recherches.  *
*                                                                             *
*  Description : Parcourt un répertoire donné à la recherche de thèmes.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void look_for_editor_themes(const char *dirname)
{
    int dirfd;                              /* Canal de lecture            */
    struct dirent **namelist;               /* Liste des trouvailles       */
    int count;                              /* Nombre de fichiers trouvés  */
    int i;                                  /* Boucle de parcours          */
    struct dirent *entry;                   /* Raccourci d'usage           */
    int ret;                                /* Bilan d'un appel            */
    char *filename;                         /* Chemin d'accès constitué    */
    GEditorTheme *theme;                    /* Nouveau thème valide        */

    dirfd = open(dirname, O_RDONLY | O_DIRECTORY);
    if (dirfd == -1) goto not_found;

    count = scandirat(dirfd, ".", &namelist, NULL, alphasort);

    for (i = 0; i < count; i++)
    {
        entry = namelist[i];

        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
            continue;

        ret = asprintf(&filename, "%s%s%s", dirname, G_DIR_SEPARATOR_S, entry->d_name);
        if (ret == -1) continue;

        if (entry->d_type == DT_DIR)
            look_for_editor_themes(filename);

        else if (entry->d_type == DT_REG)
        {
            theme = g_editor_theme_new(filename, true);

            if (theme != NULL)
            {
                _themes = realloc(_themes, ++_theme_count * sizeof(GEditorTheme *));
                _themes[_theme_count - 1] = theme;
            }

        }

        free(filename);

    }

    if (count > 0)
        free(namelist);

    close(dirfd);

 not_found:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge tous les thèmes référencés en mémoire.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_all_themes(void)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < _theme_count; i++)
        g_object_unref(G_OBJECT(_themes[i]));

    if (_themes != NULL)
        free(_themes);

    _theme_count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation du thème GTK à charger.                   *
*                                                                             *
*  Description : Charge le thème GTK pour les composants spécifiques.         *
*                                                                             *
*  Retour      : true ou false selon le bilan de l'opération.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool apply_gtk_theme(const char *name)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t i;                               /* Boucle de parcours          */
    GdkScreen *screen;                      /* Ecran(s) concerné(s)        */
    GtkSettings *settings;                  /* Propriétés du système       */
    gboolean dark;                          /* Envie d'un thème sombre ?   */

    result = false;

    for (i = 0; i < _theme_count; i++)
        if (strcmp(name, g_editor_theme_get_name(_themes[i])) == 0)
        {
            result = true;
            break;
        }

    if (!result)
        log_variadic_message(LMT_ERROR, _("Theme '%s' not found!"), name);

    else
    {
        screen = gdk_screen_get_default();

        settings = gtk_settings_get_for_screen(screen);

        g_object_get(settings, "gtk-application-prefer-dark-theme", &dark, NULL);

        g_editor_theme_load(_themes[i], screen, dark);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : screen = écran visé par le chargement d'un thème.            *
*                path   = chemin vers la nouvelle définition à ajouter.       *
*                dark   = indique une préférence pour la variante foncée.     *
*                                                                             *
*  Description : Ajoute les définitions CSS à partir d'un chemin donné.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkCssProvider *load_css_content(GdkScreen *screen, const char *path)
{
    GtkCssProvider *result;                 /* Fournisseur à renvoyer      */
    GFile *file;                            /* Fichier à charger           */
    GError *error;                          /* Relevé d'éventuelles erreurs*/

    /**
     * Comme GTK exporte les images sous forme de données encodées en base 64
     * (cf. gtk_css_image_surface_print()) et ne sait pas recharger ensuite
     * ces mêmes données (cf. gtk_css_image_url_load_image()), on ne peut pas
     * collecter les images des ressources via gtk_css_provider_to_string()
     * pour constituer un contenu CSS global...
     *
     * On intègre ainsi les contenus CSS un par un, sans pouvoir déterminer
     * si l'ensemble est complètement intégré sans erreur.
     *
     * Ce constat est valable pour la version 3.22.11-1 de Debian, au moins.
     */

    result = gtk_css_provider_new();

    error = NULL;

    assert(strstr(path, "://") != NULL);

    file = g_file_new_for_uri(path);

    gtk_css_provider_load_from_file(result, file, &error);

    g_object_unref(G_OBJECT(file));

    if (error == NULL)
    {
        log_variadic_message(LMT_INFO, _("Loaded CSS definitions from '%s'"), path);

        gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(result),
                                                  GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);

    }
    else
    {
        log_variadic_message(LMT_ERROR, _("Failed to load CSS definitions from '%s'"), path);
        g_error_free(error);

        g_object_unref(G_OBJECT(result));

    }

    return result;

}
