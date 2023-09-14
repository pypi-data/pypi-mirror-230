
/* Chrysalide - Outil d'analyse de fichiers binaires
 * vmpa.h - prototypes des adressages virtuels ou physiques
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _ARCH_VMPA_H
#define _ARCH_VMPA_H


#include <limits.h>
#include <stdbool.h>
#include <stdint.h>


#include "archbase.h"
#include "../common/cpp.h"
#include "../common/packed.h"
#include "../common/sqlite.h"



/* ---------------------- DEFINITION D'UNE POSITION EN MEMOIRE ---------------------- */


/* Taille de la plus longue chaîne de représentation */
#define VMPA_MAX_LEN (2 + sizeof(XSTR(UINT64_MAX)) + 1)

/* Constitution guidée de tampons pour impression */
#define VMPA_BUFFER(name) char name[VMPA_MAX_LEN]


/* Types pour respectivement une position physique et une adresse virtuelle */
#define phys_t uint64_t
#define virt_t uint64_t

/* Equivalents pour GLib */
#define G_TYPE_PHYS uint64_t
#define G_TYPE_VIRT uint64_t
#define G_TYPE_PHYS_T G_TYPE_UINT64
#define G_TYPE_VIRT_T G_TYPE_UINT64


#define PHYS_CAST(v) ((uint64_t)v)
#define VIRT_CAST(v) ((uint64_t)v)


#define VMPA_NO_PHYSICAL ((phys_t)-1)
#define VMPA_NO_VIRTUAL ((virt_t)-2)


/* Adresse mémoire ou position physique */
typedef struct _vmpa2t
{
    phys_t physical;                        /* Position physique           */
    virt_t virtual;                         /* Adresse virtuelle           */

} vmpa2t;


/* Initialise une localisation dans l'espace mémoire/physique. */
void init_vmpa(vmpa2t *, phys_t, virt_t);

/* Crée une localisation dans l'adressage mémoire. */
vmpa2t *make_vmpa(phys_t, virt_t);

/* Copie une localisation dans l'adressage mémoire. */
vmpa2t *dup_vmpa(const vmpa2t *);

/* Supprime une localisation de l'espace mémoire. */
void delete_vmpa(vmpa2t *);

/* Copie la définition d'un adressage dans un autre. */
void copy_vmpa(vmpa2t *, const vmpa2t *);

/* Calcule une empreinte de localisation dans l'espace mémoire. */
uint32_t hash_vmpa(const vmpa2t *);

/* Compare entre elles deux adresses physiques. */
int cmp_vmpa_by_phy(const vmpa2t *, const vmpa2t *);

/* Compare entre elles deux adresses virtuelles. */
int cmp_vmpa_by_virt(const vmpa2t *, const vmpa2t *);

/* Compare deux localisations selon leurs parties définies. */
int cmp_vmpa(const vmpa2t *, const vmpa2t *);

#define get_phy_addr(a) (a)->physical
#define get_virt_addr(a) (a)->virtual

#define has_phys_addr(a) ((a)->physical != VMPA_NO_PHYSICAL)
#define has_virt_addr(a) ((a)->virtual != VMPA_NO_VIRTUAL)

#define is_invalid_vmpa(a) (!has_phys_addr(a) && !has_virt_addr(a))

#define reset_virt_addr(a) (a)->virtual = VMPA_NO_VIRTUAL

/* Décalle une position d'une certaine quantité. */
void advance_vmpa(vmpa2t *, phys_t);

/* Décalle une position d'une certaine quantité. */
void deminish_vmpa(vmpa2t *, phys_t);

/* Aligne une localisation sur un nombre d'octets donné. */
void align_vmpa(vmpa2t *, phys_t);

/* Calcule au mieux la distance entre deux coordonnées. */
phys_t compute_vmpa_diff(const vmpa2t *, const vmpa2t *);

/* Lit la définition d'une adresse depuis un tampon. */
bool unpack_vmpa(vmpa2t *, packed_buffer_t *);

/* Ecrit la définition d'une adresse dans un tampon. */
bool pack_vmpa(const vmpa2t *, packed_buffer_t *);

/* Transforme une adresse physique en chaîne de caractères. */
char *vmpa2_phys_to_string(const vmpa2t *, MemoryDataSize, char [VMPA_MAX_LEN], size_t *);

