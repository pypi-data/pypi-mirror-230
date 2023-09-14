
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rost.c - fichier d'entrée du centre de collecte
 *
 * Copyright (C) 2023 Cyrille Bagard
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
#include <locale.h>
#include <stdlib.h>


#include <i18n.h>



#include "gleak.h"
#include "analysis/contents/file.h"
#include "analysis/scan/options.h"
#include "analysis/scan/scanner.h"
#include "analysis/scan/patterns/backends/bitap.h"
#include "analysis/scan/patterns/backends/acism.h"
#include "core/core.h"
#include "core/global.h"
#include "core/logs.h"
#include "core/paths.h"



/* Affiche des indications quant à l'utilisation du programme. */
static void show_rost_help(const char *);

/* Affiche des indications sur la version courante du programme. */
static void show_rost_version(void);



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

static void show_rost_help(const char *name)
{
    char *tmp;                              /* Conservation modifiable     */
    char *base;                             /* Version courte du nom       */

    tmp = strdup(name);

    base = basename(tmp);

    printf("\n");

    printf("Usage: %s [--help] [--version] [--verbosity] [options] <rules file> <file | dir>\n", base);

    printf("\n");

    printf("\t-h --help\t\tShow this help message.\n");
    printf("\t-v --version\t\tDisplay the program version.\n");

    printf("\n");

    printf("\t-A --algorithm=name\tSelect one of the available algorithms for data: bitmap, acism (default: acsim).\n");
    printf("\t-j --print-json\t\tPrint matching strings in JSON format.\n");
    printf("\t-s --print-strings\tPrint matching strings.\n");
    printf("\t-S --print-stats\tPrint rules' statistics.\n");
    printf("\t-V --verbosity=level\tSet the log level (0 for all messages, %u for none).\n", LMT_COUNT);

    printf("\n");

    free(tmp);

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

static void show_rost_version(void)
{
    char *edir;                             /* Répertoire de base effectif */

    printf("\n");

    printf("-o-  Chrysalide ROST r%u  -o-\n", REVISION);
    printf(_("Last compiled on %s at %s\n"), __DATE__, __TIME__);

    printf("\n");

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
    GScanOptions *options;                  /* Options d'analyses          */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    char *rules;                            /* Définition de règles        */
    char *target;                           /* Cible communiquée           */
    char *edir;                             /* Répertoire de base effectif */
    GContentScanner *scanner;               /* Encadrement d'une recherche */
    GBinContent *content;                   /* Contenu à analyser          */
    GScanContext *context;                  /* Contexte des trouvailles    */
    sized_string_t padding;                 /* Bourrage pour le JSON       */
    bool full;                              /* Détailler l'affichage ?     */

    static struct option long_options[] = {
        { "help",           no_argument,        NULL,   'h' },
        { "version",        no_argument,        NULL,   'v' },
        { "algorithm",      required_argument,  NULL,   'A' },
        { "print-json",     no_argument,        NULL,   'j' },
        { "print-strings",  no_argument,        NULL,   's' },
        { "print-stats",    no_argument,        NULL,   'S' },
        { "verbosity",      required_argument,  NULL,   'V' },
        { NULL,             0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;

    options = g_scan_options_new();

    g_scan_options_set_backend_for_data(options, G_TYPE_ACISM_BACKEND);

    while (true)
    {
        ret = getopt_long(argc, argv, "hvA:jsSV:", long_options, &index);
        if (ret == -1) break;

        switch (ret)
        {
            case 'h':
                show_help = true;
                break;

            case 'v':
                show_version = true;
                break;

            case 'A':
                if (strcmp(optarg, "bitmap") == 0)
                    g_scan_options_set_backend_for_data(options, G_TYPE_BITAP_BACKEND);
                else if (strcmp(optarg, "acism") == 0)
                    g_scan_options_set_backend_for_data(options, G_TYPE_ACISM_BACKEND);
                else
                    g_scan_options_set_backend_for_data(options, G_TYPE_INVALID);
                break;

            case 'j':
                g_scan_options_set_print_json(options, true);
                break;

            case 's':
                g_scan_options_set_print_strings(options, true);
                break;

            case 'S':
                g_scan_options_set_print_stats(options, true);
                break;

            case 'V':
                verbosity = strtoul(optarg, NULL, 10);
                break;

        }

    }

    if ((optind + 2) != argc)
    {
        show_rost_help(argv[0]);
        result = EXIT_FAILURE;
        goto done;
    }

    rules = argv[optind];
    target = argv[optind + 1];

    /* Actions de base */

    if (show_help)
    {
        show_rost_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_rost_version();
        result = EXIT_SUCCESS;
        goto done;
    }

    if (g_scan_options_get_backend_for_data(options) == G_TYPE_INVALID)
    {
        show_rost_help(argv[0]);
        result = EXIT_FAILURE;
        goto done;
    }

    /* Lancement des choses sérieuses */

    setlocale(LC_ALL, "");
    edir = get_effective_directory(LOCALE_DIR);
    bindtextdomain(PACKAGE, edir);
    free(edir);
    textdomain(PACKAGE);

    /* Initialisation de GTK */
    g_set_prgname("ROST");
    //gtk_init(&argc, &argv);

    /* Initialisation du programme */

    set_batch_mode();

    set_log_verbosity(verbosity);

    if (!load_all_core_components(true))
        goto done;

    /* Traitement des recherches */

    scanner = g_content_scanner_new_from_file(rules);

    if (scanner != NULL)
    {
        content = g_file_content_new(target);

        context = g_content_scanner_analyze(scanner, options, content);

        if (g_scan_options_get_print_json(options))
        {
            padding.data = "   ";
            padding.len = 3;

            g_content_scanner_output_to_json(scanner, context, &padding, 0, STDOUT_FILENO);

        }
        else
        {
            full = g_scan_options_get_print_strings(options);

            g_content_scanner_output_to_text(scanner, context, full, STDOUT_FILENO);

        }

        g_object_unref(G_OBJECT(context));
        g_object_unref(G_OBJECT(content));

        g_object_unref(G_OBJECT(scanner));

    }

    g_object_unref(G_OBJECT(options));

    /* Sortie */

    unload_all_core_components(false);

#ifdef TRACK_GOBJECT_LEAKS
    remember_gtypes_for_leaks();
#endif

#ifdef TRACK_GOBJECT_LEAKS
    dump_remaining_gtypes();
#endif

 done:

    return result;

}
