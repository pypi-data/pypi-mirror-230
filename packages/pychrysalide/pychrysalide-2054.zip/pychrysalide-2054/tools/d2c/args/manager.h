
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour la gestion des arguments dans leur ensemble
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


#ifndef _TOOLS_D2C_ARGS_MANAGER_H
#define _TOOLS_D2C_ARGS_MANAGER_H


#ifndef NDEBUG
#   include <sys/types.h>
#endif

#include "../bits/manager.h"


/* Liste des fonctions de conversions présentes */
typedef struct _conv_list conv_list;



/* -------------------------- REPRESENTATION D'UN ARGUMENT -------------------------- */


/* Types d'opérations unaires */
typedef enum _ConvUnaryOperation
{
    CUO_NOT,                                /* NOT (booléen)               */

    CUO_COUNT

} ConvUnaryOperation;

/* Types d'opérations binaires */
typedef enum _ConvBinaryOperation
{
    CBO_AND,                                /* Et logique                  */
    CBO_EOR,                                /* Ou exclusif (booléen)       */
    CBO_LSHIFT,                             /* Décalage à gauche           */

    CBO_COUNT

} ConvBinaryOperation;


/* Représentation d'une expression de conversion */
typedef struct _arg_expr_t arg_expr_t;


/* Référence une variable en tant qu'expression de conversion. */
arg_expr_t *build_arg_expr_from_name(char *);

/* Conserve une valeur en tant qu'expression de conversion. */
arg_expr_t *build_arg_expr_from_number(unsigned long );

/* Conserve une valeur en tant qu'expression de conversion. */
arg_expr_t *build_arg_expr_from_binval(char *);

/* Conserve une valeur en tant qu'expression de conversion. */
arg_expr_t *build_arg_expr_from_hexval(char *);

/* Conserve une valeur en tant qu'expression de conversion. */
arg_expr_t *build_arg_expr_from_string(char *);

/* Construit une base d'expression booléenne logique. */
arg_expr_t *build_logical_arg_expr(arg_expr_t *, arg_expr_t *, bool);

/* Construit une base d'expression de conversion composée. */
arg_expr_t *build_composed_arg_expr(char *, char *);

/* Etend une base d'expression de conversion composée. */
arg_expr_t *extend_composed_arg_expr(arg_expr_t *, char *);

/* Traduit une opération unaire sur expression de conversion. */
arg_expr_t *build_unary_arg_expr(arg_expr_t *, ConvUnaryOperation);

/* Traduit une opération binaire sur expression de conversion. */
arg_expr_t *build_conditional_arg_expr(arg_expr_t *, arg_expr_t *, bool);

/* Traduit une opération binaire sur expression de conversion. */
arg_expr_t *build_binary_arg_expr(arg_expr_t *, arg_expr_t *, ConvBinaryOperation);

/* Supprime tous les éléments mis en place pour un argument. */
void delete_arg_expr(arg_expr_t *);

/* Détermine la taille en bits d'une expression donnée. */
bool compute_arg_expr_size(const arg_expr_t *, const coding_bits *, const conv_list *, unsigned int *);

/* S'assure du marquage des expressions pre-requises. */
bool ensure_arg_expr_content_fully_marked(arg_expr_t *, const coding_bits *, const conv_list *);

/* S'assure de la déclaration des expressions pre-requises. */
bool ensure_arg_expr_content_fully_declared(arg_expr_t *, int, const coding_bits *, const conv_list *, const char *);

/* S'assure de la définition des expressions pre-requises. */
bool ensure_arg_expr_content_fully_defined(arg_expr_t *, int, const coding_bits *, const conv_list *, const char *, bool *);

/* Définit une expression utilisée dans une conversion. */
bool define_arg_expr(const arg_expr_t *, int, const coding_bits *, const conv_list *);



/* ----------------------- MANIPULATION DE LISTES D'ARGUMENTS ----------------------- */


/* Liste d'expressions utilisées en arguments de conversion */
typedef struct _arg_list_t arg_list_t;


/* Crée une liste vide d'arguments de conversion. */
arg_list_t *build_empty_arg_list(void);

/* Crée une liste d'arguments de conversion. */
arg_list_t *build_arg_list(arg_expr_t *);

/* Libère la mémoire occupée par une liste d'expressions. */
void delete_arg_list(arg_list_t *);

/* Ajoute un élément à une liste d'arguments de conversion. */
arg_list_t *extend_arg_list(arg_list_t *, arg_expr_t *);

/* Indique le nombre d'arguments présents dans la liste. */
#ifndef NDEBUG
size_t get_arg_list_size(const arg_list_t *);
#endif

/* S'assure du marquage des expressions pre-requises. */
bool ensure_arg_list_content_fully_marked(arg_list_t *, const coding_bits *, const conv_list *);

/* S'assure de la déclaration des expressions pre-requises. */
bool ensure_arg_list_content_fully_declared(arg_list_t *, int, const coding_bits *, const conv_list *, const char *);

/* S'assure de la définition des expressions pre-requises. */
bool ensure_arg_list_content_fully_defined(arg_list_t *, int, const coding_bits *, const conv_list *, const char *, bool *);

/* Définit les variables associées à un appel de fonction. */
bool define_arg_list(const arg_list_t *, int, const coding_bits *, const conv_list *);



#endif  /* _TOOLS_D2C_ARGS_MANAGER_H */
