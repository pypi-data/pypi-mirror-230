
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser-int.h - prototypes pour les spécifications internes d'un lecteur Kaitai
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


#ifndef PLUGINS_KAITAI_PARSER_INT_H
#define PLUGINS_KAITAI_PARSER_INT_H


#include "parser.h"



/* Parcourt un contenu binaire selon des spécifications Kaitai. */
typedef bool (* parse_kaitai_fc) (GKaitaiParser *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);



/* Spécification d'un lecteur Kaitai (instance) */
struct _GKaitaiParser
{
    GObject parent;                         /* A laisser en premier        */

};

/* Spécification d'un lecteur Kaitai (classe) */
struct _GKaitaiParserClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    parse_kaitai_fc parse;                  /* Phase d'analyse de contenu  */

};



#endif  /* PLUGINS_KAITAI_PARSER_INT_H */
