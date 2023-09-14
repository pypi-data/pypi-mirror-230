
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hub.c - fichier d'entrée du centre de collecte
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


#include <getopt.h>
#include <libgen.h>
#include <locale.h>
#include <malloc.h>
#include <signal.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include <i18n.h>


#include "gleak.h"
#include "analysis/db/auth.h"
#include "analysis/db/server.h"
#include "core/core.h"
#include "core/global.h"
#include "core/logs.h"
#include "core/paths.h"



/* Liste des commandes principales */
typedef enum _HubMainCommand
{
    HMC_NONE,                               /* Absence de commande         */
    HMC_CLIENT_ID,                          /* Création d'une identité     */
    HMC_SERVER_ID,                          /* Création d'une identité     */
    HMC_ADD_CLIENT,                         /* Enregistrement d'utilisateur*/
    HMC_RUN                                 /* Lancement d'un serveur      */

} HubMainCommand;


/* Affiche des indications quant à l'utilisation du programme. */
static void show_hub_help(const char *);

/* Affiche des indications sur la version courante du programme. */
static void show_hub_version(void);

/* Construit une identité selon les indications fournies. */
static int parse_identity_properties(const char *, x509_entries *);

/* Traite la commande "client-id" et ses arguments. */
static int exec_cmd_client_identity(int, char **);

/* Traite la commande "server-id" et ses arguments. */
static int exec_cmd_server_identity(int, char **);

/* Traite la commande "add-client" et ses arguments. */
static int exec_cmd_add_client(int, char **);

/* Traite la commande "run" et ses arguments. */
static int exec_cmd_run_server(int, char **);


/* Serveur pour les enregistrements en base */
static GHubServer *_server = NULL;



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

