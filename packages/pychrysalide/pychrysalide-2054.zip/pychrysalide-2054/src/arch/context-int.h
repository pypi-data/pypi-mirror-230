
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context-int.h - prototypes internes pour le contexte lié à l'exécution d'un processeur
 *
 * Copyright (C) 2011-2018 Cyrille Bagard
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


#ifndef _ARCH_CONTEXT_INT_H
#define _ARCH_CONTEXT_INT_H


#include "context.h"


#include <stdarg.h>


#include "../format/preload-int.h"



/* Granularité des allocations */
#define DP_ALLOC_BLOCK 10


/* Ajoute une adresse virtuelle comme point de départ de code. */
typedef void (* push_drop_point_fc) (GProcContext *, DisassPriorityLevel, virt_t, va_list);


/* Définition d'un contexte pour processeur (instance) */
struct _GProcContext
{
    GPreloadInfo parent;                    /* A laisser en premier        */

    virt_t *drop_points[DPL_COUNT];         /* Liste de points de départ   */
    size_t dp_allocated[DPL_COUNT];         /* Taille de liste allouée     */
    size_t dp_count[DPL_COUNT];             /* Quantité utile de la liste  */
    GMutex dp_access;                       /* Accès à la liste FIFO       */

    vmpa2t *extra_symbols;                  /* Adresses de symboles        */
    size_t esyms_count;                     /* Nombres de nouveautés       */
    GMutex es_access;                       /* Accès à cette même liste    */

    gint *counter;

    GDbItem **items;                        /* Eléments à insérer plus tard*/
    size_t items_allocated;                 /* Taille allouée à la liste   */
    size_t items_count;                     /* Nombre d'éléments présents  */
    GMutex items_mutex;                     /* Accès à la liste            */

};


/* Définition d'un contexte pour processeur (classe) */
struct _GProcContextClass
{
    GPreloadInfoClass parent;               /* A laisser en premier        */

	push_drop_point_fc push_point;			/* Inclusion de points de chute*/

    /* Signaux */

    void (* drop_point_pushed) (GProcContext *);

};



#endif  /* _ARCH_CONTEXT_INT_H */
