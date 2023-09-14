
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bufferview.c - affichage d'une vue particulière d'un tampon de lignes
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "bufferview.h"


#include <assert.h>



/* Vue d'un tampon pour code désassemblé (instance) */
struct _GBufferView
{
    GObject parent;                         /* A laisser en premier        */

    GBufferCache *cache;                    /* Tampon du contenu visualisé */

    segcnt_list *highlighted;               /* Segments mis en évidence    */

    bool unrestricted;                      /* Validité des informations   */
    GLineCursor *start;                     /* Première ligne intégrée     */
    GLineCursor *end;                       /* Dernière ligne intégrée     */

    size_t first;                           /* Indice de la première ligne */
    size_t last;                            /* Indice de la dernière ligne */

    GWidthTracker *tracker;                 /* Suivi des largeurs          */

};

/* Vue d'un tampon pour code désassemblé (classe) */
struct _GBufferViewClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* need_redraw) (GBufferView *);

};


/* Procède à l'initialisation d'une classe de vue de tampon. */
static void g_buffer_view_class_init(GBufferViewClass *);

/* Procède à l'initialisation d'une vue d'un tampon pour code. */
static void g_buffer_view_init(GBufferView *);

/* Supprime toutes les références externes. */
static void g_buffer_view_dispose(GBufferView *);

/* Procède à la libération totale de la mémoire. */
static void g_buffer_view_finalize(GBufferView *);

/* Accompagne une variation de la quantité de lignes du tampon. */
static void on_buffer_cache_size_changed(const GBufferCache *, bool, size_t, size_t, GBufferView *);

/* Réagit à la modification d'une ligne du tampon. */
static void on_buffer_cache_line_updated(const GBufferCache *, size_t, GBufferView *);

/* Calcule la position idéale de curseur pour un point donné. */
static bool _g_buffer_view_compute_caret_full(GBufferView *, gint, GBufferLine *, size_t, const GDisplayOptions *, cairo_rectangle_int_t *, GLineCursor **);

/* Fournit la ligne présente à une ordonnée donnée. */
static GBufferLine *g_buffer_view_find_line_at(GBufferView *, gint, size_t *);

/* Déplace le curseur au sein d'une vue de tampon. */
static bool _g_buffer_view_move_caret(GBufferView *, const GBufferLine *, size_t, cairo_rectangle_int_t *, bool, GdkScrollDirection, const GDisplayOptions *);








