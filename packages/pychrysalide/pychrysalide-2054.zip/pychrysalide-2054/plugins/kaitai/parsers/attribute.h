
/* Chrysalide - Outil d'analyse de fichiers binaires
 * attribute.h - prototypes pour la spécification d'un attribut Kaitai
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


#ifndef _PLUGINS_KAITAI_PARSERS_ATTRIBUTE_H
#define _PLUGINS_KAITAI_PARSERS_ATTRIBUTE_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>
#include <analysis/types/basic.h>
#include <plugins/yaml/node.h>


#include "../expression.h"



#define G_TYPE_KAITAI_ATTRIBUTE            g_kaitai_attribute_get_type()
#define G_KAITAI_ATTRIBUTE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_ATTRIBUTE, GKaitaiAttribute))
#define G_IS_KAITAI_ATTRIBUTE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_ATTRIBUTE))
#define G_KAITAI_ATTRIBUTE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_ATTRIBUTE, GKaitaiAttributeClass))
#define G_IS_KAITAI_ATTRIBUTE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_ATTRIBUTE))
#define G_KAITAI_ATTRIBUTE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_ATTRIBUTE, GKaitaiAttributeClass))


/* Spécification d'un attribut Kaitai (instance) */
typedef struct _GKaitaiAttribute GKaitaiAttribute;

/* Spécification d'un attribut Kaitai (classe) */
typedef struct _GKaitaiAttributeClass GKaitaiAttributeClass;


/* Type de charge associée à un attribut */
typedef enum _KaitaiAttributePayload
{
    KAP_UNINITIALIZED = (0 << 0),           /* Type non initialisé         */

    KAP_FIXED_CONTENT = (1 << 0),           /* Contenu brut attendu        */
    KAP_BASIC_TYPE    = (1 << 1),           /* Type prédéfini              */
    KAP_USER_TYPE     = (1 << 2),           /* Type personnalisé           */
    KAP_DYNAMIC_TYPE  = (1 << 3),           /* Type dynmatique             */
    KAP_SIZED         = (1 << 4),           /* Bourrage dimensionné        */
    KAP_SIZED_EOS     = (1 << 5),           /* Bourrage final              */

} KaitaiAttributePayload;

/* Types de base reconnus par Kaitai */
typedef enum _KaitaiBasicType
{
    KBT_U1,                                 /* Octet non signé             */
    KBT_U2,                                 /* Mot de 16 bits non signé    */
    KBT_U2LE,                               /* Mot de 16 bits non signé    */
    KBT_U2BE,                               /* Mot de 16 bits non signé    */
    KBT_U4,                                 /* Mot de 32 bits non signé    */
    KBT_U4LE,                               /* Mot de 32 bits non signé    */
    KBT_U4BE,                               /* Mot de 32 bits non signé    */
    KBT_U8,                                 /* Mot de 64 bits non signé    */
    KBT_U8LE,                               /* Mot de 64 bits non signé    */
    KBT_U8BE,                               /* Mot de 64 bits non signé    */
    KBT_S1,                                 /* Octet signé                 */
    KBT_S2,                                 /* Mot de 16 bits signé        */
    KBT_S2LE,                               /* Mot de 16 bits signé        */
    KBT_S2BE,                               /* Mot de 16 bits signé        */
    KBT_S4,                                 /* Mot de 32 bits signé        */
    KBT_S4LE,                               /* Mot de 32 bits signé        */
    KBT_S4BE,                               /* Mot de 32 bits signé        */
    KBT_S8,                                 /* Mot de 64 bits signé        */
    KBT_S8LE,                               /* Mot de 64 bits signé        */
    KBT_S8BE,                               /* Mot de 64 bits signé        */
    KBT_F4,                                 /* Flottant sur 32 bits        */
    KBT_F4BE,                               /* Flottant sur 32 bits        */
    KBT_F4LE,                               /* Flottant sur 32 bits        */
    KBT_F8,                                 /* Flottant sur 64 bits        */
    KBT_F8BE,                               /* Flottant sur 64 bits        */
    KBT_F8LE,                               /* Flottant sur 64 bits        */
    KBT_STR,                                /* Chaîne de caractères        */
    KBT_STRZ,                               /* Chaîne de caractères + '\0' */

} KaitaiBasicType;

/* Formes de répétition d'une lecture d'attribut */
typedef enum _KaitaiAttributeRepetition
{
    KAR_NO_REPETITION,                      /* Aucune forme de répétition  */

    KAR_END_OF_STREAM,                      /* Redites autant que possible */
    KAR_EXPRESSION,                         /* Répétitions selon quantité  */
    KAR_UNTIL,                              /* Répétitions sous condition  */

} KaitaiAttributeRepetition;


/* Indique le type défini pour un attribut de la spécification Kaitai. */
GType g_kaitai_attribute_get_type(void);

/* Construit un lecteur d'attribut Kaitai. */
GKaitaiAttribute *g_kaitai_attribute_new(GYamlNode *);

/* Dérive un lecteur d'attribut Kaitai pour un type utilisateur. */
GKaitaiAttribute *g_kaitai_attribute_dup_for_user_type(const GKaitaiAttribute *, const char *);

/* Indique l'étiquette à utiliser pour identifier un attribut. */
const char *g_kaitai_attribute_get_label(const GKaitaiAttribute *);

/* Indique la désignation brute d'un identifiant Kaitai. */
const char *g_kaitai_attribute_get_raw_id(const GKaitaiAttribute *);

/* Indique la désignation originelle d'un identifiant Kaitai. */
const char *g_kaitai_attribute_get_original_id(const GKaitaiAttribute *);

/* Fournit une éventuelle documentation concernant l'attribut. */
const char *g_kaitai_attribute_get_doc(const GKaitaiAttribute *);

/* Indique la nature de la charge représentée par l'attribut. */
KaitaiAttributePayload g_kaitai_attribute_get_payload(const GKaitaiAttribute *);

/* Précise un éventuel type de base reconnu par le lecteur. */
bool g_kaitai_attribute_get_basic_type(const GKaitaiAttribute *, BaseType *, bool *);

/* Lit les octets d'une chaîne représentée. */
bool g_kaitai_attribute_read_truncated_bytes(const GKaitaiAttribute *, const GBinContent *, const mrange_t *, bin_t **, size_t *);

/* Détermine si l'attribue porte une valeur entière signée. */
bool g_kaitai_attribute_handle_signed_integer(const GKaitaiAttribute *);

/* Lit la valeur d'un élément Kaitai entier représenté. */
bool g_kaitai_attribute_read_value(const GKaitaiAttribute *, const GBinContent *, const mrange_t *, SourceEndian, resolved_value_t *);



#endif  /* _PLUGINS_KAITAI_PARSERS_ATTRIBUTE_H */
