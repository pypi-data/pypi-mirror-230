
/* Chrysalide - Outil d'analyse de fichiers binaires
 * restricted.h - prototypes pour le chargement de données binaires à partir d'un contenu restreint
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_CONTENTS_RESTRICTED_H
#define _ANALYSIS_CONTENTS_RESTRICTED_H


#include <glib-object.h>


#include "../content.h"



#define G_TYPE_RESTRICTED_CONTENT             (g_restricted_content_get_type())
#define G_RESTRICTED_CONTENT(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RESTRICTED_CONTENT, GRestrictedContent))
#define G_IS_RESTRICTED_CONTENT(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RESTRICTED_CONTENT))
#define G_RESTRICTED_CONTENT_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RESTRICTED_CONTENT, GRestrictedContentClass))
#define G_IS_RESTRICTED_CONTENT_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RESTRICTED_CONTENT))
#define G_RESTRICTED_CONTENT_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RESTRICTED_CONTENT, GRestrictedContentClass))


/* Contenu de données binaires issues d'un contenu restreint (instance) */
typedef struct _GRestrictedContent GRestrictedContent;

/* Contenu de données binaires issues d'un contenu restreint (classe) */
typedef struct _GRestrictedContentClass GRestrictedContentClass;


/* Indique le type défini par la GLib pour les contenus de données. */
GType g_restricted_content_get_type(void);

/* Charge en mémoire le contenu d'un contenu restreint. */
GBinContent *g_restricted_content_new(GBinContent *, const mrange_t *);

/* Charge en mémoire le contenu d'un contenu restreint. */
GBinContent *g_restricted_content_new_ro(const GBinContent *, const mrange_t *);

/* Indique l'espace de restriction appliqué à un contenu. */
void g_restricted_content_get_range(const GRestrictedContent *, mrange_t *);



#endif  /* _ANALYSIS_CONTENTS_RESTRICTED_H */
