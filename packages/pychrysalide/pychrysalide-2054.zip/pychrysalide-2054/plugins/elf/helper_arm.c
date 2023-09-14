
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helper_x86.c - gestion auxiliaire de l'architecture x86
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


#include "helper_arm.h"


#include "elf_def_arm.h"
#include "elf-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : p_type = type associé à un en-tête de programme.             *
*                                                                             *
*  Description : Fournit la description humaine d'un type de segment ELF.     *
*                                                                             *
*  Retour      : Désignation prête à emploi ou NULL si aucune.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_elf_program_arm_type_desc(uint32_t p_type)
{
    const char *result;                     /* Description à renvoyer      */

#define MAKE_STRING_FROM_PT(pt) case pt: result = #pt; break;

    switch(p_type)
    {
        MAKE_STRING_FROM_PT(PT_ARM_EXIDX);

        default:
            result = NULL;
            break;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : virt = adresse virtuelle éventuellement porteuse d'infos.    *
*                                                                             *
*  Description : Fournit une adresse virtuelle prête à emploi.                *
*                                                                             *
*  Retour      : Adresse virtuelle réellement utilisable.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

virt_t fix_elf_arm_virtual_address(virt_t virt)
{
    virt_t result;                          /* Résultat à retourner        */

    result = virt & ~0x1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à manipuler.            *
*                addr   = position de la PLT à faire évoluer. [OUT]           *
*                                                                             *
*  Description : Détermine l'emplacement de la première entrée dans la PLT.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_first_plt_entry(GElfFormat *format, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à parcourir */
    vmpa2t pos;                             /* Tete de lecture             */
    uint32_t raw;                           /* Valeur brute lue            */
    bool status;                            /* Bilan d'une lecture         */

    result = false;

    content = G_KNOWN_FORMAT(format)->content;

    while (!result)
    {
        copy_vmpa(&pos, addr);

        status = g_binary_content_read_u32(content, &pos, format->endian, &raw);
        if (!status) break;

        /**
         * Analyse à mettre en relation avec la fonction retrieve_arm_linkage_offset().
         */

        if ((raw & 0xfffff000) == 0xe28fc000)
            result = true;

        else
            copy_vmpa(addr, &pos);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à manipuler.            *
*                addr   = position de la PLT à faire évoluer. [OUT]           *
*                offset = décalage retrouvé par désassemblage. [OUT]          *
*                                                                             *
*  Description : Retrouve le décalage appliqué lors d'une résolution.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool retrieve_arm_linkage_offset(GElfFormat *format, vmpa2t *addr, uint64_t *offset)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à parcourir */
    uint32_t raw;                           /* Valeur brute lue            */
    uint32_t shift;                         /* Décalage arithmétique       */

    /**
     * Pour faciliter la compréhension, on peut s'appuyer sur la lecture de :
     *
     *    http://blog.qt.io/blog/2010/12/04/moving-code-around/
     *
     */

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u32(content, addr, format->endian, &raw);
    if (!result) goto exit;

    /**
     * On ne reconnaît pour l'instant que la seule combinaison suivante.
     *
     * Charge de compléter cette reconnaissance en fonction de nouvelles
     * découvertes !
     */

    /**
     * R_ARM_JUMP_SLOT :
     *
     *    e28fc600     add ip, pc, #0, 12
     *    e28cca08     add ip, ip, #8, 20  ; 0x8000
     *    e5bcf310     ldr pc, [ip, #784]! ; 0x310
     *
     *    e28fc601     add ip, pc, #1048576 ; 0x100000
     *    e28cca03     add ip, ip, #12288   ; 0x3000
     *    e5bcff00     ldr pc, [ip, #3840]! ; 0xf00
     *
     */

    if ((raw & 0xfffff000) == 0xe28fc000)
    {
        *offset = get_virt_addr(addr) + 4;

        /**
         * Les deux premières instructions répondent à l'encodage spécifié dans :
         *
         *    A8.8.5 - ADD (immediate, ARM)
         *
         *    31 30 29 28 | 27 26 25 24 23 22 21 20 | 19 18 17 16 | 15 14 13 12 | 11 10 9 8 7 6 5 4 3 2 1 0
         *        cond    |  0  0  1  0  1  0  0  S |      Rn     |      Rd     |           imm12
         *
         * On a donc :
         *
         *    ADD{S}{<c>}{<q>} {<Rd>,} <Rn>, #<const>
         *
         * Avec :
         *
         *    - S = 0.
         *    - Rn = ip = r12 = 0xc
         *    - Rd = ip = r12 = 0xc
         *    - const = ARMExpandImm(imm12)
         *
         * Le fonctionnement de la macro ARMExpandImm est détaillé dans :
         *
         *    A5.2.4 - Modified immediate constants in ARM instructions
         *
         */

        /**
         * Première instruction...
         */

        if ((raw & 0xfffff000) != 0xe28fc000)
        {
            result = false;
            goto exit;
        }

        shift = 32 - ((raw & 0xf00) >> 8) * 2;

        *offset += (raw & 0xff) << shift;

        /**
         * Seconde instruction...
         */

        result = g_binary_content_read_u32(content, addr, format->endian, &raw);
        if (!result) goto exit;

        if ((raw & 0xfffff000) != 0xe28cc000)
        {
            result = false;
            goto exit;
        }

        shift = 32 - ((raw & 0xf00) >> 8) * 2;

        *offset += (raw & 0xff) << shift;

        /**
         * La dernière instruction répond à l'encodage spéficié dans :
         *
         *    A8.8.63 - LDR (immediate, ARM)
         *
         *    31 30 29 28 | 27 26 25 24 23 22 21 20 | 19 18 17 16 | 15 14 13 12 | 11 10 9 8 7 6 5 4 3 2 1 0
         *        cond    |  0  1  0  P  U  0  W  1 |      Rn     |      Rt     |           imm12
         *
         * On a donc :
         *
         *    LDR{<c>}{<q>} <Rt>, [<Rn>, #+/-<imm>]!
         *
         * Avec :
         *
         *    - P = 1 (index).
         *    - U = 1 (add).
         *    - W = 1 (wback).
         *    - Rn = ip = r12 = 0xc
         *    - Rt = pc = r15 = 0xf
         *
         */

        result = g_binary_content_read_u32(content, addr, format->endian, &raw);
        if (!result) goto exit;

        if ((raw & 0xfffff000) != 0xe5bcf000)
        {
            result = false;
            goto exit;
        }

        *offset += (raw & 0xfff);

    }

    else
        result = false;

 exit:

    return result;

}
