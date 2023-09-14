
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.h - prototypes pour le décodage des noms d'éléments
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


#ifndef _MANGLING_DEMANGLER_H
#define _MANGLING_DEMANGLER_H


#include "../analysis/routine.h"



#define G_TYPE_COMP_DEMANGLER            g_compiler_demangler_get_type()
#define G_COMP_DEMANGLER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_COMP_DEMANGLER, GCompDemangler))
#define G_IS_COMP_DEMANGLER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_COMP_DEMANGLER))
#define G_COMP_DEMANGLER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_COMP_DEMANGLER, GCompDemanglerClass))
#define G_IS_COMP_DEMANGLER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_COMP_DEMANGLER))
#define G_COMP_DEMANGLER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_COMP_DEMANGLER, GCompDemanglerClass))


/* Décodeur de désignations générique (instance) */
typedef struct _GCompDemangler GCompDemangler;

/* Décodeur de désignations générique (classe) */
typedef struct _GCompDemanglerClass GCompDemanglerClass;


/* Indique le type défini pour un décodeur de désignations. */
GType g_compiler_demangler_get_type(void);

/* Fournit la désignation interne du décodeur de désignations. */
char *g_compiler_demangler_get_key(const GCompDemangler *);

/* Indique le motif de séparation des espaces de noms. */
const char *g_compiler_demangler_get_ns_separator(const GCompDemangler *);

/* Tente de décoder une chaîne de caractères donnée en type. */
GDataType *g_compiler_demangler_decode_type(const GCompDemangler *, const char *);

/* Tente de décoder une chaîne de caractères donnée en routine. */
GBinRoutine *g_compiler_demangler_decode_routine(const GCompDemangler *, const char *);



#endif  /* _MANGLING_DEMANGLER_H */
