
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encapsulated.h - prototypes pour le chargement de données binaires à partir d'un fichier
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


#ifndef _ANALYSIS_CONTENTS_ENCAPSULATED_H
#define _ANALYSIS_CONTENTS_ENCAPSULATED_H


#include <glib-object.h>


#include "../content.h"



#define G_TYPE_ENCAPS_CONTENT            (g_encaps_content_get_type())
#define G_ENCAPS_CONTENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ENCAPS_CONTENT, GEncapsContent))
#define G_IS_ENCAPS_CONTENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ENCAPS_CONTENT))
#define G_ENCAPS_CONTENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ENCAPS_CONTENT, GEncapsContentClass))
#define G_IS_ENCAPS_CONTENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ENCAPS_CONTENT))
#define G_ENCAPS_CONTENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ENCAPS_CONTENT, GEncapsContentClass))


/* Contenu de issu d'un contenu plus global (instance) */
typedef struct _GEncapsContent GEncapsContent;

/* Contenu de issu d'un contenu plus global (classe) */
typedef struct _GEncapsContentClass GEncapsContentClass;


/* Indique le type défini par la GLib pour les contenus encapsulés. */
GType g_encaps_content_get_type(void);

/* Charge en mémoire un contenu binaire encapsulé. */
GBinContent *g_encaps_content_new(GBinContent *, const char *, GBinContent *);

/* Indique la base d'un contenu binaire encapsulé. */
GBinContent *g_encaps_content_get_base(const GEncapsContent *);

/* Fournit le chemin vers le contenu interne représenté. */
const char *g_encaps_content_get_path(const GEncapsContent *);

/* Indique le contenu binaire embarqué dans une encapsulation. */
GBinContent *g_encaps_content_get_endpoint(const GEncapsContent *);



#endif  /* _ANALYSIS_CONTENTS_ENCAPSULATED_H */
