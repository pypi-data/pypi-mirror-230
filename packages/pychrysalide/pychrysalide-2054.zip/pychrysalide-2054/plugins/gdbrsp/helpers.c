
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.c - assistanat dans la manipulation des paquets GDB
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


#include "helpers.h"


#include <regex.h>
#include <string.h>


#include "gdb-int.h"
#include "utils.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                addr     = emplacement en mémoire à venir consulter.         *
*                out      = zone d'impression en hexadécimal. [OUT]           *
*                                                                             *
*  Description : Traduit une adresse en chaîne hexadécimale pour GDB.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool translate_virt_to_hex(const GGdbDebugger *debugger, virt_t addr, char *out)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    uint8_t conv8;                          /* Valeur adaptée sur 8 bits   */
    uint16_t conv16;                        /* Valeur adaptée sur 16 bits  */
    uint32_t conv32;                        /* Valeur adaptée sur 32 bits  */
    uint64_t conv64;                        /* Valeur adaptée sur 64 bits  */
    char hexval[17];                        /* Valeur sous forme hexa      */
    bool got_msn;                           /* Obtention d'un quartet ?    */
    size_t i;                               /* Boucle de parcours          */

    /* Conversion */

    switch (debugger->msize)
    {
        case MDS_8_BITS:
            conv8 = addr;
            result = u8_to_hex(&conv8, hexval);
            break;

        case MDS_16_BITS:
            conv16 = addr;
            conv16 = to_u16(&conv16, SRE_BIG);
            result = u16_to_hex(&conv16, hexval);
            break;

        case MDS_32_BITS:
            conv32 = addr;
            conv32 = to_u32(&conv32, SRE_BIG);
            result = u32_to_hex(&conv32, hexval);
            break;

        case MDS_64_BITS:
            conv64 = addr;
            conv64 = to_u64(&conv64, SRE_BIG);
            result = u64_to_hex(&conv64, hexval);
            break;

        default:
            result = false;
            break;

    }

    /* On saute les zéros préliminaires... */

    if (result)
    {
        got_msn = false;

        for (i = 0; i < 17; i++)
        {
            if (!got_msn)
            {
                if (hexval[i] == '0')
                    continue;
                else
                    got_msn = true;
            }

            *out = hexval[i];
            out++;

        }

        *out = '\0';

    }

    return result;

}








/* -------------------------- PAQUETS DES REPONSES D'ARRET -------------------------- */






/******************************************************************************
*                                                                             *
*  Paramètres  : packet = paquet de deonnées à interpréter.                   *
*                sig    = identifiant du signal source. [OUT]                 *
*                addr   = adresse de l'instruction courante. [OUT]            *
*                thread = identifiant du thread concerné. [OUT]               *
*                endian = boutisme de la plateforme ciblée.                   *
*                                                                             *
*  Description : Récupère les informations liées à un arrêt suite à signal.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : Les données sont la forme :                                  *
*                T0505:00000000;04:a08de6bf;08:505878b7;thread:50dc;          *
*                                                                             *
******************************************************************************/

bool get_stop_reply_sig_info(const GGdbPacket *packet, int *sig, vmpa_t *addr, pid_t *thread, SourceEndian endian)
{
    const char *data;                       /* Données brutes du paquet    */
    size_t length;                          /* Quantité de ces données     */
    uint8_t index;                          /* Indice de 8 bits quelconque */
    size_t pos;                             /* Tête de lecture courante    */
    regex_t preg;                           /* Expression régulière        */
    int ret;                                /* Bilan d'un appel            */
    regmatch_t pmatch[3];                   /* Zones remarquées            */
    size_t key_len;                         /* Taille de l'indicatif       */

    *addr = 0ull;

    g_gdb_packet_get_data(packet, &data, &length, NULL);

    pos = 1;

    /* Lecture du numéro du signal */

    if (!strtou8(&index, data, &pos, length, SRE_LITTLE))
        return false;

    *sig = index;

    /* Reste des informations */

    ret = regcomp(&preg, "([^:]+):([^;]+);", REG_EXTENDED | REG_ICASE);
    if (ret != 0) return false;

    for (ret = regexec(&preg, &data[pos], 3, pmatch, 0);
         ret != REG_NOMATCH;
         ret = regexec(&preg, &data[pos], 3, pmatch, 0))
    {
        key_len = pmatch[1].rm_eo - pmatch[1].rm_so;

        /* Indication sur le thread */
        if (key_len == strlen("thread")
            && strncmp(&data[pos + pmatch[1].rm_so], "thread", key_len) == 0)
        {

            /* TODO printf("Thread found !\n"); */

        }

        /* Valeur de registre ? */
        else if (key_len == 2)
        {
            if (!strtou8(&index, data, (size_t []) { pos + pmatch[1].rm_so }, length, SRE_LITTLE))
                return false;

            if (index != 8 /* FIXME */)
                goto next_field;

            if (!strtou32(addr, data, (size_t []) { pos + pmatch[2].rm_so }, length, SRE_LITTLE/* FIXME */))
                return false;

        }

    next_field:
        pos += pmatch[0].rm_eo;

    }

    regfree(&preg);

    return (*addr != 0ull);

}



