
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gnhash.c - nouvelle fonction offrant une empreinte constante
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


#include "gnhash.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : v = pointeur quelconque.                                     *
*                                                                             *
*  Description : Convertit un pointeur en une empreinte constante.            *
*                                                                             *
*  Retour      : 2.                                                           *
*                                                                             *
*  Remarques   : L'algorithme actuel (12/11/10) de la GLib impose qu'une      *
*                même empreinte impose une même clef. Deux clefs distinctes,  *
*                pourtant égales, ont deux empreintes distinctes, donc on     *
*                définit une seule empreinte possible. Pas terrible, mais     *
*                cela répond au besoin (association simple clef <-> valeur).  *
*                                                                             *
******************************************************************************/

guint g_constant_hash(gconstpointer v)
{
    /**
     * La valeur doit être supérieure à 1 pour ne
     * pas être totalement inéfficace.
     */
    return 2;

}
