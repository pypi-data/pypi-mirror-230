
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour le contexte lié à l'exécution d'un processeur
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


#ifndef _ARCH_CONTEXT_H
#define _ARCH_CONTEXT_H


#include <glib-object.h>
#include <stdbool.h>


#include "vmpa.h"
#include "../analysis/db/item.h"



#define G_TYPE_PROC_CONTEXT            g_proc_context_get_type()
#define G_PROC_CONTEXT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PROC_CONTEXT, GProcContext))
#define G_IS_PROC_CONTEXT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PROC_CONTEXT))
#define G_PROC_CONTEXT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PROC_CONTEXT, GProcContextClass))
#define G_IS_PROC_CONTEXT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PROC_CONTEXT))
#define G_PROC_CONTEXT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PROC_CONTEXT, GProcContextClass))


/* Définition d'un contexte pour processeur (instance) */
typedef struct _GProcContext GProcContext;

/* Définition d'un contexte pour processeur (classe) */
typedef struct _GProcContextClass GProcContextClass;


/* Degré de priorité des points à désassembler */
typedef enum _DisassPriorityLevel
{
    DPL_ENTRY_POINT,                        /* Validité indiscutable       */
    DPL_FORMAT_POINT,                       /* Entrée liée au format #2    */
    DPL_SYMBOL,                             /* Symboles utilisés           */
    DPL_OTHER,                              /* Injections complémentaires  */

    DPL_COUNT

} DisassPriorityLevel;


/* Indique le type défini par la GLib pour le contexte de processeur. */
GType g_proc_context_get_type(void);

/* Enregistre un compteur pour le décompte des points à traiter. */
void g_proc_context_attach_counter(GProcContext *, gint *);

/* Ajoute une adresse virtuelle comme point de départ de code. */
void g_proc_context_push_drop_point(GProcContext *, DisassPriorityLevel, virt_t, ...);

/* Fournit une adresse virtuelle comme point de départ de code. */
bool g_proc_context_pop_drop_point(GProcContext *, DisassPriorityLevel *, virt_t *);

/* Empile une adresse de nouveau symbole à prendre en compte. */
void g_proc_context_push_new_symbol_at(GProcContext *, const vmpa2t *);

/* Dépile une adresse de nouveau symbole à prendre en compte. */
bool g_proc_context_pop_new_symbol_at(GProcContext *, vmpa2t *);

/* Note la mise en place d'un élément pendant le désassemblage. */
void g_proc_context_add_db_item(GProcContext *, GDbItem *);

/* Effectue un traitement sur chaque élement de base de données. */
void g_proc_context_foreach_db_item(GProcContext *, GFunc, void *);



#endif  /* _ARCH_CONTEXT_H */