static void show_hub_help(const char *name)
{
    char *tmp;                              /* Conservation modifiable     */
    char *base;                             /* Version courte du nom       */

    tmp = strdup(name);

    base = basename(tmp);

    printf("\n");

    printf("Usage: %s [--help] [--version] [--verbosity] <cmd> [options]\n", base);

    printf("\n");

    printf("\t-h --help\t\tShow this help message.\n");
    printf("\t-v --version\t\tDisplay the program version.\n");

    printf("\n");

    printf("\t-V --verbosity=level\tSet the log level (0 for all messages, %u for none).\n", LMT_COUNT);

    printf("\n");

    printf("Command client-id:\n");
    printf("------------------\n");

    printf("\n");

    printf("Usage: %s client-id [--help] [--version] [--verbosity] [--long <integer>] <fields>\n",
           base);

    printf("\n");

    printf("\t-l --long=integer\tProvide the validity time of the certicate, in seconds (default: 3 years)\n");
    printf("\tfields\t\t\tCertificate's subject fields, as comma-separated key=value pairs.\n");

    printf("\n");

    printf("Command server-id:\n");
    printf("------------------\n");

    printf("\n");

    printf("Usage: %s server-id [--help] [--version] [--verbosity] [--name <string>] [--port <integer>] [--long <integer>] <fields>\n",
           base);

    printf("\n");

    printf("\t-n --name=string\tDefine the name of the server to reach (default: standalone)\n");
    printf("\t-p --port=integer\tSpecify the listening port of this server (default: 1337)\n");
    printf("\t-l --long=integer\tProvide the validity time of the certicate, in seconds (default: 3 years)\n");
    printf("\tfields\t\t\tCertificate's subject fields, as comma-separated key=value pairs.\n");

    printf("\n");

    printf("Command add-client:\n");
    printf("-------------------\n");

    printf("\n");

    printf("Usage: %s add-client [--help] [--version] [--verbosity] [--name <string>] [--port <integer>] [--long <integer>] <csr> <outdir>\n",
           base);

    printf("\n");

    printf("\t-n --name=string\tDefine the name of the server to reach (default: standalone)\n");
    printf("\t-p --port=integer\tSpecify the listening port of this server (default: 1337)\n");
    printf("\t-l --long=integer\tProvide the validity time of the certicate, in seconds (default: 3 years)\n");
    printf("\tcsr\t\t\tCertificate Signing Request file to use in order to give an authorized access to server.\n");
    printf("\toutdir\t\t\tOutput directory for the signed certificate and the copied server CA, for the client side.\n");

    printf("\n");

    printf("Command run:\n");
    printf("------------\n");

    printf("\n");

    printf("Usage: %s run [--help] [--version] [--verbosity] [--name <string>] [--port <integer>] [--backlog <integer>] [--keep]\n",
           base);

    printf("\n");

    printf("\t-n --name=string\tDefine the name of the server to reach (default: standalone)\n");
    printf("\t-p --port=integer\tSpecify the listening port of this server (default: 1337)\n");
    printf("\t-4 --ipv4=integer\tPrefer using an IPv4 address if possible (IPv6 by default)\n");
    printf("\t-b --backlog=integer\tSet the maximum number of incoming connections (default: 10)\n");
    printf("\t-k --keep\t\tKeep the server in the foreground (default is to run as daemon)\n");

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

static void show_hub_version(void)
{
    char *edir;                             /* Répertoire de base effectif */

    printf("\n");

    printf("-o-  Chrysalide Hub r%u  -o-\n", REVISION);
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
    HubMainCommand command;                 /* Commande à satisfaire       */
    bool show_help;                         /* Affichage de l'aide ?       */
    bool show_version;                      /* Affichage de la version ?   */
    LogMessageType verbosity;               /* Niveau de filtre de message */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    char *edir;                             /* Répertoire de base effectif */

    static struct option long_options[] = {
        { "help",       no_argument,        NULL,   'h' },
        { "version",    no_argument,        NULL,   'v' },
        { "verbosity",  required_argument,  NULL,   'V' },
        { NULL,         0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /* Décodage de la commande principale */

    command = HMC_NONE;

    if (argc >= 2)
    {
        if (strcmp(argv[1], "client-id") == 0)
            command = HMC_CLIENT_ID;

        else if (strcmp(argv[1], "server-id") == 0)
            command = HMC_SERVER_ID;

        else if (strcmp(argv[1], "add-client") == 0)
            command = HMC_ADD_CLIENT;

        else if (strcmp(argv[1], "run") == 0)
            command = HMC_RUN;

    }

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;

    if (command == HMC_NONE)
        while (true)
        {
            ret = getopt_long(argc, argv, "hvV:", long_options, &index);
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

            }

        }

    /* Actions de base */

    if (show_help)
    {
        show_hub_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_hub_version();
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
    g_set_prgname("Chrysalide Hub");
#ifdef INCLUDE_GTK_SUPPORT
    gtk_init(&argc, &argv);
#endif

    /* Initialisation du programme */

    set_batch_mode();

    set_log_verbosity(verbosity);

    if (!load_all_core_components(false))
        goto done;

    /* Traitement des commandes */

    switch (command)
    {
        case HMC_CLIENT_ID:
            result = exec_cmd_client_identity(argc, argv);
            break;

        case HMC_SERVER_ID:
            result = exec_cmd_server_identity(argc, argv);
            break;

        case HMC_ADD_CLIENT:
            result = exec_cmd_add_client(argc, argv);
            break;

        case HMC_RUN:
            result = exec_cmd_run_server(argc, argv);
            break;

        default:
            show_hub_help(argv[0]);
            goto done;
            break;

    }

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


/******************************************************************************
*                                                                             *
*  Paramètres  : properties = propriétés brutes à convertir.                  *
*                identity   = éléments de l'identité à définir. [OUT]         *
*                                                                             *
*  Description : Construit une identité selon les indications fournies.       *
*                                                                             *
*  Retour      : Bilan de l'opération : EXIT_SUCCES ou un indicatif d'erreur. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int parse_identity_properties(const char *properties, x509_entries *identity)
{
    int result;                             /* Bilan de l'exécution        */
    char *tmp;                              /* Copie modifiable            */
    char *saveptr;                          /* Sauvegarde pour traitement  */
    char *pair;                             /* Ensemble clef=valeur        */
    char *eq;                               /* Signe égal présent          */

    result = EXIT_SUCCESS;

    memset(identity, 0, sizeof(*identity));

    tmp = strdup(properties);

    for (pair = strtok_r(tmp, ",", &saveptr);
         pair != NULL;
         pair = strtok_r(NULL, ",", &saveptr))
    {
        eq = strchr(pair, '=');

        if (eq == NULL)
        {
            log_variadic_message(LMT_ERROR, _("Malformed identity properties: '%s'"), properties);

            result = 3;
            goto id_error;

        }

        *eq = '\0';

        if (strcasecmp(pair, "C") == 0)
            identity->country = strdup(eq + 1);

        else if (strcasecmp(pair, "ST") == 0)
            identity->state = strdup(eq + 1);

        else if (strcasecmp(pair, "L") == 0)
            identity->locality = strdup(eq + 1);

        else if (strcasecmp(pair, "O") == 0)
            identity->organisation = strdup(eq + 1);

        else if (strcasecmp(pair, "OU") == 0)
            identity->organisational_unit = strdup(eq + 1);

        else if (strcasecmp(pair, "CN") == 0)
            identity->common_name = strdup(eq + 1);

        else
        {
            log_variadic_message(LMT_ERROR, _("Unknown identity property: '%s=%s'"), pair, eq + 1);

            result = 4;
            goto id_error;

        }

    }

 id_error:

    free(tmp);

    if (result != EXIT_SUCCESS)
        free_x509_entries(identity);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : argc = nombre d'arguments dans la ligne de commande.         *
*                argv = arguments de la ligne de commande.                    *
*                                                                             *
*  Description : Traite la commande "client-id" et ses arguments.             *
*                                                                             *
*  Retour      : EXIT_SUCCESS si le programme s'est déroulé sans encombres.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int exec_cmd_client_identity(int argc, char **argv)
{
    int result;                             /* Bilan de l'exécution        */
    bool show_help;                         /* Affichage de l'aide ?       */
    bool show_version;                      /* Affichage de la version ?   */
    LogMessageType verbosity;               /* Niveau de filtre de message */
    unsigned long valid;                    /* Durée de validité           */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    x509_entries identity;                  /* Nouvelle identité à pousser */
    bool status;                            /* Bilan d'opérations          */

    static struct option long_options[] = {
        { "help",       no_argument,        NULL,   'h' },
        { "version",    no_argument,        NULL,   'v' },
        { "verbosity",  required_argument,  NULL,   'V' },
        { "long",       required_argument,  NULL,   'l' },
        { NULL,         0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;
    valid = 3 * 365 * 24 * 60 * 60;

    while (true)
    {
        ret = getopt_long(argc - 1, argv + 1, "hvV:", long_options, &index);
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

            case 'l':
                valid = strtoul(optarg, NULL, 10);
                break;

        }

    }

    /* Actions de base */

    if (show_help)
    {
        show_hub_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_hub_version();
        result = EXIT_SUCCESS;
        goto done;
    }

    /* Initialisation du programme */

    set_log_verbosity(verbosity);

    /* Elaboration de l'identité */

    if ((optind + 1) == argc)
    {
        log_simple_message(LMT_ERROR,
                           _("Identity properties are missing; please provide at least an empty string"));
        result = 2;
        goto done;
    }

    ret = parse_identity_properties(argv[optind + 1], &identity);
    if (ret != EXIT_SUCCESS)
    {
        result = ret;
        goto done;
    }

    /* Traitement de la commande */

    status = setup_client_identity(valid, &identity);

    if (status)
        result = EXIT_SUCCESS;

    free_x509_entries(&identity);

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : argc = nombre d'arguments dans la ligne de commande.         *
*                argv = arguments de la ligne de commande.                    *
*                                                                             *
*  Description : Traite la commande "server-id" et ses arguments.             *
*                                                                             *
*  Retour      : EXIT_SUCCESS si le programme s'est déroulé sans encombres.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int exec_cmd_server_identity(int argc, char **argv)
{
    int result;                             /* Bilan de l'exécution        */
    bool show_help;                         /* Affichage de l'aide ?       */
    bool show_version;                      /* Affichage de la version ?   */
    LogMessageType verbosity;               /* Niveau de filtre de message */
    char *name;                             /* Désignation du serveur      */
    char *port;                             /* Définition du port associé  */
    unsigned long valid;                    /* Durée de validité           */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    x509_entries identity;                  /* Nouvelle identité à pousser */
    bool status;                            /* Bilan d'opérations          */

    static struct option long_options[] = {
        { "help",       no_argument,        NULL,   'h' },
        { "version",    no_argument,        NULL,   'v' },
        { "verbosity",  required_argument,  NULL,   'V' },
        { "name",       required_argument,  NULL,   'n' },
        { "port",       required_argument,  NULL,   'p' },
        { "long",       required_argument,  NULL,   'l' },
        { NULL,         0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;
    name = NULL;
    port = NULL;
    valid = 3 * 365 * 24 * 60 * 60;

    while (true)
    {
        ret = getopt_long(argc - 1, argv + 1, "hvV:n:p:l:", long_options, &index);
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

            case 'n':
                name = optarg;
                break;

            case 'p':
                port = optarg;
                break;

            case 'l':
                valid = strtoul(optarg, NULL, 10);
                break;

        }

    }

    /* Actions de base */

    if (show_help)
    {
        show_hub_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_hub_version();
        result = EXIT_SUCCESS;
        goto done;
    }

    /* Initialisation du programme */

    set_log_verbosity(verbosity);

    /* Elaboration de l'identité */

    if ((optind + 1) == argc)
    {
        log_simple_message(LMT_ERROR,
                           _("Identity properties are missing; please provide at least an empty string"));
        result = 2;
        goto done;
    }

    ret = parse_identity_properties(argv[optind + 1], &identity);
    if (ret != EXIT_SUCCESS)
    {
        result = ret;
        goto done;
    }

    /* Traitement de la commande */

    status = setup_server_identity(name, port, valid, &identity);

    if (status)
        result = EXIT_SUCCESS;

    free_x509_entries(&identity);

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : argc = nombre d'arguments dans la ligne de commande.         *
*                argv = arguments de la ligne de commande.                    *
*                                                                             *
*  Description : Traite la commande "add-client" et ses arguments.            *
*                                                                             *
*  Retour      : EXIT_SUCCESS si le programme s'est déroulé sans encombres.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int exec_cmd_add_client(int argc, char **argv)
{
    int result;                             /* Bilan de l'exécution        */
    bool show_help;                         /* Affichage de l'aide ?       */
    bool show_version;                      /* Affichage de la version ?   */
    LogMessageType verbosity;               /* Niveau de filtre de message */
    char *name;                             /* Désignation du serveur      */
    char *port;                             /* Définition du port associé  */
    unsigned long valid;                    /* Durée de validité           */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    bool status;                            /* Bilan d'opérations          */

    static struct option long_options[] = {
        { "help",       no_argument,        NULL,   'h' },
        { "version",    no_argument,        NULL,   'v' },
        { "verbosity",  required_argument,  NULL,   'V' },
        { "name",       required_argument,  NULL,   'n' },
        { "port",       required_argument,  NULL,   'p' },
        { "long",       required_argument,  NULL,   'l' },
        { NULL,         0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;
    name = NULL;
    port = NULL;
    valid = 3 * 365 * 24 * 60 * 60;

    while (true)
    {
        ret = getopt_long(argc - 1, argv + 1, "hvV:n:p:l:", long_options, &index);
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

            case 'n':
                name = optarg;
                break;

            case 'p':
                port = optarg;
                break;

            case 'l':
                valid = strtoul(optarg, NULL, 10);
                break;

        }

    }

    /* Actions de base */

    if (show_help)
    {
        show_hub_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_hub_version();
        result = EXIT_SUCCESS;
        goto done;
    }

    if ((optind + 2) >= argc)
    {
        show_hub_help(argv[0]);
        goto done;
    }

    /* Initialisation du programme */

    set_log_verbosity(verbosity);

    /* Traitement de la commande */

    status = add_client_to_server(name, port, valid, argv[optind + 1], argv[optind + 2]);

    if (status)
        result = EXIT_SUCCESS;

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sig = numéro du signal reçu.                                 *
*                                                                             *
*  Description : Réagit à la réception d'un signal SIGTERM.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_term_signal(int sig)
{
    log_simple_message(LMT_INFO, _("Stopping the server..."));

    g_hub_server_stop(_server);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : argc = nombre d'arguments dans la ligne de commande.         *
*                argv = arguments de la ligne de commande.                    *
*                                                                             *
*  Description : Traite la commande "run" et ses arguments.                   *
*                                                                             *
*  Retour      : EXIT_SUCCESS si le programme s'est déroulé sans encombres.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int exec_cmd_run_server(int argc, char **argv)
{
    int result;                             /* Bilan de l'exécution        */
    bool show_help;                         /* Affichage de l'aide ?       */
    bool show_version;                      /* Affichage de la version ?   */
    LogMessageType verbosity;               /* Niveau de filtre de message */
    char *name;                             /* Désignation du serveur      */
    char *port;                             /* Définition du port associé  */
    bool ipv6;                              /* Préférence pour IPv6 ?      */
    int backlog;                            /* Nombre de connexions max.   */
    bool keep;                              /* Maintien en avant plan ?    */
    int index;                              /* Indice d'argument           */
    int ret;                                /* Bilan d'un appel            */
    ServerStartStatus status;               /* Bilan d'un lancement        */
    sighandler_t prev;                      /* Gestionnaire précédent      */

    static struct option long_options[] = {
        { "help",       no_argument,        NULL,   'h' },
        { "version",    no_argument,        NULL,   'v' },
        { "verbosity",  required_argument,  NULL,   'V' },
        { "name",       required_argument,  NULL,   'n' },
        { "port",       required_argument,  NULL,   'p' },
        { "ipv4",       no_argument,        NULL,   '4' },
        { "backlog",    required_argument,  NULL,   'b' },
        { "keep",       no_argument,        NULL,   'k' },
        { NULL,         0,                  NULL,   0 }
    };

    result = EXIT_FAILURE;

    /* Décodage des options */

    show_help = false;
    show_version = false;

    verbosity = LMT_INFO;
    name = NULL;
    port = NULL;
    ipv6 = true;
    backlog = 10;
    keep = false;

    while (true)
    {
        ret = getopt_long(argc - 1, argv + 1, "hvV:n:p:4b:k", long_options, &index);
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

            case 'n':
                name = optarg;
                break;

            case 'p':
                port = optarg;
                break;

            case '4':
                ipv6 = false;
                break;

            case 'b':
                backlog = atoi(optarg);
                break;

            case 'k':
                keep = true;
                break;

        }

    }

    /* Actions de base */

    if (show_help)
    {
        show_hub_help(argv[0]);
        result = EXIT_SUCCESS;
        goto done;
    }

    if (show_version)
    {
        show_hub_version();
        result = EXIT_SUCCESS;
        goto done;
    }

    /* Initialisation du programme */

    set_log_verbosity(verbosity);

    /* Traitement de la commande */

    if (name == NULL)
        _server = g_hub_server_new_internal();
    else
        _server = g_hub_server_new_remote(name, port, ipv6);

    status = g_hub_server_start(_server, backlog, keep);

    switch (status)
    {
        case SSS_FAILURE:
            goto stopped;
            break;

        case SSS_SUCCESS:

            prev = signal(SIGTERM, on_term_signal);
            if (prev == SIG_ERR)
            {
                LOG_ERROR_N("signal");
                g_hub_server_stop(_server);
                goto stopped;
            }

            g_hub_server_wait_for_stop(_server);

            result = EXIT_SUCCESS;
            break;

        case SSS_ALREADY_RUNNING:
            result = EXIT_SUCCESS;
            break;

    }

 stopped:

    g_object_unref(G_OBJECT(_server));

 done:

    return result;

}
