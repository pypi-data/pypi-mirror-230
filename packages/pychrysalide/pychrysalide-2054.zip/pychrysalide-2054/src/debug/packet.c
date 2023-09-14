
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packet.c - définition des paquets issus des protocoles de débogage
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "packet-int.h"



/* Initialise la classe des paquets de débogage. */
static void g_debug_packet_class_init(GDebugPacketClass *);

/* Initialise une instance de paquet de débogage. */
static void g_debug_packet_init(GDebugPacket *);



/* Indique le type défini pour un paquet de débogage. */
G_DEFINE_TYPE(GDebugPacket, g_debug_packet, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des paquets de débogage.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_debug_packet_class_init(GDebugPacketClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de paquet de débogage.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_debug_packet_init(GDebugPacket *packet)
{
    DL_LIST_ITEM_INIT(&packet->link);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packet = instance à convertir.                               *
*                iov    = table de vecteurs. [OUT]                            *
*                iovcnt = quantité de champs renseignés. [OUT]                *
*                                                                             *
*  Description : Précise les zones mémoires correspondant au contenu.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_debug_packet_vectorize(GDebugPacket *packet, struct iovec iov[UIO_MAXIOV], int *iovcnt)
{
    packet->vectorize(packet, iov, iovcnt);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de paquets à consulter.                         *
*              : iter = position actuelle dans la liste.                      *
*                                                                             *
*  Description : Fournit l'élement suivant un autre pour un parcours.         *
*                                                                             *
*  Retour      : Elément suivant ou NULL si aucun.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDebugPacket *g_debug_packet_get_next_iter(const GDebugPacket *list, const GDebugPacket *iter)
{
    GDebugPacket *result;                   /* Elément suivant à renvoyer  */

    result = dl_list_next_iter(iter, list, GDebugPacket, link);

    return result;

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

void g_debug_packet_push(GDebugPacket **list, GDebugPacket *item)
{
    dl_list_push(item, list, GDebugPacket, link);

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

GDebugPacket *g_debug_packet_pop(GDebugPacket **list)
{
    return dl_list_pop(list, GDebugPacket, link);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list   = liste de paquets à consulter.                       *
*                packet = paquet à sortir de la liste.                        *
*                                                                             *
*  Description : Retire et fournit un élément d'une liste de paquets.         *
*                                                                             *
*  Retour      : Elément dépilé de la liste de paquets.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_debug_packet_extract(GDebugPacket **list, GDebugPacket *packet)
{
    dl_list_del(packet, list, GDebugPacket, link);

}
