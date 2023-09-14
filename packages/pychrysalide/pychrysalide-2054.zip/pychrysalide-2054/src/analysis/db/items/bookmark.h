
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmark.h - prototypes pour la gestion des signets au sein d'un binaire
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_ITEMS_BOOKMARK_H
#define _ANALYSIS_DB_ITEMS_BOOKMARK_H



#include <glib-object.h>


#include "../../../arch/vmpa.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


#define G_TYPE_DB_BOOKMARK            g_db_bookmark_get_type()
#define G_DB_BOOKMARK(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DB_BOOKMARK, GDbBookmark))
#define G_IS_DB_BOOKMARK(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DB_BOOKMARK))
#define G_DB_BOOKMARK_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_BOOKMARK, GDbBookmarkClass))
#define G_IS_DB_BOOKMARK_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_BOOKMARK))
#define G_DB_BOOKMARK_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_BOOKMARK, GDbBookmarkClass))


/* Signet à l'intérieur d'une zone de texte (instance) */
typedef struct _GDbBookmark GDbBookmark;

/* Signet à l'intérieur d'une zone de texte (classe) */
typedef struct _GDbBookmarkClass GDbBookmarkClass;


/* Indique le type défini pour un signet à l'intérieur d'une zone de texte. */
GType g_db_bookmark_get_type(void);

/* Crée une définition d'un signet dans une zone de texte. */
GDbBookmark *g_db_bookmark_new(const vmpa2t *, const char *);

/* Initialise la définition d'un signet dans une zone de texte. */
bool g_db_bookmark_fill(GDbBookmark *, const vmpa2t *, const char *);

/* Fournit l'adresse associée à un signet. */
const vmpa2t *g_db_bookmark_get_address(const GDbBookmark *);

/* Fournit le commentaire associé à un signet. */
const char *g_db_bookmark_get_comment(const GDbBookmark *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


#define G_TYPE_BM_COLLECTION            g_bookmark_collection_get_type()
#define G_BM_COLLECTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BM_COLLECTION, GBookmarkCollection))
#define G_IS_BM_COLLECTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BM_COLLECTION))
#define G_BM_COLLECTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BM_COLLECTION, GBookmarkCollectionClass))
#define G_IS_BM_COLLECTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BM_COLLECTION))
#define G_BM_COLLECTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BM_COLLECTION, GBookmarkCollectionClass))


/* Collection dédiée aux signets (instance) */
typedef struct _GBookmarkCollection GBookmarkCollection;

/* Collection dédiée aux signets (classe) */
typedef struct _GBookmarkCollectionClass GBookmarkCollectionClass;


/* Indique le type défini pour une collection de signets. */
GType g_bookmark_collection_get_type(void);

/* Crée une collection dédiée aux signets. */
GBookmarkCollection *g_bookmark_collection_new(void);



#endif  /* _ANALYSIS_DB_ITEMS_BOOKMARK_H */
