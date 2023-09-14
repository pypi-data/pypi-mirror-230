
/* Chrysalide - Outil d'analyse de fichiers binaires
 * edge.c - liens entre les noeuds d'un graphique
 *
 * Copyright (C) 2013-2019 Cyrille Bagard
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


#include "edge.h"


#include <assert.h>
#include <malloc.h>
#include <math.h>
#include <string.h>


#include "../../core/params.h"



/* Lien graphique entre deux noeuds graphiques (instance) */
struct _GGraphEdge
{
    GObject parent;                         /* A laisser en premier        */

    GCodeBlock *src;                        /* Bloc d'origine du lien      */
    GCodeBlock *dst;                        /* Bloc de destination du lien */

    EdgeColor color;                        /* Couleur du rendu            */

    union
    {
        const GdkPoint **templates;         /* Inspirations de coordonnées */
        GdkPoint *points;                   /* Points de la ligne dessinée */
    };
    size_t count;                           /* Quantité de ces points      */

};

/* Lien graphique entre deux noeuds graphiques (classe) */
struct _GGraphEdgeClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Dimensions des flêches */
#define ARROW_LENGHT 10
#define ARROW_DEGREES 10


/* Initialise la classe des liens graphiques entre deux noeuds. */
static void g_graph_edge_class_init(GGraphEdgeClass *);

/* Initialise une encapsulation de bloc virtuel. */
static void g_graph_edge_init(GGraphEdge *);

/* Supprime toutes les références externes. */
static void g_graph_edge_dispose(GGraphEdge *);

/* Procède à la libération totale de la mémoire. */
static void g_graph_edge_finalize(GGraphEdge *);

/* Dessine une flèche au bout du lien représenté. */
static void draw_link_arrow(cairo_t *, gint, gint, gint, gint);



