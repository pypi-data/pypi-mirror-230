
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context-int.h - prototypes internes pour le contexte lié à l'exécution d'un processeur
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ARM_CONTEXT_INT_H
#define _PLUGINS_ARM_CONTEXT_INT_H


#include <arch/context-int.h>


#include "context.h"



/* Découpage de la zone de désassemblage */
typedef struct _disass_arm_area
{
    virt_t start;                           /* Début de la zone            */
    virt_t end;                             /* Fin de la zone              */

    unsigned int marker;                    /* Type de décodage associé    */

} disass_arm_area;


/* Définition d'un contexte pour processeur ARM (instance) */
struct _GArmContext
{
    GProcContext parent;                    /* A laisser en premier        */

    disass_arm_area *areas;                 /* Désassemblage découpé       */
    size_t acount;                          /* Nombre de zones définies    */
    GMutex areas_access;                    /* Accès aux découpes de zones */

};


/* Définition d'un contexte pour processeur ARM (classe) */
struct _GArmContextClass
{
    GProcContextClass parent;               /* A laisser en premier        */

};



/* Enregistre l'encodage (générique) utilisé à une adresse. */
void _g_arm_context_define_encoding(GArmContext *, virt_t, unsigned int);

/* Indique l'encodage (générique) utilisé à une adresse donnée. */
unsigned int _g_arm_context_find_encoding(GArmContext *, virt_t);



#endif  /* _PLUGINS_ARM_CONTEXT_INT_H */
