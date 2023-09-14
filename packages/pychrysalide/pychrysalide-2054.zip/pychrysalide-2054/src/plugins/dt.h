
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dt.h - prototypes pour la possibilité de créer de nouveaux types de façon dynamique
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _PLUGINS_DT_H
#define _PLUGINS_DT_H


#include <glib-object.h>
#include <stdbool.h>



/* ----------------------- ACCOMPAGNEMENTS DES NOUVEAUX TYPES ----------------------- */


/* Lance le support de dérivations de types dans Chrysalide. */
bool init_chrysalide_dynamic_types(void);

/* Arrête le support de dérivations de types dans Chrysalide. */
void exit_chrysalide_dynamic_types(void);

/* Fournit un identifiant GLib pour un nouveau type. */
GType build_dynamic_type(GType, const char *, GClassInitFunc, gconstpointer, GInstanceInitFunc);

/* Crée un objet à partir d'un type, dynamique ou classique. */
gpointer create_object_from_type(GType);



#endif  /* _PLUGINS_PYCHRYSALIDE_DT_H */
