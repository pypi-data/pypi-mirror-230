
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - gestion des arguments dans leur ensemble
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "manager.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../helpers.h"
#include "../conv/manager.h"



/* Types d'expressions représentés */
typedef enum _ConvExprType
{
    CET_NAME,                               /* Désignation de variable     */
    CET_NUMBER,                             /* Valeur codée en dur         */
    CET_BINVAL,                             /* Valeur binaire bxxx         */
    CET_HEXVAL,                             /* Valeur sous forme hexa.     */
    CET_STRING,                             /* Valeur sous forme de chaîne */
    CET_LOGICAL,                            /* Expression booléenne logique*/
    CET_COMPOSED,                           /* Agrégat de champs divers    */
    CET_UNARY,                              /* Opération unaire            */
    CET_CONDITIONAL,                        /* Valeur booléenne            */
    CET_BINARY,                             /* Opération binaire           */

    CET_COUNT

} ConvExprType;


/* Représentation d'une expression de conversion */
struct _arg_expr_t
{
    ConvExprType type;

    bool declared;                          /* Expression déjà déclarée ?  */
    bool defined;                           /* Expression déjà définie ?   */

    union
    {
        /* CET_NAME */
        struct
        {
            char *original;                 /* Désignation non transformée */
            char *name;                     /* Désignation de variable     */

        };

        /* CET_NUMBER */
        unsigned long number;               /* Valeur durablement définie  */

        /* CET_BINVAL */
        char *binval;                       /* Valeur sous forme bxxx      */

        /* CET_HEXVAL */
        char *hexval;                       /* Valeur sous forme 0xxxx     */

        /* CET_STRING */
        char *string;                       /* Chaîne "..." sans '"'       */

        /* CET_LOGICAL */
        struct
        {
            arg_expr_t *logical_expr1;      /* Expression à traiter        */
            arg_expr_t *logical_expr2;      /* Expression à traiter        */
            bool and_op;                    /* Type de condition booléenne */

        };

        /* CET_COMPOSED */
        struct
        {
            char **comp_items;              /* Elements à agréger          */
            size_t comp_count;              /* Quantité de ces éléments    */

        };

        /* CET_UNARY */
        struct
        {
            arg_expr_t *un_expr;            /* Expression à traiter        */
            ConvUnaryOperation un_op;       /* Type d'opération à mener    */

        };

        /* CET_CONDITIONAL */
        struct
        {
            arg_expr_t *cond_expr1;         /* Expression à traiter        */
            arg_expr_t *cond_expr2;         /* Expression à traiter        */
            bool cond_equal;                /* Type de condition booléenne */

        };

        /* CET_BINARY */
        struct
        {
            arg_expr_t *bin_expr1;          /* Expression à traiter        */
            arg_expr_t *bin_expr2;          /* Expression à traiter        */
            ConvBinaryOperation bin_op;     /* Type d'opération à mener    */

        };

    };

};


/* Visite une expression en traitant en premier ses composantes. */
typedef bool (* visit_expr_fc) (arg_expr_t *);

/* Visite une expression en traitant en premier ses composantes. */
static bool visit_arg_expr(arg_expr_t *, visit_expr_fc);

/* Retrouve si elle existe une variable manipulée. */
static bool find_var_by_name(const coding_bits *, const conv_list *, const char *, raw_bitfield **, conv_func **);



/* ----------------------- MANIPULATION DE LISTES D'ARGUMENTS ----------------------- */


/* Liste d'expressions utilisées en arguments de conversion */
struct _arg_list_t
{
    arg_expr_t **items;                     /* Liste d'expressions         */
    size_t count;                           /* Taille de cette liste       */

};



