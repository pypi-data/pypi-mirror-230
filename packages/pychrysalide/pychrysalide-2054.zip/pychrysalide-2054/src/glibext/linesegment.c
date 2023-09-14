
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linesegment.c - concentration d'un fragment de caractères aux propriétés communes
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


#include "linesegment.h"


#include <assert.h>
#include <limits.h>
#include <malloc.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>


#include "../common/extstr.h"
#include "../common/fnv1a.h"
#include "../core/paths.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../gtkext/rendering.h"
#endif



/* ------------------------ NATURE POUR UN FRAGMENT DE TEXTE ------------------------ */


/* Nom des éléments CSS */

#define SEGMENT_NAME(s) "token-" s

static const char *_segment_names[RTT_COUNT] = {

    [RTT_NONE]          = SEGMENT_NAME("none"),
    [RTT_RAW]           = SEGMENT_NAME("raw"),
    [RTT_RAW_FULL]      = SEGMENT_NAME("raw-full"),
    [RTT_RAW_NULL]      = SEGMENT_NAME("raw-null"),
    [RTT_PRINTABLE]     = SEGMENT_NAME("printable"),
    [RTT_NOT_PRINTABLE] = SEGMENT_NAME("not-printable"),
    [RTT_COMMENT]       = SEGMENT_NAME("comment"),
    [RTT_INDICATION]    = SEGMENT_NAME("indication"),
    [RTT_PHYS_ADDR_PAD] = SEGMENT_NAME("phys-addr-padding"),
    [RTT_PHYS_ADDR]     = SEGMENT_NAME("phys-addr"),
    [RTT_VIRT_ADDR_PAD] = SEGMENT_NAME("virt-addr-padding"),
    [RTT_VIRT_ADDR]     = SEGMENT_NAME("virt-addr"),
    [RTT_RAW_CODE]      = SEGMENT_NAME("raw-code"),
    [RTT_RAW_CODE_NULL] = SEGMENT_NAME("raw-code-null"),
    [RTT_LABEL]         = SEGMENT_NAME("label"),
    [RTT_INSTRUCTION]   = SEGMENT_NAME("instruction"),
    [RTT_IMMEDIATE]     = SEGMENT_NAME("immediate"),
    [RTT_REGISTER]      = SEGMENT_NAME("register"),
    [RTT_PUNCT]         = SEGMENT_NAME("punct"),
    [RTT_HOOK]          = SEGMENT_NAME("hooks"),
    [RTT_SIGNS]         = SEGMENT_NAME("signs"),
    [RTT_LTGT]          = SEGMENT_NAME("ltgt"),
    [RTT_SECTION]       = SEGMENT_NAME("section"),
    [RTT_SEGMENT]       = SEGMENT_NAME("segment"),
    [RTT_STRING]        = SEGMENT_NAME("string"),
    [RTT_VAR_NAME]      = SEGMENT_NAME("var-name"),
    [RTT_KEY_WORD]      = SEGMENT_NAME("keyword"),
    [RTT_ERROR]         = SEGMENT_NAME("error"),

};


#ifdef INCLUDE_GTK_SUPPORT

/* Compléments à Cairo */

#define CAIRO_FONT_SLANT_COUNT  3
#define CAIRO_FONT_WEIGHT_COUNT 2

#define CAIRO_FONTS_COUNT (CAIRO_FONT_SLANT_COUNT * CAIRO_FONT_WEIGHT_COUNT)
#define CAIRO_FONT_INDEX(s, w) ((s) + (w) * CAIRO_FONT_WEIGHT_COUNT)


/* Propriétés de rendu */
typedef struct _segment_rendering
{
    rendering_color_t selection_bg;         /* Fond d'impression           */

    cairo_t *font_ctxts[CAIRO_FONTS_COUNT]; /* Contextes de police         */
    double x_advances[CAIRO_FONTS_COUNT];   /* Largeurs par caractère      */

    rendering_pattern_t patterns[RTT_COUNT];/* Modèles d'impression        */

} segment_rendering;


/* Configuration globale des rendus */
static segment_rendering _seg_params;

#endif



/* ----------------------- ISOLATION DE CONTENUS PARTAGEABLES ----------------------- */


/* Fragment de caractères aux propriétés potentiellement partagées */
struct _line_segment
{
    gint ref_count;                         /* Compteur de références      */

#ifdef INCLUDE_GTK_SUPPORT
   rendering_pattern_t *pattern;           /* Propriétés du rendu         */
#else
    RenderingTagType type;                  /* Type de rendu attendu       */
#endif

