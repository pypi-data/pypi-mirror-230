
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gbinarycursor.h - prototypes pour le suivi de positions dans des panneaux de chargement
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _GLIBEXT_BINARYCURSOR_H
#define _GLIBEXT_BINARYCURSOR_H


#include <glib-object.h>


#include "glinecursor.h"
#include "../arch/vmpa.h"



/* ----------------------- FONCTIONNALITES D'UN SUIVI DE BASE ----------------------- */


#define G_TYPE_BINARY_CURSOR            (g_binary_cursor_get_type())
#define G_BINARY_CURSOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BINARY_CURSOR, GBinaryCursor))
#define G_BINARY_CURSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BINARY_CURSOR, GBinaryCursorClass))
#define G_IS_BINARY_CURSOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BINARY_CURSOR))
#define G_IS_BINARY_CURSOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BINARY_CURSOR))
#define G_BINARY_CURSOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BINARY_CURSOR, GBinaryCursorClass))


/* Suivi de positions dans un panneau de chargement (instance) */
typedef struct _GBinaryCursor GBinaryCursor;

/* Suivi de positions dans un panneau de chargement (classe) */
typedef struct _GBinaryCursorClass GBinaryCursorClass;


/* Détermine le type du suivi de positions dans un panneau de chargement. */
GType g_binary_cursor_get_type(void);

/* Crée un nouveau suivi de positions dans un panneau. */
GLineCursor *g_binary_cursor_new(void);

/* Indique la représentation de l'emplacement. */
bool g_binary_cursor_is_raw(const GBinaryCursor *);

/* Précise la représentation de l'emplacement. */
void g_binary_cursor_set_raw(GBinaryCursor *, bool);

/* Met à jour la position suivi dans un panneau de chargement. */
void g_binary_cursor_update(GBinaryCursor *, const vmpa2t *);

/* Transmet la position de suivi dans un panneau de chargement. */
void g_binary_cursor_retrieve(const GBinaryCursor *, vmpa2t *);



/* ------------------------- LIENS AVEC UNE BASE DE DONNEES ------------------------- */


/* Donne les éléments requis pour la construction d'une table. */
char *g_binary_cursor_create_db_table(const char *);

/* Constitue les champs destinés à une insertion / modification. */
bool g_binary_cursor_store(const GBinaryCursor *, const char *, bound_value **, size_t *);



#endif  /* _GLIBEXT_BINARYCURSOR_H */
