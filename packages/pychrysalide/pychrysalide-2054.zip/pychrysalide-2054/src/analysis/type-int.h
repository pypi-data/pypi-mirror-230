
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type-int.h - prototypes pour la définition interne des types de données
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_TYPE_INT_H
#define _ANALYSIS_TYPE_INT_H


#include "type.h"


#include "storage/serialize-int.h"
#include "../glibext/objhole.h"



/* Charge un objet depuis une mémoire tampon. */
typedef bool (* type_load_fc) (GDataType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
typedef bool (* type_store_fc) (const GDataType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
typedef guint (* type_hash_fc) (const GDataType *);

/* Décrit le type fourni sous forme de caractères. */
typedef GDataType * (* type_dup_fc) (const GDataType *);

/* Décrit le type fourni sous forme de caractères. */
typedef char * (* type_to_string_fc) (const GDataType *, bool);

/* Indique si le type assure une gestion des espaces de noms. */
typedef bool (* type_handle_ns_fc) (const GDataType *);

/* Indique si le type est un pointeur. */
typedef bool (* type_is_pointer_fc) (const GDataType *);

/* Indique si le type est une référence. */
typedef bool (* type_is_reference_fc) (const GDataType *);



/* Informations glissées dans la structure GObject de GBinSymbol */
typedef struct _type_extra_data_t
{
    char ns_sep[2];                         /* Séparateur d'éléments       */
    TypeFlag flags;                         /* Propriétés du type          */

    /**
     * Afin de ne pas dépasser une taille de 31 bits, le champ de type
     * TypeQualifier suivant est ramené à un champs de bits.
     */

    unsigned int qualifiers : 2;            /* Eventuels qualificatifs     */

} type_extra_data_t;

/* Encapsulation avec un verrou d'accès */
typedef union _type_obj_extra_t
{
    type_extra_data_t data;                 /* Données embarquées          */
    lockable_obj_extra_t lockable;          /* Gestion d'accès aux fanions */

} type_obj_extra_t;


/* Description de type quelconque (instance) */
struct _GDataType
{
    GObject parent;                         /* A laisser en premier        */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

    /**
     * L'inclusion des informations suivantes dépend de l'architecture.
     *
     * Si la structure GObject possède un trou, on remplit de préférence
     * ce dernier.
     */

    type_obj_extra_t extra;                 /* Externalisation embarquée   */

#endif

    GDataType *namespace;                   /* Espace de noms / classe     */

};

/* Description de type quelconque (classe) */
struct _GDataTypeClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    type_load_fc load;                      /* Chargement                  */
    type_store_fc store;                    /* Enregistrement              */

    type_hash_fc hash;                      /* Prise d'empreinte           */
    type_dup_fc dup;                        /* Copie d'instance existante  */
    type_to_string_fc to_string;            /* Conversion au format texte  */

    type_handle_ns_fc handle_ns;            /* Gestion des espaces de noms?*/
    type_is_pointer_fc is_pointer;          /* Représentation de pointeur ?*/
    type_is_reference_fc is_reference;      /* Représentation de référence?*/

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_DATA_TYPE_EXTRA(tp) (type_extra_data_t *)&tp->extra

#else

#   define GET_DATA_TYPE_EXTRA(tp) GET_GOBJECT_EXTRA(G_OBJECT(tp), type_extra_data_t)

#endif



#endif  /* _ANALYSIS_TYPE_INT_H */