/* Détermine le type de la vue d'un tampon pour code désassemblé. */
G_DEFINE_TYPE(GBufferView, g_buffer_view, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GTK à initialiser.               *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de vue de tampon.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_view_class_init(GBufferViewClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_buffer_view_dispose;
    object->finalize = (GObjectFinalizeFunc)g_buffer_view_finalize;

    /* Sigaux */

    g_signal_new("need-redraw",
                 G_TYPE_BUFFER_VIEW,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBufferViewClass, need_redraw),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = composant GLib à initialiser.                         *
*                                                                             *
*  Description : Procède à l'initialisation d'une vue d'un tampon pour code.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_view_init(GBufferView *view)
{
    view->cache = NULL;

    view->highlighted = NULL;

    /**
     * Inversion du statut pour forcer l'actualisation lors de la création.
     */
    view->unrestricted = false;

    view->start = NULL;
    view->end = NULL;

    view->first = 0;
    view->last = 0;

    view->tracker = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_view_dispose(GBufferView *view)
{
    g_clear_object(&view->cache);

    g_clear_object(&view->start);
    g_clear_object(&view->end);

    g_clear_object(&view->tracker);

    G_OBJECT_CLASS(g_buffer_view_parent_class)->dispose(G_OBJECT(view));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_view_finalize(GBufferView *view)
{
    if (view->highlighted != NULL)
        unref_segment_content_list(view->highlighted);

    G_OBJECT_CLASS(g_buffer_view_parent_class)->finalize(G_OBJECT(view));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer      = tampon à représenter à l'écran.                *
*                highlighted = gestionnaire de surbrillance pour segments.    *
*                                                                             *
*  Description : Crée une nouvelle vue d'un tampon pour code désassemblé.     *
*                                                                             *
*  Retour      : Composant GTK créé.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferView *g_buffer_view_new(GBufferCache *cache, segcnt_list *highlighted)
{
    GBufferView *result;                    /* Composant à retourner       */

    result = g_object_new(G_TYPE_BUFFER_VIEW, NULL);

    result->cache = cache;
    g_object_ref_sink(G_OBJECT(cache));

    g_buffer_view_restrict(result, NULL, NULL);

    g_signal_connect(cache, "size-changed", G_CALLBACK(on_buffer_cache_size_changed), result);
    g_signal_connect(cache, "line-updated", G_CALLBACK(on_buffer_cache_line_updated), result);

    if (highlighted != NULL)
    {
        ref_segment_content_list(highlighted);
        result->highlighted = highlighted;
    }
    else
        result->highlighted = init_segment_content_list();

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes cohérentes à manipuler.             *
*                index = indice de la première ligne actualisée.              *
*                                                                             *
*  Description : Réagit à la modification d'une ligne du tampon.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_buffer_cache_line_updated(const GBufferCache *cache, size_t index, GBufferView *view)
{
    if (view->first <= index && index <= view->last)
        g_signal_emit_by_name(view, "need-redraw");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes cohérentes à manipuler.             *
*                added = indication sur la variation de la taille du tampon.  *
*                index = indice de la première ligne à traiter.               *
*                count = nombre de lignes à traiter.                          *
*                view  = vue active du tampon de lignes concerné.             *
*                                                                             *
*  Description : Accompagne une variation de la quantité de lignes du tampon. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_buffer_cache_size_changed(const GBufferCache *cache, bool added, size_t index, size_t count, GBufferView *view)
{
    //size_t i;                               /* Boucle de parcours          */
    //GBufferLine *line;                      /* Ligne à manipuler           */
    //const vmpa2t *addr;                     /* Localisation de ligne       */

    /**
     * Il n'y a pas besoin de verrou ici car la fonction est appelée directement par le tampon.
     * D'autre part, on considère qu'il y a toujours une ligne aux adresses de borne, si la vue est bornée.
     */

    if (added)
    {
        if (view->unrestricted)
            view->last += count;

        else
        {
#if 0

            /* Avant la zone représentée ? */
            if (index < view->first)
            {
                view->first += count;
                view->last += count;
            }

            /* Juste avant la zone représentée ? */
            else if (view->first == index)
                for (i = 0; i < count; i++)
                {
                    g_buffer_cache_get_line_addr(const GBufferCache *, size_t, gint, vmpa2t *);

                    line = g_code_buffer_find_line_by_index(buffer, index + i);
                    addr = get_mrange_addr(g_buffer_line_get_range(line));

                    if (cmp_vmpa(&view->start, addr) == 0)
                    {
                        view->first++;
                        view->last++;
                    }
                    else
                        break;

                }

            /* Dans la zone représentée ? */
            else if (view->first < index && index <= view->last)
                view->last += count;

            /* Juste après la vue représentée ? */
            else if ((view->last + 1) == index)
                for (i = 0; i < count; i++)
                {
                    g_buffer_cache_get_line_addr(const GBufferCache *, size_t, gint, vmpa2t *);

                    line = g_code_buffer_find_line_by_index(buffer, index + i);
                    addr = get_mrange_addr(g_buffer_line_get_range(line));

                    if (cmp_vmpa(&view->end, addr) == 0)
                        view->last++;
                    else
                        break;

                }

            //g_width_tracker_update_added(view->int_tracker, index, count);
#endif

        }

    }

    else
    {
        if (view->unrestricted)
            view->last -= count;

        else
        {
            /* Avant la zone représentée ? */
            if (index <= view->first)
            {
                view->first -= count;
                view->last -= count;
            }

            /* Dans la zone représentée ? */
            else if (view->first < index && index <= view->last)
                view->last -= count;

        }

        //g_width_tracker_update_deleted(view->int_tracker, index, index + count - 1);

    }

    //g_signal_emit_by_name(view, "need-redraw");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = visualisateur à consulter.                            *
*                                                                             *
*  Description : Fournit le tampon de code lié à un visualisateur donné.      *
*                                                                             *
*  Retour      : Tampon de code associé au gestionnaire d'affichage.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferCache *g_buffer_view_get_cache(const GBufferView *view)
{
    GBufferCache *result;                   /* Instance à retourner        */

    result = view->cache;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view  = visualisateur à mettre à jour.                       *
*                first = première ligne à imprimer.                           *
*                last  = première ligne hors cadre.                           *
*                                                                             *
*  Description : Restreint le champ d'application de l'affichage.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_view_restrict(GBufferView *view, GLineCursor *start, GLineCursor *end)
{
    bool state;                             /* Nouvel état à proclamer     */
    GWidthTracker *template;                /* Suivi déjà en place         */

    state = (start == NULL || end == NULL);

    if (view->unrestricted != state)
    {
        view->unrestricted = state;

        template = g_buffer_cache_get_width_tracker(view->cache);

        /* Vérification pour le cas particulier du démarrage */
        if (view->tracker != NULL)
            g_object_unref(G_OBJECT(view->tracker));

        g_buffer_cache_rlock(view->cache);

        if (view->unrestricted)
        {
            view->first = 0;
            view->last = g_buffer_cache_count_lines(view->cache) - 1;

            view->tracker = template;

        }

        else
        {
            g_object_ref_sink(G_OBJECT(start));
            g_object_ref_sink(G_OBJECT(end));

            view->start = start;
            view->end = end;

            view->first = g_buffer_cache_find_index_by_cursor(view->cache, start, true);
            view->last = g_buffer_cache_find_index_by_cursor(view->cache, end, false);

            view->tracker = g_width_tracker_new_restricted(template, view->first, view->last);

            g_object_unref(G_OBJECT(template));

        }

        g_buffer_cache_runlock(view->cache);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view  = visualisateur à consulter.                           *
*                first = première ligne à imprimer ou NULL. [OUT]             *
*                last  = première ligne hors cadre ou NULL. [OUT]             *
*                                                                             *
*  Description : Indique le champ d'application de l'affichage.               *
*                                                                             *
*  Retour      : true si des restrictions particulières sont en place.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_view_get_restrictions(const GBufferView *view, GLineCursor **start, GLineCursor **end)
{
    if (!view->unrestricted)
    {
        if (start != NULL)
        {
            *start = view->start;
            g_object_ref(G_OBJECT(*start));
        }

        if (end != NULL)
        {
            *end = view->end;
            g_object_ref(G_OBJECT(*end));
        }

    }
    else
    {
        if (start != NULL) *start = NULL;
        if (end != NULL) *end = NULL;
    }

    return !view->unrestricted;

}









/******************************************************************************
*                                                                             *
*  Paramètres  : view    = visualisation à consulter.                         *
*                options = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Fournit la largeur requise par une visualisation.            *
*                                                                             *
*  Retour      : Dimension calculée.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_buffer_view_get_width(GBufferView *view, const GDisplayOptions *options)
{
    gint result;                            /* Taille à retourner          */

    result = g_buffer_cache_get_text_position(view->cache);

    result += g_width_tracker_get_width(view->tracker, options);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view    = visualisation à consulter.                         *
*                options = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Fournit la largeur requise pour dépasser les marges gauches. *
*                                                                             *
*  Retour      : Dimension calculée.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_buffer_view_get_margin(GBufferView *view, const GDisplayOptions *options)
{
    gint result;                            /* Taille à retourner          */

    result = g_buffer_cache_get_text_position(view->cache);

    result += g_width_tracker_get_margin(view->tracker, options);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = visualisation à consulter.                            *
*                                                                             *
*  Description : Fournit la hauteur requise par une visualisation.            *
*                                                                             *
*  Retour      : Dimension calculée.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_buffer_view_get_height(const GBufferView *view)
{
    gint result;                            /* Taille à retourner          */

    result = g_buffer_cache_get_line_height(view->cache);

    result *= (view->last - view->first + 1);

    return result;

}













/******************************************************************************
*                                                                             *
*  Paramètres  : view    = vue de tampon à mettre à jour.                     *
*                x       = abscisse proposée pour le nouvel emplacement.      *
*                y       = ordonnée proposée pour le nouvel emplacement.      *
*                options = règles d'affichage des colonnes modulables.        *
*                caret   = position du curseur à construire. [OUT]            *
*                cursor  = emplacement correspondant à cette position. [OUT]  *
*                                                                             *
*  Description : Calcule la position idéale de curseur pour un point donné.   *
*                                                                             *
*  Retour      : true si les deux derniers arguments ont pu être constitués.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_view_compute_caret_full(GBufferView *view, gint x, gint y, const GDisplayOptions *options, cairo_rectangle_int_t *caret, GLineCursor **cursor)
{
    bool result;                            /* Bilan à retourner           */
    gint lheight;                           /* Hauteur d'une ligne         */
    size_t index;                           /* Indice de ligne de tampon   */
    GBufferLine *line;                      /* Ligne à la position courante*/

    result = false;

    g_buffer_cache_rlock(view->cache);

    /* Détermination de la ligne courante */

    lheight = g_buffer_cache_get_line_height(view->cache);
    index = y / lheight;

    index += view->first;

    if (index > view->last)
        goto gbvccf_done;

    line = g_buffer_cache_find_line_by_index(view->cache, index);

    assert(line != NULL);

    /* Calcul d'une position */

    result = _g_buffer_view_compute_caret_full(view, x, line, index, options, caret, cursor);

    g_object_unref(G_OBJECT(line));

 gbvccf_done:

    g_buffer_cache_runlock(view->cache);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view    = vue de tampon à mettre à jour.                     *
*                x       = abscisse proposée pour le nouvel emplacement.      *
*                line    = ligne correspondant à la position.                 *
*                index   = indice de cette même ligne dans le tampon.         *
*                options = règles d'affichage des colonnes modulables.        *
*                caret   = position du curseur à construire. [OUT]            *
*                cursor  = emplacement correspondant à cette position. [OUT]  *
*                                                                             *
*  Description : Calcule la position idéale de curseur pour un point donné.   *
*                                                                             *
*  Retour      : true si les deux derniers arguments ont pu être constitués.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_buffer_view_compute_caret_full(GBufferView *view, gint x, GBufferLine *line, size_t index, const GDisplayOptions *options, cairo_rectangle_int_t *caret, GLineCursor **cursor)
{
    bool result;                            /* Bilan à retourner           */
    gint text_pos;                          /* Abscisse de départ du texte */
    gint base;                              /* Position absolue de segment */
    bool status;                            /* Bilan de la localisation    */
    gint lheight;                           /* Hauteur d'une ligne         */

    result = false;

    /* Zone d'intervention bornée ! */

    text_pos = g_buffer_cache_get_text_position(view->cache);

    if (x < text_pos)
        goto gbvccf_done;

    /* Calcul d'une position */

    x -= text_pos;

    status = g_buffer_line_get_coord_at(line, index, view->tracker, options, &base, &x,
                                        GDK_SCROLL_LEFT, true, (col_coord_t []) { { 0 } });

    if (!status)
        goto gbvccf_done;

    /* Transmission des informations */

    lheight = g_buffer_cache_get_line_height(view->cache);

    caret->x = text_pos + base + x;

    caret->y = (index - view->first) * lheight;

    caret->width = 2;
    caret->height = lheight;

    g_buffer_cache_get_line_cursor(view->cache, index, caret->x, cursor);

    result = true;

 gbvccf_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view    = vue de tampon à manipuler.                         *
*                line    = ligne à venir consulter.                           *
*                index   = indice de cette même ligne dans le tampon.         *
*                caret   = position du curseur à faire évoluer.               *
*                ctrl    = indique la demande d'un parcours rapide.           *
*                dir     = direction du parcours.                             *
*                options = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Déplace le curseur au sein d'une vue de tampon.              *
*                                                                             *
*  Retour      : true si un déplacement a été effectué, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_buffer_view_move_caret(GBufferView *view, const GBufferLine *line, size_t index, cairo_rectangle_int_t *caret, bool ctrl, GdkScrollDirection dir, const GDisplayOptions *options)
{
    bool result;                            /* Bilan à retourner           */
    gint text_pos;                          /* Abscisse de départ du texte */
    gint offset;                            /* Point de travail modifiable */
    gint base;                              /* Position absolue de segment */
    col_coord_t coord;                      /* Coordonnées en interne      */
    line_segment *segment;                  /* Bribe de texte trouvée      */


    result = false;

    /* Zone d'intervention bornée ! */

    text_pos = g_buffer_cache_get_text_position(view->cache);

    if (caret->x < text_pos)
        goto gbvmc_done;

    offset = caret->x - text_pos;

    /* Déplacement au sein du segment courant ? */

    result = g_buffer_line_get_coord_at(line, index, view->tracker, options, &base, &offset, dir, false, &coord);

    if (result)
    {
        segment = g_buffer_line_get_segment_from_coord(line, &coord);

        result = move_caret_on_line_segment(segment, &offset, ctrl, dir);

        release_line_segment(segment);

    }

    /* Tentative de déplacement chez le segment voisin ? */

    if (!result)
    {
        base = 0;

        result = g_buffer_line_find_near_coord(line, index, &coord, view->tracker, options, dir, &offset);

    }

    /* Mise à jour éventuelle */

    if (result)
        caret->x = text_pos + base + offset;

 gbvmc_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = visualisation à consulter.                            *
*                y    = ordonnée comprise dans la ligne recherchée.           *
*                idx  = indice de la ligne trouvée ou NULL. [OUT]             *
*                                                                             *
*  Description : Fournit la ligne présente à une ordonnée donnée.             *
*                                                                             *
*  Retour      : Ligne retrouvée ou NULL si aucune.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBufferLine *g_buffer_view_find_line_at(GBufferView *view, gint y, size_t *idx)
{
    GBufferLine *result;                    /* Ligne trouvée à retourner   */
    gint lheight;                           /* Hauteur d'une ligne         */
    size_t index;                           /* Indice attendu              */

    /**
     * Le verrou sur le tampon est déjà posé.
     */

    lheight = g_buffer_cache_get_line_height(view->cache);
    index = y / lheight;

    index += view->first;

    if (index <= view->last)
        result = g_buffer_cache_find_line_by_index(view->cache, index);
    else
        result = NULL;

    if (result != NULL && idx != NULL)
        *idx = index;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view    = vue de tampon à mettre à jour.                     *
*                ctrl    = indique la demande d'un parcours rapide.           *
*                dir     = direction du parcours.                             *
*                options = règles d'affichage des colonnes modulables.        *
*                caret   = position du curseur à faire évoluer. [OUT]         *
*                cursor  = emplacement correspondant à cette position. [OUT]  *
*                                                                             *
*  Description : Déplace le curseur au sein d'une vue de tampon.              *
*                                                                             *
*  Retour      : true si les deux derniers arguments ont pu être constitués.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_view_move_caret(GBufferView *view, bool ctrl, GdkScrollDirection dir, const GDisplayOptions *options, cairo_rectangle_int_t *caret, GLineCursor **cursor)
{
    bool result;                            /* Bilan à retourner           */
    size_t index;                           /* Indice de ligne de tampon   */
    GBufferLine *line;                      /* Ligne sous le pointeur      */
    size_t first;                           /* Première ligne intégrée     */
    size_t last;                            /* Dernière ligne intégrée     */
    GBufferLine *other;                     /* Ligne voisine à visiter     */
    bool moved;                             /* Mémorisation d'une évolut°  */
    gint text_pos;                          /* Abscisse de départ du texte */

    result = false;

    g_buffer_cache_rlock(view->cache);

    line = g_buffer_view_find_line_at(view, caret->y, &index);
    if (line == NULL) goto gbvmc_done;

    first = view->first;
    last = view->last;

    switch (dir)
    {
        case GDK_SCROLL_UP:

            if (index > first)
            {
                index--;

                other = g_buffer_cache_find_line_by_index(view->cache, index);
                assert(other != NULL);

                result = _g_buffer_view_compute_caret_full(view, caret->x, other, index, options, caret, cursor);

                g_object_unref(G_OBJECT(other));

            }

            break;

        case GDK_SCROLL_DOWN:

            if (index < last)
            {
                index++;

                other = g_buffer_cache_find_line_by_index(view->cache, index);
                assert(other != NULL);

                result = _g_buffer_view_compute_caret_full(view, caret->x, other, index, options, caret, cursor);

                g_object_unref(G_OBJECT(other));

            }

            break;

        case GDK_SCROLL_LEFT:

            moved = _g_buffer_view_move_caret(view, line, index, caret, ctrl, GDK_SCROLL_LEFT, options);

            if (moved)
            {
                g_buffer_cache_get_line_cursor(view->cache, index, caret->x, cursor);
                result = true;
            }

            else if (index > first)
            {
                index--;

                other = g_buffer_cache_find_line_by_index(view->cache, index);
                assert(other != NULL);

                result = _g_buffer_view_compute_caret_full(view, INT_MAX, other, index, options, caret, cursor);

                g_object_unref(G_OBJECT(other));

            }

            break;

        case GDK_SCROLL_RIGHT:

            moved = _g_buffer_view_move_caret(view, line, index, caret, ctrl, GDK_SCROLL_RIGHT, options);

            if (moved)
            {
                g_buffer_cache_get_line_cursor(view->cache, index, caret->x, cursor);
                result = true;
            }

            else if (index < last)
            {
                index++;

                text_pos = g_buffer_cache_get_text_position(view->cache);

                other = g_buffer_cache_find_line_by_index(view->cache, index);
                assert(other != NULL);

                result = _g_buffer_view_compute_caret_full(view, text_pos, other, index, options, caret, cursor);

                g_object_unref(G_OBJECT(other));

            }

            break;

        default:    /* GDK_SCROLL_SMOOTH */
            break;

    }

    g_object_unref(G_OBJECT(line));

 gbvmc_done:

    g_buffer_cache_runlock(view->cache);

    return result;

}








/******************************************************************************
*                                                                             *
*  Paramètres  : view    = vue de tampon à mettre à jour.                     *
*                x       = abscisse de la zone principale à traiter.          *
*                y       = ordonnée de la zone principale à traiter.          *
*                options = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Trouve le créateur à l'origine d'un emplacement donné.       *
*                                                                             *
*  Retour      : Créateur trouvé ou NULL si aucun.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *g_buffer_view_find_creator(GBufferView *view, gint x, gint y, const GDisplayOptions *options)
{
    GObject *result;                        /* Trouvaille à faire remonter */
    gint text_pos;                          /* Abscisse de départ du texte */
    gint lheight;                           /* Hauteur d'une ligne         */
    size_t index;                           /* Indice de ligne de tampon   */
    GBufferLine *line;                      /* Ligne à la position courante*/

    result = NULL;

    g_buffer_cache_rlock(view->cache);

    /* Zone d'intervention bornée ! */

    text_pos = g_buffer_cache_get_text_position(view->cache);

    if (x < text_pos)
        goto gbvfc_done;

    /* Détermination de la ligne concernée */

    lheight = g_buffer_cache_get_line_height(view->cache);
    index = y / lheight;

    index += view->first;

    if (index > view->last)
        goto gbvfc_done;

    line = g_buffer_cache_find_line_by_index(view->cache, index);

    assert(line != NULL);

    /* Recherche d'un segment et de son empreinte */

    x -= text_pos;

    result = g_buffer_line_get_creator_at(line, index, view->tracker, options,
                                          (gint []) { 0 }, &x, GDK_SCROLL_LEFT, false);

    g_object_unref(G_OBJECT(line));

 gbvfc_done:

    g_buffer_cache_runlock(view->cache);

    return result;

}








/******************************************************************************
*                                                                             *
*  Paramètres  : view = vue de tampon à mettre à jour.                        *
*                                                                             *
*  Description : Supprime toute mise en évidence de segments.                 *
*                                                                             *
*  Retour      : true si un besoin d'actualisation d'affichage se fait sentir.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_view_unhighlight_segments(GBufferView *view)
{
    bool result;                            /* Bilan d'action à renvoyer   */

    result = reset_segment_content_list(view->highlighted);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view    = vue de tampon à mettre à jour.                     *
*                x       = abscisse de la zone principale à traiter.          *
*                y       = ordonnée de la zone principale à traiter.          *
*                options = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Surligne tous les segments similaires à celui sous la souris.*
*                                                                             *
*  Retour      : true si un besoin d'actualisation d'affichage se fait sentir.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_view_highlight_segments(GBufferView *view, gint x, gint y, const GDisplayOptions *options)
{
    bool result;                            /* Besoin à faire remonter     */
    gint text_pos;                          /* Abscisse de départ du texte */
    gint lheight;                           /* Hauteur d'une ligne         */
    size_t index;                           /* Indice de ligne de tampon   */
    GBufferLine *line;                      /* Ligne à la position courante*/
    line_segment *segment;                  /* Segment sélectionnable      */

    /* Réinitialisation */

    if (view->highlighted != NULL)
        result = g_buffer_view_unhighlight_segments(view);
    else
        result = false;

    /* Zone d'intervention bornée ! */

    g_buffer_cache_rlock(view->cache);

    text_pos = g_buffer_cache_get_text_position(view->cache);

    if (x < text_pos)
        goto gbvhs_done;

    /* Détermination de la ligne concernée */

    lheight = g_buffer_cache_get_line_height(view->cache);
    index = y / lheight;

    index += view->first;

    if (index > view->last)
        goto gbvhs_done;

    line = g_buffer_cache_find_line_by_index(view->cache, index);

    assert(line != NULL);

    /* Recherche d'un segment et de son empreinte */

    x -= text_pos;

    segment = g_buffer_line_get_segment_at(line, index, view->tracker, options,
                                           (gint []) { 0 }, &x, GDK_SCROLL_LEFT, true);

    g_object_unref(G_OBJECT(line));

    /* Conclusion */

    if (segment != NULL)
    {
        result |= add_segment_content_to_selection_list(view->highlighted, segment);
        release_line_segment(segment);
    }

    if (result)
        g_signal_emit_by_name(view, "need-redraw");

 gbvhs_done:

    g_buffer_cache_runlock(view->cache);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view     = visualisation à représenter.                      *
*                cr       = contexte graphique dédié à la procédure.          *
*                virt_y   = ordonnée réelle du point 0 à l'écran.             *
*                area     = position et surface à traiter.                    *
*                options  = règles d'affichage des colonnes modulables.       *
*                selected = ordonnée d'une ligne sélectionnée ou NULL.        *
*                scale    = échelle appliquée à la surface de rendu.          *
*                export   = indique si la vue est en cours d'exportation.     *
*                                                                             *
*  Description : Imprime la visualisation du tampon de lignes quelconques.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_view_draw(const GBufferView *view, cairo_t *cr, gint virt_y, const cairo_rectangle_int_t *area, const GDisplayOptions *options, gint *selected, double scale, bool export)
{
    gint line_height;                       /* Hauteur d'une ligne         */
    gint cr_y;                              /* Ordonnée pour le dessin     */
    size_t first;                           /* Première ligne visée        */
    size_t last;                            /* Dernière ligne visée        */
    segcnt_list *highlighted;               /* Segments mis en évidence    */

    line_height = g_buffer_cache_get_line_height(view->cache) * scale;

    line_height = MAX(line_height, 1);

    /* Indice et point de départ */

    first = view->first;
    first += (virt_y / line_height);

    cr_y = area->y - (virt_y % line_height);

    /* Indice de d'arrivée */

    last = first + (area->height / line_height);
    if (area->height % line_height > 0) last++;

    last = MIN(last, view->last);

    /* Phase de dessin ! */

    /**
     * Le contexte n'est pas sauvegardé avant modification ici car
     * l'appelant l'a fait pour nous avant sa translation sur les abscisses.
     */

    cairo_translate(cr, 0, cr_y);

    if (selected != NULL)
        *selected -= cr_y;

    if (export)
        highlighted = init_segment_content_list();
    else
        highlighted = view->highlighted;

    g_buffer_cache_draw(view->cache, cr, first, last, area, options, selected, highlighted);

    if (export)
        unref_segment_content_list(highlighted);

}




























/******************************************************************************
*                                                                             *
*  Paramètres  : view   = visualisation à consulter.                          *
*                cursor = emplacement à présenter à l'écran.                  *
*                code   = s'arrête si possible à une ligne avec code.         *
*                x      = position horizontale au sein du composant. [OUT]    *
*                y      = position verticale au sein du composant. [OUT]      *
*                                                                             *
*  Description : Indique la position d'affichage d'une adresse donnée.        *
*                                                                             *
*  Retour      : true si l'adresse fait partie du composant, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_view_get_cursor_coordinates(GBufferView *view, const GLineCursor *cursor, bool code, gint *x, gint *y)
{
    bool result;                            /* Bilan à retourner           */

    g_buffer_cache_rlock(view->cache);

    result = g_buffer_cache_get_cursor_coordinates(view->cache, cursor, view->first, view->last, code, x, y);

    g_buffer_cache_runlock(view->cache);

    return result;

}
