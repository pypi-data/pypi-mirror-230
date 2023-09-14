
/* Chrysalide - Outil d'analyse de fichiers binaires
 * executable-int.c - code utile aux formats d'exécutables
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#include "executable-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                off    = position physique à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une position physique. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_without_virt_translate_offset_into_vmpa(const GExeFormat *format, phys_t off, vmpa2t *pos)
{
    init_vmpa(pos, off, VMPA_NO_VIRTUAL);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse virtuelle à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une adresse virtuelle. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_without_virt_translate_address_into_vmpa(const GExeFormat *format, virt_t addr, vmpa2t *pos)
{
    /**
     * S'il n'y a pas de notion de mémoire virtuelle, positions physiques et
     * adresses virtuelles se confondent.
     *
     * On reste néanmoins cohérent, et on n'utilise donc pas d'adresse virtuelle.
     *
     * Les sauts dans le code renvoient de façon transparente vers des positions
     * physiques.
     */

    init_vmpa(pos, addr, VMPA_NO_VIRTUAL);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                off    = position physique à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une position physique. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_translate_offset_into_vmpa_using_portions(GExeFormat *format, phys_t off, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    GBinPortion *portions;                  /* Liste de découpages         */

    portions = g_exe_format_get_portions(format);

    if (portions == NULL)
        result = false;

    else
    {
        result = g_binary_portion_translate_offset_into_vmpa(portions, off, pos);

        g_object_unref(G_OBJECT(portions));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse virtuelle à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une adresse virtuelle. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_translate_address_into_vmpa_using_portions(GExeFormat *format, virt_t addr, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    GBinPortion *portions;                  /* Liste de découpages         */

    portions = g_exe_format_get_portions(format);

    if (portions == NULL)
        result = false;

    else
    {
        result = g_binary_portion_translate_address_into_vmpa(portions, addr, pos);

        g_object_unref(G_OBJECT(portions));

    }

    return result;

}
