
/* Chrysalide - Outil d'analyse de fichiers binaires
 * checks.c - validations liées au format DWARF v2
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


#include <malloc.h>
#include <stdio.h>


#include <i18n.h>
#include <common/cpp.h>
#include <format/format.h>
#include <plugins/self.h>


#include "core.h"
#include "v2/checks.h"
#include "v3/checks.h"
#include "v4/checks.h"



/**
 * Opérations disponibles par version.
 */

/* Procède à la conversion de base d'une abréviation DWARF. */
typedef bool (* check_dwarf_decl_fc) (const dw_abbrev_decl *);

/* Procède à la conversion d'un attribut d'abréviation DWARF. */
typedef bool (* check_dwarf_attrib_fc) (const dw_abbrev_raw_attr *);

typedef struct _abbrev_check_op
{
    check_dwarf_decl_fc check_decl;       /* Validation des déclarations  */
    check_dwarf_attrib_fc check_attrib;   /* Validation des attributs     */

} abbrev_check_op;

static const abbrev_check_op _check_ops[5] = {

    [2] = {
        .check_decl = (check_dwarf_decl_fc)check_dwarfv2_abbrev_decl,
        .check_attrib = (check_dwarf_attrib_fc)check_dwarfv2_abbrev_attrib
    },

    [3] = {
        .check_decl = (check_dwarf_decl_fc)check_dwarfv3_abbrev_decl,
        .check_attrib = (check_dwarf_attrib_fc)check_dwarfv3_abbrev_attrib
    },

    [4] = {
        .check_decl = (check_dwarf_decl_fc)check_dwarfv4_abbrev_decl,
        .check_attrib = (check_dwarf_attrib_fc)check_dwarfv4_abbrev_attrib
    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations de débogage à consulter.               *
*                decl   = structure brute dont le contenu est à valider.      *
*                target = version ciblée par le format.                       *
*                pos    = emplacement de l'élément à vérifier dans le binaire.*
*                                                                             *
*  Description : Procède à la conversion de base d'une abréviation DWARF.     *
*                                                                             *
*  Retour      : Validité confirmée ou non.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_dwarf_abbrev_decl(GDwarfFormat *format, const dw_abbrev_decl *decl, uint16_t target, const vmpa2t *pos)
{
    bool result;                            /* Validité à retourner        */
    char *msg;                              /* Message à imprimer          */
    uint16_t i;                             /* Boucle de parcours          */
    VMPA_BUFFER(loc);                       /* Position humainement lisible*/

    result = false;

    if (target < 2)
    {
        asprintf(&msg, _("Too old DWARF compilation unit (%hu < 2) ; fixed!"), target);

        g_binary_format_add_error(G_BIN_FORMAT(format), BFE_STRUCTURE, pos, msg);

        free(msg);

        target = 2;

    }

    for (i = target; i < ARRAY_SIZE(_check_ops); i++)
    {
        result = _check_ops[i].check_decl(decl);

        if (result)
            break;

    }

    if (result)
    {
        if (i > target)
        {
            asprintf(&msg, _("The DWARF abbreviation declaration belongs to another version (%hu vs %hu)"),
                     i, target);

            g_binary_format_add_error(G_BIN_FORMAT(format), BFE_STRUCTURE, pos, msg);

            free(msg);

        }

    }

    else
    {
        vmpa2_phys_to_string(pos, MDS_UNDEFINED, loc, NULL);

        log_plugin_variadic_message(LMT_BAD_BINARY, _("Invalid abbreviation declaration at %s"), loc);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations de débogage à consulter.               *
*                decl   = structure brute dont le contenu est à valider.      *
*                target = version ciblée par le format.                       *
*                pos    = emplacement de l'élément à vérifier dans le binaire.*
*                                                                             *
*  Description : Procède à la conversion d'un attribut d'abréviation DWARF.   *
*                                                                             *
*  Retour      : Validité confirmée ou non.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_dwarf_abbrev_attrib(GDwarfFormat *format, const dw_abbrev_raw_attr *attr, uint16_t target, const vmpa2t *pos)
{
    bool result;                            /* Validité à retourner        */
    char *msg;                              /* Message à imprimer          */
    uint16_t i;                             /* Boucle de parcours          */
    VMPA_BUFFER(loc);                       /* Position humainement lisible*/

    result = false;

    if (target < 2)
    {
        asprintf(&msg, _("Too old DWARF compilation unit (%hu < 2) ; fixed!"), target);

        g_binary_format_add_error(G_BIN_FORMAT(format), BFE_STRUCTURE, pos, msg);

        free(msg);

        target = 2;

    }

    for (i = target; i < ARRAY_SIZE(_check_ops); i++)
    {
        result = _check_ops[i].check_attrib(attr);

        if (result)
            break;

    }

    if (result)
    {
        if (i > target)
        {
            asprintf(&msg, _("The DWARF abbreviation attribute belongs to another version (%hu vs %hu)"),
                     i, target);

            g_binary_format_add_error(G_BIN_FORMAT(format), BFE_STRUCTURE, pos, msg);

            free(msg);

        }

    }

    else
    {
        vmpa2_phys_to_string(pos, MDS_UNDEFINED, loc, NULL);

        log_plugin_variadic_message(LMT_BAD_BINARY, _("Invalid abbreviation attribute at %s"), loc);

    }

    return result;

}
