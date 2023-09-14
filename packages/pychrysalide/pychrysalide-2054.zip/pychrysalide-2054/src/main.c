
/* Chrysalide - Outil d'analyse de fichiers binaires
 * main.c - fichier d'entrée du programme
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


#include <getopt.h>
#include <libgen.h>
#include <limits.h>
#include <locale.h>
#include <malloc.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include <i18n.h>


#include "gleak.h"
#include "analysis/binary.h"
#include "analysis/loading.h"
#include "analysis/contents/file.h"
#include "analysis/db/auth.h"
#include "core/core.h"
#include "core/global.h"
#include "core/logs.h"
#include "core/params.h"
#include "core/paths.h"
#include "core/queue.h"
#include "glibext/delayed.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "gui/editor.h"
#   include "gui/core/core.h"
#   include "gui/core/global.h"
#endif
#include "plugins/pglist.h"



/* Affiche des indications quant à l'utilisation du programme. */
static void show_chrysalide_help(const char *);

/* Affiche des indications sur la version courante du programme. */
static void show_chrysalide_version(void);

#ifdef INCLUDE_GTK_SUPPORT

/* Recharge le dernier projet ouvert s'il existe. */
static gboolean load_last_project(GGenConfig *);

#endif

/* Ouvre les éventuels fichiers fournis au démarrage. */
static int open_binaries(char **, int);

/* Sauvegarde le cache des binaires analysés. */
static int save_binary_caches(void);