/* Indique le type défini par la GLib pour les liens graphiques entre noeuds. */
G_DEFINE_TYPE(GGraphEdge, g_graph_edge, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des liens graphiques entre deux noeuds. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_edge_class_init(GGraphEdgeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_graph_edge_dispose;
    object->finalize = (GObjectFinalizeFunc)g_graph_edge_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise un lien graphique entre deux noeuds graphiques.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_edge_init(GGraphEdge *edge)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_edge_dispose(GGraphEdge *edge)
{
    g_clear_object(&edge->src);
    g_clear_object(&edge->dst);

    G_OBJECT_CLASS(g_graph_edge_parent_class)->dispose(G_OBJECT(edge));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_edge_finalize(GGraphEdge *edge)
{
    free(edge->points);

    G_OBJECT_CLASS(g_graph_edge_parent_class)->finalize(G_OBJECT(edge));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : templates = coordonnées des futurs points.                   *
*                count     = nombre de ces points fournis.                    *
*                color     = couleur de rendu à l'écran.                      *
*                                                                             *
*  Description : Etablit un lien graphique entre deux noeuds graphiques.      *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphEdge *_g_graph_edge_new(GCodeBlock *src, GCodeBlock *dst, const GdkPoint **templates, size_t count, EdgeColor color)
{
    GGraphEdge *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_GRAPH_EDGE, NULL);

    result->src = src;
    result->dst = dst;

    g_object_ref(G_OBJECT(src));
    g_object_ref(G_OBJECT(dst));

    result->color = color;

    assert(count == 4 || count == 6);

    result->templates = malloc(count * sizeof(GdkPoint *));
    memcpy(result->templates, templates, count * sizeof(GdkPoint *));

    result->count = count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = ligne de rendu à consulter.                           *
*                src  = bloc d'origine du lien. [OUT]                         *
*                dst  = bloc de destination du lien. [OUT]                    *
*                                                                             *
*  Description : Fournit les deux blocs aux extrémités d'un lien.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_edge_get_boundaries(const GGraphEdge *edge, GCodeBlock **src, GCodeBlock **dst)
{
    *src = edge->src;
    *dst = edge->dst;

    g_object_ref(G_OBJECT(*src));
    g_object_ref(G_OBJECT(*dst));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = ligne de rendu à consulter.                           *
*                                                                             *
*  Description : Fournit la couleur de rendu d'un lien graphique.             *
*                                                                             *
*  Retour      : Identifiant de couleur de rendu.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

EdgeColor g_graph_edge_get_color(const GGraphEdge *edge)
{
    EdgeColor result;                       /* Couleur à retourner         */

    result = edge->color;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = ligne de rendu à consulter.                           *
*                x1   = abscisse du point de départ de la ligne. [OUT]        *
*                x2   = abscisse du point d'arrivée de la ligne. [OUT]        *
*                                                                             *
*  Description : Fournit les abscisses des points extrèmes de la ligne.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_edge_get_x_borders(const GGraphEdge *edge, gint *x1, gint *x2)
{
    /**
     * A l'appel de cette fonction, les informations des points n'ont
     * pas encore été fixées ni recopiées.
     */

    *x1 = edge->templates[0]->x;
    *x2 = edge->templates[edge->count - 1]->x;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = ligne de rendu à définir dans les détails.            *
*                                                                             *
*  Description : Détermine les positions finales d'un lien graphique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_edge_resolve(GGraphEdge *edge)
{
    const GdkPoint **templates;             /* Inspirations de coordonnées */
    size_t i;                               /* Boucle de parcours          */

    templates = edge->templates;

    edge->points = malloc(edge->count * sizeof(GdkPoint));

    for (i = 0; i < edge->count; i++)
    {
        edge->points[i].x = templates[i]->x;
        edge->points[i].y = templates[i]->y;
    }

    free(templates);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = ligne de rendu à modifier dans ses positions.         *
*                dx   = déplacement à effectuer sur l'axe des abscisses.      *
*                dy   = déplacement à effectuer sur l'axe des ordonnées.      *
*                                                                             *
*  Description : Opère un décalage du lien dans une direction donnée.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_edge_offset(GGraphEdge *edge, gint dx, gint dy)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < edge->count; i++)
    {
        edge->points[i].x += dx;
        edge->points[i].y += dy;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge  = ligne de rendu avec positions à consulter.           *
*                count = quantité de points représentés. [OUT]                *
*                                                                             *
*  Description : Fournit l'ensemble des points constituant un lien graphique. *
*                                                                             *
*  Retour      : Liste de points utilisés pour le dessin d'un lien.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const GdkPoint *g_graph_edge_get_points(const GGraphEdge *edge, size_t *count)
{
    const GdkPoint *result;                 /* Liste de points à renvoyer  */

    result = edge->points;

    *count = edge->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge = ligne de rendu avec positions à consulter.            *
*                x    = emplacement de la souris sur l'axe des abscisses.     *
*                y    = emplacement de la souris sur l'axe des ordonnées.     *
*                                                                             *
*  Description : Opère un décalage du lien dans une direction donnée.         *
*                                                                             *
*  Retour      : true si un survol est en cours, false sinon.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_graph_edge_detect_at(const GGraphEdge *edge, gint x, gint y)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    gint margin;                            /* Marge de précision          */
    gint pts[2];                            /* Points d'analyse ordonnés   */
    gint inter[2];                          /* Bilan d'intersection        */

    result = false;

    for (i = 1; i < edge->count; i++)
    {
        /* Au niveau des abscisses */

        if (edge->points[i - 1].x <= edge->points[i].x)
        {
            pts[0] = edge->points[i - 1].x;
            pts[1] = edge->points[i].x;
            margin = 1;
        }
        else
        {
            pts[0] = edge->points[i].x;
            pts[1] = edge->points[i - 1].x;
            margin = 1;
        }

        margin *= (LINK_MARGIN / 2);

        inter[0] = MAX(pts[0] - margin, x);
        inter[1] = MIN(pts[1] + margin, x);

        if (inter[0] > inter[1])
            continue;

        /* Au niveau des ordonnées */

        if (edge->points[i - 1].y <= edge->points[i].y)
        {
            pts[0] = edge->points[i - 1].y;
            pts[1] = edge->points[i].y;
            margin = 1;
        }
        else
        {
            pts[0] = edge->points[i].y;
            pts[1] = edge->points[i - 1].y;
            margin = 1;
        }

        margin *= (LINK_MARGIN / 2);

        inter[0] = MAX(pts[0] - margin, y);
        inter[1] = MIN(pts[1] + margin, y);

        if (inter[0] > inter[1])
            continue;

        /* Détection ! */

        result = true;
        break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : edge     = ligne de rendu à manipuler.                       *
*                cairo    = assistant pour le rendu graphique.                *
*                arrow    = indique le besoin en flèche à l'arrivée.          *
*                selected = s'agit-il d'un lien sélectionné ?                 *
*                                                                             *
*  Description : Dessine les liens graphiques enregistrés dans le moteur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_edge_draw(const GGraphEdge *edge, cairo_t *cairo, bool arrow, bool selected)
{
    GGenConfig *config;                     /* Configuration globale       */
    GdkRGBA color;                          /* Couleur de lien définie     */
#ifndef NDEBUG
    bool status;                            /* Validité d'une couleur      */
#endif
    size_t i;                               /* Boucle de parcours          */

    if (selected)
        cairo_set_source_rgb(cairo, 1.0, 1.0, 1.0);

    else
    {
        config = get_main_configuration();

        switch (edge->color)
        {
            default:
            case EGC_DEFAULT:
#ifndef NDEBUG
                status = g_generic_config_get_value(config, MPK_LINK_DEFAULT, &color);
#else
                g_generic_config_get_value(config, MPK_LINK_DEFAULT, &color);
#endif
                break;
            case EGC_GREEN:
#ifndef NDEBUG
                status = g_generic_config_get_value(config, MPK_LINK_BRANCH_TRUE, &color);
#else
                g_generic_config_get_value(config, MPK_LINK_BRANCH_TRUE, &color);
#endif
                break;
            case EGC_RED:
#ifndef NDEBUG
                status = g_generic_config_get_value(config, MPK_LINK_BRANCH_FALSE, &color);
#else
                g_generic_config_get_value(config, MPK_LINK_BRANCH_FALSE, &color);
#endif
                break;
            case EGC_BLUE:
#ifndef NDEBUG
                status = g_generic_config_get_value(config, MPK_LINK_LOOP, &color);
#else
                g_generic_config_get_value(config, MPK_LINK_LOOP, &color);
#endif
                break;
            case EGC_DASHED_GRAY:
                cairo_set_source_rgb(cairo, 0.4, 0.4, 0.4);
                break;
        }

        assert(status);

        cairo_set_source_rgba(cairo, color.red, color.green, color.blue, color.alpha);

    }

    switch (edge->color)
    {
        default:
        case EGC_DEFAULT:
        case EGC_GREEN:
        case EGC_RED:
        case EGC_BLUE:
            cairo_set_dash(cairo, (double []) { 6.0 }, 0, 0.0);
            break;
        case EGC_DASHED_GRAY:
            cairo_set_dash(cairo, (double []) { 6.0 }, 1, 0.0);
            break;
    }

    /**
     * Si on ne veut pas de flèche, on doit se destiner à un aperçu...
     * Dans ce cas, pour plus de lisibilité, on double la taille d'impression.
     * Et pour faire ressortir les boucles, on double encore les liens associés.
     */
    cairo_set_line_width(cairo, arrow ? 1 : (edge->color == EGC_BLUE ? 4 : 2));

    cairo_move_to(cairo, edge->points[0].x + 0.5, edge->points[0].y);

    for (i = 1; i < edge->count; i++)
        cairo_line_to(cairo, edge->points[i].x + 0.5, edge->points[i].y);

    cairo_stroke(cairo);

    if (arrow)
        draw_link_arrow(cairo,
                        edge->points[edge->count - 2].x,
                        edge->points[edge->count - 2].y,
                        edge->points[edge->count - 1].x,
                        edge->points[edge->count - 1].y);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cairo   = gestionnaire de rendu graphique.                   *
*                start_x = abscisse du début du segment final.                *
*                start_y = ordonnée du début du segment final.                *
*                end_x   = abscisse de fin de segment et pointe de flèche.    *
*                end_y   = ordonnée de fin de segment et pointe de flèche.    *
*                                                                             *
*  Description : Dessine une flèche au bout du lien représenté.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void draw_link_arrow(cairo_t *cairo, gint start_x, gint start_y, gint end_x, gint end_y)
{
    double angle;                           /* Angle du triangle à remplir */
    double factor_x;                        /* Direction de la flèche #1   */
    double factor_y;                        /* Direction de la flèche #2   */
    double x1;                              /* Abscisse du point n°1       */
    double y1;                              /* Ordonnée du point n°1       */
    double x2;                              /* Abscisse du point n°2       */
    double y2;                              /* Ordonnée du point n°2       */

    angle = atan2(end_y - start_y, end_x - start_x) + M_PI;

    factor_x = -1;
    factor_y = -1;

    x1 = end_x + factor_x * ARROW_LENGHT * cos(angle - ARROW_DEGREES);
    y1 = end_y + factor_y * ARROW_LENGHT * sin(angle - ARROW_DEGREES);
    x2 = end_x + factor_x * ARROW_LENGHT * cos(angle + ARROW_DEGREES);
    y2 = end_y + factor_y * ARROW_LENGHT * sin(angle + ARROW_DEGREES);

    cairo_move_to(cairo, end_x, end_y);

    cairo_line_to(cairo, x1, y1);
    cairo_line_to(cairo, x2, y2);

    cairo_move_to(cairo, end_x, end_y);

    cairo_fill(cairo);

}
