
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linecolumn.h - prototypes pour le regroupement des segments de texte par colonnes
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


#include "linecolumn.h"


#include <assert.h>
#include <malloc.h>


#include "../common/extstr.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne à initialiser.                     *
*                                                                             *
*  Description : Initialise une colonne de ligne.                             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_line_column(line_column *column)
{
    column->segments = NULL;
    column->count = 0;

#ifdef INCLUDE_GTK_SUPPORT
    column->max_width = 0;
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne à mettre à jour.                   *
*                                                                             *
*  Description : Réinitialise une colonne de ligne.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_line_column(line_column *column)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < column->count; i++)
        release_line_segment(column->segments[i]);

    if (column->segments != NULL)
    {
        free(column->segments);
        column->segments = NULL;
    }

    column->count = 0;

#ifdef INCLUDE_GTK_SUPPORT
    column->max_width = 0;
#endif

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne à mettre à jour.                   *
*                                                                             *
*  Description : Recalcule la largeur d'une colonne de segments.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void refresh_line_column_width(line_column *column)
{
    size_t i;                               /* Boucle de parcours          */

    column->max_width = 0;

    for (i = 0; i < column->count; i++)
        column->max_width += get_line_segment_width(column->segments[i]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column  = colonne de ligne à consulter.                      *
*                                                                             *
*  Description : Fournit la quantité de pixels requise pour l'impression.     *
*                                                                             *
*  Retour      : Largeur requise par la colonne, en pixel.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint get_column_width(const line_column *column)
{
    return column->max_width;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : column  = colonne de ligne à venir compléter.                *
*                text    = texte à insérer dans l'existant.                   *
*                length  = taille du texte à traiter.                         *
*                type    = type de décorateur à utiliser.                     *
*                                                                             *
*  Description : Ajoute un fragment de texte à une colonne de ligne.          *
*                                                                             *
*  Retour      : Indice du point d'insertion.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t append_text_to_line_column(line_column *column, const char *text, size_t length, RenderingTagType type)
{
    size_t result;                          /* Indice à retourner          */
    line_segment *segment;                  /* Contenu à représenter       */

    result = column->count;

    segment = get_new_line_segment(type, text, length);

    column->segments = realloc(column->segments, ++column->count * sizeof(line_segment *));

    column->segments[result] = segment;

#ifdef INCLUDE_GTK_SUPPORT
    column->max_width += get_line_segment_width(segment);
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column  = colonne de ligne à venir compléter.                *
*                index   = indice du frament de texte à remplacer.            *
*                text    = texte à insérer dans l'existant.                   *
*                length  = taille du texte à traiter.                         *
*                                                                             *
*  Description : Remplace un fragment de texte dans une colonne de ligne.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void replace_text_in_line_column(line_column *column, size_t index, const char *text, size_t length)
{
    RenderingTagType type;                  /* Type de rendu à conserver   */
    line_segment *segment;                  /* Contenu à représenter       */

    assert(index < column->count);

    /* Retrait */

    segment = column->segments[index];

    type = get_line_segment_type(segment);

    release_line_segment(segment);

    /* Ajout */

    segment = get_new_line_segment(type, text, length);

    column->segments[index] = segment;

#ifdef INCLUDE_GTK_SUPPORT
    refresh_line_column_width(column);
#endif

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à consulter.              *
*                index  = indice du contenu enregistré à la position. [OUT]   *
*                                                                             *
*  Description : Indique l'indice du premier contenu de la colonne.           *
*                                                                             *
*  Retour      : Validité de l'indice renseigné.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_line_column_first_content_index(const line_column *column, size_t *index)
{
    bool result;                            /* Bilan à retourner           */

    result = (column->count > 0);

    if (result)
        *index = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à consulter.              *
*                index  = indice du contenu enregistré à la position. [OUT]   *
*                                                                             *
*  Description : Indique l'indice du dernier contenu de la colonne.           *
*                                                                             *
*  Retour      : Validité de l'indice renseigné.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_line_column_last_content_index(const line_column *column, size_t *index)
{
    bool result;                            /* Bilan à retourner           */

    result = (column->count > 0);

    if (result)
        *index = column->count - 1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à consulter.              *
*                index  = indice à consulter puis renseigner. [OUT]           *
*                dir    = orientation des recherches.                         *
*                                                                             *
*  Description : Fournit le segment voisin d'un autre segment identifié.      *
*                                                                             *
*  Retour      : Validité de l'indice renseigné.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_near_segment(const line_column *column, size_t *index, GdkScrollDirection dir)
{
    bool result;                            /* Bilan à faire remonter      */

    result = false;

    switch (dir)
    {
        case GDK_SCROLL_LEFT:
            if (*index > 0)
            {
                (*index)--;
                result = true;
            }
            break;

        case GDK_SCROLL_RIGHT:
            if ((*index + 1) < column->count)
            {
                (*index)++;
                result = true;
            }
            break;

        default:
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column   = colonne de ligne de texte à consulter.            *
*                x        = position de recherche, puis position locale. [OUT]*
*                dir      = direction d'un éventuel déplacement en cours.     *
*                consumed = distance pour arriver à la base du segment. [OUT] *
*                index    = indice du contenu enregistré à la position. [OUT] *
*                                                                             *
*  Description : Indique l'indice du contenu de colonne à une abscisse donnée.*
*                                                                             *
*  Retour      : Validité de l'indice renseigné.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_line_column_content_index_at(const line_column *column, gint *x, GdkScrollDirection dir, gint *consumed, size_t *index)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    gint width;                             /* Largeur à retirer           */
    bool included;                          /* Appartenance à une largeur ?*/

    result = false;
    *consumed = 0;

    for (i = 0; i < column->count && !result; i++)
    {
        width = get_line_segment_width(column->segments[i]);

        /**
         * Soit une limite entre deux segments A et B :
         *
         *  - dans le cas d'un déplacement vers la gauche, on part de cette limite
         *    pour progresser à l'intérieur de A. Donc la limite fait partie de A.
         *
         *  - dans le cas d'un déplacement vers la droite, on part de cette limite
         *    pour progresser à l'intérieur de B. Donc la limite ne fait pas partie de A.
         */
        if (dir == GDK_SCROLL_LEFT) included = (width >= *x);
        else included = (width > *x);

        if (included)
        {
            *index = i;
            result = true;
        }

        else if ((i + 1) == column->count)
        {
            *index = i;
            result = true;
            *x = width;
        }

        else
        {
            *x -= width;
            *consumed += width;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à consulter.              *
*                index  = indice du contenu à fournir.                        *
*                                                                             *
*  Description : Donne le segment d'une colonne présent à un indice donné.    *
*                                                                             *
*  Retour      : Segment trouvé ou NULL si hors borne.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

line_segment *get_line_column_content_from_index(const line_column *column, size_t index)
{
    line_segment *result;                   /* Trouvaille à retourner      */

    assert(index != -1 && index < column->count);

    result = column->segments[index];

    ref_line_segment(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à manipuler.              *
*                cairo  = contexte graphique à utiliser pour les pinceaux.    *
*                x_init = abscisse du point d'impression de départ.           *
*                y      = ordonnée du point d'impression.                     *
*                list   = liste de contenus à mettre en évidence.             *
*                                                                             *
*  Description : Imprime le contenu d'une colonne de ligne de texte.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void draw_line_column_segments(const line_column *column, cairo_t *cairo, gint x_init, gint y, const segcnt_list *list)
{
    gint x;                                 /* Abscisse d'impression       */
    size_t i;                               /* Boucle de parcours          */

    x = x_init;

    for (i = 0; i < column->count; i++)
        draw_line_segment(column->segments[i], cairo, &x, y, list);

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à venir consulter.        *
*                markup = indique si le texte doit être décoré ou non.        *
*                                                                             *
*  Description : Donne le texte représenté par une colonne de ligne de texte. *
*                                                                             *
*  Retour      : Texte à libérer de la mémoire après usage.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_line_column_text(const line_column *column, bool markup)
{
    char *result;                           /* Construction à retourner    */
    size_t i;                               /* Boucle de parcours          */
    char *extra;                            /* Contenu à intégrer au texte */

    result = NULL;

    for (i = 0; i < column->count; i++)
    {
        extra = get_line_segment_text(column->segments[i], markup);

        if (result == NULL)
            result = extra;

        else
        {
            result = stradd(result, extra);
            free(extra);
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : column = colonne de ligne de texte à manipuler.              *
*                ctx    = éléments à disposition pour l'exportation.          *
*                type   = type d'exportation attendue.                        *
*                span   = fusion de colonnes au sein des cellules ?           *
*                                                                             *
*  Description : Exporte la ligne de texte représentée.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void export_line_column_segments(const line_column *column, buffer_export_context *ctx, BufferExportType type, int span)
{
    size_t i;                               /* Boucle de parcours          */

    switch (type)
    {
        case BET_HTML:
            switch (span)
            {
                case 0:
                    break;
                case 1:
                    dprintf(ctx->fd, "\t\t<TD>");
                    break;
                default:
                    if (span > 0) dprintf(ctx->fd, "\t\t<TD colspan=\"%d\">", span);
                    break;
            }
            break;
        default:
            break;
    }

    for (i = 0; i < column->count; i++)
        export_line_segment(column->segments[i], ctx, type);

    switch (type)
    {
        case BET_HTML:
            if (span < 0 || span == 1) dprintf(ctx->fd, "</TD>\n");
            break;
        default:
            break;
    }

}
