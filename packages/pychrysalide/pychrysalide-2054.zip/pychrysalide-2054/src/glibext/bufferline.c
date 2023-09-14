
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bufferline.c - représentation de fragments de texte en ligne
 *
 * Copyright (C) 2010-2019 Cyrille Bagard
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


#include "bufferline.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "chrysamarshal.h"
#include "linecolumn.h"
#include "../common/extstr.h"
#include "../core/paths.h"



/* ---------------------------- GESTION DE LINE COMPLETE ---------------------------- */


/* Mémorisation des origines de texte */
typedef struct _content_origin
{
    col_coord_t coord;                      /* Localisation d'attachement  */

    GObject *creator;                       /* Origine de la création      */

} content_origin;

/* Représentation de fragments de texte en ligne (instance) */
struct _GBufferLine
{
    GObject parent;                         /* A laisser en premier        */

    line_column *columns;                   /* Répartition du texte        */
    size_t col_count;                       /* Nombre de colonnes présentes*/
    size_t merge_start;                     /* Début de la zone globale    */

    BufferLineFlags flags;                  /* Drapeaux particuliers       */

    content_origin *origins;                /* Mémorisation des origines   */
    size_t ocount;                          /* Nombre de ces mémorisations */

};

/* Représentation de fragments de texte en ligne (classe) */
struct _GBufferLineClass
{
    GObjectClass parent;                    /* A laisser en premier        */

#ifdef INCLUDE_GTK_SUPPORT
    cairo_surface_t *entrypoint_img;        /* Image pour les entrées      */
    cairo_surface_t *bookmark_img;          /* Image pour les signets      */
#endif

    /* Signaux */

    void (* content_changed) (GBufferLine *, line_segment *);

    void (* flip_flag) (GBufferLine *, BufferLineFlags, BufferLineFlags);

};


/* Procède à l'initialisation d'une classe de représentation. */
static void g_buffer_line_class_init(GBufferLineClass *);

/* Procède à l'initialisation d'une représentation de fragments. */
static void g_buffer_line_init(GBufferLine *);

/* Supprime toutes les références externes. */
static void g_buffer_line_dispose(GBufferLine *);

/* Procède à la libération totale de la mémoire. */
static void g_buffer_line_finalize(GBufferLine *);



/* ---------------------------------------------------------------------------------- */
/*                              GESTION DE LINE COMPLETE                              */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type de la représentation de fragments de texte en ligne. */
G_DEFINE_TYPE(GBufferLine, g_buffer_line, G_TYPE_OBJECT);