/* ---------------------------------------------------------------------------------- */
/*                            REPRESENTATION D'UN ARGUMENT                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation d'une variable quelconque.                *
*                                                                             *
*  Description : Référence une variable en tant qu'expression de conversion.  *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_arg_expr_from_name(char *name)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_NAME;

    result->original = strdup(name);
    result->name = make_string_lower(name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : number = valeur à conserver dans sa forme brute.             *
*                                                                             *
*  Description : Conserve une valeur en tant qu'expression de conversion.     *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_arg_expr_from_number(unsigned long number)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_NUMBER;

    result->number = number;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binval = valeur binaire à conserver dans sa forme brute.     *
*                                                                             *
*  Description : Conserve une valeur en tant qu'expression de conversion.     *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_arg_expr_from_binval(char *binval)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_BINVAL;

    result->binval = binval;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : number = valeur hexadécimale à conserver dans sa forme brute.*
*                                                                             *
*  Description : Conserve une valeur en tant qu'expression de conversion.     *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_arg_expr_from_hexval(char *hexval)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_HEXVAL;

    result->hexval = hexval;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : number = valeur hexadécimale à conserver dans sa forme brute.*
*                                                                             *
*  Description : Conserve une valeur en tant qu'expression de conversion.     *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_arg_expr_from_string(char *string)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_STRING;

    result->string = string;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr1 = première expression à utiliser.                      *
*                expr2 = seconde expression à utiliser.                       *
*                and_op = choix de l'opérateur ('&&' ou '||').                *
*                                                                             *
*  Description : Construit une base d'expression booléenne logique.           *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_logical_arg_expr(arg_expr_t *expr1, arg_expr_t *expr2, bool and_op)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_LOGICAL;

    result->logical_expr1 = expr1;
    result->logical_expr2 = expr2;
    result->and_op = and_op;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item1 = premier élément à agréger.                           *
*                item2 = second élément à agréger.                            *
*                                                                             *
*  Description : Construit une base d'expression de conversion composée.      *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_composed_arg_expr(char *item1, char *item2)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_COMPOSED;

    result->comp_items = (char **)calloc(2, sizeof(char *));
    result->comp_count = 2;

    result->comp_items[0] = make_string_lower(item1);
    result->comp_items[1] = make_string_lower(item2);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression déjà en place à compléter.                 *
*                item = nouvel élément à agréger.                             *
*                                                                             *
*  Description : Etend une base d'expression de conversion composée.          *
*                                                                             *
*  Retour      : Expression en place et mise à jour.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *extend_composed_arg_expr(arg_expr_t *expr, char *item)
{
    assert(expr->type == CET_COMPOSED);

    expr->comp_items = (char **)realloc(expr->comp_items, ++expr->comp_count * sizeof(char *));

    expr->comp_items[expr->comp_count - 1] = make_string_lower(item);

    return expr;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression à encapsuler.                              *
*                op   = opération unaire à associer à l'opération.            *
*                                                                             *
*  Description : Traduit une opération unaire sur expression de conversion.   *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_unary_arg_expr(arg_expr_t *expr, ConvUnaryOperation op)
{
    arg_expr_t *result;                     /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_UNARY;

    result->un_expr = expr;
    result->un_op = op;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr1 = première expression à encapsuler.                    *
*                expr2 = seconde expression à encapsuler.                     *
*                op    = opération binaire à associer à l'opération.          *
*                                                                             *
*  Description : Traduit une opération binaire sur expression de conversion.  *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_conditional_arg_expr(arg_expr_t *expr1, arg_expr_t *expr2, bool eq)
{
    arg_expr_t *result;                    /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_CONDITIONAL;

    result->cond_expr1 = expr1;
    result->cond_expr2 = expr2;
    result->cond_equal = eq;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr1 = première expression à encapsuler.                    *
*                expr2 = seconde expression à encapsuler.                     *
*                op    = opération binaire à associer à l'opération.          *
*                                                                             *
*  Description : Traduit une opération binaire sur expression de conversion.  *
*                                                                             *
*  Retour      : Nouvelle expression mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_expr_t *build_binary_arg_expr(arg_expr_t *expr1, arg_expr_t *expr2, ConvBinaryOperation op)
{
    arg_expr_t *result;                    /* Structure à retourner       */

    result = (arg_expr_t *)calloc(1, sizeof(arg_expr_t));

    result->type = CET_BINARY;

    result->bin_expr1 = expr1;
    result->bin_expr2 = expr2;
    result->bin_op = op;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression à libérer de la mémoire.                   *