    fnv64_t hash;                           /* Empreinte pour comparaisons */
    char text[0];                           /* Texte brut conservé         */

};


/* Conservation de toutes les créations partagées */
static GHashTable *_segcnt_htable;
G_LOCK_DEFINE_STATIC(_segcnt_mutex);


/* Fournit l'empreinte d'un contenu pour segments. */
static guint get_line_segment_hash(const line_segment *);

/* Détermine si deux contenus pour segments sont identiques. */
static bool is_line_segment_equal(const line_segment *, const line_segment *);

/* Détermine si deux contenus pour segments sont identiques. */
static line_segment *get_shared_segment_content(const line_segment *);

/* Abandonne un contenu pour segments. */
static void release_shared_segment_content(line_segment *);



/* -------------------- GESTION OPTIMALE D'UNE LISTE DE CONTENUS -------------------- */


#ifdef INCLUDE_GTK_SUPPORT

/* Liste identifiant un ensemble de segments */
struct _segcnt_list
{
    fnv64_t *hashes;                        /* Empreinte pour comparaisons */
    size_t count;                           /* Nommbre de ces empreintes   */

    unsigned int ref_count;                 /* Compteur de références      */

};


/* Indique si le contenu d'un segment est notable ou non. */
bool selection_list_has_segment_content(const segcnt_list *, const line_segment *);

#endif



/* ---------------------------------------------------------------------------------- */
/*                          NATURE POUR UN FRAGMENT DE TEXTE                          */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Procède à l'initialisation des paramètres de rendu de texte. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_segment_rendering_parameters(void)
{
    cairo_font_slant_t s;                   /* Boucle de parcours #1       */
    cairo_font_weight_t w;                  /* Boucle de parcours #2       */
    cairo_t **cr;                           /* Contexte à créer            */
    cairo_surface_t *surface;               /* Surface pour dessin Cairo   */
    cairo_text_extents_t extents;           /* Couverture des caractères   */
    RenderingTagType i;                     /* Boucle de parcours          */

    /* Contextes pour les mesures initiales */

    for (s = CAIRO_FONT_SLANT_NORMAL; s < CAIRO_FONT_SLANT_COUNT; s++)
        for (w = CAIRO_FONT_WEIGHT_NORMAL; w < CAIRO_FONT_WEIGHT_COUNT; w++)
        {
            cr = &_seg_params.font_ctxts[CAIRO_FONT_INDEX(s, w)];

            surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, 1, 1);
            *cr = cairo_create(surface);
            cairo_surface_destroy(surface);

            cairo_select_font_face(*cr, "mono", s, w);
            cairo_set_font_size(*cr, 13);

            cairo_text_extents(*cr, "A", &extents);
            _seg_params.x_advances[CAIRO_FONT_INDEX(s, w)] = extents.x_advance;

        }

    /* Fond d'impression */

    _seg_params.selection_bg.has_color = true;
    _seg_params.selection_bg.color.red = 0.5;
    _seg_params.selection_bg.color.green = 0.5;
    _seg_params.selection_bg.color.blue = 0.5;
    _seg_params.selection_bg.color.alpha = 1.0;

    /* Chargement des définitions utiles */

    for (i = 0; i < RTT_COUNT; i++)
        load_rendering_pattern(_segment_names[i], &_seg_params.patterns[i]);

    return true;

}


#endif



/* ---------------------------------------------------------------------------------- */
/*                         ISOLATION DE CONTENUS PARTAGEABLES                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Initialise la table mémorisant les contenus pour segments.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_segment_content_hash_table(void)
{
    _segcnt_htable = g_hash_table_new_full((GHashFunc)get_line_segment_hash,
                                           (GEqualFunc)is_line_segment_equal,
                                           free, NULL);

    return (_segcnt_htable != NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Organise la sortie de la table des contenus pour segments.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_segment_content_hash_table(void)
{
    assert(g_hash_table_size(_segcnt_htable) == 0);

    g_hash_table_unref(_segcnt_htable);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu pour segment à consulter.                  *
*                                                                             *
*  Description : Fournit l'empreinte d'un contenu pour segments.              *
*                                                                             *
*  Retour      : Empreinte de lu contenu représenté.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint get_line_segment_hash(const line_segment *content)
{
    return content->hash;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = premier contenu pour segment à analyser.           *
*                other   = second contenu pour segment à analyser.            *
*                                                                             *
*  Description : Détermine si deux contenus pour segments sont identiques.    *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_line_segment_equal(const line_segment *content, const line_segment *other)
{
    bool result;                            /* Résultat à retourner        */

