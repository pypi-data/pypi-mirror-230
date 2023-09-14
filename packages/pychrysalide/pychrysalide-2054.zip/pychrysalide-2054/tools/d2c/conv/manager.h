
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour les substitutions de valeurs depuis un contenu binaire
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


#ifndef _TOOLS_D2C_CONV_MANAGER_H
#define _TOOLS_D2C_CONV_MANAGER_H


#include <stdbool.h>


#include "../pproc.h"
#include "../args/manager.h"
#include "../bits/manager.h"



/* ---------------------------- CONVERSION DES ARGUMENTS ---------------------------- */


/* Fonction de conversion */
typedef struct _conv_func conv_func;


/* Définit une conversion à partir d'une simple expression. */
conv_func *make_conv_from_expr(char *, arg_expr_t *);

/* Définit une conversion à partir d'une function à appeler. */
conv_func *make_conv_from_func(char *, char *, arg_list_t *);

/* Libère de la mémoire une conversion enregistrée. */
void delete_conv_func(conv_func *);

/* Indique la variable de destination d'une conversion. */
const char *get_conv_dest_name(const conv_func *);

/* Détermine la taille en bits du résultat d'une fonction. */
bool compute_conv_func_size(const conv_func *, const coding_bits *, const conv_list *, unsigned int *);

/* Marque les champs utilisés par une fonction de conversion. */
bool mark_conv_func(conv_func *, bool, const coding_bits *, const conv_list *);

/* Imprime la désignation de la destination d'une conversion. */
void write_conv_func(conv_func *, int, bool);

/* Déclare les variables associées à une fonction de conversion. */
bool declare_conv_func(conv_func *, int, const coding_bits *, const conv_list *, const char *);

/* Définit les variables associées à une fonction de conversion. */
bool define_conv_func(conv_func *, int, const coding_bits *, const conv_list *, const char *, bool, bool *);



/* ---------------------------- ENSEMBLES DE CONVERSIONS ---------------------------- */


/* Liste des fonctions de conversions présentes */
typedef struct _conv_list conv_list;


/* Crée un nouvelle liste vierge de fonctions de conversion. */
conv_list *create_conv_list(void);

/* Supprime de la mémoire une de fonctions de conversion. */
void delete_conv_list(conv_list *);

/* Enregistre une function de conversion du brut à l'utile. */
void register_conversion(conv_list *, conv_func *);

/* Recherche un résultat précis dans une liste de fonctions. */
conv_func *find_named_conv_in_list(const conv_list *, const char *);



#endif  /* _TOOLS_D2C_CONV_MANAGER_H */
