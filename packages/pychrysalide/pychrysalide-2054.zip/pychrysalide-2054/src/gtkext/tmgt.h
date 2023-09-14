
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tmgt.h - prototypes pour des compléments utiles à la mise en place d'arborescences
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _COMMON_TMGT_H
#define _COMMON_TMGT_H


#include <regex.h>
#include <stdbool.h>
#include <gtk/gtk.h>



/* Met à jour un filtre selon un contenu recherché. */
void update_regex_on_search_entry_changed(GtkSearchEntry *, char **);

/* Détermine si un contenu correspond à un filtre donné. */
bool is_content_matching(const regex_t *, const char *, regmatch_t *);

/* Met en évidence le texte recherché en cas de correspondance. */
char *build_highlighted_name(const char *, const regmatch_t *, size_t);

/* Met à jour l'affichage des noeuds en fonction des besoin. */
void update_node_visibility(GtkTreeStore *, GtkTreeIter *, gint, bool);



#endif  /* _COMMON_TMGT_H */
