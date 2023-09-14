
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.h - prototypes pour le décodage des noms d'éléments Itanium
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


#ifndef _PLUGINS_ITANIUM_DEMANGLER_H
#define _PLUGINS_ITANIUM_DEMANGLER_H


#include <glib-object.h>


#include <mangling/demangler.h>



#define G_TYPE_ITANIUM_DEMANGLER            g_itanium_demangler_get_type()
#define G_ITANIUM_DEMANGLER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ITANIUM_DEMANGLER, GItaniumDemangler))
#define G_IS_ITANIUM_DEMANGLER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ITANIUM_DEMANGLER))
#define G_ITANIUM_DEMANGLER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ITANIUM_DEMANGLER, GItaniumDemanglerClass))
#define G_IS_ITANIUM_DEMANGLER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ITANIUM_DEMANGLER))
#define G_ITANIUM_DEMANGLER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ITANIUM_DEMANGLER, GItaniumDemanglerClass))


/* Décodeur de désignations Itanium (instance) */
typedef struct _GItaniumDemangler GItaniumDemangler;

/* Décodeur de désignations Itanium (classe) */
typedef struct _GItaniumDemanglerClass GItaniumDemanglerClass;


/* Indique le type défini pour un décodeur de désignations Itanium. */
GType g_itanium_demangler_get_type(void);

/* Met en place un nouveau décodeur de symboles pour Itanium. */
GCompDemangler *g_itanium_demangler_new(void);



#endif  /* _PLUGINS_ITANIUM_DEMANGLER_H */
