
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand-int.h - prototypes pour la définition générique interne des opérandes
 *
 * Copyright (C) 2008-2020 Cyrille Bagard
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


#ifndef _ARCH_OPERAND_INT_H
#define _ARCH_OPERAND_INT_H


#include "operand.h"


#include <stdbool.h>


#include "../analysis/storage/storage.h"
#include "../glibext/objhole.h"



/* Compare un opérande avec un autre. */
typedef int (* operand_compare_fc) (const GArchOperand *, const GArchOperand *, bool);

/* Détermine le chemin conduisant à un opérande interne. */
typedef char * (* find_inner_operand_fc) (const GArchOperand *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
typedef GArchOperand * (* get_inner_operand_fc) (const GArchOperand *, const char *);

/* Traduit un opérande en version humainement lisible. */
typedef void (* operand_print_fc) (const GArchOperand *, GBufferLine *);

#ifdef INCLUDE_GTK_SUPPORT

/* Construit un petit résumé concis de l'opérande. */
typedef char * (* operand_build_tooltip_fc) (const GArchOperand *, const GLoadedBinary *);

#endif

/* Fournit une liste de candidats embarqués par un candidat. */
typedef GArchOperand ** (* operand_list_inners_fc) (const GArchOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
typedef void (* operand_update_inners_fc) (GArchOperand *, GArchOperand **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
typedef guint (* operand_hash_fc) (const GArchOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
typedef bool (* load_operand_fc) (GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
typedef bool (* store_operand_fc) (GArchOperand *, GObjectStorage *, packed_buffer_t *);


/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _operand_extra_data_t
{
    ArchOperandFlag flags;                  /* Informations diverses       */

} operand_extra_data_t;

/* Encapsulation avec un verrou d'accès */
typedef union _operand_obj_extra_t
{
    operand_extra_data_t data;              /* Données embarquées          */
    lockable_obj_extra_t lockable;          /* Gestion d'accès aux fanions */

} operand_obj_extra_t;


/* Définition générique d'un opérande d'architecture (instance) */
struct _GArchOperand
{
    GObject parent;                         /* A laisser en premier        */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

    /**
     * L'inclusion des informations suivantes dépend de l'architecture.
     *
     * Si la structure GObject possède un trou, on remplit de préférence
     * ce dernier.
     */

    operand_obj_extra_t extra;              /* Externalisation embarquée   */

#endif

};

/* Définition générique d'un opérande d'architecture (classe) */
struct _GArchOperandClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    operand_compare_fc compare;             /* Comparaison d'opérandes     */
    find_inner_operand_fc find_inner;       /* Définition d'un chemin      */
    get_inner_operand_fc get_inner;         /* Récupération d'un opérande  */

    operand_print_fc print;                 /* Texte humain équivalent     */
#ifdef INCLUDE_GTK_SUPPORT
    operand_build_tooltip_fc build_tooltip; /* Construction de description */
#endif

    operand_list_inners_fc list_inner;      /* Récupération d'internes     */
    operand_update_inners_fc update_inner;  /* Mise à jour des éléments    */
    operand_hash_fc hash;                   /* Prise d'empreinte           */

    load_operand_fc load;                   /* Chargement depuis un tampon */
    store_operand_fc store;                 /* Conservation dans un tampon */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_ARCH_OP_EXTRA(op) (operand_extra_data_t *)&op->extra

#else

#   define GET_ARCH_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), operand_extra_data_t)

#endif


/* Ajoute une information complémentaire à un opérande. */
bool _g_arch_operand_set_flag(GArchOperand *, ArchOperandFlag, bool);

/* Retire une information complémentaire à un opérande. */
bool _g_arch_operand_unset_flag(GArchOperand *, ArchOperandFlag, bool);



/* ------------------------ CONTROLE DU VOLUME DES INSTANCES ------------------------ */


/* Fournit une liste de candidats embarqués par un candidat. */
GArchOperand **g_arch_operand_list_inner_instances(const GArchOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
void g_arch_operand_update_inner_instances(GArchOperand *, GArchOperand **, size_t);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge une série d'opérandes internes depuis un tampon. */
bool _g_arch_operand_load_inner_instances(GArchOperand *, GObjectStorage *, packed_buffer_t *, size_t);

/* Charge une série d'opérandes internes depuis un tampon. */
bool g_arch_operand_load_generic_fixed_1(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Charge une série d'opérandes internes depuis un tampon. */
bool g_arch_operand_load_generic_fixed_3(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Charge une série d'opérandes internes depuis un tampon. */
bool g_arch_operand_load_generic_variadic(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde une série d'opérandes internes dans un tampon. */
bool _g_arch_operand_store_inner_instances(GArchOperand *, GObjectStorage *, packed_buffer_t *, bool);

/* Sauvegarde un opérande dans un tampon de façon générique. */
bool g_arch_operand_store_generic_fixed(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un opérande dans un tampon de façon générique. */
bool g_arch_operand_store_generic_variadic(GArchOperand *, GObjectStorage *, packed_buffer_t *);



#endif  /* _ARCH_OPERAND_INT_H */
