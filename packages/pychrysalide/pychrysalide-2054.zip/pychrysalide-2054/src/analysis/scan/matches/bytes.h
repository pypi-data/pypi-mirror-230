
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bytes.h - prototypes pour la sauvegarde d'une correspondance identifiée de suite d'octets
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_MATCHES_BYTES_H
#define _ANALYSIS_SCAN_MATCHES_BYTES_H


#include <glib-object.h>


#include "../match.h"
#include "../../content.h"



#define G_TYPE_SCAN_BYTES_MATCH            g_scan_bytes_match_get_type()
#define G_SCAN_BYTES_MATCH(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_BYTES_MATCH, GScanBytesMatch))
#define G_IS_SCAN_BYTES_MATCH(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_BYTES_MATCH))
#define G_SCAN_BYTES_MATCH_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_BYTES_MATCH, GScanBytesMatchClass))
#define G_IS_SCAN_BYTES_MATCH_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_BYTES_MATCH))
#define G_SCAN_BYTES_MATCH_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_BYTES_MATCH, GScanBytesMatchClass))


/* Correspondance trouvée avec une chaîne (instance) */
typedef struct _GScanBytesMatch GScanBytesMatch;

/* Correspondance trouvée avec une chaîne (classe) */
typedef struct _GScanBytesMatchClass GScanBytesMatchClass;


/* Indique le type défini pour un correspondance de chaîne identifiée. */
GType g_scan_bytes_match_get_type(void);

/* Prend note d'une correspondance trouvée avec un motif. */
GScanMatch *g_scan_bytes_match_new(GSearchPattern *, GBinContent *, phys_t, phys_t);

/* Fournit une référence au contenu lié à la correspondance. */
GBinContent *g_scan_bytes_match_get_content(const GScanBytesMatch *);

/* Indique la localisation d'une correspondance établie. */
phys_t g_scan_bytes_match_get_location(const GScanBytesMatch *, phys_t *, phys_t *);



#endif  /* _ANALYSIS_SCAN_MATCHES_BYTES_H */
