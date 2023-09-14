
/* Chrysalide - Outil d'analyse de fichiers binaires
 * abbrev.h - prototypes pour la manipulation des abréviation DWARF
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


#ifndef _PLUGINS_DWARF_ABBREV_H
#define _PLUGINS_DWARF_ABBREV_H


#include <stdbool.h>


#include "form.h"
#include "format.h"



/* ----------------------- TRAITEMENT D'ABREVIATION A L'UNITE ----------------------- */


/* Description d'une abréviation */ 
typedef struct _dw_abbrev dw_abbrev;


/* Compte le nombre d'attributs présents dans une abréviation. */
size_t dwarf_abbreviation_count_attribs(const dw_abbrev *);


/* Forme de valeur typée */
typedef struct _dw_value
{
    DwarfAttrib attrib;                     /* Sujet de l'élément          */
    dw_form_value *value;                   /* Valeur instanciée associée  */

} dw_value;


/* Lit la valeur correspondant à un type donné. */
dw_value *translate_abbrev_attribs(const dw_abbrev *, const GDwarfFormat *, GBinContent *, vmpa2t *, const dw_compil_unit_header *);

/* Supprime de la mémoire une liste de valeurs typées. */
void free_abbrev_attribs(dw_value *, size_t);

/* Détermine si l'abréviation possède des enfants. */
bool has_abbrev_children(const dw_abbrev *);



/* ----------------------- TRAITEMENT D'ABREVIATIONS PAR LOTS ----------------------- */


/* Brochette d'abréviations */
typedef struct _dw_abbrev_brotherhood dw_abbrev_brotherhood;


/* Charge une série d'abréviations présentes dans un DWARF. */
dw_abbrev_brotherhood *load_all_dwarf_abbreviations(GDwarfFormat *, const dw_compil_unit_header *);

/* Supprime de la mémoire toute trace d'abréviations DWARF. */
void free_all_dwarf_abbreviations(dw_abbrev_brotherhood *);

/* Recherche une abréviation DWARF donnée. */
const dw_abbrev *find_dwarf_abbreviation(const dw_abbrev_brotherhood *, uleb128_t);



#endif  /* _PLUGINS_DWARF_ABBREV_H */