/* Transforme une adresse virtuelle en chaîne de caractères. */
char *vmpa2_virt_to_string(const vmpa2t *, MemoryDataSize, char [VMPA_MAX_LEN], size_t *);

/* Transforme une localisation en chaîne de caractères. */
char *vmpa2_to_string(const vmpa2t *, MemoryDataSize, char [VMPA_MAX_LEN], size_t *);

/* Transforme une chaîne de caractères en position physique. */
vmpa2t *string_to_vmpa_phy(const char *);

/* Transforme une chaîne de caractères en adresse virtuelle. */
vmpa2t *string_to_vmpa_virt(const char *);

/* Donne les éléments requis pour la construction d'une table. */
char *create_vmpa_db_table(const char *);

/* Charge les valeurs utiles pour une localisation. */
bool load_vmpa(vmpa2t *, const char *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
bool store_vmpa(const vmpa2t *, const char *, bound_value **, size_t *);



/* ------------------------ AIDES FONCTIONNELLES AUXILIAIRES ------------------------ */


/* Construit une désignation de symbole avec décalage. */
char *make_symbol_offset(const char *, phys_t);



/* ------------------------ DEFINITION D'UNE ZONE EN MEMOIRE ------------------------ */


/* Couverture mémoire */
typedef struct _mrange_t
{
    vmpa2t addr;                            /* Adresse physique/virtuelle  */
    phys_t length;                          /* Taille de la couverture     */

} mrange_t;


#define UNUSED_MRANGE_PTR (mrange_t []) { { { 0 }, 0 } }


#define get_mrange_addr(r) &(r)->addr
#define get_mrange_length(r) (r)->length

#define set_mrange_length(r, l) (r)->length = l


/* Initialise une plage dans l'espace mémoire/physique. */
void init_mrange(mrange_t *, const vmpa2t *, phys_t);

/* Copie la définition d'une plage mémoire dans une autre. */
void copy_mrange(mrange_t *, const mrange_t *);

/* Compare deux couvertures mémoire selon leurs propriétés. */
int cmp_mrange(const mrange_t *, const mrange_t *);

/* Compare une couverture mémoire avec une localisation simple. */
int cmp_mrange_with_vmpa(const mrange_t *, const vmpa2t *);

static inline int cmp_mrange_with_vmpa_swapped(const vmpa2t *k, const mrange_t *r)
{
    return cmp_mrange_with_vmpa(r, k);
}

/* Compare une couverture mémoire avec une localisation simple. */
int cmp_mrange_with_vmpa_inclusive(const mrange_t *, const vmpa2t *);

/* Indique si une zone en contient une autre ou non. */
int mrange_includes_mrange(const mrange_t *, const mrange_t *);

/* Indique si une zone en contient une autre ou non. */
bool mrange_contains_mrange(const mrange_t *, const mrange_t *);

/* Indique si une localisation est incluse dans une zone ou non. */
bool mrange_contains_addr(const mrange_t *, const vmpa2t *);

/* Indique si une localisation est incluse dans une zone ou non. */
bool mrange_contains_addr_inclusive(const mrange_t *, const vmpa2t *);

/* Détermine si deux zones mémoire se chevauchent ou non. */
bool mrange_intersects_mrange(const mrange_t *, const mrange_t *);

/* Calcule la position extérieure finale d'une couverture. */
void compute_mrange_end_addr(const mrange_t *, vmpa2t *);

/* Lit la définition d'une couverture depuis un tampon. */
bool unpack_mrange(mrange_t *, packed_buffer_t *);

/* Ecrit la définition d'une couverture dans un tampon. */
bool pack_mrange(const mrange_t *, packed_buffer_t *);

/* Transforme un emplacement physique en chaîne de caractères. */
char *mrange_phys_to_string(const mrange_t *, MemoryDataSize, bool, char [VMPA_MAX_LEN], size_t *);

/* Transforme un emplacement virtuel en chaîne de caractères. */
char *mrange_virt_to_string(const mrange_t *, MemoryDataSize, bool, char [VMPA_MAX_LEN], size_t *);

/* Transforme une taille d'emplacement en chaîne de caractères. */
char *mrange_length_to_string(const mrange_t *, MemoryDataSize, char [VMPA_MAX_LEN], size_t *);



#endif  /* _ARCH_VMPA_H */
