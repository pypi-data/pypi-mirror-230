
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope.h - prototypes pour les recherches d'éléments de lecture
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _PLUGINS_KAITAI_SCOPE_H
#define _PLUGINS_KAITAI_SCOPE_H


#include "record.h"
#include "parsers/meta.h"
#include "parsers/type.h"



/* Accès aux différentes variables de contexte */
typedef struct _kaitai_scope_t
{
    GKaitaiMeta *meta;                      /* Informations globales       */

    GMatchRecord *root;                     /* Variable "_root"            */
    GMatchRecord *parent;                   /* Variable "_parent"          */
    GMatchRecord *last;                     /* Variable "_"                */

} kaitai_scope_t;


/* Initialise un contexte pour correspondances Kaitai établies. */
void init_record_scope(kaitai_scope_t *, GKaitaiMeta *);

/* Vide un contexte de correspondances Kaitai établies. */
void reset_record_scope(kaitai_scope_t *);

/* Copie un contexte de correspondances Kaitai établies. */
void copy_record_scope(kaitai_scope_t *, const kaitai_scope_t *);

/* Retourne le souvenir d'une correspondance racine. */
GMatchRecord *get_root_record(const kaitai_scope_t *);

/* Retourne le souvenir de la correspondance parente effectuée. */
GMatchRecord *get_parent_record(const kaitai_scope_t *);

/* Conserve le souvenir de la dernière correspondance effectuée. */
void remember_last_record(kaitai_scope_t *, GMatchRecord *);

/* Retourne le souvenir de la dernière correspondance effectuée. */
GMatchRecord *get_last_record(const kaitai_scope_t *);

/* Recherche la définition d'un type nouveau pour Kaitai. */
GKaitaiType *find_sub_type(const kaitai_scope_t *, const char *);



#endif  /* _PLUGINS_KAITAI_SCOPE_H */
