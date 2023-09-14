
/* Chrysalide - Outil d'analyse de fichiers binaires
 * prologue.h - prototypes pour la génération à la volée de lignes d'introduction
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


#ifndef _GLIBEXT_GENERATORS_PROLOGUE_H
#define _GLIBEXT_GENERATORS_PROLOGUE_H


#include <glib-object.h>


#include "../../analysis/human/lang.h"
#include "../../format/format.h"



#define G_TYPE_INTRO_GENERATOR             (g_intro_generator_get_type())
#define G_INTRO_GENERATOR(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CODE_BUFFER, GIntroGenerator))
#define G_INTRO_GENERATOR_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CODE_BUFFER, GIntroGeneratorClass))
#define G_IS_INTRO_GENERATOR(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CODE_BUFFER))
#define G_IS_INTRO_GENERATOR_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CODE_BUFFER))
#define G_INTRO_GENERATOR_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CODE_BUFFER, GIntroGeneratorClass))


/* Tampon pour générateur de lignes en prologue (instance) */
typedef struct _GIntroGenerator GIntroGenerator;

/* Tampon pour générateur de lignes en prologue (classe) */
typedef struct _GIntroGeneratorClass GIntroGeneratorClass;


/* Détermine le type du générateur de lignes d'introduction à la volée. */
GType g_intro_generator_get_type(void);

/* Crée un nouveau générateur de lignes d'introduction. */
GIntroGenerator *g_intro_generator_new(const GBinFormat *, const GCodingLanguage *, char **, size_t);



#endif  /* _GLIBEXT_GENERATORS_PROLOGUE_H */
