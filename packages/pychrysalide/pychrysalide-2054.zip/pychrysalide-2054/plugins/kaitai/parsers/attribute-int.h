
/* Chrysalide - Outil d'analyse de fichiers binaires
 * attribute-int.h - prototypes pour les spécifications internes d'un attribut Kaitai
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


#ifndef _PLUGINS_KAITAI_PARSERS_ATTRIBUTE_INT_H
#define _PLUGINS_KAITAI_PARSERS_ATTRIBUTE_INT_H


#include "attribute.h"
#include "switch.h"
#include "../parser-int.h"



/* Indique l'étiquette à utiliser pour identifier un attribut. */
typedef const char * (* get_attribute_label_fc) (const GKaitaiAttribute *);

/* Spécification d'un attribut Kaitai (instance) */
struct _GKaitaiAttribute
{
    GKaitaiParser parent;                   /* A laisser en premier        */

    char *raw_id;                           /* Identifiant Kaitai          */
    char *orig_id;                          /* Identifiant humain          */

    char *doc;                              /* Eventuelle documentation    */

    KaitaiAttributePayload payload;         /* Forme de la spécialisation  */

    struct
    {
        /* KAP_FIXED_CONTENT */
        sized_string_t fixed_content;       /* Données brutes attendues    */

        /* KAP_BASIC_TYPE */
        struct
        {
            BaseType basic;                 /* Type de base                */

            bool is_string;                 /* Renvoi vers une chaîne      */

            SourceEndian endian;            /* Boutisme forcé ?            */
            bool has_endian;                /* Présence de cette force     */

        };

        /* KAP_USER_TYPE */
        char *named_type;                   /* Type particulier            */

        /* KAP_DYNAMIC_TYPE */
        GKaitaiSwitch *switchon;            /* Détermination dynamique     */

    };

    /* KAP_SIZED */
    char *fixed_size;                       /* Taille déterminée           */

    KaitaiAttributeRepetition repetition;   /* Forme de répétition         */
    char *repeat_controller;                /* Indication sur la répétition*/

    char *condition;                        /* Condition de chargement     */

    sized_string_t terminator;              /* Marqueur de fin éventuel    */
    bool consume;                           /* Consommation dans le flux   */
    bool include;                           /* Intégration de ce marqueur  */
    bool eos_error;                         /* Gestion des erreurs en bout */

};

/* Spécification d'un attribut Kaitai (classe) */
struct _GKaitaiAttributeClass
{
    GKaitaiParserClass parent;              /* A laisser en premier        */

    get_attribute_label_fc get_label;       /* Désignation d'une étiquette */

};


/* Met en place un lecteur d'attribut Kaitai. */
bool g_kaitai_attribute_create(GKaitaiAttribute *, GYamlNode *, bool);



#endif  /* _PLUGINS_KAITAI_PARSERS_ATTRIBUTE_INT_H */
