
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour les variations de décodage selon certaines conditions
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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
#include <stdbool.h>
#include <string.h>


#include "../helpers.h"
#include "../qckcall.h"



/* -------------------------- CONDITIONS DE DECLENCHEMENTS -------------------------- */


/* Type d'informations contenues */
typedef enum _CondExprType
{
    CET_NAMED,                              /* Référence à une variable    */
    CET_SIMPLE,                             /* Version simple              */
    CET_COMPOSED                            /* Version composée            */

} CondExprType;

/* Expression d'une condition */
struct _cond_expr
{
    CondExprType type;                      /* Sélection de champ          */

    union
    {
        char *named;                        /* Référence à une variable    */

        struct
        {
            char *variable;                 /* Variable manipulée          */
            CondCompType comp;              /* Type de comparaison         */
            char *value;                    /* Valeur binaire comparée     */

            bool is_binary;                 /* Binaire ou hexadécimal      */

        } simple;

        struct
        {
            cond_expr *a;                   /* Première sous-expression    */
            CondOpType operator;            /* Relation entre expressions  */
            cond_expr *b;                   /* Seconde sous-expression     */

        } composed;

    };

};


/* Libère de la mémoire une expression conditionnelle. */
static void delete_cond_expr(cond_expr *);

/* Marque les éléments de conditions comme utilisés. */
static bool mark_cond_expr(const cond_expr *, const coding_bits *, const conv_list *);

/* Traduit en code une expression de condition. */
static bool write_cond_expr(const cond_expr *, int, const coding_bits *, const conv_list *);



/* ------------------------- REGLES ET ACTIONS CONSEQUENTES ------------------------- */


/* Règle particulière */
typedef struct _extra_rule
{
    cond_expr *expr;                        /* Expression de déclenchement */
    rule_action action;                     /* Conséquence d'une validation*/

} extra_rule;

/* Règles de décodage supplémentaires */
struct _decoding_rules
{
    extra_rule *extra;                      /* Règles conditionnelles      */
    size_t extra_count;                     /* Nombre de ces règles        */

};



/* ---------------------------------------------------------------------------------- */
/*                            CONDITIONS DE DECLENCHEMENTS                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : variable  = désignation de la variable à manipuler.          *
*                                                                             *
*  Description : Crée une expression conditionnelle reposant sur une variable.*
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

cond_expr *build_named_cond_expression(char *variable)
{
    cond_expr *result;                      /* Structure à retourner       */

    result = (cond_expr *)calloc(1, sizeof(cond_expr));

    result->type = CET_NAMED;

    result->named = make_string_lower(variable);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : variable  = désignation de la variable à manipuler.          *
*                comp      = type de comparaison à utiliser.                  *
*                value     = valeur binaire à comparer.                       *
*                is_binary = indique la nature de la valeur transmise.        *
*                                                                             *
*  Description : Crée une expression conditionnelle simple.                   *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

