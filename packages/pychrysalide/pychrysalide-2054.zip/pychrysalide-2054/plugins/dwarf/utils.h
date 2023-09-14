
/* Chrysalide - Outil d'analyse de fichiers binaires
 * utils.h - prototypes pour les fonctions d'aisance vis à vis du format DWARF
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _PLUGINS_DWARF_UTILS_H
#define _PLUGINS_DWARF_UTILS_H


#include <analysis/content.h>


#include "def.h"



/* Procède à la lecture de l'en-tête d'un contenu binaire DWARF. */
bool read_dwarf_section_header(const GBinContent *, vmpa2t *, SourceEndian, dw_section_header *, vmpa2t *);

/* Procède à la lecture de l'en-tête d'une unité de compilation. */
bool read_dwarf_compil_unit_header(GBinContent *, vmpa2t *, SourceEndian, dw_compil_unit_header *, vmpa2t *);

/* Procède à la lecture d'une déclaration d'abréviation DWARF. */
bool read_dwarf_abbrev_decl(const GBinContent *, vmpa2t *, dw_abbrev_decl *);

/* Procède à la lecture d'un attribut d'abréviation DWARF. */
bool read_dwarf_abbrev_attr(const GBinContent *, vmpa2t *, dw_abbrev_raw_attr *);



#endif  /* _PLUGINS_DWARF_UTILS_H */
