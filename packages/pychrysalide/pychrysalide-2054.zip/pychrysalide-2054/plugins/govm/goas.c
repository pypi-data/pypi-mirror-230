
/* Chrysalide - Outil d'analyse de fichiers binaires
 * main.c - fichier d'entrée du programme
 *
 * Copyright (C) 2009-2016 Cyrille Bagard
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


#include <fcntl.h>
#include <getopt.h>
#include <libgen.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#include "build.h"


/* gram.y :  Procède à l'assemblage d'une ligne de code. */
bool process_govm_code(govm_info *, const char *);


/* Affiche une description des appels au programme possibles. */
static void show_usage(char *);

/* Lit le fichier d'entrée ligne par ligne et l'assemble. */
static bool feed_govm_parser(const char *, govm_info *);



/******************************************************************************
*                                                                             *
*  Paramètres  : name = nom du programme lancé.                               *
*                                                                             *
*  Description : Affiche une description des appels au programme possibles.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void show_usage(char *name)
{
    fprintf(stderr, "Usage: %s [--help] [--warn] [--output filename] [--big] [--data number] input\n", basename(name));

    fprintf(stderr, "\n");

    fprintf(stderr, "\t--help\t\t\tDisplay this help message.\n");

    fprintf(stderr, "\n");

    fprintf(stderr, "\t--warn\t\t\tDisplay warnings during the compilation.\n");
    fprintf(stderr, "\t--output filename\tDefine the output filename (a.out by default).\n");
    fprintf(stderr, "\t--big\t\t\tProduce big endian bytecode.\n");
    fprintf(stderr, "\t--data number\t\tSet the minimal data section size.\n");

    fprintf(stderr, "\n");

    fprintf(stderr, "\tinput\t\t\tFile containing the assembly code to compile.\n");

    fprintf(stderr, "\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin contenant le code à assembler.             *
*                info     = informations tirées du contenu.                   *
*                                                                             *
*  Description : Lit le fichier d'entrée ligne par ligne et l'assemble.       *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool feed_govm_parser(const char *filename, govm_info *info)
{
    bool result;                            /* Résultat à retourner        */
    int ret;                                /* Bilan d'un appel            */
    struct stat finfo;                      /* Recueil des infos. fichier  */
    char *buffer;                           /* Destination de lecture      */
    FILE *stream;                           /* Flux d'entrée               */
    size_t pos;                             /* Position du retour chariot  */

    result = true;

    ret = stat(filename, &finfo);
    if (ret == -1)
    {
        perror("stat");
        return false;
    }

    buffer = (char *)calloc(finfo.st_size + 1, sizeof(char));
    if (buffer == NULL)
    {
        perror("calloc");
        return false;
    }

    stream = fopen(filename, "r");
    if (stream == NULL)
    {
        perror("fopen");
        result = false;
        goto fgp_exit;
    }

    while (result && fgets(buffer, finfo.st_size + 1, stream) != NULL)
    {
        pos = strlen(buffer);

        if (pos > 0 && buffer[pos - 1] == '\n')
            buffer[pos - 1] = '\0';

        result = process_govm_code(info, buffer);

    }

    fclose(stream);

 fgp_exit:

    free(buffer);

    return result;

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
    int result;                             /* Statut en sortie            */
    bool help;                              /* Affichage de l'aide         */
    bool warn;                              /* Affichage d'avertissements  */
    char *output;                           /* Fichier de sortie           */
    bool big;                               /* Mode gros boutiste          */
    uint16_t data;                          /* Taille min. des données     */
    int option_index;                       /* Indice de l'argument        */
    int ret;                                /* Bilan d'un appel            */
    govm_info *info;                        /* Informations de construct°  */
    int fd;                                 /* Flux ouvert en écriture     */

    static struct option long_options[] = {
        { "help",   no_argument,        NULL,   'h' },
        { "warn",   no_argument,        NULL,   'w' },
        { "output", required_argument,  NULL,   'o' },
        { "big",    no_argument,        NULL,   'b' },
        { "data",   required_argument,  NULL,   'd' },
        { NULL,     0,                  NULL,   0   }
    };

    result = EXIT_SUCCESS;

    help = false;
    warn = false;
    output = "a.out";
    big = false;
    data = 0;

    while (1)
    {
        ret = getopt_long(argc, argv, "hwo:bd:", long_options, &option_index);
        if (ret == -1) break;

        switch (ret)
        {
            case 'h':
                help = true;
                break;

            case 'w':
                warn = true;
                break;

            case 'o':
                output = optarg;
                break;

            case 'b':
                big = true;
                break;

            case 'd':
                data = atoi(optarg);
                break;

        }

    }

    if (help || optind == argc)
    {
        show_usage(argv[0]);
        return help ? EXIT_SUCCESS : EXIT_FAILURE;
    }

    info = create_govm_info(!big, warn);

    if (!feed_govm_parser(argv[optind], info))
    {
        result = EXIT_FAILURE;
        goto error_parsing;
    }

    fd = open(output, O_WRONLY | O_TRUNC | O_CREAT, 0666);
    if (fd == -1)
    {
        perror("open");
        result = EXIT_FAILURE;
        goto error_parsing;
    }

    if (!write_govm_info(info, fd))
    {
        result = EXIT_FAILURE;
        goto error_writing;
    }

 error_writing:

    close(fd);

 error_parsing:

    delete_govm_info(info);

    return result;

}
