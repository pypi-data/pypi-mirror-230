
/* Chrysalide - Outil d'analyse de fichiers binaires
 * program.c - gestion des en-têtes de programme d'un ELF
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


#include "program.h"


#include "elf-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                p_type = type associé à un en-tête de programme.             *
*                                                                             *
*  Description : Fournit la description humaine d'un type de segment ELF.     *
*                                                                             *
*  Retour      : Désignation prête à emploi.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_elf_program_type_desc(const GElfFormat *format, uint32_t p_type)
{
    const char *result;                     /* Description à renvoyer      */

#define MAKE_STRING_FROM_PT(pt) case pt: result = #pt; break;

    switch(p_type)
    {
        MAKE_STRING_FROM_PT(PT_NULL);
        MAKE_STRING_FROM_PT(PT_LOAD);
        MAKE_STRING_FROM_PT(PT_DYNAMIC);
        MAKE_STRING_FROM_PT(PT_INTERP);
        MAKE_STRING_FROM_PT(PT_NOTE);
        MAKE_STRING_FROM_PT(PT_SHLIB);
        MAKE_STRING_FROM_PT(PT_PHDR);
        MAKE_STRING_FROM_PT(PT_TLS);
        MAKE_STRING_FROM_PT(PT_NUM);
        MAKE_STRING_FROM_PT(PT_GNU_EH_FRAME);
        MAKE_STRING_FROM_PT(PT_GNU_STACK);
        MAKE_STRING_FROM_PT(PT_GNU_RELRO);
        MAKE_STRING_FROM_PT(PT_LOSUNW);
        MAKE_STRING_FROM_PT(PT_SUNWSTACK);

        default:
            result = NULL;
            break;

    }

    if (result == NULL)
        result = format->ops.get_type_desc(p_type);

    if (result == NULL)
        switch(p_type)
        {
            MAKE_STRING_FROM_PT(PT_LOOS);
            MAKE_STRING_FROM_PT(PT_HIOS);
            MAKE_STRING_FROM_PT(PT_LOPROC);
            MAKE_STRING_FROM_PT(PT_HIPROC);

            default:
                result = "PT_???";
                break;
        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                index   = indice de la partie recherchée.                    *
*                program = ensemble d'informations à faire remonter. [OUT]    *
*                                                                             *
*  Description : Recherche un programme donné au sein de binaire par indice.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_program_by_index(const GElfFormat *format, uint16_t index, elf_phdr *program)
{
    off_t offset;                           /* Emplacement à venir lire    */

    if (index >= ELF_HDR(format, format->header, e_phnum)) return false;

    offset = ELF_HDR(format, format->header, e_phoff)
        + ELF_HDR(format, format->header, e_phentsize) * index;

    return read_elf_program_header(format, offset, program);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                type    = type de la partie recherchée.                      *
*                program = ensemble d'informations à faire remonter. [OUT]    *
*                                                                             *
*  Description : Recherche un programme donné au sein de binaire par type.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_program_by_type(const GElfFormat *format, uint32_t type, elf_phdr *program)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */

    result = false;

    for (i = 0; i < ELF_HDR(format, format->header, e_phnum) && !result; i++)
    {
        find_elf_program_by_index(format, i, program);

        if (ELF_PHDR(format, *program, p_type) == type)
            result = true;

    }

    return result;

}