cond_expr *build_simple_cond_expression(char *variable, CondCompType comp, char *value, bool is_binary)
{
    cond_expr *result;                      /* Structure à retourner       */

    result = (cond_expr *)calloc(1, sizeof(cond_expr));

    result->type = CET_SIMPLE;

    result->simple.variable = make_string_lower(variable);
    result->simple.comp = comp;
    result->simple.value = value;

    result->simple.is_binary = is_binary;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a        = première expression à intégrer.                   *
*                operator = type de comparaison à utiliser.                   *
*                b        = second expression à intégrer.                     *
*                                                                             *
*  Description : Crée une expression conditionnelle composée.                 *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

cond_expr *build_composed_cond_expression(cond_expr *a, CondOpType operator, cond_expr *b)
{
    cond_expr *result;                      /* Structure à retourner       */

    result = (cond_expr *)calloc(1, sizeof(cond_expr));

    result->type = CET_COMPOSED;

    result->composed.a = a;
    result->composed.operator = operator;
    result->composed.b = b;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = représentation d'expression à traiter.                *
*                                                                             *
*  Description : Libère de la mémoire une expression conditionnelle.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_cond_expr(cond_expr *expr)
{
    switch (expr->type)
    {
        case CET_NAMED:
            free(expr->named);
            break;

        case CET_SIMPLE:
            free(expr->simple.variable);
            free(expr->simple.value);
            break;

        case CET_COMPOSED:
            delete_cond_expr(expr->composed.a);
            delete_cond_expr(expr->composed.b);
            break;

    }

    free(expr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression simple ou composée à transposer.           *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                                                                             *
*  Description : Marque les éléments de conditions comme utilisés.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool mark_cond_expr(const cond_expr *expr, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan de marquage à renvoyer*/

    result = false;

    bool mark_cond_expr_by_name(const char *name)
    {
        conv_func *conv;                        /* Conversion utilisée         */
        bool status;                            /* Bilan d'un marquage         */
        raw_bitfield *bf;                       /* Champ de bits utilisé       */

        conv = find_named_conv_in_list(list, name);

        if (conv != NULL)
            status = mark_conv_func(conv, true, bits, list);

        else
        {
            bf = find_named_field_in_bits(bits, name);

            if (bf != NULL)
            {
                mark_raw_bitfield_as_used(bf);
                status = true;
            }

            else status = false;

        }

        if (!status)
            fprintf(stderr, "Error: nothing defined for the requested variable '%s'.\n", name);

        return status;

    }

    switch (expr->type)
    {
        case CET_NAMED:
            result = mark_cond_expr_by_name(expr->named);
            break;

        case CET_SIMPLE:
            result = mark_cond_expr_by_name(expr->simple.variable);
            break;

        case CET_COMPOSED:
            result = mark_cond_expr(expr->composed.a, bits, list);
            result &= mark_cond_expr(expr->composed.b, bits, list);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression simple ou composée à transposer.           *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                                                                             *
*  Description : Traduit en code une expression de condition.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool write_cond_expr(const cond_expr *expr, int fd, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à renvoyer            */
    const conv_func *conv;                  /* Conversion utilisée         */
    const raw_bitfield *bf;                 /* Champ de bits de définition */
    unsigned int provided;                  /* Nombre de bits fournis      */

    result = true;

    dprintf(fd, "(");

    switch (expr->type)
    {
        case CET_NAMED:

            conv = find_named_conv_in_list(list, expr->named);

            if (conv != NULL)
                dprintf(fd, "val_%s", expr->named);

            else
            {
                bf = find_named_field_in_bits(bits, expr->named);
                assert(bf != NULL);

                dprintf(fd, "raw_%s", expr->named);

            }

            break;

        case CET_SIMPLE:

            bf = find_named_field_in_bits(bits, expr->simple.variable);
            if (bf == NULL)
            {
                fprintf(stderr, "Error: no bitfield defined the requested variable '%s'.\n",
                        expr->simple.variable);
                result = false;
                goto wce_exit;
            }

            if (expr->simple.is_binary)
                provided = strlen(expr->simple.value);
            else
                provided = 4 * strlen(expr->simple.value);

            if (get_raw_bitfield_length(bf) != provided)
            {
                fprintf(stderr, "Error: variable '%s' and provided value sizes do not match (%u vs %u).\n",
                        expr->simple.variable, get_raw_bitfield_length(bf), provided);
                result = false;
                goto wce_exit;
            }

            dprintf(fd, "raw_%s", expr->simple.variable);

            switch (expr->simple.comp)
            {
                case CCT_EQUAL:
                    dprintf(fd, " == ");
                    break;
                case CCT_DIFF:
                    dprintf(fd, " != ");
                    break;
                case CCT_AND:
                    dprintf(fd, " & ");
                    break;
            }

            if (expr->simple.is_binary)
                dprintf(fd, "b%s", expr->simple.value);
            else
                dprintf(fd, "0x%s", expr->simple.value);

            break;

        case CET_COMPOSED:

            result = write_cond_expr(expr->composed.a, fd, bits, list);
            if (!result) goto wce_exit;

            switch (expr->composed.operator)
            {
                case COT_AND:
                    dprintf(fd, " && ");
                    break;
                case COT_OR:
                    dprintf(fd, " || ");
                    break;
            }

            result = write_cond_expr(expr->composed.b, fd, bits, list);
            if (!result) goto wce_exit;

            break;

    }

    dprintf(fd, ")");

 wce_exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           REGLES ET ACTIONS CONSEQUENTES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau rassemblement de règles de décodage.         *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

decoding_rules *create_decoding_rules(void)
{
    decoding_rules *result;                       /* Définition vierge à renvoyer*/

    result = (decoding_rules *)calloc(1, sizeof(decoding_rules));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rules = ensemble de règles de décodage à supprimer.          *
*                                                                             *
*  Description : Supprime de la mémoire un ensemble de règles supplémentaires.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_decoding_rules(decoding_rules *rules)
{
    size_t i;                               /* Boucle de parcours          */
    extra_rule *rule;                       /* Règle à traiter             */

    for (i = 0; i < rules->extra_count; i++)
    {
        rule = &rules->extra[i];

        if (rule->expr != NULL)
            delete_cond_expr(rule->expr);

        switch (rule->action.type)
        {
            case CAT_UNPREDICTABLE:
                break;

            case CAT_CALL:
            case CAT_CHECKED_CALL:
                free(rule->action.callee);
                delete_arg_list(rule->action.args);
                break;

        }

    }

    if (rules->extra != NULL)
        free(rules->extra);

    free(rules);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rules   = ensemble de règles à compléter.                    *
*                expr    = représentation d'expression à conserver.           *
*                action  = conséquence associée à la règle.                   *
*                                                                             *
*  Description : Ajoute une règle complète à la définition d'un codage.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_conditional_rule(decoding_rules *rules, cond_expr *expr, const rule_action *action)
{
    extra_rule *rule;                       /* Nouvelle prise en compte    */

    rules->extra = (extra_rule *)realloc(rules->extra, ++rules->extra_count * sizeof(extra_rule));

    rule = &rules->extra[rules->extra_count - 1];

    rule->expr = expr;
    rule->action = *action;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rules = ensemble de règles à manipuler.                      *
*                bits  = gestionnaire des bits d'encodage.                    *
*                list  = liste de l'ensemble des fonctions de conversion.     *
*                                                                             *
*  Description : Marque les éléments de règles effectivement utilisés.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mark_decoding_rules(const decoding_rules *rules, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    const extra_rule *rule;                 /* Règle en cours d'écriture   */

    result = true;

    for (i = 0; i < rules->extra_count && result; i++)
    {
        rule = &rules->extra[i];

        if (rule->expr != NULL)
            result = mark_cond_expr(rule->expr, bits, list);

        switch (rule->action.type)
        {
            case CAT_CALL:
            case CAT_CHECKED_CALL:
                result &= ensure_arg_list_content_fully_marked(rule->action.args, bits, list);
                break;

            default:
                break;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rules  = ensemble de règles à consulter.                     *
*                filter = filtre sur les règles à effectivement imprimer.     *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                arch   = architecture visée par l'opération.                 *
*                bits   = gestionnaire des bits d'encodage.                   *
*                list   = liste de l'ensemble des fonctions de conversion.    *
*                tab    = décalage éventuel selon l'inclusion.                *
*                exit   = exprime le besoin d'une voie de sortie. [OUT]       *
*                                                                             *
*  Description : Traduit en code les éventuelles règles présentes.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_decoding_rules(decoding_rules *rules, CondActionType filter, int fd, const char *arch, const coding_bits *bits, const conv_list *list, const char *tab, bool *exit)
{
    bool result;                            /* Bilan à remonter            */
    size_t i;                               /* Boucle de parcours          */
    const extra_rule *rule;                 /* Règle en cours d'écriture   */
    bool multi_lines;                       /* Nécessite des accolades     */
    const char *callable;                   /* Fonction à appeler          */

    result = true;

    for (i = 0; i < rules->extra_count; i++)
    {
        rule = &rules->extra[i];

        if (rule->action.type != filter)
            continue;

        switch (rule->action.type)
        {
            case CAT_CALL:
            case CAT_CHECKED_CALL:
                multi_lines = false;
                break;

            default:
                multi_lines = true;
                break;

        }

        if (rule->expr != NULL)
        {
            dprintf(fd, "\t%sif ", tab);

            result = write_cond_expr(rule->expr, fd, bits, list);
            if (!result) break;

            dprintf(fd, "\n");

            if (multi_lines)
                dprintf(fd, "\t%s{\n", tab);

        }

        switch (rule->action.type)
        {
            case CAT_UNPREDICTABLE:
                break;

            case CAT_CALL:

                /*
                callable = find_macro(pp, rule->action.callee);

                if (callable == NULL)
                */
                    callable = rule->action.callee;

                if (rule->expr != NULL)
                    dprintf(fd, "\t");

                dprintf(fd, "%s", tab);

                result = call_instr_func(callable, rule->action.args, fd, bits, list);

                break;

            case CAT_CHECKED_CALL:

                /*
                callable = find_macro(pp, rule->action.callee);

                if (callable == NULL)
                */
                    callable = rule->action.callee;

                if (rule->expr != NULL)
                    dprintf(fd, "\t");

                dprintf(fd, "%s", tab);

                result = checked_call_instr_func(callable, rule->action.args, fd, bits, list);

                if (rule->expr != NULL)
                    dprintf(fd, "\t");

                dprintf(fd, "\t\t%sgoto bad_exit;\n", tab);

                *exit = true;
                break;

        }

        if (rule->expr != NULL && multi_lines)
            dprintf(fd, "\t%s}\n", tab);

        dprintf(fd, "\n");

    }

    return result;

}
