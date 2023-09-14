
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cattribs.h - prototypes pour le rassemblement des attributs utiles au chargement d'un contenu binaire
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


#ifndef _ANALYSIS_CATTRIBS_H
#define _ANALYSIS_CATTRIBS_H


#include <glib-object.h>


#define G_TYPE_CONTENT_ATTRIBUTES            g_content_attributes_get_type()
#define G_CONTENT_ATTRIBUTES(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CONTENT_ATTRIBUTES, GContentAttributes))
#define G_IS_CONTENT_ATTRIBUTES(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CONTENT_ATTRIBUTES))
#define G_CONTENT_ATTRIBUTES_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CONTENT_ATTRIBUTES, GContentAttributesClass))
#define G_IS_CONTENT_ATTRIBUTES_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CONTENT_ATTRIBUTES))
#define G_CONTENT_ATTRIBUTES_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CONTENT_ATTRIBUTES, GContentAttributesClass))


/* Ensemble d'attributs pour contenu binaire (instance) */
typedef struct _GContentAttributes GContentAttributes;

/* Ensemble d'attributs pour contenu binaire (classe) */
typedef struct _GContentAttributesClass GContentAttributesClass;


/* Indique le type défini pour un ensemble d'attributs de contenu binaire. */
GType g_content_attributes_get_type(void);

/* Construit un ensemble d'attribut pour contenu binaire. */
GContentAttributes *g_content_attributes_new(const char *, char **);

/* Fournit l'ensemble des clefs d'un ensemble d'attributs. */
const char **g_content_attributes_get_keys(const GContentAttributes *, size_t *);

/* Indique la valeur d'un attribut appartenant à un ensemble. */
const char *g_content_attributes_get_value(const GContentAttributes *, const char *);



#endif  /* _ANALYSIS_CATTRIBS_H */