/******************************************************************************
*                                                                             *
*  Paramètres  : name = nom du programme en question.                         *
*                                                                             *
*  Description : Affiche des indications quant à l'utilisation du programme.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void show_chrysalide_help(const char *name)
{
    char *tmp;                              /* Conservation modifiable     */
    char *base;                             /* Version courte du nom       */

    tmp = strdup(name);

    base = basename(tmp);

    printf("\n");

    printf("Usage: %s [--help] [--version]\n", base);
    printf("       %s [args] <filename(s)...>\n", base);

    free(tmp);

    printf("\n");

    printf("\t-h --help\t\tShow this help message.\n");
    printf("\t-v --version\t\tDisplay the program version.\n");

    printf("\n");

    printf("\t-V --verbosity=level\tSet the log level (0 for all messages, %u for none).\n", LMT_COUNT);
    printf("\t-b --batch\t\tExit after processing files.\n");
    printf("\t-s --save\t\tSave disassembly cache after analysis in batch mode (ignored in normal mode).\n");
    printf("\t-p --project=filename\tOpen an existing project or create a new one.\n");

    printf("\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Affiche des indications sur la version courante du programme.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void show_chrysalide_version(void)
{
    char *edir;                             /* Répertoire de base effectif */

    printf("\n");

    printf("-o-  Chrysalide r%u  -o-\n", REVISION);
    printf(_("Last compiled on %s at %s\n"), __DATE__, __TIME__);

    printf("\n");

    edir = get_effective_directory(PIXMAPS_DIR);
    printf(_("Pictures directory: %s\n"), edir);
    free(edir);

    edir = get_effective_directory(THEMES_DIR);
    printf(_("Themes directory: %s\n"), edir);
    free(edir);

    edir = get_effective_directory(PLUGINS_LIB_DIR);
    printf(_("Plugins library directory: %s\n"), edir);
    free(edir);

    edir = get_effective_directory(PLUGINS_DATA_DIR);
    printf(_("Plugins data directory: %s\n"), edir);
    free(edir);

    edir = get_effective_directory(LOCALE_DIR);
    printf(_("Locale directory: %s\n"), edir);
    free(edir);

    printf("\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : argc = nombre d'arguments dans la ligne de commande.         *
*                argv = arguments de la ligne de commande.                    *
*                                                                             *
*  Description : Point d'entrée du programme.                                 *
*                                                                             *
*  Retour      : EXIT_SUCCESS si le prgm s'est déroulé sans encombres.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int main(int argc, char **argv)
{
    int result;                             /* Bilan de l'exécution        */
    bool show_help;                         /* Affichage de l'aide ?       */
    bool show_version;                      /* Affichage de la version ?   */
    LogMessageType verbosity;               /* Niveau de filtre de message */
#ifdef INCLUDE_GTK_SUPPORT
    bool batch_mode;                        /* Exécution sans GUI ?        */
#endif
    bool save;                              /* Sauvegarde du cache ?       */
    char *prj_filename;                     /* Chemin vers un projet       */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    char *edir;                             /* Répertoire de base effectif */
    bool status;                            /* Bilan d'opérations          */
#ifdef INCLUDE_GTK_SUPPORT
    GtkWidget *editor;                      /* Fenêtre graphique           */
    GGenConfig *config;                     /* Configuration globale       */
    bool welcome;                           /* Affichage de la bienvenue ? */
#endif
    char resolved[PATH_MAX];                /* Résolution de nom de fichier*/
    GStudyProject *project;                 /* Nouveau projet courant      */

    static struct option long_options[] = {
        { "help",       no_argument,        NULL,   'h' },
        { "version",    no_argument,        NULL,   'v' },
        { "verbosity",  required_argument,  NULL,   'V' },
        { "batch",      no_argument,        NULL,   'b' },
        { "save",       no_argument,        NULL,   's' },
        { "project",    required_argument,  NULL,   'p' },
        { "new-prefix", required_argument,  NULL,   'n' },
        { NULL,         0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /**
     * Initialisation de la bibliothèque et validation des correspondances
     * d'ABI entre la version du moment de la compilation et celle présente
     * sur le système courant.
     */
    LIBXML_TEST_VERSION;

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;
#ifdef INCLUDE_GTK_SUPPORT
    batch_mode = false;
#endif
    save = false;
    prj_filename = NULL;

    while (true)
    {
        ret = getopt_long(argc, argv, "hvV:bsp:", long_options, &index);
        if (ret == -1) break;

        switch (ret)
        {
            case 'h':
                show_help = true;
                break;

            case 'v':
                show_version = true;
                break;

            case 'V':
                verbosity = strtoul(optarg, NULL, 10);
                break;

            case 'b':
#ifdef INCLUDE_GTK_SUPPORT
                batch_mode = true;
#endif
                break;

            case 's':
                save = true;
                break;

            case 'p':
                prj_filename = optarg;
                break;

            case 'n':
                register_new_prefix(optarg);
                break;

        }

    }

    /* Actions de base */

    if (show_help)
    {
        show_chrysalide_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_chrysalide_version();
        result = EXIT_SUCCESS;
        goto done;
    }

    /* Lancement des choses sérieuses */

    setlocale(LC_ALL, "");
    edir = get_effective_directory(LOCALE_DIR);
    bindtextdomain(PACKAGE, edir);
    free(edir);
    textdomain(PACKAGE);

    /* Initialisation de GTK */
    g_set_prgname("Chrysalide");
#ifdef INCLUDE_GTK_SUPPORT
    gtk_init(&argc, &argv);
#endif

    /* Initialisation du programme */

#ifdef INCLUDE_GTK_SUPPORT
    if (batch_mode)
#endif
        set_batch_mode();

    set_log_verbosity(verbosity);

    if (!load_all_core_components(true))
        goto done;

    /* Création de l'interface */

#ifdef INCLUDE_GTK_SUPPORT

    if (!batch_mode)
    {
        editor = create_editor();
        if (editor == NULL) goto failed_to_load_editor;

        status = load_all_gui_components();
        if (!status) goto failed_to_load_gui_components;

        gtk_widget_show_now(editor);

    }

    /**
     * Pour éviter le message de GCC :
     *
     *    """
     *    warning: ‘editor’ may be used uninitialized in this function [-Wmaybe-uninitialized]
     *    """
     */
    else
        editor = NULL;

#endif

    init_all_plugins(true);

#ifdef INCLUDE_GTK_SUPPORT

    config = get_main_configuration();

    if (!batch_mode)
    {
        status = complete_loading_of_all_gui_components(config);
        if (!status) goto exit_complete_gui;
    }

#endif

    /* Lancement du serveur local */

    status = ensure_internal_connections_setup();

    if (!status)
        goto no_internal_server;

    status = launch_internal_server();

    if (!status)
        goto no_internal_server;

    /* Charge le dernier projet ? */

#ifdef INCLUDE_GTK_SUPPORT

    if (batch_mode)
        welcome = true;
    else
        g_generic_config_get_value(config, MPK_WELCOME_STARTUP, &welcome);

    if (!welcome && prj_filename == NULL)
        g_idle_add((GSourceFunc)load_last_project, config);

    else

#endif

    {
        if (prj_filename != NULL)
        {
            prj_filename = realpath(prj_filename, resolved);

            if (prj_filename == NULL)
                LOG_ERROR_N("realpath");

        }

        if (prj_filename == NULL)
            project = g_study_project_new();

        else
        {
            ret = access(prj_filename, R_OK);

            if (ret == 0)
            {
#ifdef INCLUDE_GTK_SUPPORT
                project = g_study_project_open(prj_filename, !batch_mode);
#else
                project = g_study_project_open(prj_filename, false);
#endif
                if (project == NULL) goto bad_project;
            }

            else
            {
                project = g_study_project_new();

                status = g_study_project_save(project, prj_filename);

                if (!status)
                {
                    g_object_unref(G_OBJECT(project));
                    goto bad_project;
                }

            }

        }

        set_current_project(project);

    }

    /* Exécution du programme */

    result = open_binaries(argv + optind, argc - optind);

#ifdef INCLUDE_GTK_SUPPORT

    if (batch_mode)

#endif

    {
        wait_for_all_global_works();

        if (save && result == EXIT_SUCCESS)
        {
            result = save_binary_caches();
            wait_for_all_global_works();
        }

    }

#ifdef INCLUDE_GTK_SUPPORT

    else
        gtk_main();

#endif

    set_current_project(NULL);

 bad_project:

 no_internal_server:

#ifdef INCLUDE_GTK_SUPPORT
 exit_complete_gui:
#endif

#ifdef TRACK_GOBJECT_LEAKS
    remember_gtypes_for_leaks();
#endif

    exit_all_plugins();

#ifdef INCLUDE_GTK_SUPPORT

    if (!batch_mode)
        unload_all_gui_components();

 failed_to_load_gui_components:

    if (!batch_mode)
        g_object_unref(G_OBJECT(editor));

 failed_to_load_editor:

#endif

    unload_all_core_components(true);

#ifdef TRACK_GOBJECT_LEAKS
    dump_remaining_gtypes();
#endif

 done:

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : cfg = configuration globale sur laquelle s'appuyer.          *
*                                                                             *
*  Description : Recharge le dernier projet ouvert s'il existe.               *
*                                                                             *
*  Retour      : G_SOURCE_REMOVE pour ne pas répéter l'action.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean load_last_project(GGenConfig *cfg)
{
    const char *filename;                   /* Chemin du dernier projet    */
    GStudyProject *project;                 /* Nouveau projet courant      */

    if (!g_generic_config_get_value(cfg, MPK_LAST_PROJECT, &filename))
        filename = NULL;

    if (filename == NULL) project = g_study_project_new();
    else project = g_study_project_open(filename, !is_batch_mode());

    set_current_project(project);

    return G_SOURCE_REMOVE;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : files = noms de fichier fournis en ligne de commande.        *
*                count = nombre d'arguments restant à traiter.                *
*                                                                             *
*  Description : Ouvre les éventuels fichiers fournis au démarrage.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int open_binaries(char **files, int count)
{
    int result;                             /* Bilan à retourner           */
    GStudyProject *project;                 /* Projet courant à compléter  */
    int i;                                  /* Boucle de parcours          */
    GContentAttributes *attribs;            /* Attributs à lier au contenu */
    char *filename;                         /* Chemin d'accès au contenu   */
    GBinContent *content;                   /* Contenu binaire à charger   */

    result = EXIT_SUCCESS;

    project = get_current_project();

    for (i = 0; i < count && result == EXIT_SUCCESS; i++)
    {
        attribs = g_content_attributes_new(files[i], &filename);

        if (filename == NULL)
            content = NULL;
        else
        {
            content = g_file_content_new(filename);
            free(filename);
        }

        if (content != NULL)
        {
            g_binary_content_set_attributes(content, attribs);

            g_study_project_discover_binary_content(project, content, !is_batch_mode(), NULL, NULL);
            g_object_unref(G_OBJECT(content));

        }

        else
            result = EXIT_FAILURE;

        g_object_unref(G_OBJECT(attribs));

    }

    g_object_unref(G_OBJECT(project));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Sauvegarde le cache des binaires analysés.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int save_binary_caches(void)
{
    int result;                             /* Bilan à retourner           */
    GStudyProject *project;                 /* Projet courant à compléter  */
    GLoadedContent **loaded;                /* Contenus chargés et analysés*/
    size_t count;                           /* Quantité de ces contenus    */
    size_t i;                               /* Boucle de parcours          */
    bool status;                            /* Bilan de lancement          */

    result = EXIT_SUCCESS;

    project = get_current_project();

    loaded = g_study_project_get_contents(project, &count);

    for (i = 0; i < count; i++)
    {
        if (G_IS_LOADED_BINARY(loaded[i]))
        {
            status = g_loaded_binary_save_cache(G_LOADED_BINARY(loaded[i]));
            if (!status) result = EXIT_FAILURE;
        }

        g_object_unref(G_OBJECT(loaded[i]));

    }

    if (loaded != NULL)
        free(loaded);

    g_object_unref(G_OBJECT(project));

    return result;

}
