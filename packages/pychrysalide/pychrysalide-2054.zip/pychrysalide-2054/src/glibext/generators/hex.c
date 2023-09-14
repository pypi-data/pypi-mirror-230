
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.c - génération à la volée de lignes hexadécimales
 *
 * Copyright (C) 2019 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "hex.h"


#include <assert.h>
#include <ctype.h>


#include "../bufferline.h"
#include "../gbinarycursor.h"
#include "../linegen-int.h"
#include "../linesegment.h"
#include "../../core/columns.h"
#include "../../core/params.h"
#include "../../gtkext/hexdisplay.h"



/* --------------------------- RENDU AMIQUE D'HEXADECIMAL --------------------------- */


/* Tampon pour générateur de lignes hexadécimales (instance) */
struct _GHexGenerator
{
    GObject parent;                         /* A laisser en premier        */

    GBinContent *content;                   /* Contenu à représenter       */

    gint left_start;                        /* Abscisse des impressions    */
    gint padding;                           /* Bourrage supplémentaire     */

    phys_t bytes_per_line;                  /* Nombre d'octets par ligne   */

};

/* Tampon pour générateur de lignes hexadécimales (classe) */
struct _GHexGeneratorClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    gint addr_width;                        /* Largeur des positions       */
    gint byte_width;                        /* Largeur d'un octet brut     */
    gint sep_width;                         /* Largeur de séparation       */
    gint char_width;                        /* Largeur d'un caractère      */

};


/* Procède à l'initialisation d'une classe de générateur. */
static void g_hex_generator_class_init(GHexGeneratorClass *);

