
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proto.h - prototypes supplémentaires pour les fonctions GLib
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


#ifndef _GLIBEXT_PROTO_H
#define _GLIBEXT_PROTO_H


#include <glib-object.h>



/**
 * Boucle de parcours avec plusieurs arguments :
 * - #1 : conteneur.
 * - #2 : élément parcouru.
 * - #3 : éventuelle donnée de l'utilisateur.
 */
typedef void (* GExtFunc) (gpointer container, gpointer item, gpointer data);



#endif  /* _GLIBEXT_PROTO_H */
