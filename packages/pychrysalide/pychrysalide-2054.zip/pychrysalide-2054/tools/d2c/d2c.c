
/* Chrysalide - Outil d'analyse de fichiers binaires
 * d2c.c - compilation d'asbtractions d'instructions
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include <assert.h>
#include <getopt.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "coder.h"
#include "decl.h"



/* Affiche des indications sur l'utilisation du programme. */
static void show_usage(const char *);


/* Commandes générales supportées */
typedef enum _AvailableD2cCommand
{
    ADC_NONE,                               /* Aucune action renseignée    */
    ADC_COMPILE,                            /* Créations principales       */
    ADC_FINI                                /* Finition de fichier global  */

} AvailableD2cCommand;



/******************************************************************************
*                                                                             *
*  Paramètres  : argv0 = nombre du programme exécuté.                         *
*                                                                             *
*  Description : Affiche des indications sur l'utilisation du programme.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void show_usage(const char *argv0)
{
    printf("\n");

    printf("Usage: %s [options] <input file>\n", argv0);

    printf("\n");

    printf("General options:\n");

    printf("\n");

    printf("\t-h | --help\t\t\tDisplay this messsage.\n");
    printf("\t-x | --exec <cc|fini>\t\tRun as compiler mode or complete the generation.\n");
    printf("\t-o | --outdir <string>\t\tSpecify the main output directory.\n");
    printf("\t-t | --type <raw|format>\tSet the type of the input file.\n");
    printf("\t-a | --arch <string>\t\tDefine the archicture to handle (CamelCase allowed).\n");
    printf("\t-n | --name <string>\t\tSet the name of the archicture for source code (CamelCase allowed).\n");
    printf("\t-G | --guard <string>\t\tSet the base of the header macros guards.\n");
    printf("\t-e | --encoding <none|string>\tDefine one encoding prefix for files.\n");

    printf("\n");

    printf("\t--id-prefix <string>\t\tDefine a common prefix for all uniq identifiers.\n");
    printf("\t--id-expected <number>\t\tProvide the expected number of instructions.\n");

    printf("\n");

    printf("Raw specific options:\n");

    printf("\n");

    printf("\t--export\t\t\tDefine if read functions have to be exported to external headers (not by default).\n");
    printf("\t--filename-reuse <length>\tSet the length of filename to include in identifiers (default = 0).\n");

    printf("\n");

    printf("Format specific options:\n");

    printf("\n");

    printf("\t--op-prefix <string>\t\tDefine a prefix to format operand type constants.\n");

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
    int result;                             /* Bilan à retourner           */
    bool need_help;                         /* Affichage de l'aide ?       */
    AvailableD2cCommand execute;            /* Exécution globale attendue  */
    output_info info;                       /* Regroupement d'infos utiles */
    pre_processor *pp;                      /* Pré-processeur avec macros  */
    bool has_error;                         /* Erreur dans la ligne de cmd.*/
    int index;                              /* Indice d'argument à traiter */
    int ret;                                /* Bilan d'une lecture d'arg.  */
    char *sep;                              /* Caratère '=' en coupure     */
    unsigned long int expected;             /* Nombre total de définitions */
    rented_coder *coder;                    /* Codeur à briffer & employer */
    bool status;                            /* Bilan d'une génération      */
    char *temp;                             /* Zone de travail temporaire  */
    char *base;                             /* Identification de fichier   */
    char *underscore;                       /* Dernier caractère '_'       */

    static struct option long_options[] = {

        { "help",           no_argument,        NULL,   'h' },
        { "exec",           required_argument,  NULL,   'x' },
        { "outdir",         required_argument,  NULL,   'o' },
        { "type",           required_argument,  NULL,   't' },
        { "arch",           required_argument,  NULL,   'a' },
        { "name",           required_argument,  NULL,   'n' },
        { "guard",          required_argument,  NULL,   'G' },
        { "encoding",       required_argument,  NULL,   'e' },

        { "id-prefix",      required_argument,  NULL,   0x100 },
        { "id-expected",    required_argument,  NULL,   0x101 },

        { "export",         no_argument,        NULL,   0x200 },
        { "filename-reuse", required_argument,  NULL,   0x201 },

        { "op-prefix",      required_argument,  NULL,   0x300 },

        { NULL,             0,                  NULL,   0   }

    };

    /* Récupération des commandes */

    need_help = false;
    execute = ADC_NONE;
    memset(&info, 0, sizeof(info));

    pp = create_pre_processor();

    has_error = false;

    while (!has_error)
    {
        ret = getopt_long(argc, argv, "hx:o:t:a:n:G:e:", long_options, &index);
        if (ret == -1) break;

        switch (ret)
        {
            case 'h':
                need_help = true;
                break;

            case 'x':

                if (strcmp(optarg, "cc") == 0)
                    execute = ADC_COMPILE;

                else if (strcmp(optarg, "fini") == 0)
                    execute = ADC_FINI;

                else
                    has_error = true;

                break;

            case 'o':

                ret = asprintf(&info.opcodes_dir, "%sopcodes%c", optarg, optarg[strlen(optarg) - 1]);

                if (ret == -1)
                {
                    info.opcodes_dir = NULL;
                    fprintf(stderr, "unable to memorize the specified main output directory; exiting...\n");
                    goto exit;
                }
                break;

            case 't':

                if (strcmp(optarg, "raw") == 0)
                    info.type = IOT_RAW;

                else if (strcmp(optarg, "format") == 0)
                    info.type = IOT_FORMAT;

                else
                    has_error = true;

                break;

            case 'a':
                info.arch = optarg;
                break;

            case 'n':
                info.arch_cn = optarg;
                break;

            case 'G':
                info.guard = optarg;
                break;

            case 'e':

                if (strcmp(optarg, "none") == 0)
                    register_empty_encoding(pp);
 
                else
                {
                    sep = strchr(optarg, '=');
                    has_error = (sep == NULL);

                    if (!has_error)
                    {
                        *sep = '\0';
                        register_encoding(pp, optarg, sep + 1);
                    }

                }

                break;

            case 0x100:
                info.id_prefix = optarg;
                break;

            case 0x101:
                expected = strtoul(optarg, NULL, 10);
                info.id_len = (int)ceil(log(expected) / log(16));;
                break;

            case 0x200:
                info.export = true;
                break;

            case 0x201:
                info.filename_reuse = strtoul(optarg, NULL, 10);
                break;

            case 0x300:
                info.fmt_prefix = optarg;
                break;

            default:
                has_error = true;
                break;

        }

    }

    /* Vérifications supplémentaires */

    if (execute == ADC_NONE)
        has_error = true;

    if (info.opcodes_dir == NULL || info.arch == NULL || info.arch_cn == NULL || info.guard == NULL)
        has_error = true;

    if (need_help || has_error || (optind + 1) != argc)
    {
        show_usage(argv[0]);
        result = (need_help ? EXIT_SUCCESS : EXIT_FAILURE);
        goto exit;
    }

    /* Execution attendue */

    result = EXIT_FAILURE;

    switch (execute)
    {
        case ADC_COMPILE:

            coder = process_definition_file(argv[optind], pp);
            if (coder == NULL) goto exit;

            status = output_coder_body(coder, &info);
            if (!status) goto clean_exit;

            status = output_coder_identifier(coder, &info);
            if (!status) goto clean_exit;

            if (info.type == IOT_RAW)
            {
                status = output_coder_sub_identifier(coder, &info);
                if (!status) goto clean_exit;
            }

            status = output_coder_keyword(coder, &info);
            if (!status) goto clean_exit;

            status = output_coder_hooks(coder, &info);
            if (!status) goto clean_exit;

            status = output_coder_description(coder, &info);
            if (!status) goto clean_exit;

            break;

        case ADC_FINI:

            coder = NULL;

            temp = strdup(argv[optind]);
            base = basename(temp);

            underscore = rindex(base, '_');

            if (underscore == NULL && strcmp(base, "opcodes.h") == 0)
                status = fini_coder_opcodes_file(argv[optind], &info);

            else if (underscore != NULL && strcmp(underscore, "_opcodes.h") == 0)
                status = fini_coder_opcodes_file(argv[optind], &info);

            else if (strcmp(base, "identifiers.h") == 0)
                status = fini_coder_identifiers_file(argv[optind], &info);

            else if (strcmp(base, "subidentifiers.h") == 0 && info.type == IOT_RAW)
                status = fini_coder_sub_identifiers_file(argv[optind], &info);

            else if (strcmp(base, "keywords.h") == 0)
                status = fini_coder_keywords_file(argv[optind], &info);

            else if (strcmp(base, "hooks.h") == 0)
                status = fini_coder_hooks_file(argv[optind], &info);

            else if (strcmp(base, "descriptions.h") == 0)
                status = fini_coder_descriptions_file(argv[optind], &info);

            else
                status = false;

            free(temp);

            if (!status) goto exit;

            break;

        default:
            assert(false);
            break;

    }

    result = EXIT_SUCCESS;

 clean_exit:

    if (coder != NULL)
        delete_coder(coder);

 exit:

    if (info.opcodes_dir != NULL)
        free(info.opcodes_dir);

    return result;

}
