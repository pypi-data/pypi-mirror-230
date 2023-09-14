
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rborder.h - prototypes pour la génération à la volée de délimitations de routines
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _GLIBEXT_GENERATORS_RBORDER_H
#define _GLIBEXT_GENERATORS_RBORDER_H


#include <glib-object.h>
#include <stdbool.h>


#include "../../analysis/human/lang.h"
#include "../../arch/vmpa.h"



#define G_TYPE_BORDER_GENERATOR             (g_border_generator_get_type())
#define G_BORDER_GENERATOR(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CODE_BUFFER, GBorderGenerator))
#define G_BORDER_GENERATOR_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CODE_BUFFER, GBorderGeneratorClass))
#define G_IS_BORDER_GENERATOR(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CODE_BUFFER))
#define G_IS_BORDER_GENERATOR_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CODE_BUFFER))
#define G_BORDER_GENERATOR_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CODE_BUFFER, GBorderGeneratorClass))


/* Tampon pour générateur de délimitations de routines (instance) */
typedef struct _GBorderGenerator GBorderGenerator;

/* Tampon pour générateur de délimitations de routines (classe) */
typedef struct _GBorderGeneratorClass GBorderGeneratorClass;


/* Détermine le type du générateur de délimitations de routines à la volée. */
GType g_border_generator_get_type(void);

/* Crée un nouveau générateur de délimitations de routines. */
GBorderGenerator *g_border_generator_new(GCodingLanguage *, const vmpa2t *, bool, MemoryDataSize);



#endif  /* _GLIBEXT_GENERATORS_RBORDER_H */
