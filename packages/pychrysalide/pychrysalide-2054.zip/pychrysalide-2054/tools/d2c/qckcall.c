
/* Chrysalide - Outil d'analyse de fichiers binaires
 * qckcall.c - appel rapide et facilité à une fonction C de Chrysalide
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#include "qckcall.h"


#include <malloc.h>
#include <regex.h>
#include <string.h>
#include <sys/param.h>


#include "helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : callee = fonction appelée à nommer.                          *
*                                                                             *
*  Description : Prépare au besoin la définition d'une macro de transtypage.  *
*                                                                             *
*  Retour      : Macro de transtypage à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_cast_if_needed(const char *callee)
{
    char *result;                           /* Macro à retourner           */
    regex_t preg;                           /* Expression régulière        */
    int ret;                                /* Bilan d'une manipulation    */
    regmatch_t pmatch[3];                   /* Correspondances de chaînes  */
    size_t cmplen;                          /* Taille de comparaison       */

    result = NULL;

    ret = regcomp(&preg, "(g_([a-z0-9]*)_instruction)", REG_EXTENDED);
    if (ret != 0)
    {
        fprintf(stderr, "Internal error: bad regular expression.\n");
        return NULL;
    }

    ret = regexec(&preg, callee, sizeof(pmatch) / sizeof(regmatch_t), pmatch, 0);
    if (ret == REG_NOMATCH)
    {
        fprintf(stderr, "Internal error: bad function for dealing wih instruction: '%s'.\n", callee);
        goto cif_exit;
    }

    /**
     * La variable de résultat est de type 'GArchInstruction',
     * donc toute fonction différente de g_arch_instruction_*() attend un transtypage...
     */

    cmplen = MAX(strlen("arch"), pmatch[2].rm_eo - pmatch[2].rm_so);

    if (strncmp("arch", &callee[pmatch[2].rm_so], cmplen) != 0)
    {
        result = strndup(&callee[pmatch[1].rm_so], pmatch[1].rm_eo - pmatch[1].rm_so);

        result = make_string_upper(result);

    }

 cif_exit:

    regfree(&preg);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : callee = fonction appelée à nommer.                          *
*                args   = précise si la conversion est la dernière.           *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                bits   = gestionnaire des bits d'encodage.                   *
*                list   = liste de l'ensemble des fonctions de conversion.    *
*                                                                             *
*  Description : Réalise un appel à une fonction liée à une instruction.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool call_instr_func(const char *callee, const arg_list_t *args, int fd, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à remonter            */
    char *cast;                             /* Macro de transtypage        */

    cast = build_cast_if_needed(callee);

    if (cast == NULL)
        dprintf(fd, "\t%s(result, ", callee);

    else
    {
        dprintf(fd, "\t%s(%s(result), ", callee, cast);
        free(cast);
    }

    result = define_arg_list(args, fd, bits, list);

    dprintf(fd, ");\n");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : callee = fonction appelée à nommer.                          *
*                args   = précise si la conversion est la dernière.           *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                bits   = gestionnaire des bits d'encodage.                   *
*                list   = liste de l'ensemble des fonctions de conversion.    *
*                                                                             *
*  Description : Réalise un appel à une fonction liée à une instruction.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool checked_call_instr_func(const char *callee, const arg_list_t *args, int fd, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à remonter            */
    char *cast;                             /* Macro de transtypage        */

    cast = build_cast_if_needed(callee);

    if (cast == NULL)
        dprintf(fd, "\tif (!%s(result, ", callee);

    else
    {
        dprintf(fd, "\tif (!%s(%s(result), ", callee, cast);
        free(cast);
    }

    result = define_arg_list(args, fd, bits, list);

    dprintf(fd, "))\n");

    return result;

}
