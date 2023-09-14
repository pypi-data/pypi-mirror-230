
/* Chrysalide - Outil d'analyse de fichiers binaires
 * diagram.c - composant d'affichage avec de digrammes
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


#include "diagram.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>



/* Composant de dessin de diagramme (instance) */
struct _GtkDiagram
{
    GtkDrawingArea parent;                  /* A laisser en premier        */

    DiagramRenderingType rendering;         /* Type de représentation      */
    GdkRGBA fore_color;                     /* Couleur principale          */

    diagram_stat_t *stats;                  /* Statistiques fournies       */
    size_t count;                           /* Quantité de ces éléments    */

};

/* Composant de dessin de diagramme (classe) */
struct _GtkDiagramClass
{
    GtkDrawingAreaClass parent;             /* A laisser en premier        */

};


/* Initialise la classe des dessins de diagramme. */
static void gtk_diagram_class_init(GtkDiagramClass *);

/* Initialise une instance de dessin de diagramme. */
static void gtk_diagram_init(GtkDiagram *);

/* Supprime toutes les références externes. */
static void gtk_diagram_dispose(GtkDiagram *);

/* Procède à la libération totale de la mémoire. */
static void gtk_diagram_finalize(GtkDiagram *);

/* Applique une police choisie à un contexte de rendu. */
static void gtk_diagram_set_font(GtkWidget *, cairo_t *);

/* Assure le dessin du diagramme courant. */
static gboolean gtk_diagram_draw(GtkWidget *, cairo_t *);

/* Dessine un diagramme en camembert. */
static void gtk_diagram_draw_pie(GtkWidget *, cairo_t *, const GdkRGBA *, const diagram_stat_t *, size_t);

/* Dessine un diagramme en barres. */
static void gtk_diagram_draw_histo(GtkWidget *, cairo_t *, const GdkRGBA *, const diagram_stat_t *, size_t);

/* Indique le mode privilégié pour la détermination de taille. */
static GtkSizeRequestMode gtk_diagram_get_request_mode(GtkWidget *);

/* Indique le mode privilégié pour la détermination de taille. */
static void gtk_diagram_get_preferred_width_for_height(GtkWidget *, gint, gint *, gint *);