*                                                                             *
*  Description : Supprime tous les éléments mis en place pour un argument.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_arg_expr(arg_expr_t *expr)
{
    size_t i;                               /* Boucle de parcours          */

    switch (expr->type)
    {
        case CET_NAME:
            free(expr->original);
            free(expr->name);
            break;

        case CET_BINVAL:
            free(expr->binval);
            break;

        case CET_HEXVAL:
            free(expr->hexval);
            break;

        case CET_LOGICAL:
            free(expr->logical_expr1);
            free(expr->logical_expr2);
            break;

        case CET_COMPOSED:
            for (i = 0; i < expr->comp_count; i++)
                free(expr->comp_items[i]);
            free(expr->comp_items);
            break;

        case CET_UNARY:
            delete_arg_expr(expr->un_expr);
            break;

        case CET_BINARY:
            delete_arg_expr(expr->bin_expr1);
            delete_arg_expr(expr->bin_expr2);
            break;

        default:
            break;

    }

    free(expr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = première expression à consulter.                      *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                size = taille déterminée avec précision. [OUT]               *
*                                                                             *
*  Description : Détermine la taille en bits d'une expression donnée.         *
*                                                                             *
*  Retour      : true si la taille a pu être déterminée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool compute_arg_expr_size(const arg_expr_t *expr, const coding_bits *bits, const conv_list *list, unsigned int *size)
{
    bool result;                            /* Bilan à retourner           */
    raw_bitfield *field;                    /* Eventuel champ brut associé */
    conv_func *func;                        /* Eventuelle fonction liée    */
    size_t i;                               /* Boucle de parcours          */
    unsigned int tmp;                       /* Stockage temporaire         */

    switch (expr->type)
    {
        case CET_NAME:

            result = find_var_by_name(bits, list, expr->name, &field, &func);

            if (result)
            {
                if (field != NULL)
                    *size = get_raw_bitfield_length(field);
                else
                    result = compute_conv_func_size(func, bits, list, size);
            }

            /**
             * On autorise le passage de constante inconnue par d2c mais valable pour gcc.
             */
            else result = true;

            break;

        case CET_COMPOSED:

            result = true;
            *size = 0;

            for (i = 0; i < expr->comp_count && result; i++)
            {
                if (isdigit(expr->comp_items[i][0]))
                    *size += strlen(expr->comp_items[i]);

                else
                {
                    if (!find_var_by_name(bits, list, expr->comp_items[i], &field, &func))
                        result = false;

                    else
                    {
                        if (field != NULL)
                            *size += get_raw_bitfield_length(field);
                        else
                        {
                            result = compute_conv_func_size(func, bits, list, &tmp);
                            *size += tmp;
                        }
                    }

                }

            }

            break;

        case CET_UNARY:
            result = compute_arg_expr_size(expr->un_expr, bits, list, size);
            break;

        case CET_BINARY:

            result = compute_arg_expr_size(expr->bin_expr1, bits, list, &tmp);

            if (result)
                result = compute_arg_expr_size(expr->bin_expr1, bits, list, size);

            if (tmp > *size) *size = tmp;

            break;

        default:
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = première expression encapsulée.                      *
*                visit = fonction à appeler pour chaque élément recontré.     *
*                                                                             *
*  Description : Visite une expression en traitant en premier ses composantes.*
*                                                                             *
*  Retour      : Bilan des traitements effectués.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool visit_arg_expr(arg_expr_t *expr, visit_expr_fc visit)
{
    bool result;                            /* Bilan à retourner           */

    switch (expr->type)
    {
        case CET_LOGICAL:
            result = visit_arg_expr(expr->logical_expr1, visit);
            if (result)
                result = visit_arg_expr(expr->logical_expr2, visit);
            break;

        case CET_UNARY:
            result = visit_arg_expr(expr->un_expr, visit);
            break;

        case CET_CONDITIONAL:
            result = visit_arg_expr(expr->cond_expr1, visit);
            if (result)
                result = visit_arg_expr(expr->cond_expr2, visit);
            break;

        case CET_BINARY:
            result = visit_arg_expr(expr->bin_expr1, visit);
            if (result)
                result = visit_arg_expr(expr->bin_expr2, visit);
            break;

        default:
            result = true;
            break;

    }

    if (result)
        result = visit(expr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits  = gestionnaire des bits d'encodage.                    *
*                list  = liste de l'ensemble des fonctions de conversion.     *
*                name  = déssignation de la variable recherchée.              *
*                field = éventuel élement brut de décodage.                   *
*                func  = éventuelle fonction de conversion pour intermédiaire.*
*                                                                             *
*  Description : Retrouve si elle existe une variable manipulée.              *
*                                                                             *
*  Retour      : Bilan des recherches : trouvaille ou non ?                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool find_var_by_name(const coding_bits *bits, const conv_list *list, const char *name, raw_bitfield **field, conv_func **func)
{
    bool result;                            /* Bilan à retourner           */
    raw_bitfield *cached_field;             /* Champ, version cachée       */
    conv_func *cached_func;                 /* Fonction, version cachée    */

    cached_field = find_named_field_in_bits(bits, name);
    result = (cached_field != NULL);

    if (!result)
    {
        cached_func = find_named_conv_in_list(list, name);
        result = (cached_func != NULL);
    }
    else
        cached_func = NULL;

    if (field != NULL) *field = cached_field;
    if (func != NULL) *func = cached_func;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = première expression à encapsuler.                     *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                                                                             *
*  Description : S'assure du marquage des expressions pre-requises.           *
*                                                                             *
*  Retour      : Bilan des traitements effectués.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_arg_expr_content_fully_marked(arg_expr_t *expr, const coding_bits *bits, const conv_list *list)
{
    bool mark_sub_expr(arg_expr_t *sub)
    {
        bool result;                        /* Bilan à retourner           */
        size_t i;                           /* Boucle de parcours          */

        bool mark_by_name(const char *name)
        {
            bool found;                     /* Bilan d'opération à renvoyer*/
            raw_bitfield *field;            /* Eventuel champ brut associé */
            conv_func *func;                /* Eventuelle fonction liée    */

            found = find_var_by_name(bits, list, name, &field, &func);

            if (found)
            {
                if (field != NULL)
                    mark_raw_bitfield_as_used(field);
                else /*if (func != NULL) */
                    mark_conv_func(func, true, bits, list);

            }

            return found;

        }

        /* Il est uniquement nécessaire de s'attacher aux références */
        switch (sub->type)
        {
            case CET_NAME:
                /* result = */mark_by_name(sub->name);
                result = true;
                break;

            case CET_COMPOSED:
                result = true;
                for (i = 0; i < sub->comp_count && result; i++)
                    if (!isdigit(sub->comp_items[i][0]))
                        result = mark_by_name(sub->comp_items[i]);
                break;

            default:
                result = true;
                break;

        }

        return result;

    }

    return visit_arg_expr(expr, (visit_expr_fc)mark_sub_expr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = première expression à encapsuler.                     *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                arch = architecture visée par l'opération globale.           *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                tab  = décalage éventuel selon l'inclusion.                  *
*                                                                             *
*  Description : S'assure de la déclaration des expressions pre-requises.     *
*                                                                             *
*  Retour      : Bilan des traitements effectués.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_arg_expr_content_fully_declared(arg_expr_t *expr, int fd, const coding_bits *bits, const conv_list *list, const char *tab)
{
    bool declare_sub_expr(arg_expr_t *sub)
    {
        bool result;                        /* Bilan à retourner           */
        size_t i;                           /* Boucle de parcours          */

        /**
         * Si l'expression a déjà été définie lors d'un précédent besoin...
         */

        if (sub->declared) return true;

        bool declare_by_name(const char *name)
        {
            bool found;                     /* Bilan d'opération à renvoyer*/
            conv_func *func;                /* Eventuelle fonction liée    */

            found = find_var_by_name(bits, list, name, NULL, &func);

            if (found && func != NULL)
                found = declare_conv_func(func, fd, bits, list, tab);

            return found;

        }

        /* Il est uniquement nécessaire de s'attacher aux références */
        switch (sub->type)
        {
            case CET_NAME:
                /* result = */declare_by_name(sub->name);
                result = true;
                break;

            case CET_COMPOSED:
                result = true;
                for (i = 0; i < sub->comp_count && result; i++)
                    if (!isdigit(sub->comp_items[i][0]))
                        result = declare_by_name(sub->comp_items[i]);
                break;

            default:
                result = true;
                break;

        }

        sub->declared = result;

        return result;

    }

    return visit_arg_expr(expr, (visit_expr_fc)declare_sub_expr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = première expression à encapsuler.                     *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                tab  = décalage éventuel selon l'inclusion.                  *
*                exit = exprime le besoin d'une voie de sortie. [OUT]         *
*                                                                             *
*  Description : S'assure de la définition des expressions pre-requises.      *
*                                                                             *
*  Retour      : Bilan des traitements effectués.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_arg_expr_content_fully_defined(arg_expr_t *expr, int fd, const coding_bits *bits, const conv_list *list, const char *tab, bool *exit)
{
    bool define_sub_expr(arg_expr_t *sub)
    {
        bool result;                        /* Bilan à retourner           */
        size_t i;                           /* Boucle de parcours          */

        /* Si l'expression a déjà été définie lors d'un précédent besoin... */
        if (sub->defined) return true;

        bool define_by_name(const char *name)
        {
            bool found;                     /* Bilan d'opération à renvoyer*/
            conv_func *func;                /* Eventuelle fonction liée    */

            found = find_var_by_name(bits, list, name, NULL, &func);

            if (found && func != NULL)
                found = define_conv_func(func, fd, bits, list, tab, false, exit);

            return found;

        }

        /* Il est uniquement nécessaire de s'attacher aux références */
        switch (sub->type)
        {
            case CET_NAME:
                /* result = */define_by_name(sub->name);
                result = true;
                break;

            case CET_COMPOSED:
                result = true;
                for (i = 0; i < sub->comp_count && result; i++)
                    if (!isdigit(sub->comp_items[i][0]))
                        result = define_by_name(sub->comp_items[i]);
                break;

            default:
                result = true;
                break;

        }

        sub->defined = result;

        return result;

    }

    return visit_arg_expr(expr, (visit_expr_fc)define_sub_expr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = première expression à encapsuler.                     *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                                                                             *
*  Description : Définit une expression utilisée dans une conversion.         *
*                                                                             *
*  Retour      : Bilan des traitements effectués.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_arg_expr(const arg_expr_t *expr, int fd, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à retourner           */
    raw_bitfield *field;                    /* Eventuel champ brut associé */
    conv_func *func;                        /* Eventuelle fonction liée    */
    unsigned int max_size;                  /* Quantité de bits totale     */
    size_t i;                               /* Boucle de parcours          */
    const char *cname;                      /* Raccourci de confort        */
    unsigned int used_size;                 /* Quantité de bits utilisée   */

    result = true;

    switch (expr->type)
    {
        case CET_NAME:

            if (!find_var_by_name(bits, list, expr->name, &field, &func))
                dprintf(fd, "%s", expr->original);

            else
            {
                if (field != NULL)
                    write_raw_bitfield(field, fd);
                else
                    write_conv_func(func, fd, true);
            }

            break;

        case CET_NUMBER:
            dprintf(fd, "%lu", expr->number);
            break;

        case CET_BINVAL:
            dprintf(fd, "b%s", expr->binval);
            break;

        case CET_HEXVAL:
            dprintf(fd, "0x%s", expr->hexval);
            break;

        case CET_STRING:
            dprintf(fd, "\"%s\"", expr->string);
            break;

        case CET_LOGICAL:

            result = define_arg_expr(expr->logical_expr1, fd, bits, list);

            dprintf(fd, expr->and_op ? " && " : " || ");

            result &= define_arg_expr(expr->logical_expr2, fd, bits, list);

            break;

        case CET_COMPOSED:

            result = compute_arg_expr_size(expr, bits, list, &max_size);

            if (result && expr->comp_count > 1)
                dprintf(fd, "(");

            for (i = 0; i < expr->comp_count && result; i++)
            {
                cname = expr->comp_items[i];

                if (i > 0)
                    dprintf(fd, " | ");

                /* Constante binaire ? */
                if (isdigit(cname[0]))
                {
                    max_size -= strlen(cname);

                    if (max_size == 0)
                        dprintf(fd, "b%s", cname);
                    else
                        dprintf(fd, "b%s << %u", cname, max_size);

                }

                /* Ou variable définie ? */
                else
                {
                    result = find_var_by_name(bits, list, cname, &field, &func);

                    if (result)
                    {
                        if (field != NULL)
                            used_size = get_raw_bitfield_length(field);
                        else
                            /*result = */compute_conv_func_size(func, bits, list, &used_size);

                        max_size -= used_size;

                        if (field != NULL)
                        {
                            write_raw_bitfield(field, fd);
                            if (max_size > 0)
                                dprintf(fd, " << %u", max_size);
                        }
                        else
                        {
                            write_conv_func(func, fd, true);
                            if (max_size > 0)
                                dprintf(fd, " << %u", max_size);
                        }

                    }

                }

            }

            if (result && expr->comp_count > 1)
                dprintf(fd, ")");

            break;

        case CET_UNARY:

            switch (expr->un_op)
            {
                case CUO_NOT:
                    dprintf(fd, "(");
                    break;
                default:
                    result = false;
                    break;
            }

            if (result)
                result = define_arg_expr(expr->un_expr, fd, bits, list);

            if (result)
                result = compute_arg_expr_size(expr, bits, list, &max_size);

            if (result)
                switch (expr->un_op)
                {
                    case CUO_NOT:
                        dprintf(fd, " ^ ");
                        if (max_size >= 64)
                            dprintf(fd, "0xffffffffffffffff");
                        else
                            dprintf(fd, "0x%x", (1 << max_size) - 1);
                        dprintf(fd, ")");
                        break;
                    default:
                        break;
                }

            break;

        case CET_CONDITIONAL:

            dprintf(fd, "(");

            result = define_arg_expr(expr->cond_expr1, fd, bits, list);

            if (expr->cond_equal)
                dprintf(fd, " == ");
            else
                dprintf(fd, " != ");

            result &= define_arg_expr(expr->cond_expr2, fd, bits, list);

            dprintf(fd, ")");

            break;

        case CET_BINARY:

            dprintf(fd, "(");

            result = define_arg_expr(expr->bin_expr1, fd, bits, list);

            switch (expr->bin_op)
            {
                case CBO_AND:
                    dprintf(fd, " & ");
                    break;
                case CBO_EOR:
                    dprintf(fd, " ^ ");
                    break;
                case CBO_LSHIFT:
                    dprintf(fd, " << ");
                    break;
                default:
                    result = false;
                    break;
            }

            result &= define_arg_expr(expr->bin_expr2, fd, bits, list);

            dprintf(fd, ")");

            break;

        default:
            result = false;
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         MANIPULATION DE LISTES D'ARGUMENTS                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une liste vide d'arguments de conversion.               *
*                                                                             *
*  Retour      : Nouvelle structure mise en place.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_list_t *build_empty_arg_list(void)
{
    arg_list_t *result;                     /* Structure à retourner       */

    result = (arg_list_t *)calloc(1, sizeof(arg_list_t));

    result->items = NULL;
    result->count = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression initial pour constituer une liste.         *
*                                                                             *
*  Description : Crée une liste d'arguments de conversion.                    *
*                                                                             *
*  Retour      : Nouvelle structure mise en place.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_list_t *build_arg_list(arg_expr_t *expr)
{
    arg_list_t *result;                     /* Structure à retourner       */

    result = (arg_list_t *)calloc(1, sizeof(arg_list_t));

    result->items = (arg_expr_t **)calloc(1, sizeof(arg_expr_t *));
    result->count = 1;

    result->items[0] = expr;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste d'expressions à supprimer de la mémoire.        *
*                                                                             *
*  Description : Libère la mémoire occupée par une liste d'expressions.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_arg_list(arg_list_t *list)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < list->count; i++)
        delete_arg_expr(list->items[i]);

    if (list->items != NULL)
        free(list->items);

    free(list);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste d'expressions à supprimer de la mémoire. [OUT]  *
*                expr = expression à ajouter à la liste courante.             *
*                                                                             *
*  Description : Ajoute un élément à une liste d'arguments de conversion.     *
*                                                                             *
*  Retour      : Structure en place mise à jour.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

arg_list_t *extend_arg_list(arg_list_t *list, arg_expr_t *expr)
{
    list->items = (arg_expr_t **)realloc(list->items, ++list->count * sizeof(arg_expr_t *));

    list->items[list->count - 1] = expr;

    return list;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : args = liste d'expressions à traiter.                        *
*                                                                             *
*  Description : Indique le nombre d'arguments présents dans la liste.        *
*                                                                             *
*  Retour      : Nombre positif ou nul.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#ifndef NDEBUG
size_t get_arg_list_size(const arg_list_t *args)
{
    return args->count;

}
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : args = liste d'expressions à supprimer de la mémoire.        *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                                                                             *
*  Description : S'assure du marquage des expressions pre-requises.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_arg_list_content_fully_marked(arg_list_t *args, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à remonter            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < args->count && result; i++)
        result = ensure_arg_expr_content_fully_marked(args->items[i], bits, list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : args = liste d'expressions à supprimer de la mémoire.        *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                tab  = décalage éventuel selon l'inclusion.                  *
*                                                                             *
*  Description : S'assure de la déclaration des expressions pre-requises.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_arg_list_content_fully_declared(arg_list_t *args, int fd, const coding_bits *bits, const conv_list *list, const char *tab)
{
    bool result;                            /* Bilan à remonter            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < args->count && result; i++)
        result = ensure_arg_expr_content_fully_declared(args->items[i], fd, bits, list, tab);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : args = liste d'expressions à supprimer de la mémoire.        *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                tab  = décalage éventuel selon l'inclusion.                  *
*                exit = exprime le besoin d'une voie de sortie. [OUT]         *
*                                                                             *
*  Description : S'assure de la définition des expressions pre-requises.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_arg_list_content_fully_defined(arg_list_t *args, int fd, const coding_bits *bits, const conv_list *list, const char *tab, bool *exit)
{
    bool result;                            /* Bilan à remonter            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < args->count && result; i++)
        result = ensure_arg_expr_content_fully_defined(args->items[i], fd, bits, list, tab, exit);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : args = liste d'expressions à supprimer de la mémoire.        *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                                                                             *
*  Description : Définit les variables associées à un appel de fonction.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_arg_list(const arg_list_t *args, int fd, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à remonter            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < args->count && result; i++)
    {
        if (i > 0) dprintf(fd, ", ");
        result = define_arg_expr(args->items[i], fd, bits, list);
    }

    return result;

}
