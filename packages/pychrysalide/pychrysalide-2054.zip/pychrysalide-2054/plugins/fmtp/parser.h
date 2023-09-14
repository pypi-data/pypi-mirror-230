
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.h - prototypes pour l'interprétation des champs d'un format binaire
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_FMTP_PARSER_H
#define _PLUGINS_FMTP_PARSER_H


#include <stdbool.h>


#include <format/format.h>
#include <format/preload.h>


#include "def.h"



/* Lance l'interprétation d'une série de définitions de champs. */
bool parse_field_definitions(const fmt_field_def *, size_t, GBinFormat *, GPreloadInfo *, vmpa2t *, void *);



#endif  /* _PLUGINS_FMTP_PARSER_H */