/* Procède à l'initialisation d'un générateur de lignes hexa. */
static void g_hex_generator_init(GHexGenerator *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_hex_generator_interface_init(GLineGeneratorInterface *);

/* Supprime toutes les références externes. */
static void g_hex_generator_dispose(GHexGenerator *);

/* Procède à la libération totale de la mémoire. */
static void g_hex_generator_finalize(GHexGenerator *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_hex_generator_count_lines(const GHexGenerator *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_hex_generator_compute_cursor(const GHexGenerator *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_hex_generator_contain_cursor(const GHexGenerator *, size_t, size_t, const GLineCursor *);

#endif

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_hex_generator_get_flags(const GHexGenerator *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_hex_generator_print(GHexGenerator *, GBufferLine *, size_t, size_t);



/* ---------------------------------------------------------------------------------- */
/*                             RENDU AMIQUE D'HEXADECIMAL                             */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du générateur de lignes hexadécimales à la volée. */
G_DEFINE_TYPE_WITH_CODE(GHexGenerator, g_hex_generator, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_hex_generator_interface_init));


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

static void g_hex_generator_class_init(GHexGeneratorClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    line_segment *segment;                  /* Segment de test pour mesure */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_hex_generator_dispose;
    object->finalize = (GObjectFinalizeFunc)g_hex_generator_finalize;

    /* Mesure de quelques dimensions */

    segment = get_new_line_segment(RTT_PHYS_ADDR, "0x00000000", 10);

    class->addr_width = get_line_segment_width(segment);

    release_line_segment(segment);

    segment = get_new_line_segment(RTT_RAW_CODE, "00", 2);

    class->byte_width = get_line_segment_width(segment);

    release_line_segment(segment);

    segment = get_new_line_segment(RTT_RAW_CODE, "\t", 1);

    class->sep_width = get_line_segment_width(segment);

    release_line_segment(segment);

    segment = get_new_line_segment(RTT_RAW_CODE, "0", 1);

    class->char_width = get_line_segment_width(segment);

    release_line_segment(segment);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = composant GLib à initialiser.                    *
*                                                                             *
*  Description : Procède à l'initialisation d'un générateur de lignes hexa.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hex_generator_init(GHexGenerator *generator)
{
    generator->bytes_per_line = 4;

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

static void g_hex_generator_interface_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_hex_generator_count_lines;
#ifdef INCLUDE_GTK_SUPPORT
    iface->compute = (linegen_compute_fc)g_hex_generator_compute_cursor;
    iface->contain = (linegen_contain_fc)g_hex_generator_contain_cursor;
#endif
    iface->get_flags = (linegen_get_flags_fc)g_hex_generator_get_flags;
    iface->print = (linegen_print_fc)g_hex_generator_print;

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

static void g_hex_generator_dispose(GHexGenerator *generator)
{
    if (generator->content != NULL)
        g_object_unref(G_OBJECT(generator->content));

    G_OBJECT_CLASS(g_hex_generator_parent_class)->dispose(G_OBJECT(generator));

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

static void g_hex_generator_finalize(GHexGenerator *generator)
{
    G_OBJECT_CLASS(g_hex_generator_parent_class)->finalize(G_OBJECT(generator));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à représenter partiellement.        *
*                                                                             *
*  Description : Crée un nouveau générateur de lignes hexadécimales.          *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GHexGenerator *g_hex_generator_new(GBinContent *content)
{
    GHexGenerator *result;                  /* Composant à retourner       */

    result = g_object_new(G_TYPE_HEX_GENERATOR, NULL);

    result->content = content;

    g_object_ref(G_OBJECT(result->content));

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

static size_t g_hex_generator_count_lines(const GHexGenerator *generator)
{
    size_t result;                          /* Quantité à retourner        */
    phys_t size;                            /* Taille du contenu binaire   */

    size = g_binary_content_compute_size(generator->content);

    result = size / generator->bytes_per_line;

    if (size % generator->bytes_per_line > 0)
        result++;

    return result;

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

static void g_hex_generator_compute_cursor(const GHexGenerator *generator, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    phys_t phys;                            /* Position physique           */
    GHexGeneratorClass *class;              /* Accès aux informations      */
    phys_t block_count;                     /* Nombre de blocs d'octets    */
    gint bytes_width;                       /* Largeur des octets occupée  */
    phys_t i;                               /* Boucle de parcours          */
    gint requested;                         /* Espace requis pour X octets */
    vmpa2t pos;                             /* Position de la portion      */

    x -= generator->left_start;

    phys = generator->bytes_per_line * index;

    class = G_HEX_GENERATOR_GET_CLASS(generator);

    block_count = (generator->bytes_per_line / 4);

    bytes_width = generator->bytes_per_line * class->byte_width
        + 3 * block_count * class->char_width
        + (block_count > 1 ? block_count - 1 : 0) * class->sep_width;

    if (x <= bytes_width)
    {
        for (i = 1; i <= generator->bytes_per_line; i++)
        {
            block_count = (i / 4);

            requested = i * class->byte_width + (3 * block_count + ((i - 1) % 3)) * class->char_width;
            requested += (block_count > 1 ? block_count - 1 : 0) * class->sep_width;

            if (requested > x)
                break;

            phys++;

        }

    }
    else
    {
        x -= (bytes_width + COL_MARGIN + generator->padding + COL_MARGIN);

        phys += (x / class->char_width);

    }

    init_vmpa(&pos, phys, VMPA_NO_VIRTUAL);

    *cursor = g_binary_cursor_new();
    g_binary_cursor_set_raw(G_BINARY_CURSOR(*cursor), true);

    g_binary_cursor_update(G_BINARY_CURSOR(*cursor), &pos);

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

static int g_hex_generator_contain_cursor(const GHexGenerator *generator, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Bilan d'étude à renvoyer    */
    vmpa2t addr;                            /* Autre emplacement à comparer*/
    vmpa2t pos;                             /* Position de la portion      */
    phys_t length;                          /* Quantité affichable         */
    mrange_t range;                         /* Emplacement associé         */

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    init_vmpa(&pos, generator->bytes_per_line * index, VMPA_NO_VIRTUAL);

    length = g_binary_content_compute_size(generator->content) - get_phy_addr(&pos);

    if (length > generator->bytes_per_line)
        length = generator->bytes_per_line;

    init_mrange(&range, &pos, length);

    result = cmp_mrange_with_vmpa(&range, &addr);

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

static BufferLineFlags g_hex_generator_get_flags(const GHexGenerator *generator, size_t index, size_t repeat)
{
    return BLF_HAS_CODE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à utiliser pour l'impression.         *
*                line      = ligne de rendu à compléter.                      *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hex_generator_print(GHexGenerator *generator, GBufferLine *line, size_t index, size_t repeat)
{
    GGenConfig *config;                     /* Configuration à consulter   */
    bool upper_case;                        /* Casse des données en hexa   */
#ifndef NDEBUG
    bool status;                            /* Bilan de la consultation    */
#endif
    const char *hexa;                       /* Chaîne à considérer #0      */
    const char *ff;                         /* Chaîne à considérer #1      */
    vmpa2t pos;                             /* Position définie à la volée */
    phys_t got;                             /* Quantité affichable         */
    const bin_t *raw;                       /* Accès direct et brut        */
    phys_t i;                               /* Boucle de parcours          */
    bin_t byte;                             /* Copie pour confort          */
    char tmp[2];                            /* Représentation d'un octet   */

    static const char hexa_lower[] = "0123456789abcdef";
    static const char hexa_upper[] = "0123456789ABCDEF";
    static const char ff_lower[] = "ff";
    static const char ff_upper[] = "FF";

    config = get_main_configuration();

#ifndef NDEBUG
    status = g_generic_config_get_value(config, MPK_HEX_UPPER_CASE, &upper_case);
    assert(status);
#else
    g_generic_config_get_value(config, MPK_HEX_UPPER_CASE, &upper_case);
#endif

    if (upper_case)
    {
        hexa = hexa_upper;
        ff = ff_upper;
    }
    else
    {
        hexa = hexa_lower;
        ff = ff_lower;
    }

    /* Position physique */

    init_vmpa(&pos, generator->bytes_per_line * index, VMPA_NO_VIRTUAL);

    g_buffer_line_fill_phys(line, HLC_PHYSICAL, MDS_32_BITS_UNSIGNED, &pos);

    /* Contenu brut */

    got = g_binary_content_compute_size(generator->content) - get_phy_addr(&pos);

    if (got > generator->bytes_per_line)
        got = generator->bytes_per_line;

    raw = g_binary_content_get_raw_access(generator->content, &pos, got);

    for (i = 0; i < got; i++)
    {
        /* Séparation ? */

        if (i > 0)
        {
            if (i % 4 == 0)
                g_buffer_line_append_text(line, HLC_BINARY, "\t", 1, RTT_RAW, NULL);
            else
                g_buffer_line_append_text(line, HLC_BINARY, " ", 1, RTT_RAW, NULL);
        }

        /* Binaire brut */

        byte = raw[i];

        if (byte == 0x00)
            g_buffer_line_append_text(line, HLC_BINARY, "00", 2, RTT_RAW_NULL, NULL);

        else if (byte == 0xff)
            g_buffer_line_append_text(line, HLC_BINARY, ff, 2, RTT_RAW_FULL, NULL);

        else
        {
            tmp[1] = hexa[byte & 0xf];
            tmp[0] = hexa[(byte >> 4) & 0xf];

            g_buffer_line_append_text(line, HLC_BINARY, tmp, 2, RTT_RAW, NULL);

        }

        /* Représentation humaine ? */

        if (isgraph(byte) || byte == ' ')
            g_buffer_line_append_text(line, HLC_TRANSLATION, (char *)raw + i, 1, RTT_PRINTABLE, NULL);
        else
            g_buffer_line_append_text(line, HLC_TRANSLATION, ".", 1, RTT_NOT_PRINTABLE, NULL);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                                                                             *
*  Description : Fournit le contenu associé au générateur de lignes hexa.     *
*                                                                             *
*  Retour      : Contenu dans lequel puise le générateur pour les lignes.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_hex_generator_get_content(const GHexGenerator *generator)
{
    GBinContent *result;                    /* Référence à retourner       */

    result = generator->content;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à ajuster.                            *
*                left      = position de départ à gauche pour le texte.       *
*                show_pos  = affichage des positions sur la gauche ?          *
*                padding   = bourrage entre les colonnes de brut et ASCII.    *
*                width     = largeur maximale disponible.                     *
*                                                                             *
*  Description : Ajuste la génération à une nouvelle largeur de rendu.        *
*                                                                             *
*  Retour      : true si le nombre d'octets par ligne a changé, false sinon.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_hex_generator_auto_fit(GHexGenerator *generator, gint left, bool show_pos, gint padding, gint width)
{
    bool result;                            /* Bilan à faire remonter      */
    GHexGeneratorClass *class;              /* Accès aux informations      */
    phys_t i;                               /* Boucle de parcours          */
    gint requested;                         /* Espace requis pour X octets */
    phys_t block_count;                     /* Nombre de blocs d'octets    */

    class = G_HEX_GENERATOR_GET_CLASS(generator);

    generator->left_start = left;
    generator->padding = padding;

    if (show_pos)
        generator->left_start += class->addr_width + COL_MARGIN;

    for (i = 4; ; i += 4)
    {
        requested = generator->left_start;

        block_count = (i / 4);

        requested += i * class->byte_width + 3 * block_count * class->char_width;
        requested += (block_count > 1 ? block_count - 1 : 0) * class->sep_width;
        requested += COL_MARGIN;

        requested += padding;
        requested += COL_MARGIN;

        requested += i * class->char_width;
        requested += COL_MARGIN;

        /* Limite atteinte ? */
        if (requested > width)
        {
            i -= 4;
            break;
        }

    }

    result = (generator->bytes_per_line != i);

    generator->bytes_per_line = i;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                                                                             *
*  Description : Indique le nombre d'octets programmés constituer une ligne.  *
*                                                                             *
*  Retour      : Nombre d'octets représentés sur chaque ligne.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

phys_t g_hex_generator_get_bytes_per_line(const GHexGenerator *generator)
{
    return generator->bytes_per_line;

}
