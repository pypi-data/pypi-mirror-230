
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list-int.h - prototypes internes pour la gestion d'une liste de transformateurs
 *
 * Copyright (C) 2023 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_MODIFIERS_LIST_INT_H
#define _ANALYSIS_SCAN_MODIFIERS_LIST_INT_H


#include "list.h"


#include "../modifier-int.h"



/* Liste de transformations d'une séquence d'octets (instance) */
struct _GScanModifierList
{
    GScanTokenModifier parent;              /* A laisser en premier        */

    GScanTokenModifier **modifiers;         /* Liste de transformateurs    */
    size_t count;                           /* Taille de cette liste       */

};

/* Liste de transformations d'une séquence d'octets (classe) */
struct _GScanModifierListClass
{
    GScanTokenModifierClass parent;         /* A laisser en premier        */

};



#endif  /* _ANALYSIS_SCAN_MODIFIERS_LIST_INT_H */
