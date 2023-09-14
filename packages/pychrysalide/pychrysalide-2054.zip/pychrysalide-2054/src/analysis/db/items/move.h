
/* Chrysalide - Outil d'analyse de fichiers binaires
 * move.h - prototypes pour la mémorisation des déplacements au sein de code
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_ITEMS_MOVE_H
#define _ANALYSIS_DB_ITEMS_MOVE_H


#include <glib-object.h>


#include "../../../glibext/glinecursor.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


#define G_TYPE_DB_MOVE               g_db_move_get_type()
#define G_DB_MOVE(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_db_move_get_type(), GDbMove))
#define G_IS_DB_MOVE(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_db_move_get_type()))
#define G_DB_MOVE_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_MOVE, GDbMoveClass))
#define G_IS_DB_MOVE_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_MOVE))
#define G_DB_MOVE_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_MOVE, GDbMoveClass))


/* Déplacement d'un emplacement à un autre dans du code (instance) */
typedef struct _GDbMove GDbMove;

/* Déplacement d'un emplacement à un autre dans du code (classe) */
typedef struct _GDbMoveClass GDbMoveClass;


/* Indique le type défini pour un déplacement au sein de code. */
GType g_db_move_get_type(void);

/* Organise un déplacement d'une position à une autre. */
GDbMove *g_db_move_new(const GLineCursor *, const GLineCursor *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


#define G_TYPE_MOVE_COLLECTION               g_move_collection_get_type()
#define G_MOVE_COLLECTION(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_move_collection_get_type(), GMoveCollection))
#define G_IS_MOVE_COLLECTION(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_move_collection_get_type()))
#define G_MOVE_COLLECTION_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_MOVE_COLLECTION, GMoveCollectionClass))
#define G_IS_MOVE_COLLECTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_MOVE_COLLECTION))
#define G_MOVE_COLLECTION_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_MOVE_COLLECTION, GMoveCollectionClass))


/* Collection dédiée aux basculements d'affichage (instance) */
typedef struct _GMoveCollection GMoveCollection;

/* Collection dédiée aux basculements d'affichage (classe) */
typedef struct _GMoveCollectionClass GMoveCollectionClass;


/* Indique le type défini pour une collection de déplacements dans du code. */
GType g_move_collection_get_type(void);

/* Crée une collection dédiée aux déplacements dans du code. */
GMoveCollection *g_move_collection_new(void);



#endif  /* _ANALYSIS_DB_ITEMS_MOVE_H */
