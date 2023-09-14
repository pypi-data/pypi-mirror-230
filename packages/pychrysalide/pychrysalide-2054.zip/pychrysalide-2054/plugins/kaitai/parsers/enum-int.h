
/* Chrysalide - Outil d'analyse de fichiers binaires
 * enum-int.h - prototypes internes pour la gestion des énumérations Kaitai
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef PLUGINS_KAITAI_PARSERS_ENUM_INT_H
#define PLUGINS_KAITAI_PARSERS_ENUM_INT_H


#include "enum.h"



/* ------------------------- MANIPULATION D'UNE ENUMERATION ------------------------- */


/* Mémorisation d'une valeur d'énumération */
typedef struct _enum_value_t
{
    resolved_value_t value;                 /* Valeur entière représentée  */
    char *label;                            /* Elément associé à une valeur*/
    char *doc;                              /* Eventuelle documentation    */

} enum_value_t;



/* ----------------------- GESTION D'UN GROUPE D'ENUMERATIONS ----------------------- */


/* Définition d'un ensemble d'énumérations Kaitai (instance) */
struct _GKaitaiEnum
{
    GObject parent;                         /* A laisser en premier        */

    char *name;                             /* Désignation de l'énumération*/

    enum_value_t **cases_v2l;               /* Choix indexés par valeur    */
    size_t cases_v2l_count;                 /* Quantité de ces choix       */

    enum_value_t **cases_l2v;               /* Choix indexés par étiquette */
    size_t cases_l2v_count;                 /* Quantité de ces choix       */

    enum_value_t *defcase;                  /* Choix par défaut ou NULL    */

};

/* Définition d'un ensemble d'énumérations Kaitai (classe) */
struct _GKaitaiEnumClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Met en place un groupe d'énumérations Kaitai. */
bool g_kaitai_enum_create(GKaitaiEnum *, GYamlNode *);



#endif  /* PLUGINS_KAITAI_PARSERS_ENUM_INT_H */
