
/* Chrysalide - Outil d'analyse de fichiers binaires
 * empty.h - prototypes pour la notification d'une absence de correspondance attendue
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _PLUGINS_KAITAI_RECORDS_EMPTY_H
#define _PLUGINS_KAITAI_RECORDS_EMPTY_H


#include <glib-object.h>


#include "../record.h"



#define G_TYPE_RECORD_EMPTY            g_record_empty_get_type()
#define G_RECORD_EMPTY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RECORD_EMPTY, GRecordEmpty))
#define G_IS_RECORD_EMPTY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RECORD_EMPTY))
#define G_RECORD_EMPTY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RECORD_EMPTY, GRecordEmptyClass))
#define G_IS_RECORD_EMPTY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RECORD_EMPTY))
#define G_RECORD_EMPTY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RECORD_EMPTY, GRecordEmptyClass))


/* Marque d'une zone de correspondance vide (instance) */
typedef struct _GRecordEmpty GRecordEmpty;

/* Marque d'une zone de correspondance vide (classe) */
typedef struct _GRecordEmptyClass GRecordEmptyClass;


/* Indique le type défini pour une zone de correspondance vide. */
GType g_record_empty_get_type(void);

/* Crée une zone de correspondance vide à une position donnée. */
GRecordEmpty *g_record_empty_new(GKaitaiParser *, GBinContent *, const vmpa2t *);



#endif  /* _PLUGINS_KAITAI_RECORDS_EMPTY_H */
