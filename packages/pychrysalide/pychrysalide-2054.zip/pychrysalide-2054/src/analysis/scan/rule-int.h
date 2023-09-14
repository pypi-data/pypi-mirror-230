
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rule-int.h - prototypes internes pour la gestion d'une règle de détection par motifs
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_RULE_INT_H
#define _ANALYSIS_SCAN_RULE_INT_H


#include "rule.h"



#define PATTERN_ALLOC_SIZE 20


/* Représentation d'une règle de détection statique (instance) */
struct _GScanRule
{
    GObject parent;                         /* A laisser en premier        */

    char *name;                             /* Désignation de la règle     */
    fnv64_t name_hash;                      /* Empreinte de la désignation */

    GSearchPattern **bytes_locals;          /* Variables de données        */
    size_t bytes_allocated;                 /* Taille allouée du tableau   */
    size_t bytes_used;                      /* Nombre d'éléments présents  */

    GScanExpression *condition;             /* Condition de correspondance */

};

/* Représentation d'une règle de détection statique (classe) */
struct _GScanRuleClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _ANALYSIS_SCAN_RULE_INT_H */
