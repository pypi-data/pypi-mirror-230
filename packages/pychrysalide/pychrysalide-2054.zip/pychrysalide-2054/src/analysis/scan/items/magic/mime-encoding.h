
/* Chrysalide - Outil d'analyse de fichiers binaires
 * mime-encoding.h - prototypes pour la reconnaissance de l'encodage d'un contenu
 *
 * Copyright (C) 2023 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_ITEMS_MAGIC_MIME_ENCODING_H
#define _ANALYSIS_SCAN_ITEMS_MAGIC_MIME_ENCODING_H


#include <glib-object.h>


#include "../../item.h"



#define G_TYPE_SCAN_MIME_ENCODING_FUNCTION            g_scan_mime_encoding_function_get_type()
#define G_SCAN_MIME_ENCODING_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_MIME_ENCODING_FUNCTION, GScanMimeEncodingFunction))
#define G_IS_SCAN_MIME_ENCODING_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_MIME_ENCODING_FUNCTION))
#define G_SCAN_MIME_ENCODING_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_MIME_ENCODING_FUNCTION, GScanMimeEncodingFunctionClass))
#define G_IS_SCAN_MIME_ENCODING_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_MIME_ENCODING_FUNCTION))
#define G_SCAN_MIME_ENCODING_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_MIME_ENCODING_FUNCTION, GScanMimeEncodingFunctionClass))


/* Reconnaissance d'encodages de contenus (instance) */
typedef GRegisteredItem GScanMimeEncodingFunction;

/* Reconnaissance d'encodages de contenus (classe) */
typedef GRegisteredItemClass GScanMimeEncodingFunctionClass;


/* Indique le type défini pour une reconnaissance d'encodages de contenus. */
GType g_scan_mime_encoding_function_get_type(void);

/* Constitue une fonction de cernement d'encodages de contenus. */
GRegisteredItem *g_scan_mime_encoding_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_MAGIC_MIME_ENCODING_H */
