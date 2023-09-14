
/* Chrysalide - Outil d'analyse de fichiers binaires
 * prologue.c - génération à la volée de délimitations de routines
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


#include "rborder.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../bufferline.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../gbinarycursor.h"
#endif
#include "../linegen-int.h"
#include "../linesegment.h"
#include "../../core/columns.h"



/* -------------------------- MARQUE DE BORDURE DE ROUTINE -------------------------- */


/* Tampon pour générateur de délimitations de routines (instance) */
struct _GBorderGenerator
{
    GObject parent;                         /* A laisser en premier        */

    GCodingLanguage *lang;                  /* Traduction de la sortie     */

    vmpa2t addr;                            /* Position de la limite       */
    bool start;                             /* Début ou fin de routine ?   */

    MemoryDataSize msize;                   /* Taille du bus d'adresses    */

};

/* Tampon pour générateur de délimitations de routines (classe) */
struct _GBorderGeneratorClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


#define ROUTINE_INTRO_MSG "--------------- BEGIN OF PROCEDURE ---------------"

#define ROUTINE_OUTRO_MSG "---------------- END OF PROCEDURE ----------------"


/* Procède à l'initialisation d'une classe de générateur. */
static void g_border_generator_class_init(GBorderGeneratorClass *);

/* Procède à l'initialisation d'un générateur de délimitations. */
static void g_border_generator_init(GBorderGenerator *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_border_generator_interface_init(GLineGeneratorInterface *);

/* Supprime toutes les références externes. */
static void g_border_generator_dispose(GBorderGenerator *);

/* Procède à la libération totale de la mémoire. */
static void g_border_generator_finalize(GBorderGenerator *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_border_generator_count_lines(const GBorderGenerator *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_border_generator_compute_cursor(const GBorderGenerator *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_border_generator_contain_cursor(const GBorderGenerator *, size_t, size_t, const GLineCursor *);

#endif

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_border_generator_get_flags(const GBorderGenerator *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_border_generator_print(GBorderGenerator *, GBufferLine *, size_t, size_t, const GBinContent *);



/* ---------------------------------------------------------------------------------- */
/*                            MARQUE DE BORDURE DE ROUTINE                            */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du générateur de délimitations de routines à la volée. */
G_DEFINE_TYPE_WITH_CODE(GBorderGenerator, g_border_generator, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_border_generator_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GLib à initialiser.              *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de générateur.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_border_generator_class_init(GBorderGeneratorClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_border_generator_dispose;
    object->finalize = (GObjectFinalizeFunc)g_border_generator_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = composant GLib à initialiser.                    *
*                                                                             *
*  Description : Procède à l'initialisation d'un générateur de délimitations. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_border_generator_init(GBorderGenerator *generator)
{

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

static void g_border_generator_interface_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_border_generator_count_lines;
#ifdef INCLUDE_GTK_SUPPORT
    iface->compute = (linegen_compute_fc)g_border_generator_compute_cursor;
    iface->contain = (linegen_contain_fc)g_border_generator_contain_cursor;
#endif
    iface->get_flags = (linegen_get_flags_fc)g_border_generator_get_flags;
    iface->print = (linegen_print_fc)g_border_generator_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_border_generator_dispose(GBorderGenerator *generator)
{
    g_object_unref(G_OBJECT(generator->lang));

    G_OBJECT_CLASS(g_border_generator_parent_class)->dispose(G_OBJECT(generator));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_border_generator_finalize(GBorderGenerator *generator)
{
    G_OBJECT_CLASS(g_border_generator_parent_class)->finalize(G_OBJECT(generator));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang  = trauducteur pour l'impression finale.                *
*                addr  = position correspondant à la délimitation à marquer.  *
*                start = indique le type de délimitation observée.            *
*                msize = taille des adresses représentées.                    *
*                                                                             *
*  Description : Crée un nouveau générateur de délimitations de routines.     *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBorderGenerator *g_border_generator_new(GCodingLanguage *lang, const vmpa2t *addr, bool start, MemoryDataSize msize)
{
    GBorderGenerator *result;                  /* Composant à retourner       */

    result = g_object_new(G_TYPE_BORDER_GENERATOR, NULL);

    result->lang = lang;
    g_object_ref(G_OBJECT(lang));

    copy_vmpa(&result->addr, addr);
    result->start = start;

    result->msize = msize;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          OFFRE DE CAPACITES DE GENERATION                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_border_generator_count_lines(const GBorderGenerator *generator)
{
    return 3;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                x         = position géographique sur la ligne concernée.    *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                cursor    = emplacement à constituer. [OUT]                  *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_border_generator_compute_cursor(const GBorderGenerator *generator, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    *cursor = g_binary_cursor_new();

    g_binary_cursor_update(G_BINARY_CURSOR(*cursor), &generator->addr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                cursor    = emplacement à analyser.                          *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_border_generator_contain_cursor(const GBorderGenerator *generator, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Conclusion à retourner      */
    vmpa2t addr;                            /* Autre emplacement à comparer*/

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    result = cmp_vmpa(&addr, &generator->addr);

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BufferLineFlags g_border_generator_get_flags(const GBorderGenerator *generator, size_t index, size_t repeat)
{
    return BLF_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à utiliser pour l'impression.         *
*                line      = ligne de rendu à compléter.                      *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                content   = éventuel contenu binaire brut à imprimer.        *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_border_generator_print(GBorderGenerator *generator, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    char *text;                             /* Texte principal à insérer   */

    assert(repeat < 3);

    g_buffer_line_fill_phys(line, DLC_PHYSICAL, generator->msize, &generator->addr);

    g_buffer_line_fill_virt(line, DLC_VIRTUAL, generator->msize, &generator->addr);

    if (repeat == 1)
    {
        text = strdup(generator->start ? ROUTINE_INTRO_MSG : ROUTINE_OUTRO_MSG);
        g_coding_language_encapsulate_comment(generator->lang, &text);

        g_buffer_line_start_merge_at(line, DLC_ASSEMBLY_LABEL);
        g_buffer_line_append_text(line, DLC_ASSEMBLY_LABEL, SL(text), RTT_COMMENT, NULL);

        free(text);

    }

}
