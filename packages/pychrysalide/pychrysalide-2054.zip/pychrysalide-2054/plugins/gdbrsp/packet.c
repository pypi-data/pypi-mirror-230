
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packet.c - manipulation des paquets de données GDB.
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


#include "packet.h"


#include <malloc.h>
#include <string.h>


#include "../../common/dllist.h"



/* Répresentation d'un paquet GDB (instance) */
struct _GGdbPacket
{
    GObject parent;                         /* A laisser en premier        */

    DL_LIST_ITEM(link);                     /* Lien vers les autres        */

    char *buffer;                           /* Données à traiter           */
    size_t len;                             /* Quantité de ces données     */
    size_t allocated;                       /* Taille du tampon            */

    uint8_t checksum;                       /* Empreinte de contrôle       */

};


/* Répresentation d'un paquet GDB (classe) */
struct _GGdbPacketClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des représentations des paquets GDB. */
static void g_gdb_packet_class_init(GGdbPacketClass *);

/* Initialise une instance de représentation de paquet GDB. */
static void g_gdb_packet_init(GGdbPacket *);



/* Indique le type défini pour une répresentation de paquet GDB. */
G_DEFINE_TYPE(GGdbPacket, g_gdb_packet, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des représentations des paquets GDB.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_packet_class_init(GGdbPacketClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de représentation de paquet GDB.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_packet_init(GGdbPacket *packet)
{
    DL_LIST_ITEM_INIT(&packet->link);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une représentation de paquet GDB.                       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbPacket *g_gdb_packet_new(void)
{
    GGdbPacket *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_GDB_PACKET, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = paquet à préparer pour une émission.                *
*                                                                             *
*  Description : Prépare un paquet pour un envoi prochain.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_packet_start_new_command(GGdbPacket *packet)
{
    if (packet->allocated == 0)
    {
        packet->allocated = 1;
        packet->buffer = (char *)calloc(packet->allocated, sizeof(char));
    }

    packet->buffer[0] = '\0';
    packet->len = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = paquet à préparer pour une émission.                *
*                string = chaîne à inclure dans le paquet.                    *
*                                                                             *
*  Description : Complète un paquet pour un envoi prochain.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_packet_append(GGdbPacket *packet, const char *string)
{
    size_t len;                             /* Taille de la chaîne donnée  */

    len = strlen(string);

    /* Si la place n'est pas assez grande */
    if ((packet->len + len + 1) > packet->allocated)
    {
        packet->buffer = (char *)realloc(packet->buffer, (packet->len + len + 1) * sizeof(char));
        packet->allocated = packet->len + len + 1;
    }


    memcpy(packet->buffer + packet->len, string, len + 1);
    //strcat(packet->buffer, string);

    packet->len += len;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = paquet à analyser.                                  *
*                                                                             *
*  Description : Détermine l'empreinte des données d'un paquet GDB.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_packet_compute_checksum(GGdbPacket *packet)
{
    int sum;                                /* Valeur cumulée des données  */
    size_t i;                               /* Boucle de parcours          */

    sum = 0;

    for (i = 0; i < packet->len; i++)
        sum += packet->buffer[i];

    packet->checksum = sum % 256;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet   = paquet à analyser.                                *
*                checksum = contrôle d'intégrité à retrouver.                 *
*                                                                             *
*  Description : Contrôle l'intégrité des données d'un paquet GDB.            *
*                                                                             *
*  Retour      : Bilan de la vérification.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_gdb_packet_verify_checksum(GGdbPacket *packet, uint8_t checksum)
{
    g_gdb_packet_compute_checksum(packet);

    return checksum == packet->checksum;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = paquet à décoder et/ou décompresser.                *
*                                                                             *
*  Description : Décode et/ou décompresse un paquet GDB.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_gdb_packet_decode(GGdbPacket *packet)
{
    bool result;                            /* Bilan à retourner           */
    char *buffer;                           /* Données transcrites         */
    size_t allocated;                       /* Quantité de données gérées  */
    size_t i;                               /* Boucle de parcours          */
    size_t k;                               /* Point d'insertion           */
    size_t repeat;                          /* Nombre de répétitions       */

    result = true;

    allocated = packet->len + 1;
    buffer = (char *)calloc(allocated, sizeof(char));

    for (i = 0, k = 0; i < packet->len && result; i++)
        switch (packet->buffer[i])
        {
            case '#':
            case '$':
                result = false;
                break;

            case '*':

                if (++i == packet->len || k == 0)
                {
                    result = false;
                    break;
                }

                repeat = packet->buffer[i] - ' ' + 3;

                allocated += repeat;
                buffer = (char *)realloc(buffer, allocated * sizeof(char));

                memset(&buffer[k], buffer[k - 1], repeat);
                k += repeat;

                break;

            case '}':

                if (++i == packet->len)
                {
                    result = false;
                    break;
                }

                buffer[k++] = packet->buffer[i] ^ 0x20;

                break;

            default:
                buffer[k++] = packet->buffer[i];
                break;

        }

    if (packet->buffer != NULL)
        free(packet->buffer);

    buffer[k] = '\0';

    packet->buffer = buffer;
    packet->len = k;
    packet->allocated = allocated;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet   = paquet à analyser.                                *
*                data     = données contenues dans le paquet. [OUT]           *
*                len      = quantité de ces données ou NULL. [OUT]            *
*                checksum = contrôle d'intégrité des données ou NULL. [OUT]   *
*                                                                             *
*  Description : Fournit le contenu du paquet.                                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_packet_get_data(const GGdbPacket *packet, const char **data, size_t *len, uint8_t *checksum)
{
    *data = packet->buffer;

    if (len != NULL)
        *len = packet->len;

    if (checksum != NULL)
        *checksum = packet->checksum;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de paquets à compléter.                         *
*                item = paquet à ajouter à la liste.                          *
*                                                                             *
*  Description : Ajoute un paquet à une liste de paquets.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_packet_push(GGdbPacket **list, GGdbPacket *item)
{
    dl_list_push(item, list, GGdbPacket, link);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de paquets à consulter.                         *
*                                                                             *
*  Description : Retire et fournit le premier élément d'une liste de paquets. *
*                                                                             *
*  Retour      : Elément dépilé de la liste de paquets.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbPacket *g_gdb_packet_pop(GGdbPacket **list)
{
    return dl_list_pop(list, GGdbPacket, link);

}
