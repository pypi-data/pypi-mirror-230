
/* Chrysalide - Outil d'analyse de fichiers binaires
 * content-int.h - définitions internes propres aux contenus binaires
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_CONTENT_INT_H
#define _ANALYSIS_CONTENT_INT_H


#include "content.h"



/* Associe un ensemble d'attributs au contenu binaire. */
typedef void (* set_content_attributes) (GBinContent *, GContentAttributes *);

/* Fournit l'ensemble des attributs associés à un contenu. */
typedef GContentAttributes * (* get_content_attributes) (const GBinContent *);

/* Donne l'origine d'un contenu binaire. */
typedef GBinContent * (* get_content_root_fc) (GBinContent *);

/* Fournit le nom associé au contenu binaire. */
typedef char * (* describe_content_fc) (const GBinContent *, bool);

/* Calcule une empreinte unique (SHA256) pour les données. */
typedef void (* compute_checksum_fc) (GBinContent *, GChecksum *);

/* Détermine le nombre d'octets lisibles. */
typedef phys_t (* compute_size_fc) (const GBinContent *);

/* Détermine la position initiale d'un contenu. */
typedef void (* compute_start_pos_fc) (const GBinContent *, vmpa2t *);

/* Détermine la position finale d'un contenu. */
typedef void (* compute_end_pos_fc) (const GBinContent *, vmpa2t *);

/* Avance la tête de lecture d'une certaine quantité de données. */
typedef bool (* seek_fc) (const GBinContent *, vmpa2t *, phys_t);

/* Donne accès à une portion des données représentées. */
typedef const bin_t * (* get_raw_access_fc) (const GBinContent *, vmpa2t *, phys_t);

/* Fournit une portion des données représentées. */
typedef bool (* read_raw_fc) (const GBinContent *, vmpa2t *, phys_t, bin_t *);

/* Lit un nombre non signé sur quatre bits. */
typedef bool (* read_u4_fc) (const GBinContent *, vmpa2t *, bool *, uint8_t *);

/* Lit un nombre non signé sur un octet. */
typedef bool (* read_u8_fc) (const GBinContent *, vmpa2t *, uint8_t *);

/* Lit un nombre non signé sur deux octets. */
typedef bool (* read_u16_fc) (const GBinContent *, vmpa2t *, SourceEndian, uint16_t *);

/* Lit un nombre non signé sur quatre octets. */
typedef bool (* read_u32_fc) (const GBinContent *, vmpa2t *, SourceEndian, uint32_t *);

/* Lit un nombre non signé sur huit octets. */
typedef bool (* read_u64_fc) (const GBinContent *, vmpa2t *, SourceEndian, uint64_t *);

/* Lit un nombre non signé encodé au format LEB128. */
typedef bool (* read_uleb128_fc) (const GBinContent *, vmpa2t *, uleb128_t *);

/* Lit un nombre signé encodé au format LEB128. */
typedef bool (* read_leb128_fc) (const GBinContent *, vmpa2t *, leb128_t *);


/* Accès à un contenu binaire quelconque (interface) */
struct _GBinContentIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    set_content_attributes set_attribs;     /* Enregistrement d'attributs  */
    get_content_attributes get_attribs;     /* Fourniture d'attributs      */

    get_content_root_fc get_root;           /* Renvoie à l'origine         */

    describe_content_fc describe;           /* Fournit une description     */

    compute_checksum_fc compute_checksum;   /* Calcul de l'empreinte       */

    compute_size_fc compute_size;           /* Calcul de la taille totale  */
    compute_start_pos_fc compute_start_pos; /* Calcul de position initiale */
    compute_end_pos_fc compute_end_pos;     /* Calcul de position finale   */

    seek_fc seek;                           /* Avancée de tête de lecture  */

    get_raw_access_fc get_raw_access;       /* Accès brut à une position   */

    read_raw_fc read_raw;                   /* Lecture brute               */
    read_u4_fc read_u4;                     /* Lecture de 4 bits           */
    read_u8_fc read_u8;                     /* Lecture de 8 bits           */
    read_u16_fc read_u16;                   /* Lecture de 16 bits          */
    read_u32_fc read_u32;                   /* Lecture de 32 bits          */
    read_u64_fc read_u64;                   /* Lecture de 64 bits          */

    read_uleb128_fc read_uleb128;           /* Lecture d'un LEB non signé  */
    read_leb128_fc read_leb128;             /* Lecture d'un LEB signé      */

};


/* Redéfinition */
typedef GBinContentIface GBinContentInterface;



#endif  /* _ANALYSIS_CONTENT_INT_H */
