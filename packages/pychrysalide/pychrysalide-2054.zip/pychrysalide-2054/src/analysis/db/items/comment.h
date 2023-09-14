
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comment.h - prototypes pour la gestion des commentaires dans du texte
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_ITEMS_COMMENT_H
#define _ANALYSIS_DB_ITEMS_COMMENT_H



#include <glib-object.h>


#include "../../../arch/vmpa.h"
#include "../../../glibext/bufferline.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Incrustations possibles pour un commentaire */
typedef enum _CommentEmbeddingType
{
    CET_INLINED,                            /* En bout de ligne            */
    CET_REPEATED,                           /* Reproduit à chaque référence*/
    CET_BEFORE,                             /* Placé sur une ligne avant   */
    CET_AFTER,                              /* Placé sur une ligne après   */

    CET_COUNT

} CommentEmbeddingType;


#define G_TYPE_DB_COMMENT            g_db_comment_get_type()
#define G_DB_COMMENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DB_COMMENT, GDbComment))
#define G_IS_DB_COMMENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DB_COMMENT))
#define G_DB_COMMENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_COMMENT, GDbCommentClass))
#define G_IS_DB_COMMENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_COMMENT))
#define G_DB_COMMENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_COMMENT, GDbCommentClass))


/* Commentaire à placer dans du texte quelconque (instance) */
typedef struct _GDbComment GDbComment;

/* Commentaire à placer dans du texte quelconque (classe) */
typedef struct _GDbCommentClass GDbCommentClass;


/* Indique le type défini pour un commentaire à l'intérieur d'une zone de texte. */
GType g_db_comment_get_type(void);

/* Crée une définition de commentaire textuel. */
GDbComment *g_db_comment_new(const vmpa2t *, CommentEmbeddingType, BufferLineFlags, const char *);

/* Initialise la définition d'un commentaire à incruster. */
bool g_db_comment_fill(GDbComment *, const vmpa2t *, CommentEmbeddingType, BufferLineFlags, const char *);

/* Etablit la comparaison d'une adresse avec un commentaire. */
int compare_comment_by_addr(const vmpa2t *, const GDbComment * const *);

/* Fournit l'adresse associée à un commentaire. */
const vmpa2t *g_db_comment_get_address(const GDbComment *);

/* Indique le type d'incrustation prévue pour un commentaire. */
CommentEmbeddingType g_db_comment_get_embedding_type(const GDbComment *);

/* Fournit les particularités d'accroche liées à un commentaire. */
BufferLineFlags g_db_comment_get_flags(const GDbComment *);

/* Fournit le commentaire associé à un commentaire. */
char *g_db_comment_get_text(GDbComment *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


#define G_TYPE_COMMENT_COLLECTION            g_comment_collection_get_type()
#define G_COMMENT_COLLECTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_COMMENT_COLLECTION, GCommentCollection))
#define G_IS_COMMENT_COLLECTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_COMMENT_COLLECTION))
#define G_COMMENT_COLLECTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_COMMENT_COLLECTION, GCommentCollectionClass))
#define G_IS_COMMENT_COLLECTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_COMMENT_COLLECTION))
#define G_COMMENT_COLLECTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_COMMENT_COLLECTION, GCommentCollectionClass))


/* Collection dédiée aux commentaires textuels (instance) */
typedef struct _GCommentCollection GCommentCollection;

/* Collection dédiée aux commentaires textuels (classe) */
typedef struct _GCommentCollectionClass GCommentCollectionClass;


/* Indique le type défini pour une collection de commentaires. */
GType g_comment_collection_get_type(void);

/* Crée une collection dédiée aux commentaires. */
GCommentCollection *g_comment_collection_new(void);



#endif  /* _ANALYSIS_DB_ITEMS_COMMENT_H */
