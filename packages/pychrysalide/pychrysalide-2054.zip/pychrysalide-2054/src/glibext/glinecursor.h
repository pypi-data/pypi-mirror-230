
/* Chrysalide - Outil d'analyse de fichiers binaires
 * glinecursor.h - prototypes pour le suivi de positions dans des panneaux de chargement
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


#ifndef _GLIBEXT_GLINECURSOR_H
#define _GLIBEXT_GLINECURSOR_H


#include <glib-object.h>
#include <stdbool.h>


#include "../analysis/loaded.h"
#include "../common/packed.h"
#include "../common/sqlite.h"
#include "../glibext/notifier.h"



/* ----------------------- FONCTIONNALITES D'UN SUIVI DE BASE ----------------------- */


#define G_TYPE_LINE_CURSOR            (g_line_cursor_get_type())
#define G_LINE_CURSOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LINE_CURSOR, GLineCursor))
#define G_LINE_CURSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_LINE_CURSOR, GLineCursorClass))
#define G_IS_LINE_CURSOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LINE_CURSOR))
#define G_IS_LINE_CURSOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_LINE_CURSOR))
#define G_LINE_CURSOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_LINE_CURSOR, GLineCursorClass))


/* Suivi de positions dans un panneau de chargement (instance) */
typedef struct _GLineCursor GLineCursor;

/* Suivi de positions dans un panneau de chargement (classe) */
typedef struct _GLineCursorClass GLineCursorClass;


/* Détermine le type du suivi de positions dans un panneau de chargement. */
GType g_line_cursor_get_type(void);

/* Réalise la copie d'un suivi d'emplacements. */
GLineCursor *g_line_cursor_duplicate(const GLineCursor *);

/* Compare deux suivis d'emplacements. */
int g_line_cursor_compare(const GLineCursor *, const GLineCursor *);

/* Détermine si la position de suivi est pertinente ou non. */
bool g_line_cursor_is_valid(const GLineCursor *);

/* Construit une étiquette de représentation d'un suivi. */
char *g_line_cursor_build_label(const GLineCursor *);

/* Affiche une position dans une barre de statut. */
void g_line_cursor_show_status(const GLineCursor *, GtkStatusStack *, GLoadedContent *);



/* ---------------------- ENCADREMENT DES TRANSFERTS DE DONEES ---------------------- */


/* Exporte la définition d'un emplacement dans un flux réseau. */
bool g_line_cursor_serialize(const GLineCursor *, packed_buffer_t *);

/* Importe la définition d'un emplacement depuis un flux réseau. */
bool g_line_cursor_unserialize(GLineCursor *, packed_buffer_t *);



/* ------------------------- LIENS AVEC UNE BASE DE DONNEES ------------------------- */


/* Donne les éléments requis pour la construction d'une table. */
char *g_line_cursor_create_db_table(const GLineCursor *, const char *);

/* Décrit les colonnes utiles à un chargement de données. */
bool g_line_cursor_setup_load(const GLineCursor *, const char *, bound_value **, size_t *);

/* Charge les valeurs utiles pour une localisation. */
bool g_line_cursor_load(GLineCursor *, const char *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
bool g_line_cursor_store(const GLineCursor *, const char *, bound_value **, size_t *);



#endif  /* _GLIBEXT_GLINECURSOR_H */
