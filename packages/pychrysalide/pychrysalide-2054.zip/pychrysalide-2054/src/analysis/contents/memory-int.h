
/* Chrysalide - Outil d'analyse de fichiers binaires
 * memory-int.h - prototypes internes pour le chargement de données binaires à partir de la mémoire
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _ANALYSIS_CONTENTS_MEMORY_INT_H
#define _ANALYSIS_CONTENTS_MEMORY_INT_H


#include "memory.h"



/* Contenu de données binaires résidant en mémoire (instance) */
struct _GMemoryContent
{
    GObject parent;                         /* A laisser en premier        */

    GContentAttributes *attribs;            /* Attributs liés au contenu   */

    bin_t *data;                            /* Contenu binaire représenté  */
    phys_t length;                          /* Taille totale du contenu    */
    bool allocated;                         /* Nature de la zone de données*/

    char *full_desc;                        /* Description de l'ensemble   */
    char *desc;                             /* Description de l'ensemble   */

};

/* Contenu de données binaires résidant en mémoire (classe) */
struct _GMemoryContentClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _ANALYSIS_CONTENTS_MEMORY_INT_H */
