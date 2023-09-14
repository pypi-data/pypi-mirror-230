
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.h - prototypes pour la génération à la volée de lignes hexadécimales
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GLIBEXT_GENERATORS_HEX_H
#define _GLIBEXT_GENERATORS_HEX_H


#include <glib-object.h>


#include "../../analysis/content.h"



#define G_TYPE_HEX_GENERATOR            (g_hex_generator_get_type())
#define G_HEX_GENERATOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_HEX_GENERATOR, GHexGenerator))
#define G_IS_HEX_GENERATOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_HEX_GENERATOR))
#define G_HEX_GENERATOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_HEX_GENERATOR, GHexGeneratorClass))
#define G_IS_HEX_GENERATOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_HEX_GENERATOR))
#define G_HEX_GENERATOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_HEX_GENERATOR, GHexGeneratorClass))


/* Tampon pour générateur de lignes hexadécimales (instance) */
typedef struct _GHexGenerator GHexGenerator;

/* Tampon pour générateur de lignes hexadécimales (classe) */
typedef struct _GHexGeneratorClass GHexGeneratorClass;


/* Détermine le type du générateur de lignes hexadécimales à la volée. */
GType g_hex_generator_get_type(void);

/* Crée un nouveau générateur de lignes hexadécimales. */
GHexGenerator *g_hex_generator_new(GBinContent *);

/* Fournit le contenu associé au générateur de lignes hexa. */
GBinContent *g_hex_generator_get_content(const GHexGenerator *);

/* Ajuste la génération à une nouvelle largeur de rendu. */
bool g_hex_generator_auto_fit(GHexGenerator *, gint, bool, gint, gint);

/* Indique le nombre d'octets programmés constituer une ligne. */
phys_t g_hex_generator_get_bytes_per_line(const GHexGenerator *);



#endif  /* _GLIBEXT_GENERATORS_HEX_H */
