
/* Chrysalide - Outil d'analyse de fichiers binaires
 * record.h - prototypes pour la définition d'une correspondance avec un attribut Kaitai
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


#ifndef _PLUGINS_KAITAI_RECORD_H
#define _PLUGINS_KAITAI_RECORD_H


#include <glib-object.h>


#include <analysis/content.h>
#include <arch/vmpa.h>
#include <common/szstr.h>



/* Depuis parser.h : spécification d'un lecteur Kaitai (instance) */
typedef struct _GKaitaiParser GKaitaiParser;

/* Depuis expression.h : informations transportées par une expression */
typedef struct _resolved_value_t resolved_value_t;



#define G_TYPE_MATCH_RECORD            g_match_record_get_type()
#define G_MATCH_RECORD(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_MATCH_RECORD, GMatchRecord))
#define G_IS_MATCH_RECORD(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_MATCH_RECORD))
#define G_MATCH_RECORD_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_MATCH_RECORD, GMatchRecordClass))
#define G_IS_MATCH_RECORD_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_MATCH_RECORD))
#define G_MATCH_RECORD_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_MATCH_RECORD, GMatchRecordClass))


/* Correspondance entre un attribut et du binaire (instance) */
typedef struct _GMatchRecord GMatchRecord;

/* Correspondance entre un attribut et du binaire (classe) */
typedef struct _GMatchRecordClass GMatchRecordClass;


/* Indique le type défini pour une correspondance avec du binaire. */
GType g_match_record_get_type(void);

/* Renvoie vers le lecteur à l'origine de la correspondance. */
GKaitaiParser *g_match_record_get_creator(const GMatchRecord *);

/* Modifie la référence au créateur de la correspondance. */
void g_match_record_fix_creator(GMatchRecord *, GKaitaiParser *);

/* Fournit le contenu lié à une correspondance établie. */
GBinContent *g_match_record_get_content(const GMatchRecord *);

/* Calcule ou fournit la zone couverte par une correspondance. */
void g_match_record_get_range(const GMatchRecord *, mrange_t *);

/* Lit les octets bruts couverts par une correspondance. */
void g_match_record_read_raw_bytes(const GMatchRecord *, bin_t **, size_t *);

#define DIRECT_SEARCH_DEEP_LEVEL 1

/* Recherche la correspondance associée à un identifiant. */
GMatchRecord *g_match_record_find_by_name(GMatchRecord *, const char *, size_t, unsigned int);

/* Transforme une énumération en constante entière. */
bool g_match_record_resolve_enum(const GMatchRecord *, const sized_string_t *, const sized_string_t *, resolved_value_t *);



#endif  /* _PLUGINS_KAITAI_RECORD_H */
