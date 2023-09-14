
/* Chrysalide - Outil d'analyse de fichiers binaires
 * prologue.c - génération à la volée de lignes d'introduction
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


#include "prologue.h"


#include <assert.h>
#include <malloc.h>


#include "../bufferline.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../gbinarycursor.h"
#endif
#include "../linegen-int.h"
#include "../linesegment.h"
#include "../../core/columns.h"
#include "../../format/executable.h"



/* ------------------------- MARQUE D'INTRODUCTION DE RENDU ------------------------- */


/* Tampon pour générateur de lignes en prologue (instance) */
struct _GIntroGenerator
{
    GObject parent;                         /* A laisser en premier        */

    vmpa2t addr;                            /* Position première           */

    char **text;                            /* Lignes brutes à représenter */
    size_t count;                           /* Quantité de ces lignes      */

};

/* Tampon pour générateur de lignes en prologue (classe) */
struct _GIntroGeneratorClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Procède à l'initialisation d'une classe de générateur. */
static void g_intro_generator_class_init(GIntroGeneratorClass *);

/* Procède à l'initialisation d'un générateur de lignes d'intro. */
static void g_intro_generator_init(GIntroGenerator *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_intro_generator_interface_init(GLineGeneratorInterface *);

/* Supprime toutes les références externes. */
static void g_intro_generator_dispose(GIntroGenerator *);

/* Procède à la libération totale de la mémoire. */
static void g_intro_generator_finalize(GIntroGenerator *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_intro_generator_count_lines(const GIntroGenerator *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_intro_generator_compute_cursor(const GIntroGenerator *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_intro_generator_contain_cursor(const GIntroGenerator *, size_t, size_t, const GLineCursor *);

#endif

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_intro_generator_get_flags(const GIntroGenerator *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_intro_generator_print(GIntroGenerator *, GBufferLine *, size_t, size_t, const GBinContent *);



/* ---------------------------------------------------------------------------------- */
/*                           MARQUE D'INTRODUCTION DE RENDU                           */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du générateur de lignes d'introduction à la volée. */
G_DEFINE_TYPE_WITH_CODE(GIntroGenerator, g_intro_generator, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_intro_generator_interface_init));


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

static void g_intro_generator_class_init(GIntroGeneratorClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_intro_generator_dispose;
    object->finalize = (GObjectFinalizeFunc)g_intro_generator_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = composant GLib à initialiser.                    *
*                                                                             *
*  Description : Procède à l'initialisation d'un générateur de lignes d'intro.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_intro_generator_init(GIntroGenerator *generator)
{
    generator->text = NULL;
    generator->count = 0;

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

static void g_intro_generator_interface_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_intro_generator_count_lines;
#ifdef INCLUDE_GTK_SUPPORT
    iface->compute = (linegen_compute_fc)g_intro_generator_compute_cursor;
    iface->contain = (linegen_contain_fc)g_intro_generator_contain_cursor;
#endif
    iface->get_flags = (linegen_get_flags_fc)g_intro_generator_get_flags;
    iface->print = (linegen_print_fc)g_intro_generator_print;

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

static void g_intro_generator_dispose(GIntroGenerator *generator)
{
    G_OBJECT_CLASS(g_intro_generator_parent_class)->dispose(G_OBJECT(generator));

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

static void g_intro_generator_finalize(GIntroGenerator *generator)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < generator->count; i++)
        free(generator->text[i]);

    if (generator->text != NULL)
        free(generator->text);

    G_OBJECT_CLASS(g_intro_generator_parent_class)->finalize(G_OBJECT(generator));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang  = trauducteur pour l'impression finale.                *
*                text  = tableau de lignes à conserver.                       *
*                count = taille du tableau fourni.                            *
*                                                                             *
*  Description : Crée un nouveau générateur de lignes d'introduction.         *
*                                                                             *
*  Retour      : Composant GLib créé ou NULL en cas d'échec.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GIntroGenerator *g_intro_generator_new(const GBinFormat *format, const GCodingLanguage *lang, char **text, size_t count)
{
    GIntroGenerator *result;                /* Composant à retourner       */
    vmpa2t first;                           /* Première position           */

    if (!g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), 0, &first))
    {
        /**
         * Dans les faits, le premier octet d'en-tête est toujours chargé en mémoire
         * (du moins chez les ELF).
         *
         * Cependant, il s'agit plus d'une facilité que d'une contrainte. Donc rien
         * n'empêcherait la position 0 de ne pas avoir de correspondance en mémoire
         * virtuelle.
         *
         * Dans tous les cas, la mise en place d'un prologue est attendue, et on ne
         * peut donc pas échouer ici, que la correspondance existe ou non. On fait
         * ainsi avec le peu qu'on sait.
         */

        init_vmpa(&first, 0, VMPA_NO_VIRTUAL);

    }

    result = g_object_new(G_TYPE_INTRO_GENERATOR, NULL);

    copy_vmpa(&result->addr, &first);

    result->text = text;
    result->count = count;

    g_coding_language_encapsulate_comments(lang, &result->text, &result->count);

    result->text = (char **)realloc(result->text, ++result->count * sizeof(char *));

    result->text[result->count - 1] = NULL;

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

static size_t g_intro_generator_count_lines(const GIntroGenerator *generator)
{
    return generator->count;

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

static void g_intro_generator_compute_cursor(const GIntroGenerator *generator, gint x, size_t index, size_t repeat, GLineCursor **cursor)
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

static int g_intro_generator_contain_cursor(const GIntroGenerator *generator, size_t index, size_t repeat, const GLineCursor *cursor)
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

static BufferLineFlags g_intro_generator_get_flags(const GIntroGenerator *generator, size_t index, size_t repeat)
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

static void g_intro_generator_print(GIntroGenerator *generator, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    assert(repeat < generator->count);

    if ((repeat + 1) != generator->count)
    {
        g_buffer_line_start_merge_at(line, DLC_PHYSICAL);

        g_buffer_line_append_text(line, DLC_PHYSICAL, SL(generator->text[repeat]), RTT_COMMENT, NULL);

        if (repeat == 0)
            g_buffer_line_add_flag(line, BLF_WIDTH_MANAGER);

    }

}
