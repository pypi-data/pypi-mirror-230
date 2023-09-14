
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rendering.h - prototypes pour la transformation de paramètres du thème GTK courant
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GTKEXT_RENDERING_H
#define _GTKEXT_RENDERING_H


#include <stdbool.h>
#include <gdk/gdk.h>



/* Restitution d'une couleur */
typedef struct _rendering_color_t
{
    GdkRGBA color;                          /* Couleur de rendu            */
    bool has_color;                         /* Définition en place ?       */

} rendering_color_t;

/* Restitution d'un élément de thème */
typedef struct _rendering_pattern_t
{
    rendering_color_t foreground;           /* Couleur d'impression        */
    rendering_color_t inverted;             /* Couleur inversée pour sél.  */

    cairo_font_slant_t slant;               /* Style d'impression          */
    cairo_font_weight_t weight;             /* Poids de la police          */

} rendering_pattern_t;


/* Récupère les informations de rendus d'un élément de thème. */
void load_rendering_pattern(const char *, rendering_pattern_t *);

/* Enjolive du texte selon les paramètres d'un élément de thème. */
char *build_pango_markup_for(const char *, const rendering_pattern_t *);

/* Ajoute du texte enjolivé selon un élément de thème. */
char *append_pango_markup_with(char *, const char *, const rendering_pattern_t *);



#endif  /* _GTKEXT_RENDERING_H */
