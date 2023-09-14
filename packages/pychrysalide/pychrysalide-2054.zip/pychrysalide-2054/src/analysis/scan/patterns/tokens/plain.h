
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plain.h - prototypes pour la recherche d'une chaîne de caractères brute
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_PLAIN_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_PLAIN_H


#include <glib-object.h>


#include "node.h"
#include "../../pattern.h"



#define G_TYPE_SCAN_PLAIN_BYTES            g_scan_plain_bytes_get_type()
#define G_SCAN_PLAIN_BYTES(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_PLAIN_BYTES, GScanPlainBytes))
#define G_IS_SCAN_PLAIN_BYTES(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_PLAIN_BYTES))
#define G_SCAN_PLAIN_BYTES_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_PLAIN_BYTES, GScanPlainBytesClass))
#define G_IS_SCAN_PLAIN_BYTES_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_PLAIN_BYTES))
#define G_SCAN_PLAIN_BYTES_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_PLAIN_BYTES, GScanPlainBytesClass))


/* Représentation d'une suite d'octets à retrouver (instance) */
typedef struct _GScanPlainBytes GScanPlainBytes;

/* Représentation d'une suite d'octets à retrouver (classe) */
typedef struct _GScanPlainBytesClass GScanPlainBytesClass;


/* Indique le type défini pour une suite d'octets à retrouver dans un binaire. */
GType g_scan_plain_bytes_get_type(void);

/* Construit un gestionnaire de recherche de texte brut. */
GSearchPattern *g_scan_plain_bytes_new(GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_PLAIN_H */
