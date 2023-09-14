
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.h - prototypes pour la spécification d'un lecteur Kaitai
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


#ifndef PLUGINS_KAITAI_PARSER_H
#define PLUGINS_KAITAI_PARSER_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>


#include "record.h"
#include "scope.h"



#define G_TYPE_KAITAI_PARSER            g_kaitai_parser_get_type()
#define G_KAITAI_PARSER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_PARSER, GKaitaiParser))
#define G_IS_KAITAI_PARSER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_PARSER))
#define G_KAITAI_PARSER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_PARSER, GKaitaiParserClass))
#define G_IS_KAITAI_PARSER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_PARSER))
#define G_KAITAI_PARSER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_PARSER, GKaitaiParserClass))


/* Spécification d'un lecteur Kaitai (instance) */
typedef struct _GKaitaiParser GKaitaiParser;

/* Spécification d'un lecteur Kaitai (classe) */
typedef struct _GKaitaiParserClass GKaitaiParserClass;


/* Indique le type défini pour un lecteur de spécification Kaitai. */
GType g_kaitai_parser_get_type(void);

/* Parcourt un contenu binaire selon des spécifications Kaitai. */
bool g_kaitai_parser_parse_content(GKaitaiParser *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);



#endif  /* PLUGINS_KAITAI_PARSER_H */
