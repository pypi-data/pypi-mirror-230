
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switch-int.h - prototypes internes pour la gestion des énumérations Kaitai
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


#ifndef PLUGINS_KAITAI_PARSERS_SWITCH_INT_H
#define PLUGINS_KAITAI_PARSERS_SWITCH_INT_H


#include "switch.h"
#include "../parser-int.h"



/* ------------------------ BASCULE DYNAMIQUE SELON CONTEXTE ------------------------ */


/* Mémorisation d'une valeur d'énumération */
typedef struct _switch_case_t
{
    char *value;                            /* Valeur d'association        */
    char *type;                             /* Désignation du type associé */

} switch_case_t;



/* ----------------------- SELECTION DYNAMIQUE DE TYPE KAITAI ----------------------- */


/* Sélection d'un type selon un contexte (instance) */
struct _GKaitaiSwitch
{
    GKaitaiParser parent;                   /* A laisser en premier        */

    char *target;                           /* Source de bascule           */

    switch_case_t **cases;                  /* Choix de types potentiels   */
    size_t count;                           /* Quantité de ces choix       */

    switch_case_t *defcase;                 /* Choix par défaut ou NULL    */

    GKaitaiAttribute *generic;              /* Attribut à dériver          */

};

/* Sélection d'un type selon un contexte (classe) */
struct _GKaitaiSwitchClass
{
    GKaitaiParserClass parent;              /* A laisser en premier        */

};


/* Met en place une sélection dynamique de type Kaitai. */
bool g_kaitai_switch_create(GKaitaiSwitch *, GYamlNode *, GKaitaiAttribute *);



#endif  /* PLUGINS_KAITAI_PARSERS_SWITCH_INT_H */
