
/* Chrysalide - Outil d'analyse de fichiers binaires
 * def.h - prototypes pour la définition des unités de lecture
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#ifndef _PLUGINS_FMTP_DEF_H
#define _PLUGINS_FMTP_DEF_H


#include <stdbool.h>


#include <arch/operands/immediate.h>
#include <common/cpp.h>



/**
 * Assurément utile pour les déclarations ou les appels...
 */

#define __(s) s

#define PARSING_DEFS(a) a, ARRAY_SIZE(a)


/**
 * Méthodes de définitions des déclarations.
 */

/* Définition générale */
typedef struct _fmt_field_def fmt_field_def;

/* Eventuel appel préalable */
typedef bool (* get_fdef_value_cb) (const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, void *);

/* Possibilités pour un champ à commenter */
typedef struct _field_desc_switch
{
    bool is_range;                          /* Sélection de définition     */

    union
    {
        uint64_t fixed;                     /* Valeur fixe                 */

        struct
        {
            uint64_t lower;                 /* Borne basse                 */
            uint64_t upper;                 /* Borne haute                 */
        };

    };

    const char *desc;                       /* Description associée        */

} field_desc_switch;

/* Partie de commentaire */
typedef struct _comment_part
{
    bool is_static;                         /* Choix du champ textuel      */
    bool avoid_i18n;                        /* Pas de traduction !         */

    union
    {
        const char *static_text;            /* Texte alloué statiquement   */
        char *dynamic_text;                 /* Texte alloué dynamiquement  */
    };

} comment_part;

/* Type de commentaires associés */
typedef enum _FieldCommentType
{
    FCT_PLAIN,                              /* Brut et statique            */
    FCT_SWITCH,                             /* Eventail des possibles      */
    FCT_MULTI                               /* En plusieurs parties        */

} FieldCommentType;

/* Définition générale */
struct _fmt_field_def
{
    const char *name;                       /* Nom du champ                */

    get_fdef_value_cb get_value;            /* Obtention de la valeur      */

    bool is_uleb128;                        /* Element de type uleb128     */
    bool is_leb128;                        /* Element de type sleb128     */
    MemoryDataSize size;                    /* Taille d'un élément         */
    size_t repeat;                          /* Quantité d'éléments présents*/

    bool is_padding;                        /* Simple bourrage ?           */

    bool has_display_rules;                 /* Validité des champs suivants*/
    const ImmOperandDisplay *disp_rules;    /* Règles d'affichage          */
    size_t disp_count;                      /* Quantité de ces règles      */

    FieldCommentType ctype;                 /* Type de commentaire         */
    union
    {
        const char *plain;                  /* Commentaire simple          */

        struct
        {
            const field_desc_switch *choices; /* Choix multiples           */
            size_t ccount;                  /* Quantité de ces choix       */
            const char *def_choice;         /* Commentaire par défaut      */
        };

        struct
        {
            comment_part *parts;            /* Parties à considérer        */
            size_t pcount;                  /* Quantité de ces parties     */
        };

    } comment;

};


/* Règles d'affichage */

#define DISPLAY_RULES(...)                                              \
    .has_display_rules = true,                                          \
    .disp_rules = (ImmOperandDisplay []) { __VA_ARGS__ },               \
    .disp_count = ARRAY_SIZE(((ImmOperandDisplay []) { __VA_ARGS__ }))

/* Rédaction des commentaires */

#define PLAIN_COMMENT(txt)                  \
    .ctype = FCT_PLAIN,                     \
    .comment.plain = txt

#define SWITCH_COMMENT(array, def)          \
    .ctype = FCT_SWITCH,                    \
    .comment.choices = array,               \
    .comment.ccount = ARRAY_SIZE(array),    \
    .comment.def_choice = def



#endif  /* _PLUGINS_FMTP_DEF_H */
