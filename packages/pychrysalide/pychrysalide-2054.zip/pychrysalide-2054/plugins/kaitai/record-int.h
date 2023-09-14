
/* Chrysalide - Outil d'analyse de fichiers binaires
 * record-int.h - prototypes internes pour la mémorisation d'une correspondance avec un attribut Kaitai
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


#ifndef PLUGINS_KAITAI_RECORD_INT_H
#define PLUGINS_KAITAI_RECORD_INT_H


#include "record.h"


#include "parser.h"



/* Calcule ou fournit la zone couverte par une correspondance. */
typedef void (* get_record_range_fc) (const GMatchRecord *, mrange_t *);

/* Recherche la correspondance associée à un identifiant. */
typedef GMatchRecord * (* find_record_by_name_fc) (GMatchRecord *, const char *, size_t, unsigned int);

/* Transforme une énumération en constante entière. */
typedef bool (* resolve_record_enum_fc) (const GMatchRecord *, const sized_string_t *, const sized_string_t *, resolved_value_t *);


/* Correspondance entre un attribut et du binaire (instance) */
struct _GMatchRecord
{
    GObject parent;                         /* A laisser en premier        */

    GKaitaiParser *creator;                 /* Lecteur à l'origine         */

    GBinContent *content;                   /* Contenu binaire analysé     */

};

/* Correspondance entre un attribut et du binaire (classe) */
struct _GMatchRecordClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_record_range_fc get_range;          /* Fourniture de couverture    */
    find_record_by_name_fc find;            /* Recherche selon identifiant */
    resolve_record_enum_fc resolve;         /* Conversion d'une énumération*/

};


/* Met en place une correspondance entre attribut et binaire. */
bool g_match_record_create(GMatchRecord *, GKaitaiParser *, GBinContent *);



#endif  /* PLUGINS_KAITAI_RECORD_INT_H */
