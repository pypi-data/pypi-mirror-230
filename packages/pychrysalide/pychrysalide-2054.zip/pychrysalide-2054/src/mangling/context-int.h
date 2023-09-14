
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes internes liés aux contextes de décodage
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _MANGLING_CONTEXT_INT_H
#define _MANGLING_CONTEXT_INT_H


#include "context.h"


#include "../common/ibuf.h"



/* Procède au décodage d'une chaîne de caractères. */
typedef bool (* demangle_fc) (GDemanglingContext *, const char *);

/* Décode une définition de routine. */
typedef GBinRoutine * (* decode_routine_fc) (GDemanglingContext *);

/* Décode une définition de type. */
typedef GDataType * (* decode_type_fc) (GDemanglingContext *);


/* Contexte de décodage (instance) */
struct _GDemanglingContext
{
    GObject parent;                         /* A laisser en premier        */

    input_buffer buffer;                    /* Tampon de lecture           */

    union
    {
        GObject *gobj;                      /* Utile pour le nettoyage !   */
        GBinRoutine *routine;               /* Routine décodée             */
        GDataType *type;                    /* Type décodé                 */
    };

};

/* Contexte de décodage (classe) */
struct _GDemanglingContextClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    demangle_fc demangle_type;              /* Décodage de type            */
    demangle_fc demangle_routine;           /* Décodage de routine         */

    decode_type_fc decode_type;             /* Décodage de type            */
    decode_routine_fc decode_routine;       /* Décodage de routine         */

};



#endif  /* _MANGLING_CONTEXT_INT_H */
