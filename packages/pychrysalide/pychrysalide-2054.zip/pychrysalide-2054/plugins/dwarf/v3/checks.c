
/* Chrysalide - Outil d'analyse de fichiers binaires
 * checks.c - validations liées au format DWARF v3
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


#include "checks.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : decl = structure brute dont le contenu est à valider.        *
*                                                                             *
*  Description : Procède à la conversion de base d'une abréviation DWARF.     *
*                                                                             *
*  Retour      : Validité confirmée ou non.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_dwarfv3_abbrev_decl(const dw_abbrev_decl *decl)
{
    bool result;                            /* Validité à retourner        */

    result = (decl->tag >= DW_TAG_array_type && decl->tag <= DW_TAG_shared_type)
        || (decl->tag >= DW_TAG_lo_user && decl->tag <= DW_TAG_hi_user);

    if (result)
        result = (decl->has_children == DW_CHILDREN_no
                  || decl->has_children == DW_CHILDREN_yes);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : decl = structure brute dont le contenu est à valider.        *
*                                                                             *
*  Description : Procède à la conversion d'un attribut d'abréviation DWARF.   *
*                                                                             *
*  Retour      : Validité confirmée ou non.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_dwarfv3_abbrev_attrib(const dw_abbrev_raw_attr *attr)
{
    bool result;                            /* Validité à retourner        */

    result = (attr->name >= DW_AT_sibling && attr->name <= DW_AT_recursive)
        || (attr->name >= DW_AT_lo_user && attr->name <= DW_AT_hi_user);

    if (result)
        result = (attr->form >= DW_FORM_addr && attr->form <= DW_FORM_indirect);

    return result;

}