/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GTK à initialiser.               *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de représentation.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_line_class_init(GBufferLineClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
#ifdef INCLUDE_GTK_SUPPORT
    gchar *filename;                        /* Chemin d'accès à utiliser   */
#endif

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_buffer_line_dispose;
    object->finalize = (GObjectFinalizeFunc)g_buffer_line_finalize;

#ifdef INCLUDE_GTK_SUPPORT

    filename = find_pixmap_file("entrypoint.png");
    assert(filename != NULL);

    class->entrypoint_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

    filename = find_pixmap_file("bookmark.png");
    assert(filename != NULL);

    class->bookmark_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

#endif

    g_signal_new("content-changed",
                 G_TYPE_BUFFER_LINE,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBufferLineClass, content_changed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

    g_signal_new("flip-flag",
                 G_TYPE_BUFFER_LINE,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBufferLineClass, flip_flag),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__ENUM_ENUM,
                 G_TYPE_NONE, 2, G_TYPE_UINT, G_TYPE_UINT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = composant GTK à initialiser.                          *
*                                                                             *
*  Description : Procède à l'initialisation d'une représentation de fragments.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_line_init(GBufferLine *line)
{
    line->columns = NULL;
    line->col_count = 0;
    line->merge_start = -1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_line_dispose(GBufferLine *line)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < line->ocount; i++)
        g_object_unref(G_OBJECT(line->origins[i].creator));

    G_OBJECT_CLASS(g_buffer_line_parent_class)->dispose(G_OBJECT(line));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_line_finalize(GBufferLine *line)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < line->col_count; i++)
        reset_line_column(&line->columns[i]);

    if (line->columns != NULL)
        free(line->columns);

    if (line->origins != NULL)
        free(line->origins);

    G_OBJECT_CLASS(g_buffer_line_parent_class)->finalize(G_OBJECT(line));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : col_count = quantité de colonnes à considérer.               *
*                                                                             *
*  Description : Crée une nouvelle représentation de fragments de texte.      *
*                                                                             *
*  Retour      : Composant GTK créé.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferLine *g_buffer_line_new(size_t col_count)
{
    GBufferLine *result;                    /* Composant à retourner       */
    size_t i;                               /* Boucle de parcours          */

    result = g_object_new(G_TYPE_BUFFER_LINE, NULL);

    result->columns = malloc(col_count * sizeof(line_column));

    for (i = 0; i < col_count; i++)
        init_line_column(&result->columns[i]);

    result->col_count = col_count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = ligne à venir compléter.                              *
*                col  = indice de la colonne à constituer.                    *
*                size = taille souhaitée de l'impression des positions.       *
*                addr = localisation physique à venir représenter.            *
*                                                                             *
*  Description : Construit le tronc commun d'une ligne autour de sa position. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_fill_phys(GBufferLine *line, size_t col, MemoryDataSize size, const vmpa2t *addr)
{
    VMPA_BUFFER(position);                  /* Emplacement au format texte */
    size_t len;                             /* Taille de l'élément inséré  */
    size_t i;                               /* Boucle de parcours #1       */

    vmpa2_phys_to_string(addr, size, position, &len);

    for (i = 2; i < len; i++)
        if (position[i] != '0') break;

    if (i == len)
        i = len - 1;

    if (i > 0)
        g_buffer_line_append_text(line, col, position, i, RTT_PHYS_ADDR_PAD, NULL);

    g_buffer_line_append_text(line, col, &position[i], len - i, RTT_PHYS_ADDR, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = ligne à venir compléter.                              *
*                col  = indice de la colonne à constituer.                    *
*                size = taille souhaitée de l'impression des positions.       *
*                addr = localisation virtuelle à venir représenter.           *
*                                                                             *
*  Description : Construit le tronc commun d'une ligne autour de sa position. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_fill_virt(GBufferLine *line, size_t col, MemoryDataSize size, const vmpa2t *addr)
{
    VMPA_BUFFER(position);                  /* Emplacement au format texte */
    size_t len;                             /* Taille de l'élément inséré  */
    size_t i;                               /* Boucle de parcours #1       */

    vmpa2_virt_to_string(addr, size, position, &len);

    if (has_virt_addr(addr))
    {
        for (i = 2; i < len; i++)
            if (position[i] != '0') break;

        if (i == len)
            i = len - 1;

        if (i > 0)
            g_buffer_line_append_text(line, col, position, i, RTT_VIRT_ADDR_PAD, NULL);

        g_buffer_line_append_text(line, col, &position[i], len - i, RTT_VIRT_ADDR, NULL);

    }

    else
        g_buffer_line_append_text(line, col, position, len, RTT_VIRT_ADDR_PAD, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir compléter.                           *
*                col     = indice de la colonne à constituer.                 *
*                content = contenu binaire global à venir lire.               *
*                range   = localisation des données à venir lire et présenter.*
*                max     = taille maximale de la portion binaire en octets.   *
*                                                                             *
*  Description : Construit le tronc commun d'une ligne autour de son contenu. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_fill_content(GBufferLine *line, size_t col, const GBinContent *content, const mrange_t *range, phys_t max)
{
    phys_t length;                          /* Taille de la couverture     */
    bool truncated;                         /* Indique si le code est coupé*/
    size_t required;                        /* Taille de traitement requise*/
    char static_buffer[64];                 /* Petit tampon local rapide   */
    char *bin_code;                         /* Tampon utilisé pour le code */
    vmpa2t pos;                             /* Boucle de parcours #1       */
    phys_t i;                               /* Boucle de parcours #2       */
    char *iter;                             /* Boucle de parcours #3       */
    int ret;                                /* Progression dans l'écriture */
    uint8_t byte;                           /* Octet à représenter         */

    static const char *charset = "0123456789abcdef";

    /* Détermination du réceptacle */

    length = get_mrange_length(range);

    truncated = (max != VMPA_NO_PHYSICAL && length > max);

    if (truncated)
    {
        length = max;
        required = length * 3 + 4 /* "..." */ + 1;
    }
    else
        required = length * 3 + 1;

    if (required <= sizeof(static_buffer))
        bin_code = static_buffer;
    else
        bin_code = (char *)calloc(required, sizeof(char));

    /* Code brut */

    copy_vmpa(&pos, get_mrange_addr(range));

    for (i = 0, iter = bin_code; i < length; i++, iter += ret)
    {
        if (i == 0)
            ret = 0;
        else
        {
            iter[0] = ' ';
            ret = 1;
        }

        if (!g_binary_content_read_u8(content, &pos, &byte))
        {
            iter[ret + 0] = '?';
            iter[ret + 1] = '?';
        }
        else
        {
            iter[ret + 0] = charset[byte >> 4];
            iter[ret + 1] = charset[byte & 0x0f];
        }

        ret += 2;

    }

    if (truncated)
    {
        strcpy(iter, "...");
        iter += 3;
    }
    else
        *iter = '\0';

    /* Conclusion */

    g_buffer_line_append_text(line, col, bin_code, iter - bin_code, RTT_RAW_CODE, NULL);

    if (bin_code != static_buffer)
        free(bin_code);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line   = ligne à venir consulter.                            *
*                column = indice de la colonne visée par les recherches.      *
*                                                                             *
*  Description : Recherche le premier créateur enregistré dans des segments.  *
*                                                                             *
*  Retour      : Créateur trouvé à déréférencer par la suite ou NULL si échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *g_buffer_line_find_first_segment_creator(const GBufferLine *line, size_t column)
{
    GObject *result;                        /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    assert(column < line->col_count);

    result = NULL;

    for (i = 0; i < line->ocount && result == NULL; i++)
    {
        if (line->origins[i].coord.column == column)
            result = line->origins[i].creator;
    }

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir compléter.                           *
*                column  = colonne de la ligne visée par l'insertion.         *
*                text    = texte à insérer dans l'existant.                   *
*                length  = taille du texte à traiter.                         *
*                type    = type de décorateur à utiliser.                     *
*                creator = instance GLib quelconque à associer.               *
*                                                                             *
*  Description : Ajoute du texte à formater dans une ligne donnée.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_append_text(GBufferLine *line, size_t column, const char *text, size_t length, RenderingTagType type, GObject *creator)
{
    size_t index;                           /* Indice d'insertion          */
    content_origin *origin;                 /* Définition d'une origine    */

    assert(column < line->col_count);
    assert(length > 0);

    index = append_text_to_line_column(&line->columns[column], text, length, type);

    if (creator != NULL)
    {
        line->origins = realloc(line->origins, ++line->ocount * sizeof(content_origin));

        origin = &line->origins[line->ocount - 1];

        origin->coord.column = column;
        origin->coord.index = index;

        origin->creator = creator;
        g_object_ref(G_OBJECT(creator));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir compléter.                           *
*                creator = instance GLib quelconque identifiant un segment.   *
*                text    = texte à insérer dans l'existant.                   *
*                length  = taille du texte à traiter.                         *
*                                                                             *
*  Description : Remplace du texte dans une ligne donnée.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_line_replace_text(GBufferLine *line, const GObject *creator, const char *text, size_t length)
{
    bool result;                            /* Bilan à retourner            */
    size_t i;                               /* Boucle de parcours          */
    const col_coord_t *coord;               /* Emplacement du contenu visé */

    result = false;

    for (i = 0; i < line->ocount && !result; i++)
    {
        if (line->origins[i].creator == creator)
        {
            coord = &line->origins[i].coord;

            replace_text_in_line_column(&line->columns[coord->column], coord->index, text, length);

            g_signal_emit_by_name(line, "content-changed", NULL);

            result = true;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line   = ligne à venir consulter.                            *
*                first  = première colonne à parcourir.                       *
*                end    = colonne de fin de parcours.                         *
*                                                                             *
*  Description : Indique si du texte est présent dans une ligne de tampon.    *
*                                                                             *
*  Retour      : true pour indiquer la présence de texte, false pour du vide. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_line_has_text(const GBufferLine *line, size_t first, size_t end)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    assert(first < end);

    for (i = first; i < end && !result; i++)
        result = (line->columns[i].count > 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line   = ligne à venir consulter.                            *
*                first  = première colonne à parcourir.                       *
*                end    = colonne de fin de parcours.                         *
*                markup = indique si le texte doit être décoré ou non.        *
*                                                                             *
*  Description : Donne le texte représenté par une ligne de tampon.           *
*                                                                             *
*  Retour      : Texte à libérer de la mémoire après usage.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_buffer_line_get_text(const GBufferLine *line, size_t first, size_t end, bool markup)
{
    char *result;                           /* Construction à retourner    */
    size_t i;                               /* Boucle de parcours          */
    char *extra;                            /* Contenu à intégrer au texte */

    result = NULL;

    assert(first < end);

    for (i = first; i < end; i++)
    {
        if (i > first && result != NULL)
            result = stradd(result, " ");

        extra = get_line_column_text(&line->columns[i], markup);

        /* Si la colonne était vide, suivante ! */
        if (extra == NULL) continue;

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
*  Paramètres  : line  = ligne à venir modifier.                              *
*                first = première colonne à parcourir.                        *
*                end   = colonne de fin de parcours.                          *
*                                                                             *
*  Description : Supprime du texte représenté par une ligne de tampon.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_delete_text(GBufferLine *line, size_t first, size_t end)
{
    size_t i;                               /* Boucle de parcours          */

    assert(first < end);

    for (i = first; i < end; i++)
        reset_line_column(&line->columns[i]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = ligne à venir consulter.                              *
*                                                                             *
*  Description : Fournit la colonne à partir de laquelle une fusion opère.    *
*                                                                             *
*  Retour      : Début de la première (et unique) zone globale.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_buffer_line_get_merge_start(const GBufferLine *line)
{
    return line->merge_start;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line  = ligne à venir compléter.                             *
*                start = début de la première (et unique) zone globale.       *
*                                                                             *
*  Description : Définit la colonne à partir de laquelle la fusion opère.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_start_merge_at(GBufferLine *line, size_t start)
{
    line->merge_start = start;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = ligne à venir compléter.                              *
*                flag = propriété à intégrer.                                 *
*                                                                             *
*  Description : Ajoute une propriété particulière à une ligne donnée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_add_flag(GBufferLine *line, BufferLineFlags flag)
{
    if ((line->flags & flag) == 0)
    {
        g_signal_emit_by_name(line, "flip-flag", line->flags, flag);

        line->flags |= flag;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = ligne à venir consulter.                              *
*                                                                             *
*  Description : Renseigne sur les propriétés particulières liées à une ligne.*
*                                                                             *
*  Retour      : Propriétés intégrées.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BufferLineFlags g_buffer_line_get_flags(const GBufferLine *line)
{
    return line->flags;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line = ligne à venir compléter.                              *
*                flag = propriété à supprimer.                                *
*                                                                             *
*  Description : Retire une propriété particulière à une ligne donnée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_remove_flag(GBufferLine *line, BufferLineFlags flag)
{
    if ((line->flags & flag) != 0)
    {
        g_signal_emit_by_name(line, "flip-flag", line->flags, flag);

        line->flags &= ~flag;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line      = ligne de texte à manipuler.                      *
*                ctx       = éléments à disposition pour l'exportation.       *
*                type      = type d'exportation attendue.                     *
*                col_count = quantité de colonnes existantes au total.        *
*                options   = règles d'affichage des colonnes modulables.      *
*                                                                             *
*  Description : Exporte la ligne de texte représentée.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_export(GBufferLine *line, buffer_export_context *ctx, BufferExportType type, const GDisplayOptions *options)
{
    size_t opt_count;                       /* Qté de colonnes en option   */
    size_t i;                               /* Boucle de parcours          */
    int col_span;                           /* Fusion de colonnes ?        */

    switch (type)
    {
        case BET_HTML:
            dprintf(ctx->fd, "\t<TR>\n");
            break;
        default:
            break;
    }

    opt_count = g_display_options_count(options);
    assert(opt_count < line->col_count);

    for (i = 0; i < line->col_count; i++)
    {
        if (i < opt_count)
        {
            if (!g_display_options_get(options, i))
                continue;
        }

        switch (type)
        {
            case BET_TEXT:
                if (i > 0) dprintf(ctx->fd, "%s", ctx->sep);
                break;
            default:
                break;
        }

        /**
         * Pour la signification des différentes valeurs assignées,
         * se référer au code de export_line_column_segments().
         *
         * En gros :
         *   - 1  = rien de spécial.
         *   - >1 = il s'agit de la première cellule fusionnée de la ligne.
         *   - 0  = fusion déjà faite, on ne peut que rajouter du contenu dedans.
         *   - <1 = il s'agit de la dernière cellule fusionnée de la ligne.
         *
         * On considère qu'une fusion ne peut pas se réaliser sur la dernière
         * cellule uniquement (ce qui a du sens : c'est inutile).
         */

        if (i < line->merge_start)
            col_span = 1;

        else if (i == line->merge_start)
            col_span = line->col_count - i;

        else
            col_span = ((i + 1) == line->col_count ? -1 : 0);

        export_line_column_segments(&line->columns[i], ctx, type, col_span);

    }

    switch (type)
    {
        case BET_TEXT:
            dprintf(ctx->fd, "\n");
            break;
        case BET_HTML:
            dprintf(ctx->fd, "</TR>\n");
            break;
        default:
            break;
    }

}



/*----------------------------------------------------------------------------------- */
/*                         MANIPULATION DES LARGEURS REQUISES                         */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : line      = ligne à venir consulter.                         *
*                col_count = quantité de colonnes à considérer.               *
*                opt_count = quantité de colonnes optionnelles.               *
*                widths    = largeur mesurée pour chacune des colonnes. [OUT] *
*                merged    = largeur cumulée en cas de fusion. [OUT]          *
*                                                                             *
*  Description : Fait remonter les largeurs requises par une ligne donnée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_collect_widths(const GBufferLine *line, size_t col_count, size_t opt_count, gint *widths, gint *merged)
{
    size_t i;                               /* Boucle de parcours          */
    gint width;                             /* Largeur d'une colonne       */

    assert(col_count == line->col_count);

    *merged = 0;

    for (i = 0; i < col_count; i++)
    {
        width = get_column_width(&line->columns[i]);

        widths[i] = (i < line->merge_start ? width : 0);

        if (line->merge_start != -1 && i >= opt_count)
        {
            *merged += width;

            if (i < line->merge_start && (i + 1) < col_count)
                *merged += COL_MARGIN;

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line  = ligne à venir consulter.                             *
*                coord = coordonnées interne du segment à retrouver.          *
*                                                                             *
*  Description : Fournit le segment présent à une position donnée.            *
*                                                                             *
*  Retour      : Segment trouvé ou NULL si hors borne.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

line_segment *g_buffer_line_get_segment_from_coord(const GBufferLine *line, const col_coord_t *coord)
{
    line_segment *result;                   /* Trouvaille à retourner      */

    if (coord->column < line->col_count)
        result = get_line_column_content_from_index(&line->columns[coord->column], coord->index);
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir consulter.                           *
*                index   = indice de ligne associé.                           *
*                tracker = gestionnaire de largeur à consulter au besoin.     *
*                options = règles d'affichage des colonnes modulables.        *
*                offsets = décalages supplémentaires à appliquer.             *
*                base    = position jusqu'au segment trouvé. [OUT]            *
*                offset  = position à la colonne visée. [OUT]                 *
*                dir     = direction d'un éventuel déplacement en cours.      *
*                force   = accepte les segments en bordure au pire.           *
*                coord   = cordonnées à usage interne à renseigner. [OUT]     *
*                                                                             *
*  Description : Fournit les coordonnées correspondant à une abscisse donnée. *
*                                                                             *
*  Retour      : true si des coordonnées valides ont été renseignées.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_line_get_coord_at(const GBufferLine *line, size_t index, GWidthTracker *tracker, const GDisplayOptions *options, gint *base, gint *offset, GdkScrollDirection dir, bool force, col_coord_t *coord)
{
    bool result;                            /* Bilan à retourner           */
    size_t last;                            /* Dernière colonne remplie    */
    gint last_base;                         /* Dernière abscisse associée  */
    size_t col_count;                       /* Qté de colonnes présentes   */
    size_t opt_count;                       /* Qté de colonnes en option   */
    size_t i;                               /* Boucle de parcours          */
    gint width;                             /* Largeur d'une colonne donnée*/
    gint limit;                             /* Limite d'appartenance       */
    gint consumed;                          /* Distance vers le segment    */
    gint old_base;                          /* Somme de toutes les largeurs*/

    result = false;

    *base = 0;

    last = line->col_count;
    last_base = 0;

    /* On cible déjà la colonne idéale */

    col_count = g_width_tracker_count_columns(tracker);
    opt_count = g_display_options_count(options);

    for (i = 0; i < col_count; i++)
    {
        if (i < opt_count)
        {
            if (!g_display_options_get(options, i))
                continue;
        }

        /* Mémorisation de la dernière colonne contenant quelque chose... */
        if (get_column_width(&line->columns[i]) > 0)
        {
            last = i;
            last_base = *base;
        }

        if (i < line->merge_start)
        {
            width = g_width_tracker_get_local_column_width(tracker, index, i, opt_count);

            /* Si la colonne n'est absolument pas visible, on ne s'arrête pas dessus ! */
            if (width == 0) continue;

            if ((i + 1) < col_count) limit = width + COL_MARGIN / 2;
            else limit = width;

            if (*offset <= limit) break;
            else
            {
                *offset -= width + COL_MARGIN;
                *base += width + COL_MARGIN;
            }

        }
        else
        {
            width = get_column_width(&line->columns[i]);

            if (*offset <= width) break;
            else
            {
                *offset -= width;
                *base += width;
            }

        }


    }

    /* Si l'abscisse fournie tombe encore dans une colonne... */

    if (i < col_count)
    {
        /* Il y a bien du contenu dans cette colonne */

        if (get_column_width(&line->columns[i]) > 0)
        {
            /**
             * Si la position était au milieu d'une marge, la sélection a pu pousser
             * jusqu'à la colonne suivante, plus proche.
             * Relativment à la base de cette dernière, la position est donc devenue négative.
             */
            if (*offset < 0) *offset = 0;

            result = get_line_column_content_index_at(&line->columns[i], offset, dir, &consumed, &coord->index);

            if (result)
            {
                coord->column = i;

                *base += consumed;

            }

        }

        /* La position fournie tombe dans une colonne vide ! */

        else
        {
            if (force || get_column_width(&line->columns[i]) == 0)
            {
                result = false;
                *offset = 0;

                old_base = *base;

                for (i++; i < col_count && !result; i++)
                {
                    if ((i - 1) < line->merge_start)
                    {
                        width = g_width_tracker_get_local_column_width(tracker, index, i - 1, opt_count);

                        if (width > 0)
                            *base += (width + COL_MARGIN);

                    }
                    else
                        *base += get_column_width(&line->columns[i - 1]);

                    result = get_line_column_first_content_index(&line->columns[i], &coord->index);

                    if (result)
                        coord->column = i;

                }

                if (!result)
                {
                    *base = old_base;
                    goto use_right_border;
                }

            }

        }

    }

    else /* if (i == col_count) */
    {
        if (force)
        {
 use_right_border:

            if (last != col_count)
            {
                result = get_line_column_last_content_index(&line->columns[last], &coord->index);

                if (result)
                {
                    coord->column = last;

                    *base = last_base;
                    *offset = get_column_width(&line->columns[last]);

                }

            }

            /* Il n'y a rien sur la ligne ! */
            else
            {
                result = true;

                *base = 0;
                *offset = 0;

                coord->column = col_count;
                coord->index = -1;

            }

        }
        else
            result = false;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir consulter.                           *
*                index   = indice de ligne associé.                           *
*                tracker = gestionnaire de largeur à consulter au besoin.     *
*                options = règles d'affichage des colonnes modulables.        *
*                base    = position jusqu'au segment trouvé. [OUT]            *
*                offset  = position à la colonne visée. [OUT]                 *
*                dir     = direction d'un éventuel déplacement en cours.      *
*                force   = accepte les segments en bordure au pire.           *
*                                                                             *
*  Description : Donne le segment présent à une abscisse donnée.              *
*                                                                             *
*  Retour      : Segment trouvé ou NULL si hors borne.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

line_segment *g_buffer_line_get_segment_at(const GBufferLine *line, size_t index, GWidthTracker *tracker, const GDisplayOptions *options, gint *base, gint *offset, GdkScrollDirection dir, bool force)
{
    line_segment *result;                   /* Trouvaille à retourner      */
    col_coord_t coord;                      /* Emplacement du contenu visé */
    bool status;                            /* Bilan de la localisation    */

    status = g_buffer_line_get_coord_at(line, index, tracker, options, base, offset, dir, force, &coord);

    if (status)
        result = g_buffer_line_get_segment_from_coord(line, &coord);
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir consulter.                           *
*                index   = indice de ligne associé.                           *
*                tracker = gestionnaire de largeur à consulter au besoin.     *
*                options = règles d'affichage des colonnes modulables.        *
*                base    = position jusqu'au segment trouvé. [OUT]            *
*                offset  = position à la colonne visée. [OUT]                 *
*                dir     = direction d'un éventuel déplacement en cours.      *
*                force   = accepte les segments en bordure au pire.           *
*                                                                             *
*  Description : Donne le créateur présent à une abscisse donnée.             *
*                                                                             *
*  Retour      : Créateur trouvé ou NULL si hors borne.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *g_buffer_line_get_creator_at(const GBufferLine *line, size_t index, GWidthTracker *tracker, const GDisplayOptions *options, gint *base, gint *offset, GdkScrollDirection dir, bool force)
{
    GObject *result;                        /* Trouvaille à retourner      */
    col_coord_t target;                     /* Emplacement du contenu visé */
    bool status;                            /* Bilan de la localisation    */
    size_t i;                               /* Boucle de parcours          */
    const col_coord_t *coord;               /* Emplacement du contenu visé */

    result = NULL;

    status = g_buffer_line_get_coord_at(line, index, tracker, options, base, offset, dir, force, &target);

    if (status)
    {
        for (i = 0; i < line->ocount && result == NULL; i++)
        {
            coord = &line->origins[i].coord;

            if (coord->column == target.column && coord->index == target.index)
                result = line->origins[i].creator;

        }

        if (result != NULL)
            g_object_ref(G_OBJECT(result));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne à venir consulter.                           *
*                index   = indice de ligne associé.                           *
*                coord   = cordonnées à consulter puis renseigner. [OUT]      *
*                tracker = gestionnaire de largeur à consulter au besoin.     *
*                options = règles d'affichage des colonnes modulables.        *
*                dir     = orientation des recherches.                        *
*                offset  = décalage pour amener à l'extrémité nouvelle. [OUT] *
*                                                                             *
*  Description : Fournit des coordonnées voisines selon une direction donnée. *
*                                                                             *
*  Retour      : true si des coordonnées valides ont été renseignées.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_line_find_near_coord(const GBufferLine *line, size_t index, col_coord_t *coord, GWidthTracker *tracker, const GDisplayOptions *options, GdkScrollDirection dir, gint *offset)
{
    bool result;                            /* Bilan à retourner           */
    size_t col_count;                       /* Qté de colonnes présentes   */
    size_t i;                               /* Boucle de parcours #1       */
    size_t opt_count;                       /* Qté de colonnes en option   */
    bool displayed;                         /* Confort de lecture          */
    size_t k;                               /* Boucle de parcours #2       */
    gint width;                             /* Largeur d'une colonne donnée*/

    result = false;

    col_count = g_width_tracker_count_columns(tracker);

    /* Recherche dans la colonne de départ */

    i = coord->column;

    if (i == col_count) return false;

    result = find_near_segment(&line->columns[i], &coord->index, dir);

    /* Recherche dans la direction des colonnes voisines */

    opt_count = g_display_options_count(options);

    if (!result)
        switch (dir)
        {
            case GDK_SCROLL_LEFT:

                /* Si on a atteint la première colonne sans trouver... */
                if (i == 0) break;

                /* On s'assure que la colonne précédente est visible et peuplée */
                for (; i > 0 && !result; i--)
                {
                    displayed = (i <= opt_count ? g_display_options_get(options, i - 1) : true);

                    if (displayed)
                    {
                        result = get_line_column_first_content_index(&line->columns[i - 1], &coord->index);

                        if (result)
                            coord->column = i - 1;

                    }

                }

                break;

            case GDK_SCROLL_RIGHT:

                /* On s'assure que la colonne suivante est visible et peuplée */
                for (; (i + 1) < col_count && !result; i++)
                {
                    displayed = ((i + 1) < opt_count ? g_display_options_get(options, i + 1) : true);

                    if (displayed)
                    {
                        result = get_line_column_first_content_index(&line->columns[i + 1], &coord->index);

                        if (result)
                            coord->column = i + 1;

                    }

                }

                break;

        default:
            break;

    }

    /* Calcul de la position finale */

    if (result)
    {
        *offset = 0;

        for (k = 0; k < i; k++)
        {
            displayed = (k < opt_count ? g_display_options_get(options, k) : true);

            if (displayed)
            {

                if (k >= line->merge_start)
                    width = get_column_width(&line->columns[index]);
                else
                    width = g_width_tracker_get_local_column_width(tracker, index, k, opt_count);

                if (width > 0)
                {
                    *offset += width;
                    if (k < line->merge_start) *offset += COL_MARGIN;
                }

            }

        }

        switch (dir)
        {
            case GDK_SCROLL_LEFT:
                *offset += get_column_width(&line->columns[i]);
                break;

            case GDK_SCROLL_RIGHT:
                /**offset += 0;*/
                break;

            default:
                break;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : line    = ligne de texte à manipuler.                        *
*                index   = indice de ligne associé.                           *
*                cairo   = contexte graphique à utiliser pour les pinceaux.   *
*                x_init  = abscisse du point d'impression de départ.          *
*                y       = ordonnée du point d'impression.                    *
*                tracker = gestionnaire de largeur à consulter au besoin.     *
*                options = règles d'affichage des colonnes modulables.        *
*                list    = liste de contenus à mettre en évidence.            *
*                                                                             *
*  Description : Imprime la ligne de texte représentée.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_line_draw(GBufferLine *line, size_t index, cairo_t *cairo, gint x_init, gint y, GWidthTracker *tracker, const GDisplayOptions *options, const segcnt_list *list)
{
    GBufferLineClass *class;                /* Stockage de briques de base */
    bool has_src_surface;                   /* Note une présence définie   */
    gint x;                                 /* Point de départ d'impression*/
    size_t col_count;                       /* Qté de colonnes présentes   */
    size_t opt_count;                       /* Qté de colonnes en option   */
    size_t i;                               /* Boucle de parcours          */
    gint max_width;                         /* Largeur maximale de colonne */

    if (line->flags != BLF_NONE)
    {
        class = G_BUFFER_LINE_GET_CLASS(line);

        if (line->flags & BLF_ENTRYPOINT)
        {
            cairo_set_source_surface(cairo, class->entrypoint_img, 5, y);
            has_src_surface = true;
        }
        else if (line->flags & BLF_BOOKMARK)
        {
            cairo_set_source_surface(cairo, class->bookmark_img, 5, y);
            has_src_surface = true;
        }
        else
            has_src_surface = false;

        if (has_src_surface)
            cairo_paint(cairo);

    }

    x = x_init;

    col_count = g_width_tracker_count_columns(tracker);
    opt_count = g_display_options_count(options);

    for (i = 0; i < col_count; i++)
    {
        if (i < opt_count)
        {
            if (!g_display_options_get(options, i))
                continue;
        }

        draw_line_column_segments(&line->columns[i], cairo, x, y, list);

        if (i < line->merge_start)
        {
            max_width = g_width_tracker_get_local_column_width(tracker, index, i, opt_count);

            if (max_width > 0)
                x += max_width + COL_MARGIN;

        }

    }

}


#endif
