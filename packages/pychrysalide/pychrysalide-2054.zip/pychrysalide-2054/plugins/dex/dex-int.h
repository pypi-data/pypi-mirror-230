
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dex-int.h - prototypes pour les structures internes du format DEX
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#ifndef _PLUGINS_DEX_DEX_INT_H
#define _PLUGINS_DEX_DEX_INT_H


#include <format/executable-int.h>


#include "class.h"
#include "dex_def.h"
#include "format.h"
#include "pool.h"



/* Format d'exécutable DEX (instance) */
struct _GDexFormat
{
    GExeFormat parent;                      /* A laisser en premier        */

    dex_header header;                      /* En-tête du programme        */

    GDexPool *pool;                         /* Table de ressources         */

};

/* Format d'exécutable DEX (classe) */
struct _GDexFormatClass
{
    GExeFormatClass parent;                 /* A laisser en premier        */

};


/* Retrouve si possible la méthode associée à une adresse. */
GDexMethod *g_dex_format_find_method_by_address(const GDexFormat *, vmpa_t);

/* Dénombre le nombre de classes trouvées. */
size_t g_dex_format_count_classes(const GDexFormat *);

/* Fournit une classe du format chargée en mémoire. */
GDexClass *g_dex_format_get_class(const GDexFormat *, size_t);


/* -------------------------- DESCRIPTION DU FORMAT DALVIK -------------------------- */


/* Procède à la lecture d'une en-tête de programme DEX. */
bool read_dex_header(const GDexFormat *, vmpa2t *, dex_header *);



/* ------------------------ ELEMENTS DE TABLE DES CONSTANTES ------------------------ */


/* Procède à la lecture d'un identifiant de chaîne DEX. */
bool read_dex_string_id_item(const GDexFormat *, vmpa2t *, string_id_item *);

/* Procède à la lecture de proriétés de chaîne DEX. */
bool read_dex_string_data_item(const GDexFormat *, vmpa2t *, vmpa2t *, string_data_item *);

/* Procède à la lecture d'un identifiant de type DEX. */
bool read_dex_type_id_item(const GDexFormat *, vmpa2t *, type_id_item *);

/* Procède à la lecture d'une description de prototype. */
bool read_dex_proto_id_item(const GDexFormat *, vmpa2t *, proto_id_item *);

/* Procède à la lecture d'une description de champ. */
bool read_dex_field_id_item(const GDexFormat *, vmpa2t *, field_id_item *);

/* Procède à la lecture d'une description de méthode. */
bool read_dex_method_id_item(const GDexFormat *, vmpa2t *, method_id_item *);

/* Procède à la lecture des propriétés d'une classe DEX. */
bool read_dex_class_def_item(const GDexFormat *, vmpa2t *, class_def_item *);



/* --------------------------- DESCRIPTION DE CLASSES DEX --------------------------- */


/* Procède à la lecture d'un champ quelconque DEX. */
bool read_dex_encoded_field(const GDexFormat *, vmpa2t *, encoded_field *);

/* Procède à la lecture d'une méthode quelconque DEX. */
bool read_dex_encoded_method(const GDexFormat *, vmpa2t *, encoded_method *);

/* Procède à la lecture d'un type DEX. */
bool read_dex_type_item(const GDexFormat *, vmpa2t *, type_item *);

/* Procède à la lecture d'une liste de types DEX. */
bool read_dex_type_list(const GDexFormat *, vmpa2t *, type_list *);

/* Procède à la lecture d'un contenu de classe DEX. */
bool read_dex_class_data_item(const GDexFormat *, vmpa2t *, class_data_item *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_class_data_item(class_data_item *);



/* --------------------------- PORTION DE CODE EXECUTABLE --------------------------- */


/* Procède à la lecture d'une association exception <-> code. */
bool read_dex_encoded_type_addr_pair(const GDexFormat *, vmpa2t *, encoded_type_addr_pair *);

/* Procède à la lecture d'une association exception <-> code. */
bool read_dex_encoded_catch_handler(const GDexFormat *, vmpa2t *, encoded_catch_handler *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_encoded_catch_handler(encoded_catch_handler *);

/* Procède à la lecture d'une association exception <-> code. */
bool read_dex_encoded_catch_handler_list(const GDexFormat *, vmpa2t *, encoded_catch_handler_list *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_encoded_catch_handler_list(encoded_catch_handler_list *);

/* Procède à la lecture d'une association exception <-> code. */
bool read_dex_try_item(const GDexFormat *, vmpa2t *, try_item *);

/* Procède à la lecture d'une portion de code DEX. */
bool read_dex_code_item(const GDexFormat *, vmpa2t *, code_item *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_code_item(code_item *);



/* ------------------------------- AIGUILLAGES DIVERS ------------------------------- */


/* Procède à la lecture d'un contenu d'aiguillage compact. */
bool read_dex_packed_switch(const GDexFormat *, vmpa2t *, packed_switch *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_packed_switch(packed_switch *);

/* Procède à la lecture d'un contenu d'aiguillage dispersé. */
bool read_dex_sparse_switch(const GDexFormat *, vmpa2t *, sparse_switch *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_sparse_switch(sparse_switch *);

/* Procède à la lecture d'un contenu d'aiguillage Dex interne. */
bool read_dex_switch(const GDexFormat *, vmpa2t *, dex_switch *);

/* Supprime tous les éléments chargés en mémoire à la lecture. */
void reset_dex_switch(dex_switch *);



#endif  /* _PLUGINS_DEX_DEX_INT_H */
