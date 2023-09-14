
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linesegment.h - prototypes pour la concentration d'un fragment de caractères aux propriétés communes
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


#ifndef _GLIBEXT_LINESEGMENT_H
#define _GLIBEXT_LINESEGMENT_H


#include <glib-object.h>
#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gdk/gdk.h>
#   include <pango/pango.h>
#endif


#ifdef INCLUDE_GTK_SUPPORT

/* Liste identifiant un ensemble de segments */
typedef struct _segcnt_list segcnt_list;

#endif



/* ------------------------ NATURE POUR UN FRAGMENT DE TEXTE ------------------------ */


#ifdef INCLUDE_GTK_SUPPORT

/* Procède à l'initialisation des paramètres de rendu de texte. */
bool load_segment_rendering_parameters(void);

#endif



/* ----------------------- ISOLATION DE CONTENUS PARTAGEABLES ----------------------- */


/* Fragment de caractères aux propriétés potentiellement partagées */
typedef struct _line_segment line_segment;


/* Initialise la table mémorisant les contenus pour segments. */
bool init_segment_content_hash_table(void);

/* Organise la sortie de la table des contenus pour segments. */
void exit_segment_content_hash_table(void);



/* -------------------- NATURE DE BASE POUR UN FRAGMENT DE TEXTE -------------------- */


/* Types de partie de rendu */
typedef enum _RenderingTagType
{
    RTT_NONE,                               /* Espace ou tabulation        */

    RTT_RAW,                                /* Contenu brut                */
    RTT_RAW_FULL,                           /* Contenu brut et complet     */
    RTT_RAW_NULL,                           /* Contenu brut et nul         */
    RTT_PRINTABLE,                          /* Caractère imprimable        */
    RTT_NOT_PRINTABLE,                      /* Caractère non imprimable    */

    RTT_COMMENT,                            /* Commentaire                 */
    RTT_INDICATION,                         /* Aide à la lecture           */

    RTT_PHYS_ADDR_PAD,                      /* Position physique (début)   */
    RTT_PHYS_ADDR,                          /* Position physique           */
    RTT_VIRT_ADDR_PAD,                      /* Adresse virtuelle (début)   */
    RTT_VIRT_ADDR,                          /* Adresse virtuelle           */
    RTT_RAW_CODE,                           /* Code binaire brut           */
    RTT_RAW_CODE_NULL,                      /* Code binaire brut et nul    */

    RTT_LABEL,                              /* Etiquette sur une adresse   */

    RTT_INSTRUCTION,                        /* Code binaire brut           */

    RTT_IMMEDIATE,                          /* Valeur immédiate            */

    RTT_REGISTER,                           /* Registre                    */

    RTT_PUNCT,                              /* Signes de ponctuation       */
    RTT_HOOK,                               /* Crochets '[' et ']'         */
    RTT_SIGNS,                              /* Signes '+', '-' et '*'      */
    RTT_LTGT,                               /* Caractères '<' et '>'       */

    RTT_SECTION,                            /* Identifiant de section      */
    RTT_SEGMENT,                            /* Indication de segment       */
    RTT_STRING,                             /* Chaîne de caractères avec " */

    RTT_VAR_NAME,                           /* Nom de variable             */

    RTT_KEY_WORD,                           /* Mot clef de langage         */

    RTT_ERROR,                              /* Erreur "interne"            */

    RTT_COUNT

} RenderingTagType;


/* Crée un nouveau fragment de texte avec des propriétés. */
line_segment *get_new_line_segment(RenderingTagType, const char *, size_t);

/* Augmente le compteur de références d'un fragment de texte. */
void ref_line_segment(line_segment *);

/* Retire une utilisation à un fragment de texte. */
void release_line_segment(line_segment *);

/* Indique le type de rendu associé à un segment de ligne. */
RenderingTagType get_line_segment_type(const line_segment *);

/* Fournit le texte brut conservé dans le segment. */
char *get_line_segment_text(const line_segment *, bool);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la quantité de pixels requise pour l'impression. */
gint get_line_segment_width(const line_segment *);

/* Fournit la position idéale pour un marqueur. */
gint get_caret_position_from_line_segment(const line_segment *, gint);

/* Déplace le curseur au sein d'un segment de tampon. */
bool move_caret_on_line_segment(const line_segment *, gint *, bool, GdkScrollDirection);

/* Imprime le fragment de texte représenté. */
void draw_line_segment(const line_segment *, cairo_t *, gint *, gint, const segcnt_list *);

#endif


/* Types d'exportation */
typedef enum _BufferExportType
{
    BET_TEXT,                               /* Exportation en texte brut   */
    BET_HTML,                               /* Exportation en HTML         */

    BET_COUNT

} BufferExportType;

/* Elements sur lesquels une exportation peut s'appuyer */
typedef struct _buffer_export_context
{
    int fd;                                 /* Flux ouvert en écriture     */

    union
    {
        /* BET_TEXT */
        char *sep;                          /* Séparation entre colonnes   */

        /* BET_HTML */
        struct
        {
            char *font_name;                /* Police d'impression         */
            char *bg_color;                 /* Fond du tableau HTML        */

        };

    };

} buffer_export_context;

#ifdef INCLUDE_GTK_SUPPORT

/* Exporte tous les styles utilisés par des segments. */
void export_line_segment_style(buffer_export_context *, BufferExportType);

#endif

/* Exporte le fragment de texte représenté. */
void export_line_segment(const line_segment *, buffer_export_context *, BufferExportType);



/* -------------------- GESTION OPTIMALE D'UNE LISTE DE CONTENUS -------------------- */


#ifdef INCLUDE_GTK_SUPPORT

/* Initilise une liste de contenus de segments. */
segcnt_list *init_segment_content_list(void);

/* Libère la mémoire occupée par une liste de contenus. */
void exit_segment_content_list(segcnt_list *);

/* Incrémente le nombre d'utilisation de la liste de contenus. */
void ref_segment_content_list(segcnt_list *);

/* Décrémente le nombre d'utilisation de la liste de contenus. */
void unref_segment_content_list(segcnt_list *);

/* Vide, si besoin est, une liste de contenus de segments. */
bool reset_segment_content_list(segcnt_list *);

/* Marque le contenu d'un segment comme remarquable. */
bool add_segment_content_to_selection_list(segcnt_list *, const line_segment *);

#endif



#endif  /* _GLIBEXT_LINESEGMENT_H */
