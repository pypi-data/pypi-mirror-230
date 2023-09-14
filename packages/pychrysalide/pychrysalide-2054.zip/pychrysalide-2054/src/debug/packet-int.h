
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packet.h - prototypes pour la définition interne des paquets utiles au débogage
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


#ifndef _DEBUG_PACKET_INT_H
#define _DEBUG_PACKET_INT_H


#include "packet.h"


#include "../common/dllist.h"



/* Précise les zones mémoires correspondant au contenu. */
typedef void (* debug_vectorize_fc) (GDebugPacket *, struct iovec [UIO_MAXIOV], int *);


/* Répresentation d'un paquet de débogage (instance) */
struct _GDebugPacket
{
    GObject parent;                         /* A laisser en premier        */

    DL_LIST_ITEM(link);                     /* Lien vers les autres        */

    debug_vectorize_fc vectorize;           /* Découpage des données       */

};


/* Répresentation d'un paquet de débogage (classe) */
struct _GDebugPacketClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _DEBUG_PACKET_INT_H */
