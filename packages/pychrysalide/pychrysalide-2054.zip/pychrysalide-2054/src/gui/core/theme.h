
/* Chrysalide - Outil d'analyse de fichiers binaires
 * theme.h - prototypes pour l'ajout d'extensions au thème GTK
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_CORE_THEME_H
#define _GUI_CORE_THEME_H


#include <stdbool.h>
#include <gtk/gtk.h>



/* Parcourt tous les répertoires connus pour trouver un thème. */
void load_all_themes(void);

/* Décharge tous les thèmes référencés en mémoire. */
void unload_all_themes(void);

/* Charge le thème GTK pour les composants spécifiques. */
bool apply_gtk_theme(const char *);

/* Ajoute les définitions CSS à partir d'un chemin donné. */
GtkCssProvider *load_css_content(GdkScreen *, const char *);



#endif  /* _GUI_CORE_THEME_H */
