
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


#include "rendering.h"


#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <gtk/gtk.h>


#include "../common/extstr.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : name    = désignation d'un élément dans une feuille de style.*
*                pattern = paramètres restitués en interne. |OUT]             *
*                                                                             *
*  Description : Récupère les informations de rendus d'un élément de thème.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_rendering_pattern(const char *name, rendering_pattern_t *pattern)
{
    GtkStyleContext *context;               /* Contexte pour les styles    */
    GtkWidgetPath *path;                    /* Chemin d'accès aux thèmes   */
    GdkRGBA *tmp_color;                     /* Description d'une couleur   */
    PangoFontDescription *font_desc;        /* Description d'une police    */

    /* Création d'un contexte d'accès */

    path = gtk_widget_path_new();
    gtk_widget_path_append_type(path, G_TYPE_OBJECT);

    context = gtk_style_context_new();
    gtk_style_context_set_path(context, path);
    gtk_style_context_set_screen(context, gdk_screen_get_default());

    gtk_style_context_add_class(context, name);

    gtk_style_context_get(context, GTK_STATE_FLAG_NORMAL, GTK_STYLE_PROPERTY_COLOR, &tmp_color, NULL);

    pattern->foreground.has_color = true;
    pattern->foreground.color = *tmp_color;

    pattern->inverted.has_color = true;
    pattern->inverted.color.red = 1.0 - tmp_color->red;
    pattern->inverted.color.green = 1.0 - tmp_color->green;
    pattern->inverted.color.blue = 1.0 - tmp_color->blue;
    pattern->inverted.color.alpha = tmp_color->alpha;

    gdk_rgba_free(tmp_color);

    gtk_style_context_get(context, GTK_STATE_FLAG_NORMAL, GTK_STYLE_PROPERTY_FONT, &font_desc, NULL);

    switch (pango_font_description_get_style(font_desc))
    {
        case PANGO_STYLE_NORMAL:
            pattern->slant = CAIRO_FONT_SLANT_NORMAL;
            break;
        case PANGO_STYLE_ITALIC:
            pattern->slant = CAIRO_FONT_SLANT_ITALIC;
            break;
        case PANGO_STYLE_OBLIQUE:
            pattern->slant = CAIRO_FONT_SLANT_OBLIQUE;
            break;
    }

    switch (pango_font_description_get_weight(font_desc))
    {
        case PANGO_WEIGHT_THIN:
        case PANGO_WEIGHT_ULTRALIGHT:	
        case PANGO_WEIGHT_LIGHT:
        case PANGO_WEIGHT_SEMILIGHT:
        case PANGO_WEIGHT_BOOK:
        case PANGO_WEIGHT_NORMAL:
        case PANGO_WEIGHT_MEDIUM:
            pattern->weight = CAIRO_FONT_WEIGHT_NORMAL;
            break;
        case PANGO_WEIGHT_SEMIBOLD:
        case PANGO_WEIGHT_BOLD:
        case PANGO_WEIGHT_ULTRABOLD:
        case PANGO_WEIGHT_HEAVY:
        case PANGO_WEIGHT_ULTRAHEAVY:
            pattern->weight = CAIRO_FONT_WEIGHT_BOLD;
            break;
    }

    pango_font_description_free(font_desc);

    gtk_widget_path_free(path);
    g_object_unref(context);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : text    = texte à encadrer par des balises Pango.            *
*                pattern = paramètres restitués en interne.                   *
*                                                                             *
*  Description : Enjolive du texte selon les paramètres d'un élément de thème.*
*                                                                             *
*  Retour      : Chaîne de caractère à libérer après usage.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_pango_markup_for(const char *text, const rendering_pattern_t *pattern)
{
    char *result;                           /* Construction à retourner    */
    char color[10];                         /* Définition hexa de couleur  */

    result = strdup(text);

    if (pattern->foreground.has_color)
    {
        snprintf(color, sizeof(color), "#%02hhx%02hhx%02hhx%02hhx",
                (unsigned char)(255 * pattern->foreground.color.red),
                (unsigned char)(255 * pattern->foreground.color.green),
                (unsigned char)(255 * pattern->foreground.color.blue),
                (unsigned char)(255 * pattern->foreground.color.alpha));

        result = strprep(result, "\">");
        result = strprep(result, color);
        result = strprep(result, "<span color=\"");

        result = stradd(result, "</span>");

    }

    if (pattern->slant == CAIRO_FONT_SLANT_ITALIC || pattern->slant == CAIRO_FONT_SLANT_OBLIQUE)
    {
        result = strprep(result, "<i>");
        result = stradd(result, "</i>");
    }

    if (pattern->weight == CAIRO_FONT_WEIGHT_BOLD)
    {
        result = strprep(result, "<b>");
        result = stradd(result, "</b>");
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base    = base de texte à compléter.                         *
*                text    = texte à encadrer par des balises Pango.            *
*                pattern = paramètres restitués en interne.                   *
*                                                                             *
*  Description : Ajoute du texte enjolivé selon un élément de thème.          *
*                                                                             *
*  Retour      : Chaîne de caractère à libérer après usage.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *append_pango_markup_with(char *base, const char *text, const rendering_pattern_t *pattern)
{
    char *result;                           /* Construction à retourner    */
    char *tmp;                              /* Stockage temporaire         */

    tmp = build_pango_markup_for(text, pattern);

    result = stradd(base, tmp);

    free(tmp);

    return result;

}
