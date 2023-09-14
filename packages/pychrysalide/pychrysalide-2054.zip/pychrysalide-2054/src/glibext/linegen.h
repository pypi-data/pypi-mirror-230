
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linegen.h - prototypes pour les intermédiaires de génération de lignes
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


#ifndef _GLIBEXT_LINEGEN_H
#define _GLIBEXT_LINEGEN_H


#include <glib-object.h>


#include "bufferline.h"
#include "glinecursor.h"
#include "../analysis/content.h"



#define G_TYPE_LINE_GENERATOR               g_line_generator_get_type()
#define G_LINE_GENERATOR(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LINE_GENERATOR, GLineGenerator))
#define G_LINE_GENERATOR_CLASS(vtable)      (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_LINE_GENERATOR, GLineGeneratorIface))
#define GTK_IS_LINE_GENERATOR(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LINE_GENERATOR))
#define GTK_IS_LINE_GENERATOR_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_LINE_GENERATOR))
#define G_LINE_GENERATOR_GET_IFACE(inst)    (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_LINE_GENERATOR, GLineGeneratorIface))


/* Intermédiaire pour la génération de lignes (coquille vide) */
typedef struct _GLineGenerator GLineGenerator;

/* Intermédiaire pour la génération de lignes (interface) */
typedef struct _GLineGeneratorIface GLineGeneratorIface;


/* Détermine le type d'une interface pour la mise en place de lignes. */
GType g_line_generator_get_type(void) G_GNUC_CONST;

/* Indique le nombre de ligne prêtes à être générées. */
size_t g_line_generator_count_lines(const GLineGenerator *);

/* Retrouve l'emplacement correspondant à une position donnée. */
GLineCursor *g_line_generator_compute_cursor(const GLineGenerator *, gint, size_t, size_t);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
int g_line_generator_contain_cursor(const GLineGenerator *, size_t, size_t, const GLineCursor *);

/* Renseigne sur les propriétés liées à un générateur. */
BufferLineFlags g_line_generator_get_flags(const GLineGenerator *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
void g_line_generator_print(GLineGenerator *, GBufferLine *, size_t, size_t, const GBinContent *);



#endif  /* _GLIBEXT_LINEGEN_H */
