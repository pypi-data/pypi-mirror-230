
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour la fourniture de contexte aux phases de décodage
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


#ifndef _FORMAT_MANGLING_CONTEXT_H
#define _FORMAT_MANGLING_CONTEXT_H


#include <glib-object.h>


#include "../analysis/routine.h"



#define G_TYPE_DEMANGLING_CONTEXT               g_demangling_context_get_type()
#define G_DEMANGLING_CONTEXT(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_demangling_context_get_type(), GDemanglingContext))
#define G_IS_DEMANGLING_CONTEXT(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_demangling_context_get_type()))
#define G_DEMANGLING_CONTEXT_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEMANGLING_CONTEXT, GDemanglingContextClass))
#define G_IS_DEMANGLING_CONTEXT_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEMANGLING_CONTEXT))
#define G_DEMANGLING_CONTEXT_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEMANGLING_CONTEXT, GDemanglingContextClass))


/* Contexte de décodage (instance) */
typedef struct _GDemanglingContext GDemanglingContext;

/* Contexte de décodage (classe) */
typedef struct _GDemanglingContextClass GDemanglingContextClass;


/* Indique le type défini pour un contexte de décodage. */
GType g_demangling_context_get_type(void);

/* Fournit la routine créée à l'issue du codage. */
GBinRoutine *g_demangling_context_get_decoded_routine(GDemanglingContext *, const char *);

/* Fournit le type créé à l'issue du codage. */
GDataType *g_demangling_context_get_decoded_type(GDemanglingContext *, const char *);

/* Décode une définition de type. */
GDataType *g_demangling_context_decode_type(GDemanglingContext *, const char *);

/* Décode une définition de routine. */
GBinRoutine *g_demangling_context_decode_routine(GDemanglingContext *, const char *);



#endif  /* _FORMAT_MANGLING_CONTEXT_H */
