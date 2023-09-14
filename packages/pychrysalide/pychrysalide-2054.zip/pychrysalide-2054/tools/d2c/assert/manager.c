
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - désassemblage sous condition
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


#include "manager.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../helpers.h"



/* Elément d'une condition décodée */
typedef struct _def_cond
{
    char *field;                            /* Désignation du champ        */
    DisassCondOp op;                        /* Opération de comparaison    */
    char *value;                            /* Désignation de la valeur    */

    char *lower;                            /* Version minuscule           */

} def_cond;

/* Ligne de condition(s) */
typedef struct _cond_line
{
    def_cond *conditions;                   /* Conditions à vérifier       */
    size_t count;                           /* Taille de cette liste       */

    DisassCondGroup group;                  /* Type du groupe              */

} cond_line;

/* Représentation de l'ensemble de conditions préalables */
struct _disass_assert
{
    cond_line *lines;                       /* Lignes de conditions        */
    size_t count;                           /* Taille de cette liste       */

};


/* Définit le masque correspondant à une valeur booléenne. */
static char *get_disass_assert_mask(const char *);

/* Définit la valeur correspondant à une valeur booléenne. */
static char *get_disass_assert_value(const char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau gestionnaire de conditions de désassemblage. *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

disass_assert *create_disass_assert(void)
{
    disass_assert *result;                  /* Définition vierge à renvoyer*/

    result = (disass_assert *)calloc(1, sizeof(disass_assert));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = gestionnaire d'un ensemble de conditions à libérer.*
*                                                                             *
*  Description : Supprime de la mémoire un gestionnaire de conditions.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_disass_assert(disass_assert *dassert)
{
    size_t i;                               /* Boucle de parcours #1       */
    cond_line *line;                        /* Ligne à compléter           */
    size_t j;                               /* Boucle de parcours #2       */

    for (i = 0; i < dassert->count; i++)
    {
        line = &dassert->lines[i];

        for (j = 0; j < line->count; j++)
        {
            free(line->conditions[j].field);
            free(line->conditions[j].value);

            free(line->conditions[j].lower);

        }

        if (line->conditions != NULL)
            free(line->conditions);

    }

    if (dassert->lines != NULL)
        free(dassert->lines);

    free(dassert);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = gestionnaire de conditions à consulter.            *
*                group   = type du groupe de conditions attendues.            *
*                field   = champ de bits à prendre en compte.                 *
*                op      = type d'opération impliquée.                        *
*                value   = valeur soumise à condition.                        *
*                                                                             *
*  Description : Initie une nouvelle condition à vérifier.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_disass_assert(disass_assert *dassert, DisassCondGroup group, char *field, DisassCondOp op, char *value)
{
    cond_line *new;                         /* Nouvelle ligne de conditions*/

    dassert->lines = (cond_line *)realloc(dassert->lines,
                                          ++dassert->count * sizeof(cond_line));

    new = &dassert->lines[dassert->count - 1];

    new->conditions = NULL;
    new->count = 0;

    new->group = group;

    extend_disass_assert(dassert, field, op, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = gestionnaire de conditions à consulter.            *
*                field   = champ de bits à prendre en compte.                 *
*                op      = type d'opération impliquée.                        *
*                value   = valeur soumise à condition.                        *
*                                                                             *
*  Description : Enregistre une nouvelle condition à vérifier.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void extend_disass_assert(disass_assert *dassert, char *field, DisassCondOp op, char *value)
{
    cond_line *line;                        /* Ligne à compléter           */
    def_cond *new;                          /* Nouvelle définition         */

    assert(dassert->count > 0);

    line = &dassert->lines[dassert->count - 1];

    line->conditions = (def_cond *)realloc(line->conditions,
                                           ++line->count * sizeof(def_cond));

    new = &line->conditions[line->count - 1];

    new->field = field;
    new->op = op;
    new->value = value;

    new->lower = strdup(field);
    make_string_lower(new->lower);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = gestionnaire de conditions à consulter.            *
*                                                                             *
*  Description : Indique la présence de conditions à vérifier.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_disass_assert_empty(const disass_assert *dassert)
{
    bool result;                            /* Bilan à retourner           */

    result = (dassert->count == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = gestionnaire d'un ensemble de conditions à marquer.*
*                bits    = gestionnaire des bits d'encodage.                  *
*                                                                             *
*  Description : Marque les éléments de condition effectivement utilisés.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mark_disass_assert(const disass_assert *dassert, const coding_bits *bits)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    cond_line *line;                        /* Ligne de condition(s)       */
    size_t j;                               /* Boucle de parcours #2       */
    def_cond *cond;                         /* Condition à marquer         */
    raw_bitfield *rf;                       /* Champ de bits à marquer     */

    result = true;

    for (i = 0; i < dassert->count && result; i++)
    {
        line = &dassert->lines[i];

        for (j = 0; j < line->count && result; j++)
        {
            cond = &line->conditions[j];

            rf = find_named_field_in_bits(bits, cond->lower);

            if (rf == NULL)
            {
                fprintf(stderr, "Unknown bitfield '%s' for condition!\n", cond->field);
                result = false;
            }

            else
                mark_raw_bitfield_as_used(rf);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = gestionnaire d'un ensemble de conditions à définir.*
*                fd      = descripteur d'un flux ouvert en écriture.          *
*                bits    = gestionnaire des bits d'encodage.                  *
*                                                                             *
*  Description : Définit les éléments de condition à appliquer.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_disass_assert(const disass_assert *dassert, int fd, const coding_bits *bits)
{
    size_t i;                               /* Boucle de parcours #1       */
    cond_line *line;                        /* Ligne de condition(s)       */
    size_t j;                               /* Boucle de parcours #2       */
    def_cond *cond;                         /* Condition à marquer         */
    raw_bitfield *rf;                       /* Champ de bits à marquer     */
    char *mask;                             /* Eventuel masque à appliquer */
    char *expected;                         /* Valeur attendue             */

    for (i = 0; i < dassert->count; i++)
    {
        line = &dassert->lines[i];

        if (i > 0)
            dprintf(fd, " && ");

        if (dassert->count > 1 && line->count > 1)
            dprintf(fd, "(");

        for (j = 0; j < line->count; j++)
        {
            cond = &line->conditions[j];

            rf = find_named_field_in_bits(bits, cond->lower);

            assert(rf != NULL);

            if (j > 0)
                switch (line->group)
                {
                    case DCG_UNIQ:
                        assert(false);
                        break;

                    case DCG_AND:
                        dprintf(fd, " && ");
                        break;

                    case DCG_OR:
                        dprintf(fd, " || ");
                        break;

                }

            mask = get_disass_assert_mask(cond->value);

            if (mask == NULL)
                write_raw_bitfield(rf, fd);

            else
            {
                dprintf(fd, "(");

                write_raw_bitfield(rf, fd);

                dprintf(fd, " & %s)", mask);

                free(mask);

            }

            switch (cond->op)
            {
                case DCO_EQ:
                    dprintf(fd, " == ");
                    break;

                case DCO_NE:
                    dprintf(fd, " != ");
                    break;

            }

            expected = get_disass_assert_value(cond->value);

            dprintf(fd, "%s", expected);

            free(expected);

        }

        if (dassert->count > 1 && line->count > 1)
            dprintf(fd, ")");

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur booléenne à écrire.                           *
*                                                                             *
*  Description : Définit le masque correspondant à une valeur booléenne.      *
*                                                                             *
*  Retour      : Masque à appliquer (et libérer) ou NULL si aucun.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *get_disass_assert_mask(const char *value)
{
    char *result;                           /* Masque à renvoyer           */
    char *iter;                             /* Boucle de parcours          */

    if (strchr(value, 'x') == NULL)
        result = NULL;

    else
    {
        result = strdup(value);

        for (iter = result; *iter != '\0'; iter++)
            switch (*iter)
            {
                case '0':
                case '1':
                    *iter = '1';
                    break;

                case 'x':
                    *iter = '0';
                    break;

                default:
                    assert(false);
                    break;

            }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur booléenne à écrire.                           *
*                                                                             *
*  Description : Définit la valeur correspondant à une valeur booléenne.      *
*                                                                             *
*  Retour      : Valeur à comparer et libérer.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *get_disass_assert_value(const char *value)
{
    char *result;                           /* Masque à renvoyer           */
    char *iter;                             /* Boucle de parcours          */

    result = strdup(value);

    if (strchr(value, 'x') != NULL)
        for (iter = result; *iter != '\0'; iter++)
            switch (*iter)
            {
                case '0':
                case '1':
                    break;

                case 'x':
                    *iter = '0';
                    break;

                default:
                    assert(false);
                    break;

            }

    return result;

}
