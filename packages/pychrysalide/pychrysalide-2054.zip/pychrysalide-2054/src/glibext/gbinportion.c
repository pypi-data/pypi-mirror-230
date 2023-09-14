
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binportion.c - représentation graphique de portions de binaire
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


#include "gbinportion.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include "gbinportion-int.h"
#include "../analysis/human/asm/lang.h"
#include "../common/extstr.h"
#include "../common/sort.h"
#include "../core/columns.h"
#include "../glibext/gbinarycursor.h"
#include "../glibext/linegen-int.h"



/* ------------------------------- PORTION DE BINAIRE ------------------------------- */


/* Initialise la classe des portions de données binaires. */
static void g_binary_portion_class_init(GBinPortionClass *);

/* Initialise une instance de portion de données binaires. */
static void g_binary_portion_init(GBinPortion *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_binary_portion_interface_init(GLineGeneratorInterface *);

/* Supprime toutes les références externes. */
static void g_binary_portion_dispose(GBinPortion *);

/* Procède à la libération totale de la mémoire. */
static void g_binary_portion_finalize(GBinPortion *);

#ifdef INCLUDE_GTK_SUPPORT

/* Détermine l'aire d'une sous-portion. */
static bool g_binary_portion_compute_sub_area(const GBinPortion *, phys_t, const GdkRectangle *, GdkRectangle *);

#endif



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_binary_portion_count_lines(const GBinPortion *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_binary_portion_compute_cursor(const GBinPortion *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_binary_portion_contain_cursor(const GBinPortion *, size_t, size_t, const GLineCursor *);

#endif

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_binary_portion_get_flags(const GBinPortion *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_binary_portion_print(GBinPortion *, GBufferLine *, size_t, size_t, const GBinContent *);



/* ------------------------ PARCOURS D'ENSEMBLES DE PORTIONS ------------------------ */


/* Détermine si une portion contient une adresse donnée. */
static bool g_binary_portion_contains_vmpa(const GBinPortion *, const vmpa2t *);

#ifdef INCLUDE_GTK_SUPPORT

/* Recherche la portion présente à une adresse donnée. */
static GBinPortion *g_binary_portion_find_with_area_at_addr(GBinPortion *, const vmpa2t *, GdkRectangle *);

/* Détermine si une portion contient une position donnée. */
static bool g_binary_portion_contains_physical(const GBinPortion *, phys_t);

/* Détermine si une portion contient une adresse donnée. */
static bool g_binary_portion_contains_virtual(const GBinPortion *, virt_t);

#endif



/* ---------------------------------------------------------------------------------- */
/*                                 PORTION DE BINAIRE                                 */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les portions de données binaires. */
G_DEFINE_TYPE_WITH_CODE(GBinPortion, g_binary_portion, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_binary_portion_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des portions de données binaires.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_class_init(GBinPortionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_binary_portion_dispose;
    object->finalize = (GObjectFinalizeFunc)g_binary_portion_finalize;


}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de portion de données binaires.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_init(GBinPortion *portion)
{
    vmpa2t dummy;                           /* Coquille presque vide       */

    portion->code = NULL;

#ifdef INCLUDE_GTK_SUPPORT
    portion->icon = NULL;
#endif

    portion->desc = NULL;
    portion->text = NULL;
    portion->lcount = 0;

    init_vmpa(&dummy, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);
    init_mrange(&portion->range, &dummy, VMPA_NO_VIRTUAL);

    portion->continued = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_interface_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_binary_portion_count_lines;
#ifdef INCLUDE_GTK_SUPPORT
    iface->compute = (linegen_compute_fc)g_binary_portion_compute_cursor;
    iface->contain = (linegen_contain_fc)g_binary_portion_contain_cursor;
#endif
    iface->get_flags = (linegen_get_flags_fc)g_binary_portion_get_flags;
    iface->print = (linegen_print_fc)g_binary_portion_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_dispose(GBinPortion *portion)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < portion->count; i++)
        g_clear_object(&portion->subs[i]);

    G_OBJECT_CLASS(g_binary_portion_parent_class)->dispose(G_OBJECT(portion));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_finalize(GBinPortion *portion)
{
    size_t i;                               /* Boucle de parcours          */

    if (portion->code != NULL)
        free(portion->code);

#ifdef INCLUDE_GTK_SUPPORT
    if (portion->icon != NULL)
        cairo_surface_destroy(portion->icon);
#endif

    if (portion->desc != NULL)
        free(portion->desc);

    for (i = 0; i < portion->lcount; i++)
        free(portion->text[i]);

    if (portion->text != NULL)
        free(portion->text);

    if (portion->subs != NULL)
        free(portion->subs);

    G_OBJECT_CLASS(g_binary_portion_parent_class)->finalize(G_OBJECT(portion));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : code = désignation humaine de la couleur de fond.            *
*                addr = emplacement de la section à conserver.                *
*                size = taille de la section à conserver.                     *
*                                                                             *
*  Description : Crée une description de partie de code vierge.               *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinPortion *g_binary_portion_new(const char *code, const vmpa2t *addr, phys_t size)
{
    GBinPortion *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_BIN_PORTION, NULL);

    result->code = strdup(code);

    init_mrange(&result->range, addr, size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premières informations à consulter.                      *
*                b = secondes informations à consulter.                       *
*                                                                             *
*  Description : Etablit la comparaison ascendante entre deux portions.       *
*                                                                             *
*  Retour      : Bilan : -1 (a < b), 0 (a == b) ou 1 (a > b).                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_binary_portion_compare(const GBinPortion **a, const GBinPortion **b)
{
    int result;                             /* Bilan à retourner           */
    const vmpa2t *addr_a;                   /* Adresse de la portion 'a'   */
    const vmpa2t *addr_b;                   /* Adresse de la portion 'b'   */

    addr_a = get_mrange_addr(&(*a)->range);
    addr_b = get_mrange_addr(&(*b)->range);

    result = cmp_vmpa(addr_a, addr_b);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à mettre à jour.             *
*                icon    = image miniature de représentation à associer.      *
*                                                                             *
*  Description : Attribue à la portion une éventuelle image de représentation.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_portion_set_icon(GBinPortion *portion, cairo_surface_t *icon)
{
    if (icon != NULL)
        portion->icon = cairo_surface_reference(icon);

    else
        portion->icon = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à consulter.                 *
*                                                                             *
*  Description : Fournit une éventuelle image de représentation de portion.   *
*                                                                             *
*  Retour      : Image miniature de représentation associée.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

cairo_surface_t *g_binary_portion_get_icon(const GBinPortion *portion)
{
    cairo_surface_t *result;

    result = portion->icon;

    if (result != NULL)
        cairo_surface_reference(result);

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à mettre à jour.             *
*                desc    = nom à donner à la partie.                          *
*                                                                             *
*  Description : Attribue une description humaine à une partie de code.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_portion_set_desc(GBinPortion *portion, const char *desc)
{
    size_t i;                               /* Boucle de parcours          */
    GCodingLanguage *lang;                  /* Langage de sortie préféré   */

    if (portion->desc != NULL)
    {
        free(portion->desc);

        for (i = 0; i < portion->lcount; i++)
            free(portion->text[i]);

        if (portion->text != NULL)
        {
            free(portion->text);
            portion->text = NULL;
        }

    }

    if (desc == NULL)
        portion->desc = NULL;

    else
    {
        portion->desc = strdup(desc);

        if (portion->continued)
            portion->desc = stradd(portion->desc, _(" (continued)"));

        /* Constitution du rendu */

        portion->text = calloc(5, sizeof(char *));
        portion->lcount = 5;

        portion->text[0] = strdup("======================================================");
        portion->text[1] = strdup("");

        asprintf(&portion->text[2], "%s (%s%s%s%s)", portion->desc, _("rights: "),
                 portion->rights & PAC_READ ? "r" : "-",
                 portion->rights & PAC_WRITE ? "w" : "-",
                 portion->rights & PAC_EXEC ? "x" : "-");

        portion->text[3] = strdup("");
        portion->text[4] = strdup("======================================================");

        /* Ajout de la touche "commentaires" */

        lang = g_asm_language_new();

        g_coding_language_encapsulate_comments(lang, &portion->text, &portion->lcount);

        g_object_unref(G_OBJECT(lang));

        /* Ajout de deux bordures vides */

        portion->lcount += 2;
        portion->text = realloc(portion->text, portion->lcount * sizeof(char *));

        memmove(&portion->text[1], &portion->text[0], (portion->lcount - 2) * sizeof(char *));

        portion->text[0] = NULL;
        portion->text[portion->lcount - 1] = NULL;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à consulter.                 *
*                                                                             *
*  Description : Fournit la description attribuée à une partie de code.       *
*                                                                             *
*  Retour      : Nom donné à la partie.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_binary_portion_get_desc(const GBinPortion *portion)
{
    return portion->desc;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à mettre à jour.             *
*                                                                             *
*  Description : Fournit l'emplacement d'une partie de code binaire.          *
*                                                                             *
*  Retour      : Espace de couverture associé à la portion.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const mrange_t *g_binary_portion_get_range(const GBinPortion *portion)
{
    return &portion->range;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à mettre à jour.             *
*                max     = taille maximale accordée à la portion.             *
*                                                                             *
*  Description : Assure qu'une portion ne dépasse pas une position donnée.    *
*                                                                             *
*  Retour      : true si la portion a été modifiée, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_portion_limit_range(GBinPortion *portion, phys_t max)
{
    bool result;                            /* Bilan à retourner           */
    phys_t current;                         /* Taille courante             */

    current = get_mrange_length(&portion->range);

    result = (current > max);

    if (result)
        set_mrange_length(&portion->range, max);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = portion dont la définition est à metre à jour.     *
*                                                                             *
*  Description : Définit la nature de la portion en terme d'originalité.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : L'action ne modifie aucunement la description courante.      *
*                C'est le changement de description qui s'appuie sur la       *
*                notée ici.                                                   *
*                                                                             *
******************************************************************************/

void g_binary_portion_mark_as_continued(GBinPortion *portion, bool continued)
{
    portion->continued = continued;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = portion dont la définition est à consulter.        *
*                                                                             *
*  Description : Indique la nature de la portion en terme d'originalité.      *
*                                                                             *
*  Retour      : true si la portion est la suite d'une portion découpée.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_portion_is_continuation(const GBinPortion *portion)
{
    return portion->continued;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à mettre à jour.             *
*                rights  = droits d'accès de la partie.                       *
*                                                                             *
*  Description : Définit les droits associés à une partie de code.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_portion_set_rights(GBinPortion *portion, PortionAccessRights rights)
{
    portion->rights = rights;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à consulter.                 *
*                                                                             *
*  Description : Fournit les droits associés à une partie de code.            *
*                                                                             *
*  Retour      : Droits d'accès de la partie.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PortionAccessRights g_binary_portion_get_rights(const GBinPortion *portion)
{
    return portion->rights;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à mettre à jour.             *
*                tooltip = astuce à compléter. [OUT]                          *
*                                                                             *
*  Description : Prépare une astuce concernant une portion pour son affichage.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_portion_query_tooltip(GBinPortion *portion, GtkTooltip *tooltip)
{
    char *markup;                           /* Description à construire    */
    VMPA_BUFFER(value);                     /* Traduction en texte         */

    /* Nom */

    if (portion->desc != NULL)
    {
        markup = strdup("<b>");
        markup = stradd(markup, portion->desc);
        markup = stradd(markup, "</b>\n");
        markup = stradd(markup, "\n");

    }
    else markup = strdup("");

    markup = stradd(markup, "taille : ");
    mrange_length_to_string(&portion->range, MDS_UNDEFINED, value, NULL);
    markup = stradd(markup, value);
    markup = stradd(markup, "\n");

    /* Localisation */

    markup = stradd(markup, "<b>");
    markup = stradd(markup, _("Localisation"));
    markup = stradd(markup, "</b>\n");

    markup = stradd(markup, _("physical: from "));

    mrange_phys_to_string(&portion->range, MDS_UNDEFINED, true, value, NULL);
    markup = stradd(markup, value);
    markup = stradd(markup, _(" to "));
    mrange_phys_to_string(&portion->range, MDS_UNDEFINED, false, value, NULL);
    markup = stradd(markup, value);
    markup = stradd(markup, "\n");

    markup = stradd(markup, _("memory: from "));

    mrange_virt_to_string(&portion->range, MDS_UNDEFINED, true, value, NULL);
    markup = stradd(markup, value);
    markup = stradd(markup, _(" to "));
    mrange_virt_to_string(&portion->range, MDS_UNDEFINED, false, value, NULL);
    markup = stradd(markup, value);

    markup = stradd(markup, "\n\n");

    /* Droits d'accès */

    markup = stradd(markup, "<b>");
    markup = stradd(markup, _("Rights"));
    markup = stradd(markup, "</b>\n");

    snprintf(value, 2 * VMPA_MAX_SIZE, "%s%s%s",
             portion->rights & PAC_READ ? "r" : "-",
             portion->rights & PAC_WRITE ? "w" : "-",
             portion->rights & PAC_EXEC ? "x" : "-");

    markup = stradd(markup, value);

    /* Impression finale */

    gtk_tooltip_set_markup(tooltip, markup);
    free(markup);

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : portion  = portion mère à consulter.                         *
*                full     = taille totale de la couche parente.               *
*                area     = étendue de représentation de la portion mère.     *
*                sub_area = étendue de représentation de la portion fille.    *
*                                                                             *
*  Description : Détermine l'aire d'une sous-portion.                         *
*                                                                             *
*  Retour      : true si la sous-surface a été calculée correctement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_portion_compute_sub_area(const GBinPortion *portion, phys_t full, const GdkRectangle *area, GdkRectangle *sub_area)
{
    phys_t length;                          /* Taille de la portion        */
    phys_t start;                           /* Position de départ          */

    length = get_mrange_length(&portion->range);

    /* On saute les portions comme le segment GNU_STACK... */
    if (length == 0) return false;

    start = get_phy_addr(get_mrange_addr(&portion->range));

    sub_area->y = area->y;
    sub_area->height = area->height;

    sub_area->x = area->x + (start * area->width) / full;
    sub_area->width = (length * area->width) / full;

    return true;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = description de partie à consulter.                 *
*                context = contexte graphique associé à la procédure.         *
*                cr      = contexte graphique pour le dessin.                 *
*                area    = étendue mise à disposition.                        *
*                                                                             *
*  Description : Représente la portion sur une bande dédiée.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_portion_draw(const GBinPortion *portion, GtkStyleContext *context, cairo_t *cr, const GdkRectangle *area)
{
    phys_t full;                            /* Espace total représenté     */
    size_t i;                               /* Boucle de parcours          */
    GBinPortion *sub;                       /* Portion incluse à montrer   */
    GdkRectangle sub_area;                  /* Etendue d'une sous-portion  */

    /* Dessin de la portion courante */

    cairo_set_antialias(cr, CAIRO_ANTIALIAS_NONE);

    gtk_style_context_save(context);

    if (portion->code != NULL)
        gtk_style_context_add_class(context, portion->code);

    gtk_render_background(context, cr, area->x, area->y, area->width, area->height);

    gtk_render_frame(context, cr, area->x, area->y, area->width, area->height);

    gtk_style_context_restore(context);

    /* Dessin des portions contenues */

    full = get_mrange_length(&portion->range);

    for (i = 0; i < portion->count; i++)
    {
        sub = portion->subs[i];

        if (!g_binary_portion_compute_sub_area(sub, full, area, &sub_area))
            continue;

        g_binary_portion_draw(sub, context, cr, &sub_area);

    }

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = portion principale à compléter.                    *
*                sub     = portion à inclure dans la définition courante.     *
*                                                                             *
*  Description : Procède à l'inclusion d'une portion dans une autre.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_portion_include(GBinPortion *portion, GBinPortion *sub)
{
    bool found;                             /* Zone d'accueil trouvée ?    */
    size_t best;                            /* Meilleur point d'insertion  */
    size_t missed;                          /* Indice de zone à déplacer   */
    const mrange_t *brange;                 /* Raccourci de confort d'usage*/
    vmpa2t end;                             /* Fin de la zone commune      */
    phys_t overlapping;                     /* Taille de la zone commune   */
    bool continued;                         /* Suite d'une découpe ?       */
    GBinPortion *left_part;                 /* Partie intégrable           */
    vmpa2t start;                           /* Départ de la seconde partie */
    GBinPortion *right_part;                /* Partie restante             */

    int g_binary_portion_is_included(const GBinPortion **a, const GBinPortion **b)
    {
        int result;                         /* Bilan à retourner           */

        result = mrange_includes_mrange(&(*b)->range, &(*a)->range);

        return result;

    }

    found = bsearch_index(&sub, portion->subs, portion->count, sizeof(GBinPortion *),
                          (__compar_fn_t)g_binary_portion_is_included, &best);

    if (!found)
    {
        /**
         * On se prépare à réaliser une insertion au niveau courant. Mais des
         * portions précédentes sont peut-être à déplacer dans la nouvelle zone :
         *
         *   EXIDX          0x001178 0x00009178 0x00009178 0x00008 0x00008 R   0x4
         *   PHDR           0x000034 0x00008034 0x00008034 0x00120 0x00120 R E 0x4
         *   INTERP         0x000154 0x00008154 0x00008154 0x00019 0x00019 R   0x1
         *   LOAD           0x000000 0x00008000 0x00008000 0x01184 0x01184 R E 0x8000
         *
         * On refait donc une passe sur toutes les sous-portions du niveau.
         *
         * Cette approche a le mérite de traiter également et naturellement les
         * sections définies dans le désordre :
         *
         *   [21] .bss                NOBITS          00088240 07823c 0018c8 00  WA  0   0  8
         *   [22] __libc_freeres_ptrs NOBITS          00089b08 07823c 000018 00  WA  0   0  4
         *   [23] .comment            PROGBITS        00000000 07823c 000022 01  MS  0   0  1
         *
         * Quant aux cas de figure où les portions sont identiques, l'ordre d'appel
         * induit l'ordre d'inclusion.
         *
         * Cela concerne par exemple les zones de données :
         *
         *   En-têtes de section:
         *     [Nr] Nom               Type            Adr      Décala.Taille ES Fan LN Inf Al
         *     ...
         *     [ 2] .data             PROGBITS        00010098 000098 00000c 00  WA  0   0  1
         *
         *   En-têtes de programme:
         *     Type           Décalage Adr. vir.  Adr.phys.  T.Fich. T.Mém.  Fan Alignement
         *     ...
         *     LOAD           0x000098 0x00010098 0x00010098 0x0000c 0x0000c RW  0x8000
         *
         */

        int g_binary_portion_track_missed_inclusion(const GBinPortion **a, const GBinPortion **b)
        {
            int result;                     /* Bilan à retourner           */

            result = mrange_includes_mrange(&(*a)->range, &(*b)->range);

            return result;

        }

        do
        {
            found = bsearch_index(&sub, portion->subs, portion->count, sizeof(GBinPortion *),
                                  (__compar_fn_t)g_binary_portion_track_missed_inclusion, &missed);

            if (found)
            {
                g_binary_portion_include(sub, portion->subs[missed]);

                portion->subs = _qdelete(portion->subs, &portion->count, sizeof(GBinPortion *), missed);

            }

        }
        while (found);

        /**
         * Il peut arriver que certaines portions débordent de leur zone d'inclusion :
         *
         *   [24] .bss              NOBITS          00012088 002084 000044 00  WA  0   0  8
         *   [25] .ARM.attributes   ARM_ATTRIBUTES  00000000 002084 000037 00      0   0  1
         *   [26] .shstrtab         STRTAB          00000000 0020bb 0000ed 00      0   0  1
         *
         * Afin de respecter une certaine cohérence dans l'arbre des portions, on choisit
         * de découper la portion qui déborde.
         */

        int g_binary_portion_track_partial_inclusion(const GBinPortion **a, const GBinPortion **b)
        {
            int result;                     /* Bilan à retourner           */

            result = cmp_mrange_with_vmpa(&(*b)->range, get_mrange_addr(&(*a)->range));

            return result;

        }

        found = bsearch_index(&sub, portion->subs, portion->count, sizeof(GBinPortion *),
                              (__compar_fn_t)g_binary_portion_track_partial_inclusion, &best);

        if (found)
        {
            brange = &portion->subs[best]->range;

            compute_mrange_end_addr(brange, &end);
            overlapping = compute_vmpa_diff(get_mrange_addr(&sub->range), &end);

            continued = g_binary_portion_is_continuation(sub);

            /* Partie contenue */

            left_part = g_binary_portion_new(sub->code, get_mrange_addr(&sub->range), overlapping);

            g_binary_portion_set_desc(left_part, sub->desc);
            g_binary_portion_mark_as_continued(left_part, continued);
            g_binary_portion_set_rights(left_part, sub->rights);

            /* Partie qui déborde... */

            /**
             * Comme la portion incluante peut avoir une définition d'adresse
             * virtuelle différente de celle de la portion incluse, on recalcule
             * la position de départ de la seconde partie de la portion découpée
             * à partir des données d'origine.
             */

            copy_vmpa(&start, get_mrange_addr(&sub->range));
            advance_vmpa(&start, overlapping);

            right_part = g_binary_portion_new(sub->code, &start, get_mrange_length(&sub->range) - overlapping);

            if (!continued)
                g_binary_portion_mark_as_continued(right_part, true);

            g_binary_portion_set_desc(right_part, sub->desc);

            if (continued)
                g_binary_portion_mark_as_continued(right_part, true);

            g_binary_portion_set_rights(right_part, sub->rights);

            /* Inclusions des parties */

            g_binary_portion_include(portion, left_part);
            g_binary_portion_include(portion, right_part);

            g_object_unref(G_OBJECT(sub));

        }

        else
            portion->subs = qinsert(portion->subs, &portion->count, sizeof(GBinPortion *),
                                    (__compar_fn_t)g_binary_portion_compare, &sub);

    }

    /* Poursuite de l'inclusion dans la sous-portion adaptée... */
    else
        g_binary_portion_include(portion->subs[best], sub);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = première couche amorçant la visite.                *
*                visitor = fonction à appeler à chaque étape de la descente.  *
*                data    = adresse pointant vers des données de l'utilisateur.*
*                                                                             *
*  Description : Parcourt un ensemble de portions binaires.                   *
*                                                                             *
*  Retour      : true si la visite a été jusqu'à son terme, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_portion_visit(GBinPortion *portion, visit_portion_fc visitor, void *data)
{
    bool result;                            /* Etat à retourner            */

    bool visit_portion(GBinPortion *p, GBinPortion *pp)
    {
        bool ret;                           /* Etat à retourner            */
        size_t i;                           /* Boucle de parcours          */

        if (p->count == 0)
            ret = visitor(p, pp, BPV_SHOW, data);

        else
        {
            ret = visitor(p, pp, BPV_ENTER, data);

            for (i = 0; i < p->count && ret; i++)
                ret = visit_portion(p->subs[i], p);

            if (ret)
                ret = visitor(p, pp, BPV_EXIT, data);

        }

        return ret;

    }

    result = visit_portion(portion, NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          OFFRE DE CAPACITES DE GENERATION                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = générateur à consulter.                            *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_binary_portion_count_lines(const GBinPortion *portion)
{
    return portion->lcount;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = générateur à consulter.                            *
*                x       = position géographique sur la ligne concernée.      *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                cursor  = emplacement à constituer. [OUT]                    *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_compute_cursor(const GBinPortion *portion, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    *cursor = g_binary_cursor_new();

    g_binary_cursor_update(G_BINARY_CURSOR(*cursor), get_mrange_addr(&portion->range));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = générateur à consulter.                            *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                cursor  = emplacement à analyser.                            *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_binary_portion_contain_cursor(const GBinPortion *portion, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Conclusion à retourner      */
    vmpa2t addr;                            /* Autre emplacement à comparer*/

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    result = cmp_vmpa(&addr, get_mrange_addr(&portion->range));

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = générateur à consulter.                            *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BufferLineFlags g_binary_portion_get_flags(const GBinPortion *portion, size_t index, size_t repeat)
{
    return (repeat == 0 ? BLF_WIDTH_MANAGER : BLF_NONE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = générateur à utiliser pour l'impression.           *
*                line    = ligne de rendu à compléter.                        *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                content = éventuel contenu binaire brut à imprimer.          *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_portion_print(GBinPortion *portion, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    assert(repeat < portion->lcount);

    g_buffer_line_fill_phys(line, DLC_PHYSICAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&portion->range));

    g_buffer_line_fill_virt(line, DLC_VIRTUAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&portion->range));

    if (portion->text[repeat] != NULL)
    {
        g_buffer_line_start_merge_at(line, DLC_ASSEMBLY_LABEL);

        g_buffer_line_append_text(line, DLC_ASSEMBLY_LABEL, SL(portion->text[repeat]), RTT_COMMENT, NULL);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                          PARCOURS D'ENSEMBLES DE PORTIONS                          */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = couche de portions à parcourir pour les recherches.*
*                                                                             *
*  Description : Compte le nombre de portions présentes dans une arborescence.*
*                                                                             *
*  Retour      : Quantité de portions présentes.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_binary_portion_count(const GBinPortion *portion)
{
    size_t result;                          /* Quantité à retourner        */


    size_t measure_portion_size(const GBinPortion *root)
    {
        size_t count;                       /* Nombre de trouvailles       */
        size_t i;                           /* Boucle de parcours          */

        count = 1;

        for (i = 0; i < root->count; i++)
            count += measure_portion_size(root->subs[i]);

        return count;

    }


    result = measure_portion_size(portion);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = couche de portions à parcourir pour les recherches.*
*                x       = abscisse du point de recherche.                    *
*                area    = étendue de portion mère, puis celle trouvée. [OUT] *
*                                                                             *
*  Description : Recherche la portion présente à un point donné.              *
*                                                                             *
*  Retour      : Portion trouvée à l'endroit indiqué.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinPortion *g_binary_portion_find_at_pos(GBinPortion *portion, gint x, GdkRectangle *area)
{
    GBinPortion *result;                    /* Portion à retourner         */
    phys_t full;                            /* Espace total représenté     */
    size_t i;                               /* Boucle de parcours          */
    GBinPortion *sub;                       /* Portion incluse à traiter   */
    GdkRectangle sub_area;                  /* Etendue d'une sous-portion  */

    result = NULL;

    full = get_mrange_length(&portion->range);

    for (i = 0; i < portion->count && result == NULL; i++)
    {
        sub = portion->subs[i];

        if (!g_binary_portion_compute_sub_area(sub, full, area, &sub_area))
            continue;

        if (sub_area.x <= x && x < (sub_area.x + sub_area.width))
        {
            result = g_binary_portion_find_at_pos(sub, x, &sub_area);

            if (result != NULL)
                *area = sub_area;

        }

    }

    if (result == NULL)
    {
        result = portion;
        g_object_ref(G_OBJECT(result));
    }

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = portion mère à consulter.                          *
*                addr    = adresse du point de recherche.                     *
*                                                                             *
*  Description : Détermine si une portion contient une adresse donnée.        *
*                                                                             *
*  Retour      : true ou false selon le résultat.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_portion_contains_vmpa(const GBinPortion *portion, const vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    const mrange_t *range;                  /* Emplacement de portion      */

    result = false;

    range = g_binary_portion_get_range(portion);

    /* Portion non allouée en mémoire : on écarte */
    if (!has_virt_addr(get_mrange_addr(range)))
        goto not_found;

    result = mrange_contains_addr(range, addr);

 not_found:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = couche de portions à parcourir pour les recherches.*
*                addr    = adresse du point de recherche.                     *
*                                                                             *
*  Description : Recherche la portion présente à une adresse donnée.          *
*                                                                             *
*  Retour      : Portion trouvée à l'endroit indiqué.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinPortion *g_binary_portion_find_at_addr(GBinPortion *portion, const vmpa2t *addr)
{
    GBinPortion *result;                    /* Portion à retourner         */
    phys_t full;                            /* Espace total représenté     */
    size_t i;                               /* Boucle de parcours #1       */
    GBinPortion *sub;                       /* Portion incluse à traiter   */

    result = NULL;

    full = get_mrange_length(&portion->range);

    for (i = 0; i < portion->count && result == NULL; i++)
    {
        sub = portion->subs[i];

        if (!g_binary_portion_contains_vmpa(sub, addr))
            continue;

        result = g_binary_portion_find_at_addr(sub, addr);

    }

    if (result == NULL)
    {
        result = portion;
        g_object_ref(G_OBJECT(result));
    }

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = couche de portions à parcourir pour les recherches.*
*                addr    = adresse du point de recherche.                     *
*                area    = étendue de portion mère, puis celle trouvée. [OUT] *
*                                                                             *
*  Description : Recherche la portion présente à une adresse donnée.          *
*                                                                             *
*  Retour      : Portion trouvée à l'endroit indiqué.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinPortion *g_binary_portion_find_with_area_at_addr(GBinPortion *portion, const vmpa2t *addr, GdkRectangle *area)
{
    GBinPortion *result;                    /* Portion à retourner         */
    phys_t full;                            /* Espace total représenté     */
    size_t i;                               /* Boucle de parcours #1       */
    GBinPortion *sub;                       /* Portion incluse à traiter   */
    GdkRectangle sub_area;                  /* Etendue d'une sous-portion  */

    result = NULL;

    full = get_mrange_length(&portion->range);

    for (i = 0; i < portion->count && result == NULL; i++)
    {
        sub = portion->subs[i];

        if (!g_binary_portion_contains_vmpa(sub, addr))
            continue;

        if (!g_binary_portion_compute_sub_area(sub, full, area, &sub_area))
            continue;

        result = g_binary_portion_find_with_area_at_addr(sub, addr, &sub_area);

        if (result != NULL)
            *area = sub_area;

    }

    if (result == NULL)
    {
        result = portion;
        g_object_ref(G_OBJECT(result));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root = couche de portions à parcourir pour les recherches.   *
*                x    = abscisse du point de recherche.                       *
*                area = étendue de représentation de la portion mère.         *
*                addr = adresse correspondante. [OUT]                         *
*                                                                             *
*  Description : Fournit la position correspondant à une adresse donnée.      *
*                                                                             *
*  Retour      : Succès de la traduction.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_binary_portion_addr_from_pos(GBinPortion *root, gint x, const GdkRectangle *area, vmpa2t *addr)
{
    GdkRectangle owner_area;                /* Aire de contenance          */
    GBinPortion *owner;                     /* Conteneur propriétaire      */

    owner_area = *area;

    owner = g_binary_portion_find_at_pos(root, x, &owner_area);
    if (owner == NULL) return false;

    copy_vmpa(addr, get_mrange_addr(&owner->range));

    advance_vmpa(addr, (get_mrange_length(&owner->range) * (x - owner_area.x)) / owner_area.width);

    g_object_unref(G_OBJECT(owner));

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root = couche de portions à parcourir pour les recherches.   *
*                addr = adresse du point de recherche.                        *
*                area = étendue de représentation de la portion mère.         *
*                x    = position correspondante. [OUT]                        *
*                                                                             *
*  Description : Fournit l'adresse correspondant à une position donnée.       *
*                                                                             *
*  Retour      : Succès de la traduction.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_binary_portion_pos_from_addr(GBinPortion *root, const vmpa2t *addr, const GdkRectangle *area, gint *x)
{
    GdkRectangle owner_area;                /* Aire de contenance          */
    GBinPortion *owner;                     /* Conteneur propriétaire      */
    phys_t diff;                            /* Décalage à appliquer        */

    owner_area = *area;

    owner = g_binary_portion_find_with_area_at_addr(root, addr, &owner_area);
    if (owner == NULL) return false;

    diff = compute_vmpa_diff(addr, get_mrange_addr(&owner->range));

    *x = owner_area.x + (diff * owner_area.width) / get_mrange_length(&owner->range);

    g_object_unref(G_OBJECT(owner));

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : layer   = couche de portions à consulter.                    *
*                x       = abscisse du point de recherche.                    *
*                y       = ordonnée du point de recherche.                    *
*                area    = étendue de représentation de la portion mère.      *
*                tooltip = astuce à compléter. [OUT]                          *
*                                                                             *
*  Description : Prépare une astuce concernant une portion pour son affichage.*
*                                                                             *
*  Retour      : TRUE pour valider l'affichage.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gboolean query_tooltip_for_binary_portion(GBinPortion *root, gint x, gint y, const GdkRectangle *area, GtkTooltip *tooltip)
{
    GBinPortion *selected;                  /* Portion à décrire ici       */

    selected = g_binary_portion_find_at_pos(root, x, (GdkRectangle []) { *area });
    if (selected == NULL) return FALSE;

    g_binary_portion_query_tooltip(selected, tooltip);

    g_object_unref(G_OBJECT(selected));

    return TRUE;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = portion mère à consulter.                          *
*                off     = position physique du point de recherche.           *
*                                                                             *
*  Description : Détermine si une portion contient une position donnée.       *
*                                                                             *
*  Retour      : true ou false selon le résultat.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_portion_contains_physical(const GBinPortion *portion, phys_t off)
{
    bool result;                            /* Bilan à retourner           */
    const mrange_t *range;                  /* Emplacement de portion      */
    const vmpa2t *addr;                     /* Départ de la portion        */

    range = g_binary_portion_get_range(portion);
    addr = get_mrange_addr(range);

    if (!has_phys_addr(addr))
        result = false;

    else
        result = (addr->physical <= off && off < (addr->physical + range->length));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = couche de portions à parcourir pour les recherches.*
*                off     = position physique à retrouver.                     *
*                pos     = position correspondante. [OUT]                     *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une position physique. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_portion_translate_offset_into_vmpa(const GBinPortion *portion, phys_t off, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    GBinPortion *sub;                       /* Portion incluse à traiter   */
    const mrange_t *range;                  /* Emplacement de portion      */
    const vmpa2t *addr;                     /* Départ de la portion        */

    result = false;

    for (i = 0; i < portion->count; i++)
    {
        sub = portion->subs[i];

        if (!g_binary_portion_contains_physical(sub, off))
            continue;

        result = g_binary_portion_translate_offset_into_vmpa(sub, off, pos);

        break;

    }

    if (i == portion->count)
    {
        result = g_binary_portion_contains_physical(portion, off);

        if (result)
        {
            range = g_binary_portion_get_range(portion);
            addr = get_mrange_addr(range);

            if (has_virt_addr(get_mrange_addr(range)))
                init_vmpa(pos, off, addr->virtual + off - addr->physical);

            else
                init_vmpa(pos, off, VMPA_NO_VIRTUAL);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = portion mère à consulter.                          *
*                virt    = adresse virtuelle du point de recherche.           *
*                                                                             *
*  Description : Détermine si une portion contient une adresse donnée.        *
*                                                                             *
*  Retour      : true ou false selon le résultat.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_portion_contains_virtual(const GBinPortion *portion, virt_t virt)
{
    bool result;                            /* Bilan à retourner           */
    const mrange_t *range;                  /* Emplacement de portion      */
    const vmpa2t *addr;                     /* Départ de la portion        */

    range = g_binary_portion_get_range(portion);
    addr = get_mrange_addr(range);

    if (!has_virt_addr(addr))
        result = false;

    else
        result = (addr->virtual <= virt && virt < (addr->virtual + range->length));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : portion = couche de portions à parcourir pour les recherches.*
*                virt    = adresse virtuelle à retrouver.                     *
*                pos     = position correspondante. [OUT]                     *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une adresse virtuelle. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_portion_translate_address_into_vmpa(const GBinPortion *portion, virt_t virt, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    GBinPortion *sub;                       /* Portion incluse à traiter   */
    const mrange_t *range;                  /* Emplacement de portion      */
    const vmpa2t *addr;                     /* Départ de la portion        */

    result = false;

    for (i = 0; i < portion->count; i++)
    {
        sub = portion->subs[i];

        if (!g_binary_portion_contains_virtual(sub, virt))
            continue;

        result = g_binary_portion_translate_address_into_vmpa(sub, virt, pos);

        break;

    }

    if (i == portion->count)
    {
        result = g_binary_portion_contains_virtual(portion, virt);

        if (result)
        {
            range = g_binary_portion_get_range(portion);
            addr = get_mrange_addr(range);

            if (has_phys_addr(addr) && has_virt_addr(addr))
                init_vmpa(pos, addr->physical + virt - addr->virtual, virt);

            else
                init_vmpa(pos, VMPA_NO_PHYSICAL, virt);

        }

    }

    return result;

}
