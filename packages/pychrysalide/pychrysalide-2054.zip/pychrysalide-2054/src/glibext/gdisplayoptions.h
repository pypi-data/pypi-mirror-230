
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gdisplayoptions.h - prototypes pour les options de rendus des lignes de code
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


#ifndef _GLIBEXT_GDISPLAYOPTIONS_H
#define _GLIBEXT_GDISPLAYOPTIONS_H


#include <glib-object.h>
#include <stdbool.h>



#define G_TYPE_DISPLAY_OPTIONS            g_display_options_get_type()
#define G_DISPLAY_OPTIONS(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DISPLAY_OPTIONS, GDisplayOptions))
#define G_IS_DISPLAY_OPTIONS(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DISPLAY_OPTIONS))
#define G_DISPLAY_OPTIONS_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DISPLAY_OPTIONS, GDisplayOptionsClass))
#define G_IS_DISPLAY_OPTIONS_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DISPLAY_OPTIONS))
#define G_DISPLAY_OPTIONS_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DISPLAY_OPTIONS, GDisplayOptionsClass))


/* Options de représentation (instance) */
typedef struct _GDisplayOptions GDisplayOptions;

/* Options de représentation (classe) */
typedef struct _GDisplayOptionsClass GDisplayOptionsClass;


/* Indique le type défini pour des options de représentation. */
GType g_display_options_get_type(void);

/* Crée un groupe d'options pour le rendu des lignes. */
GDisplayOptions *g_display_options_new(void);

/* Copie un groupe d'options pour le rendu des lignes. */
GDisplayOptions *g_display_options_dup(const GDisplayOptions *);

/* Dénombre la quantité d'options représentées. */
size_t g_display_options_count(const GDisplayOptions *);

/* Ajoute une nouvelle option à l'ensemble. */
void g_display_options_add(GDisplayOptions *, const char *, bool);

/* Fournit la désignation d'une option donnée. */
const char *g_display_options_get_name(const GDisplayOptions *, size_t);

/* Fournit la valeur d'une option donnée. */
bool g_display_options_get(const GDisplayOptions *, size_t);

/* Définit la valeur d'une option donnée. */
void g_display_options_set(GDisplayOptions *, size_t, bool);



#endif  /* _GLIBEXT_GDISPLAYOPTIONS_H */
