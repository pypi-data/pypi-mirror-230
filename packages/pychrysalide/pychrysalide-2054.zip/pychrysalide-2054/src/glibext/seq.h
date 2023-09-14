
/* Chrysalide - Outil d'analyse de fichiers binaires
 * seq.h - prototypes pour la constitution d'un traitement séquentiel générique
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


#ifndef _GLIBEXT_SEQ_H
#define _GLIBEXT_SEQ_H


#include <glib-object.h>
#include <stdbool.h>
#include <sys/types.h>


#include "notifier.h"



#define G_TYPE_SEQ_WORK            g_seq_work_get_type()
#define G_SEQ_WORK(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SEQ_WORK, GSeqWork))
#define G_IS_SEQ_WORK(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SEQ_WORK))
#define G_SEQ_WORK_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SEQ_WORK, GSeqWorkClass))
#define G_IS_SEQ_WORK_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SEQ_WORK))
#define G_SEQ_WORK_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SEQ_WORK, GSeqWorkClass))


/* Portion de traitement séquentiel à mener (instance) */
typedef struct _GSeqWork GSeqWork;

/* Portion de traitement séquentiel à mener (classe) */
typedef struct _GSeqWorkClass GSeqWorkClass;


/* Traitement simple */
typedef void (* seq_work_cb) (void *, size_t, GtkStatusStack *, activity_id_t);

/* Traitement avec retour booléen */
typedef bool (* seq_work_bool_cb) (void *, size_t, GtkStatusStack *, activity_id_t);

/* Traitement avec mise en place d'un objet */
typedef GObject * (* seq_work_obj_cb) (void *, size_t, GtkStatusStack *, activity_id_t);


/* Indique le type défini pour les tâches de traitement séquentiel et partiel. */
GType g_seq_work_get_type(void);

/* Crée une tâche de traitement séquentiel basique. */
GSeqWork *g_seq_work_new(void *, size_t, size_t, activity_id_t, seq_work_cb);

/* Crée une tâche de traitement séquentiel avec retour booléen. */
GSeqWork *g_seq_work_new_boolean(void *, size_t, size_t, activity_id_t, seq_work_bool_cb, bool *);

/* Crée une tâche de traitement séquentiel avec objects. */
GSeqWork *g_seq_work_new_object(void *, size_t, size_t, activity_id_t, seq_work_obj_cb, bool *);

#define g_gen_work_new(d, i, c) g_seq_work_new(d, 0, 1, i, c)
#define g_gen_work_new_boolean(d, i, c, b) g_seq_work_new_boolean(d, 0, 1, i, c, b)
#define g_gen_work_new_object(d, i, c, b) g_seq_work_new_object(d, 0, 1, i, c, b)



#endif  /* _GLIBEXT_SEQ_H */