#ifdef INCLUDE_GTK_SUPPORT
    result = (content->pattern == other->pattern);
#else
    result = (content->type == other->type);
#endif

    if (result)
        result = (cmp_fnv_64a(content->hash, other->hash) == 0);

    if (result)
        result = (strcmp(content->text, other->text) == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = premier contenu pour segment à analyser.           *
*                other   = second contenu pour segment à analyser.            *
*                                                                             *
*  Description : Détermine si deux contenus pour segments sont identiques.    *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static line_segment *get_shared_segment_content(const line_segment *content)
{
    line_segment *result;                    /* Contenu partagé à renvoyer  */
    gboolean found;                         /* Le contenu existe déjà ?    */
    size_t allocated;                       /* Besoin complet en mémoire   */
#ifndef NDEBUG
    gboolean created;                       /* Validation de mise en place */
#endif

    G_LOCK(_segcnt_mutex);

    found = g_hash_table_lookup_extended(_segcnt_htable, content, (gpointer *)&result, NULL);

    if (!found)
    {
        allocated = sizeof(line_segment) + strlen(content->text) + 1;

        result = (line_segment *)malloc(allocated);

        memcpy(result, content, allocated);

        g_atomic_int_set(&result->ref_count, 1);

#ifndef NDEBUG
        created = g_hash_table_insert(_segcnt_htable, result, result);
        assert(created);
#else
        g_hash_table_insert(_segcnt_htable, result, result);
#endif

    }

    else
    {
        assert(result->ref_count < UINT_MAX);

        g_atomic_int_inc(&result->ref_count);

    }

    G_UNLOCK(_segcnt_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu pour segments à délaisser.                 *
*                                                                             *
*  Description : Abandonne un contenu pour segments.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void release_shared_segment_content(line_segment *content)
{
#ifndef NDEBUG
    gboolean deleted;                       /* Validation de suppression   */
#endif

    if (g_atomic_int_dec_and_test(&content->ref_count))
    {
        G_LOCK(_segcnt_mutex);

#ifndef NDEBUG
        deleted = g_hash_table_remove(_segcnt_htable, content);
        assert(deleted);
#else
        g_hash_table_remove(_segcnt_htable, content);
#endif

        G_UNLOCK(_segcnt_mutex);

    }

}




/* ---------------------------------------------------------------------------------- */
/*                      NATURE DE BASE POUR UN FRAGMENT DE TEXTE                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type   = propriétés de la zone de texte.                     *
*                text   = chaîne de caractères à traiter.                     *
*                length = quantité de ces caractères.                         *
*                                                                             *
*  Description : Crée un nouveau fragment de texte avec des propriétés.       *
*                                                                             *
*  Retour      : Elément créé ou recyclé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

line_segment *get_new_line_segment(RenderingTagType type, const char *text, size_t length)
{
    line_segment *result;                   /* Elément à retourner         */
    char atmp[sizeof(line_segment) + 128];  /* Allocation static facile    */
    line_segment *content;                  /* Contenu à mettre en place ? */

    assert(length > 0);

    if (length < (sizeof(atmp) - sizeof(line_segment)))
        content = (line_segment *)atmp;
    else
        content = (line_segment *)malloc(sizeof(line_segment) + length + 1);

#ifdef INCLUDE_GTK_SUPPORT
    content->pattern = &_seg_params.patterns[type];
#else
    content->type = type;
#endif

    content->hash = fnv_64a_hash(text);

    memcpy(content->text, text, length);
    content->text[length] = '\0';

    result = get_shared_segment_content(content);

    if (content != (line_segment *)atmp)
        free(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à traiter.                       *
*                                                                             *
*  Description : Augmente le compteur de références d'un fragment de texte.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void ref_line_segment(line_segment *segment)
{
    g_atomic_int_inc(&segment->ref_count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à libérer de la mémoire.         *
*                                                                             *
*  Description : Retire une utilisation à un fragment de texte.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void release_line_segment(line_segment *segment)
{
    release_shared_segment_content(segment);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à consulter.                     *
*                                                                             *
*  Description : Indique le type de rendu associé à un segment de ligne.      *
*                                                                             *
*  Retour      : Identifiant de type de rendu.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

RenderingTagType get_line_segment_type(const line_segment *segment)
{
    RenderingTagType result;                /* Résultat à renvoyer         */

#ifdef INCLUDE_GTK_SUPPORT
    result = (RenderingTagType)(segment->pattern - _seg_params.patterns);
#else
    result = segment->type;
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à consulter.                     *
*                markup  = indique si le texte doit être décoré ou non.       *
*                                                                             *
*  Description : Fournit le texte brut conservé dans le segment.              *
*                                                                             *
*  Retour      : Texte conservé en interne.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_line_segment_text(const line_segment *segment, bool markup)
{
#ifndef INCLUDE_GTK_SUPPORT

    char *result;                           /* Description à renvoyer      */

    result = strdup(segment->text);

    return result;

#else

    char *result;                           /* Description à renvoyer      */
    char color[7];                          /* Couleur hexadécimale        */
    char *valid;

    /* Résolution du cas simple */
    if (!markup)
        return strdup(segment->text);

    result = strdup("<span ");

    /* Couleur */

    result = stradd(result, "foreground=\"#");

    snprintf(color, sizeof(color), "%02hhx%02hhx%02hhx",
             (unsigned char)(segment->pattern->foreground.color.red * 255),
             (unsigned char)(segment->pattern->foreground.color.green * 255),
             (unsigned char)(segment->pattern->foreground.color.blue * 255));

    result = stradd(result, color);

    result = stradd(result, "\"");

    /* Style */

    result = stradd(result, "style=\"");

    switch (segment->pattern->slant)
    {
        case CAIRO_FONT_SLANT_NORMAL:
            result = stradd(result, "normal");
            break;

        case CAIRO_FONT_SLANT_ITALIC:
            result = stradd(result, "italic");
            break;

        case CAIRO_FONT_SLANT_OBLIQUE:
            result = stradd(result, "oblique");
            break;

    }

    result = stradd(result, "\"");

    /* Epaisseur */

    result = stradd(result, "weight=\"");

    switch (segment->pattern->weight)
    {
        case CAIRO_FONT_WEIGHT_NORMAL:
            result = stradd(result, "normal");
            break;

        case CAIRO_FONT_WEIGHT_BOLD:
            result = stradd(result, "bold");
            break;

    }

    result = stradd(result, "\"");

    /* Conclusion */

    result = stradd(result, ">");

    valid = strdup(segment->text);
    valid = strrpl(valid, "&", "&amp;");
    valid = strrpl(valid, "<", "&lt;");

    result = stradd(result, valid);

    free(valid);

    result = stradd(result, "</span>");

    return result;

#endif

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à consulter.                     *
*                                                                             *
*  Description : Fournit la quantité de pixels requise pour l'impression.     *
*                                                                             *
*  Retour      : Largeur requise par la colonne, en pixel.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint get_line_segment_width(const line_segment *segment)
{
    gint result;                            /* Largeur à retourner         */
    cairo_font_slant_t slant;               /* Style d'impression          */
    cairo_font_weight_t weight;             /* Poids de la police          */
    size_t length;                          /* Taille du texte représenté  */

    slant = segment->pattern->slant;
    weight = segment->pattern->weight;

    length = strlen(segment->text);

    if (length == 1 && segment->text[0] == '\t')
        length = 2;

    result = _seg_params.x_advances[CAIRO_FONT_INDEX(slant, weight)] * length;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à consulter.                     *
*                x       = position horizontale au niveau du segment.         *
*                                                                             *
*  Description : Fournit la position idéale pour un marqueur.                 *
*                                                                             *
*  Retour      : Position dans le segment donné.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint get_caret_position_from_line_segment(const line_segment *segment, gint x)
{
    gint result;                            /* Position à retourner        */
    gint width;                             /* Largeur du segment          */
    gint char_width;                        /* Largeur de police fixe      */

    width = get_line_segment_width(segment);

    if (x <= 0)
        result = 0;

    else if (x >= width)
        result = width;

    else
    {
        char_width = width / strlen(segment->text);

        result = (x / char_width) * char_width;
        if ((x % char_width) > (char_width / 2))
            result += char_width;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à manipuler.                     *
*                x       = position du curseur à faire évoluer. [OUT]         *
*                ctrl    = indique la demande d'un parcours rapide.           *
*                dir     = direction du parcours.                             *
*                                                                             *
*  Description : Déplace le curseur au sein d'un segment de tampon.           *
*                                                                             *
*  Retour      : true si un déplacement a été effectué, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool move_caret_on_line_segment(const line_segment *segment, gint *x, bool ctrl, GdkScrollDirection dir)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    gint width;                             /* Largeur du segment          */
    gint char_width;                        /* Largeur de police fixe      */

    result = false;

    width = get_line_segment_width(segment);
    char_width = width / strlen(segment->text);

    if (dir == GDK_SCROLL_LEFT)
    {
        if (*x > width) *x = width + char_width;

        if (*x == 0) goto gbsmc_done;

        if (ctrl) *x = 0;
        else *x = MAX(0, *x - char_width);

        result = true;

    }

    else if (dir == GDK_SCROLL_RIGHT)
    {
        if (*x == width) goto gbsmc_done;

        if (ctrl) *x = width;
        else *x = MIN(width, *x + char_width);

        result = true;

    }

 gbsmc_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à manipuler.                     *
*                cr      = contexte graphique à utiliser pour les pinceaux.   *
*                x       = abscisse du point d'impression (à maj). [OUT]      *
*                y       = ordonnée du point d'impression.                    *
*                list    = liste de contenus à mettre en évidence.            *
*                                                                             *
*  Description : Imprime le fragment de texte représenté.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void draw_line_segment(const line_segment *segment, cairo_t *cr, gint *x, gint y, const segcnt_list *list)
{
    bool selected;                          /* Marquer une sélection ?     */
    gint width;                             /* Largeur du segment          */
    cairo_operator_t old;                   /* Sauvegarde avant changement */
    const rendering_color_t *used_fg;       /* Couleur d'impression utile  */

    selected = selection_list_has_segment_content(list, segment);

    width = get_line_segment_width(segment);

    if (segment->text[0] == '\t' && segment->text[1] == '\0')
        goto small_sep;

    /* Fond du texte */
    if (selected)
    {
        cairo_set_source_rgba(cr,
                              _seg_params.selection_bg.color.red,
                              _seg_params.selection_bg.color.green,
                              _seg_params.selection_bg.color.blue,
                              _seg_params.selection_bg.color.alpha);

        cairo_rectangle(cr, *x, y, width, 17);

        old = cairo_get_operator(cr);
        cairo_set_operator(cr, CAIRO_OPERATOR_DIFFERENCE);
        cairo_fill(cr);
        cairo_set_operator(cr, old);

    }

    /* Couleur d'impression */

    if (selected)
        used_fg = &segment->pattern->inverted;
    else
        used_fg = &segment->pattern->foreground;

    if (used_fg->has_color)
        cairo_set_source_rgba(cr,
                              used_fg->color.red,
                              used_fg->color.green,
                              used_fg->color.blue,
                              used_fg->color.alpha);
    else
        cairo_set_source_rgb(cr, 0, 0, 0);

    /* Impression du texte */

    cairo_select_font_face(cr, "mono", segment->pattern->slant, segment->pattern->weight);
    cairo_set_font_size(cr, 13);

    cairo_move_to(cr, *x, y + 17 - 3);  /* 3 = font extents.descent */

    cairo_show_text(cr, segment->text);

 small_sep:

    *x += width;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = éléments à disposition pour l'exportation.            *
*                type = type d'exportation attendue.                          *
*                                                                             *
*  Description : Exporte tous les styles utilisés par des segments.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void export_line_segment_style(buffer_export_context *ctx, BufferExportType type)
{
    size_t i;                               /* Boucle de parcours          */
    const rendering_pattern_t *pattern;     /* Modèle à transcrire         */

    for (i = 0; i < RTT_COUNT; i++)
    {
        pattern = &_seg_params.patterns[i];

        switch (type)
        {
            case BET_HTML:

                dprintf(ctx->fd, ".%s {\n", _segment_names[i]);

                if (pattern->foreground.has_color)
                    dprintf(ctx->fd, "\tcolor: #%02hhx%02hhx%02hhx;\n",
                            (unsigned char)(pattern->foreground.color.red * 255),
                            (unsigned char)(pattern->foreground.color.green * 255),
                            (unsigned char)(pattern->foreground.color.blue * 255));

                switch (pattern->slant)
                {
                    case CAIRO_FONT_SLANT_ITALIC:
                        dprintf(ctx->fd, "\tfont-style: italic;\n");
                        break;
                    case CAIRO_FONT_SLANT_OBLIQUE:
                        dprintf(ctx->fd, "\tfont-style: oblique;\n");
                        break;
                    default:
                        dprintf(ctx->fd, "\tfont-style: normal;\n");
                        break;
                }

                switch (pattern->weight)
                {
                    case CAIRO_FONT_WEIGHT_BOLD:
                        dprintf(ctx->fd, "\tfont-weight: bold;\n");
                        break;
                    default:
                        dprintf(ctx->fd, "\tfont-weight: normal;\n");
                        break;
                }

                dprintf(ctx->fd, "}\n");

                break;

            default:
                break;

        }

    }

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : segment = fragment de texte à manipuler.                     *
*                ctx     = éléments à disposition pour l'exportation.         *
*                type    = type d'exportation attendue.                       *
*                                                                             *
*  Description : Exporte le fragment de texte représenté.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void export_line_segment(const line_segment *segment, buffer_export_context *ctx, BufferExportType type)
{
    RenderingTagType index;                 /* Indice du modèle de rendu   */

    switch (type)
    {
        case BET_HTML:
            index = get_line_segment_type(segment);
            dprintf(ctx->fd, "<SPAN class=\"%s\">", _segment_names[index]);
            break;
        default:
            break;
    }

    dprintf(ctx->fd, "%s", segment->text);

    switch (type)
    {
        case BET_HTML:
            dprintf(ctx->fd, "</SPAN>");
            break;
        default:
            break;
    }

}



/* ---------------------------------------------------------------------------------- */
/*                      GESTION OPTIMALE D'UNE LISTE DE CONTENUS                      */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Initilise une liste de contenus de segments.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

segcnt_list *init_segment_content_list(void)
{
    segcnt_list *result;                    /* Structure à retourner       */

    result = malloc(sizeof(segcnt_list));

    result->hashes = NULL;
    result->count = 0;

    result->ref_count = 1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de références de contenus à traiter.         *
*                                                                             *
*  Description : Libère la mémoire occupée par une liste de contenus.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_segment_content_list(segcnt_list *list)
{
    assert(list->ref_count == 0);

    reset_segment_content_list(list);

    free(list);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de références de contenus à traiter.         *
*                                                                             *
*  Description : Incrémente le nombre d'utilisation de la liste de contenus.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void ref_segment_content_list(segcnt_list *list)
{
    assert(list->ref_count > 0);

    list->ref_count++;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de références de contenus à traiter.         *
*                                                                             *
*  Description : Décrémente le nombre d'utilisation de la liste de contenus.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unref_segment_content_list(segcnt_list *list)
{
    assert(list->ref_count > 0);

    list->ref_count--;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de références de contenus à manipuler.       *
*                                                                             *
*  Description : Vide, si besoin est, une liste de contenus de segments.      *
*                                                                             *
*  Retour      : true si des éléments ont été purgés, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool reset_segment_content_list(segcnt_list *list)
{
    bool result;                            /* Bilan d'action à renvoyer   */

    result = (list->count > 0);

    if (list->hashes != NULL)
    {
        free(list->hashes);
        list->hashes = NULL;
    }

    list->count = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list    = ensemble de références de contenus à manipuler.    *
*                segment = fragment de texte à conservr.                      *
*                                                                             *
*  Description : Marque le contenu d'un segment comme remarquable.            *
*                                                                             *
*  Retour      : true si la liste a été complétée, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_segment_content_to_selection_list(segcnt_list *list, const line_segment *segment)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    static const char white_list[] = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    result = false;

    for (i = 0; i < (sizeof(white_list) - 1) && !result; i++)
        result = (strchr(segment->text, white_list[i]) != NULL);

    if (result)
    {
        list->hashes = realloc(list->hashes, ++list->count * sizeof(fnv64_t));

        list->hashes[list->count - 1] = segment->hash;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list    = ensemble de références de contenus à consulter.    *
*                segment = fragment de texte à comparer.                      *
*                                                                             *
*  Description : Indique si le contenu d'un segment est notable ou non.       *
*                                                                             *
*  Retour      : true si le segment a un contenu présent dans la sélection.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool selection_list_has_segment_content(const segcnt_list *list, const line_segment *segment)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    for (i = 0; i < list->count && !result; i++)
        result = (cmp_fnv_64a(list->hashes[i], segment->hash) == 0);

    return result;

}


#endif
