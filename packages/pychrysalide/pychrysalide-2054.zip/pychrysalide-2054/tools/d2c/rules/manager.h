
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


#ifndef _TOOLS_D2C_RULES_MANAGER_H
#define _TOOLS_D2C_RULES_MANAGER_H


#include "../args/manager.h"
#include "../bits/manager.h"
#include "../conv/manager.h"



/* -------------------------- CONDITIONS DE DECLENCHEMENTS -------------------------- */


/* Types de comparaison */
typedef enum _CondCompType
{
    CCT_EQUAL,                              /* Egalité '=='                */
    CCT_DIFF,                               /* Différence '!='             */
    CCT_AND                                 /* Et logique '&'              */

} CondCompType;

/* Types de combinaison d'expressions */
typedef enum _CondOpType
{
    COT_AND,                                /* Combinaison ET ('&&')       */
    COT_OR                                  /* Combinaison OU ('||')       */

} CondOpType;

/* Expression d'une condition */
typedef struct _cond_expr cond_expr;


/* Crée une expression conditionnelle reposant sur une variable. */
cond_expr *build_named_cond_expression(char *);

/* Crée une expression conditionnelle simple. */
cond_expr *build_simple_cond_expression(char *, CondCompType, char *, bool);

/* Crée une expression conditionnelle composée. */
cond_expr *build_composed_cond_expression(cond_expr *, CondOpType, cond_expr *);



/* ------------------------- REGLES ET ACTIONS CONSEQUENTES ------------------------- */


/* Conséquence en cas de condition remplie */
typedef enum _CondActionType
{
    CAT_UNPREDICTABLE,                      /* Cas de figure improbable    */
    CAT_CALL,                               /* Appel à une fonction C      */
    CAT_CHECKED_CALL                        /* Appel à une fonction C      */

} CondActionType;

/* Définition d'une action de règle */
typedef struct _rule_action
{
    CondActionType type;                    /* Conséquence d'une validation*/

    union
    {
        /* CAT_CALL / CAT_CHECKED_CALL */
        struct
        {
            char *callee;                   /* Fonction appelée            */
            arg_list_t *args;               /* Arguments à fournir         */

        };

    };

} rule_action;

/* Règles de décodage supplémentaires */
typedef struct _decoding_rules decoding_rules;


/* Crée un nouveau rassemblement de règles de décodage. */
decoding_rules *create_decoding_rules(void);

/* Supprime de la mémoire un ensemble de règles supplémentaires. */
void delete_decoding_rules(decoding_rules *);

/* Ajoute une règle complète à la définition d'un codage. */
void register_conditional_rule(decoding_rules *, cond_expr *, const rule_action *);

/* Marque les éléments de règles effectivement utilisés. */
bool mark_decoding_rules(const decoding_rules *, const coding_bits *, const conv_list *);

/* Traduit en code les éventuelles règles présentes. */
bool write_decoding_rules(decoding_rules *, CondActionType, int, const char *, const coding_bits *, const conv_list *, const char *, bool *);



#endif  /* _TOOLS_D2C_RULES_MANAGER_H */