/* Détermine le type de l'afficheur de diagramme. */
G_DEFINE_TYPE(GtkDiagram, gtk_diagram, GTK_TYPE_DRAWING_AREA)


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Initialise la classe des dessins de diagramme.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_class_init(GtkDiagramClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GtkWidgetClass *widget;                 /* Composant GTK générique     */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_diagram_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_diagram_finalize;

    widget = GTK_WIDGET_CLASS(klass);

    widget->draw = gtk_diagram_draw;
    widget->get_request_mode = gtk_diagram_get_request_mode;
    widget->get_preferred_width_for_height = gtk_diagram_get_preferred_width_for_height;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : diag = instance GTK à initialiser.                           *
*                                                                             *
*  Description : Initialise une instance de dessin de diagramme.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_init(GtkDiagram *diagram)
{
    diagram->stats = NULL;
    diagram->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : diag = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_dispose(GtkDiagram *diagram)
{
    G_OBJECT_CLASS(gtk_diagram_parent_class)->dispose(G_OBJECT(diagram));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : diag = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_finalize(GtkDiagram *diagram)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < diagram->count; i++)
        if (diagram->stats[i].desc != NULL)
            free(diagram->stats[i].desc);

    if (diagram->stats != NULL)
        free(diagram->stats);

    G_OBJECT_CLASS(gtk_diagram_parent_class)->finalize(G_OBJECT(diagram));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rendering = type de rendu des données.                       *
*                color     = couleur complémentaire pour le dessin.           *
*                                                                             *
*  Description : Crée une nouvelle instance de dessinateur de diagramme.      *
*                                                                             *
*  Retour      : Composant GTK mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_diagram_new(DiagramRenderingType rendering, const GdkRGBA *color)
{
    GtkDiagram *result;                     /* Composant à retourner       */

    result = g_object_new(GTK_TYPE_DIAGRAM, NULL);

    result->rendering = rendering;
    result->fore_color = *color;

    return GTK_WIDGET(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique à redessiner.                   *
*                cr     = contexte graphique à utiliser.                      *
*                                                                             *
*  Description : Applique une police choisie à un contexte de rendu.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_set_font(GtkWidget *widget, cairo_t *cr)
{
    GtkStyleContext *context;               /* Contexte du style courant   */
    const PangoFontDescription *fdesc;      /* Description de police       */
    double dpi;                             /* Résolution de l'écran       */

    context = gtk_widget_get_style_context(widget);

    gtk_style_context_save(context);

    gtk_style_context_add_class(context, GTK_STYLE_CLASS_LABEL);

    gtk_style_context_get(context, gtk_style_context_get_state(context),
                          GTK_STYLE_PROPERTY_FONT, &fdesc, NULL);

    cairo_select_font_face(cr, pango_font_description_get_family(fdesc),
                           CAIRO_FONT_SLANT_NORMAL,
                           CAIRO_FONT_WEIGHT_BOLD);

    dpi = gdk_screen_get_resolution(gtk_widget_get_screen(widget));

    cairo_set_font_size(cr, (pango_font_description_get_size(fdesc) * dpi) / (PANGO_SCALE * 72.0));

    gtk_style_context_restore(context);


}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique à redessiner.                   *
*                cr     = contexte graphique à utiliser.                      *
*                                                                             *
*  Description : Assure le dessin du diagramme courant.                       *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_diagram_draw(GtkWidget *widget, cairo_t *cr)
{
    GtkDiagram *diagram;                    /* Autre version du composant  */

    diagram = GTK_DIAGRAM(widget);

    gtk_diagram_set_font(widget, cr);

    if (diagram->count > 0)
        switch (diagram->rendering)
        {
            case DRT_PIE:
                gtk_diagram_draw_pie(widget, cr, &diagram->fore_color, diagram->stats, diagram->count);
                break;

            case DRT_HISTO:
                gtk_diagram_draw_histo(widget, cr, &diagram->fore_color, diagram->stats, diagram->count);
                break;

        }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique à redessiner.                   *
*                cr     = contexte graphique à utiliser.                      *
*                color  = couleur d'impression principale.                    *
*                stats  = élements statistiques à présenter.                  *
*                count  = quantité de ces éléments.                           *
*                                                                             *
*  Description : Dessine un diagramme en camembert.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_draw_pie(GtkWidget *widget, cairo_t *cr, const GdkRGBA *color, const diagram_stat_t *stats, size_t count)
{
    guint height;                           /* Hauteur de l'espace dispo   */
    double cx;                              /* Centre du camember #1       */
    double cy;                              /* Centre du camember #2       */
    double radius;                          /* Taille dudit camember       */
    double sum;                             /* Somme de toutes les valeurs */
    size_t i;                               /* Boucle de parcours          */
    double init_angle;                      /* Angle de départ             */
    double last_angle;                      /* Dernier angle utilisé       */
    const diagram_stat_t *stat;             /* Statistique courante        */
    double angle_1;                         /* Angle de départ             */
    double angle_2;                         /* Angle d'arrivée             */
    GdkRGBA tmp;                            /* Stockage temporaire         */
    double tx;                              /* Abscisse du texte de légende*/
    cairo_text_extents_t extents;           /* Taille de la police         */
    double ty;                              /* Ordonnée du texte de légende*/

    /* Préparatifs */

    height = gtk_widget_get_allocated_height(widget);

    cx = height / 2;
    cy = height / 2;

    radius = (height - 2 * DIAGRAM_MARGIN) / 2;

    sum = 0;

    for (i = 0; i < count; i++)
        sum += stats[i].value;

    init_angle = 0;

    for (i = 0; i < count; i++)
    {
        init_angle = G_PI - (stats[i].value * 2 * G_PI) / 200;

        if (stats[i].value != 0)
            break;

    }

    assert(i < count);

    /* Contenu */

    cairo_set_line_width(cr, 2.0);

    last_angle = init_angle;

    for (; i < count; i++)
    {
        stat = &stats[i];

        if (stat->value > 0)
        {
            angle_1 = last_angle;

            if ((i + 1) == count)
                angle_2 = (init_angle != 0 ? init_angle : G_PI);
            else
                angle_2 = angle_1 + (stat->value * 2 * G_PI) / sum;

            cairo_move_to(cr, cx, cy);
            cairo_arc(cr, cx, cy, radius, angle_1, angle_2);
            cairo_line_to(cr, cx, cy);

            tmp = stat->color;
            tmp.alpha /= 2;

            gdk_cairo_set_source_rgba(cr, &tmp);
            cairo_fill_preserve(cr);

            gdk_cairo_set_source_rgba(cr, color);
            cairo_stroke(cr);

            last_angle = angle_2;

        }

    }

    /* Bordures */

    cairo_set_line_width(cr, 10.0);

    last_angle = init_angle;

    for (i = 0; i < count; i++)
    {
        stat = &stats[i];

        if (stat->value > 0)
        {
            angle_1 = last_angle;

            if ((i + 1) == count)
                angle_2 = (init_angle != 0 ? init_angle : G_PI);
            else
                angle_2 = angle_1 + (stat->value * 2 * G_PI) / sum;

            cairo_arc(cr, cx, cy, radius, angle_1, angle_2);

            gdk_cairo_set_source_rgba(cr, &stat->color);
            cairo_stroke(cr);

            last_angle = angle_2;

        }

    }

    /* Légende */

    cairo_set_line_width(cr, 2.0);

    tx = height + DIAGRAM_MARGIN;

    cairo_text_extents(cr, "A", &extents);

    ty = (height - extents.height - 3 * extents.height * (count - 1)) / 2;

    for (i = 0; i < count; i++)
    {
        stat = &stats[i];

        cairo_rectangle(cr, tx, ty, 2 * extents.height, extents.height);

        tmp = stat->color;
        tmp.alpha /= 2;

        gdk_cairo_set_source_rgba(cr, &tmp);
        cairo_fill_preserve(cr);

        gdk_cairo_set_source_rgba(cr, &stat->color);
        cairo_stroke(cr);

        cairo_move_to(cr, tx + 3 * extents.height, ty - extents.y_bearing);
        cairo_show_text(cr, stat->desc);

        ty += 3 * extents.height;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique à redessiner.                   *
*                cr     = contexte graphique à utiliser.                      *
*                color  = couleur d'impression principale.                    *
*                stats  = élements statistiques à présenter.                  *
*                count  = quantité de ces éléments.                           *
*                                                                             *
*  Description : Dessine un diagramme en barres.                              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_draw_histo(GtkWidget *widget, cairo_t *cr, const GdkRGBA *color, const diagram_stat_t *stats, size_t count)
{
    guint height;                           /* Hauteur de l'espace dispo   */
    cairo_text_extents_t extents;           /* Taille de la police         */
    guint graph_height;                     /* Hauteur du graphique        */
    guint zero_x;                           /* Abscisse de l'origine       */
    guint zero_y;                           /* Ordonnée de l'origine       */
    double sum;                             /* Somme de toutes les valeurs */
    guint graph_width;                      /* Largeur du graphique        */
    size_t i;                               /* Boucle de parcours          */
    const diagram_stat_t *stat;             /* Statistique courante        */
    double ty;                              /* Ordonnée du texte de légende*/
    double tx;                              /* Abscisse du texte de légende*/

    static const char *scale[4] = { "0%  ", "25%  ", "50%  ", "100%  " };

    /* Préparatifs */

    height = gtk_widget_get_allocated_height(widget);

    cairo_text_extents(cr, scale[3], &extents);

    graph_height = height - DIAGRAM_MARGIN * 2 - extents.height;

    zero_x = extents.x_advance;
    zero_y = DIAGRAM_MARGIN + graph_height;

    sum = 0;

    graph_width = 0;

    for (i = 0; i < count; i++)
    {
        stat = &stats[i];

        sum += stat->value;

        cairo_text_extents(cr, stat->desc, &extents);

        graph_width += extents.x_advance + DIAGRAM_MARGIN;

    }

    /* Echelles et légende */

    gdk_cairo_set_source_rgba(cr, color);

    cairo_move_to(cr, zero_x, zero_y);
    cairo_line_to(cr, zero_x, zero_y - graph_height);

    cairo_stroke(cr);

    cairo_move_to(cr, zero_x, zero_y);
    cairo_line_to(cr, zero_x + graph_width, zero_y);

    cairo_stroke(cr);

    for (i = 0; i < 4; i++)
    {
        ty = zero_y - (i * graph_height) / 3;

        cairo_move_to(cr, zero_x - 2, ty);
        cairo_line_to(cr, zero_x + 2, ty);

        cairo_stroke(cr);

        cairo_text_extents(cr, scale[i], &extents);

        cairo_move_to(cr, zero_x - extents.x_advance, ty - extents.y_bearing / 2);
        cairo_show_text(cr, scale[i]);

    }

    tx = zero_x;

    ty = zero_y + DIAGRAM_MARGIN / 2;

    for (i = 0; i < count; i++)
    {
        stat = &stats[i];

        cairo_text_extents(cr, stat->desc, &extents);

        gdk_cairo_set_source_rgba(cr, color);

        cairo_move_to(cr, tx + DIAGRAM_MARGIN / 2 + extents.x_advance / 2, zero_y - 2);
        cairo_line_to(cr, tx + DIAGRAM_MARGIN / 2 + extents.x_advance / 2, zero_y + 2);

        cairo_stroke(cr);

        gdk_cairo_set_source_rgba(cr, &stat->color);

        cairo_move_to(cr, tx + DIAGRAM_MARGIN / 2, ty - extents.y_bearing);
        cairo_show_text(cr, stat->desc);

        tx += extents.x_advance + DIAGRAM_MARGIN;

    }

    /* Représentation des valeurs */

    tx = zero_x;

    ty = zero_y + DIAGRAM_MARGIN / 2;

    cairo_set_line_width(cr, 8);
    cairo_set_line_cap(cr, CAIRO_LINE_CAP_ROUND);

    for (i = 0; i < count; i++)
    {
        stat = &stats[i];

        cairo_text_extents(cr, stat->desc, &extents);

        if (stat->value > 0)
        {
            gdk_cairo_set_source_rgba(cr, &stat->color);

            cairo_move_to(cr, tx + DIAGRAM_MARGIN / 2 + extents.x_advance / 2, zero_y);
            cairo_line_to(cr, tx + DIAGRAM_MARGIN / 2 + extents.x_advance / 2,
                          zero_y - (stat->value * graph_height) / sum);

            cairo_stroke(cr);

        }

        tx += extents.x_advance + DIAGRAM_MARGIN;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique à consulter.                    *
*                                                                             *
*  Description : Indique le mode privilégié pour la détermination de taille.  *
*                                                                             *
*  Retour      : Toujours la largeur à partir de la hauteur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkSizeRequestMode gtk_diagram_get_request_mode(GtkWidget *widget)
{
    return GTK_SIZE_REQUEST_WIDTH_FOR_HEIGHT;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique à consulter.                   *
*                height  = hauteur à considérer.                              *
*                minimum = largeur minimale correspondante.                   *
*                natural = largeur idéale correspondante.                     *
*                                                                             *
*  Description : Indique le mode privilégié pour la détermination de taille.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_diagram_get_preferred_width_for_height(GtkWidget *widget, gint height, gint *minimum, gint *natural)
{
    GdkWindow *window;                      /* Fenêtre du composant        */
    GtkDiagram *diagram;                    /* Autre version du composant  */
    gint text_width;                        /* Plus grande longueur        */
    cairo_surface_t *surface;               /* Espace graphique de support */
    cairo_t *cr;                            /* Contexte de rendu           */
    size_t i;                               /* Boucle de parcours          */
    cairo_text_extents_t extents;           /* Taille de la police         */

    window = gtk_widget_get_window(widget);

    if (window == NULL)
    {
        *minimum = 1;
        goto conclusion;
    }

    diagram = GTK_DIAGRAM(widget);

    text_width = 0;

    surface = gdk_window_create_similar_surface(gtk_widget_get_window(widget), CAIRO_CONTENT_COLOR, 1, 1);

    cr = cairo_create(surface);

    gtk_diagram_set_font(widget, cr);

    switch (diagram->rendering)
    {
        case DRT_PIE:

            for (i = 0; i < diagram->count; i++)
            {
                if (diagram->stats[i].desc == NULL)
                    continue;

                cairo_text_extents(cr, diagram->stats[i].desc, &extents);

                if (extents.width > text_width)
                    text_width = extents.width;

            }

            if (text_width > 0)
                *minimum = height + 2 * DIAGRAM_MARGIN + 3 * extents.height + text_width;
            else
                *minimum = 0;

            break;

        case DRT_HISTO:

            cairo_text_extents(cr, "100%  ", &extents);

            *minimum = extents.x_advance;

            for (i = 0; i < diagram->count; i++)
            {
                cairo_text_extents(cr, diagram->stats[i].desc, &extents);

                *minimum += extents.x_advance + DIAGRAM_MARGIN;

            }

            *minimum += DIAGRAM_MARGIN;

    }

    cairo_destroy(cr);
    cairo_surface_destroy(surface);

 conclusion:

    /* Répercution */

    *natural = *minimum;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : diagram = diagramme à vider.                                 *
*                                                                             *
*  Description : Supprime tous les éléments représentés dans le diagramme.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_diagram_clear_stats(GtkDiagram *diagram)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < diagram->count; i++)
    {
        if (diagram->stats[i].desc != NULL)
            free(diagram->stats[i].desc);
    }

    if (diagram->stats != NULL)
        free(diagram->stats);

    diagram->stats = NULL;
    diagram->count = 0;

    gtk_widget_queue_resize(GTK_WIDGET(diagram));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : diagram = diagramme à compléter.                             *
*                stats   = nouvelles statistiques à intégrer.                 *
*                count   = quantité de ces statistiques.                      *
*                                                                             *
*  Description : Ajoute des éléments à représenter dans le diagramme.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_diagram_add_stats(GtkDiagram *diagram, const diagram_stat_t *stats, size_t count)
{
    size_t i;                               /* Boucle de parcours          */
    diagram_stat_t *dest;                   /* Destination d'une copie     */

    diagram->stats = (diagram_stat_t *)realloc(diagram->stats, (diagram->count + count) * sizeof(diagram_stat_t));

    for (i = 0; i < count; i++)
    {
        dest = &diagram->stats[diagram->count + i];

        dest->value = stats[i].value;

        dest->color = stats[i].color;

        if (stats[i].desc == NULL)
            dest->desc = NULL;

        else
            dest->desc = strdup(stats[i].desc);

    }

    diagram->count += count;

    gtk_widget_queue_resize(GTK_WIDGET(diagram));

}
