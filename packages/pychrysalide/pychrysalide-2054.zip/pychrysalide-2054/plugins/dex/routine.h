
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.h - prototypes pour la manipulation des routines du format Dex
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


#ifndef _PLUGINS_DEX_ROUTINE_H
#define _PLUGINS_DEX_ROUTINE_H


#include <glib-object.h>


#include "method.h"



#define G_TYPE_DEX_ROUTINE            g_dex_routine_get_type()
#define G_DEX_ROUTINE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_ROUTINE, GDexRoutine))
#define G_IS_DEX_ROUTINE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_ROUTINE))
#define G_DEX_ROUTINE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_ROUTINE, GDexRoutineClass))
#define G_IS_DEX_ROUTINE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_ROUTINE))
#define G_DEX_ROUTINE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_ROUTINE, GDexRoutineClass))


/* Représentation de routine Dex (instance) */
typedef struct _GDexRoutine GDexRoutine;

/* Représentation de routine Dex (classe) */
typedef struct _GDexRoutineClass GDexRoutineClass;


/* Indique le type défini pour une représentation de routine. */
GType g_dex_routine_get_type(void);

/* Crée une représentation de routine. */
GDexRoutine *g_dex_routine_new(void);

/* Lie une routine à sa méthode Dex d'origine. */
void g_dex_routine_attach_method(GDexRoutine *, GDexMethod *);

/* Fournit la méthode liée à une routine d'origine Dex. */
GDexMethod *g_dex_routine_get_method(const GDexRoutine *);



#endif  /* _PLUGINS_DEX_ROUTINE_H */
