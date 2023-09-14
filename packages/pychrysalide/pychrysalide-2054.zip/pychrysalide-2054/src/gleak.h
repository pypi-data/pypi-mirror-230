
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gleak.h - prototypes pour l'aide à la détection de fuites d'instances de GTypes
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _GLEAK_H
#define _GLEAK_H


/* Constitue une base de données de nom de tous les GTypes. */
void remember_gtypes_for_leaks(void);

/* Affiche la liste des instances courantes restantes par type. */
void dump_remaining_gtypes(void);



#endif  /* _GLEAK_H */
