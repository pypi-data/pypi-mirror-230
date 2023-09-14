
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loaded-int.h - définitions internes propres aux définitions de routine
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


#ifndef _ANALYSIS_ROUTINE_INT_H
#define _ANALYSIS_ROUTINE_INT_H


#include "routine.h"
#include "../format/symbol-int.h"



/* Représentation générique de routine (instance) */
struct _GBinRoutine
{
    GBinSymbol parent;                      /* A laisser en premier        */

    RoutineType type;                       /* Type de routine             */

    GDataType *ret_type;                    /* Type retourné               */

    GDataType *namespace;                   /* Espace de noms / classe     */
    char *ns_sep;                           /* Séparateur d'éléments       */
    char *name;                             /* Désignation humaine         */
    GDataType *full_name;                   /* Désignation très complète   */

    GBinVariable **args;                    /* Arguments de la routines    */
    size_t args_count;                      /* Nombre d'arguments          */

    GBinVariable **locals;                  /* Variables locales du code   */
    size_t locals_count;                    /* Nombre de variables locales */

    GBlockList *blocks;                     /* Blocs basiques d'instruct°  */

};


/* Représentation générique de routine (classe) */
struct _GBinRoutineClass
{
    GBinSymbolClass parent;                 /* A laisser en premier        */

};



#endif  /* _ANALYSIS_ROUTINE_INT_H */
