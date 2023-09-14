
/* Chrysalide - Outil d'analyse de fichiers binaires
 * form.h - prototypes pour la transmission des valeurs d'attributs
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


#ifndef _FORMAT_DWARF_FORM_H
#define _FORMAT_DWARF_FORM_H


#include "format.h"


#include <analysis/content.h>



/* Valeurs dans DWARF */
typedef union _dw_form_value dw_form_value;


/* Lit la valeur correspondant à un type donné. */
bool read_dwarf_form_value(const GDwarfFormat *, GBinContent *, vmpa2t *, const dw_compil_unit_header *, DwarfForm, dw_form_value **);

/* Supprime de la mémoire une valeur correspondant à un type. */
void free_dwarf_form_value(dw_form_value *);

/* Transcrit une valeur Dwarf brute en adresse virtuelle. */
bool translate_form_into_address(const dw_form_value *, DwarfForm, virt_t *);

/* Transcrit une valeur Dwarf brute en chaîne de caractères. */
const char *translate_form_into_string(const dw_form_value *, DwarfForm);



#endif  /* _FORMAT_DWARF_FORM_H */
