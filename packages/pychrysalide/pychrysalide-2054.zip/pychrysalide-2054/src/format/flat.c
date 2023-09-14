
/* Chrysalide - Outil d'analyse de fichiers binaires
 * flat.c - support des formats à plat
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "flat.h"


#include <malloc.h>
#include <string.h>


#include "flat-int.h"



/* Initialise la classe des formats d'exécutables à plat. */
static void g_flat_format_class_init(GFlatFormatClass *);

/* Initialise une instance de format d'exécutable à plat. */
static void g_flat_format_init(GFlatFormat *);

/* Supprime toutes les références externes. */
static void g_flat_format_dispose(GFlatFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_flat_format_finalize(GFlatFormat *);

/* Indique la désignation interne du format. */
static char *g_flat_format_get_key(const GFlatFormat *);

/* Fournit une description humaine du format. */
static char *g_flat_format_get_description(const GFlatFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_flat_format_analyze(GFlatFormat *, wgroup_id_t, GtkStatusStack *);

/* Informe quant au boutisme utilisé. */
static SourceEndian g_flat_format_get_endianness(const GFlatFormat *);

/* Indique le type d'architecture visée par le format. */
static const char *g_flat_format_get_target_machine(const GFlatFormat *);

/* Fournit l'adresse principale associée à un format à plat. */
static bool g_flat_format_get_main_address(GFlatFormat *, vmpa2t *);



/* Indique le type défini pour un format d'exécutable à plat. */
G_DEFINE_TYPE(GFlatFormat, g_flat_format, G_TYPE_EXE_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables à plat.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_flat_format_class_init(GFlatFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de format connu     */
    GBinFormatClass *fmt;                   /* Version en format basique   */
    GExeFormatClass *exe;                   /* Version en exécutable       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_flat_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_flat_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_flat_format_get_key;
    known->get_desc = (known_get_desc_fc)g_flat_format_get_description;

    known->analyze = (known_analyze_fc)g_flat_format_analyze;

    fmt = G_BIN_FORMAT_CLASS(klass);

    fmt->get_endian = (format_get_endian_fc)g_flat_format_get_endianness;

    exe = G_EXE_FORMAT_CLASS(klass);

    exe->get_machine = (get_target_machine_fc)g_flat_format_get_target_machine;
    exe->get_main_addr = (get_main_addr_fc)g_flat_format_get_main_address;

    exe->translate_phys = (translate_phys_fc)g_exe_format_translate_offset_into_vmpa_using_portions;
    exe->translate_virt = (translate_virt_fc)g_exe_format_translate_address_into_vmpa_using_portions;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable à plat.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_flat_format_init(GFlatFormat *format)
{
    format->machine = NULL;
    format->endian = SRE_LITTLE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_flat_format_dispose(GFlatFormat *format)
{
    G_OBJECT_CLASS(g_flat_format_parent_class)->dispose(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_flat_format_finalize(GFlatFormat *format)
{
    if (format->machine != NULL)
        free(format->machine);

    G_OBJECT_CLASS(g_flat_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Prend en charge un nouveau format à plat.                    *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GExeFormat *g_flat_format_new(GBinContent *content, const char *machine, SourceEndian endian)
{
    GFlatFormat *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_FLAT_FORMAT, NULL);

    g_known_format_set_content(G_KNOWN_FORMAT(result), content);

    result->machine = strdup(machine);
    result->endian = endian;

    return G_EXE_FORMAT(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Indique la désignation interne du format.                    *
*                                                                             *
*  Retour      : Désignation du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_flat_format_get_key(const GFlatFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("flat");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Fournit une description humaine du format.                   *
*                                                                             *
*  Retour      : Description du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_flat_format_get_description(const GFlatFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("Flat executable format");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure l'interprétation d'un format en différé.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_flat_format_analyze(GFlatFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    g_executable_format_setup_portions(G_EXE_FORMAT(format), status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Informe quant au boutisme utilisé.                           *
*                                                                             *
*  Retour      : Indicateur de boutisme.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static SourceEndian g_flat_format_get_endianness(const GFlatFormat *format)
{
    return format->endian;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Indique le type d'architecture visée par le format.          *
*                                                                             *
*  Retour      : Identifiant de l'architecture ciblée par le format.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_flat_format_get_target_machine(const GFlatFormat *format)
{
    const char *result;                     /* Identifiant à retourner     */

    result = format->machine;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse principale trouvée si possible. [OUT]       *
*                                                                             *
*  Description : Fournit l'adresse principale associée à un format à plat.    *
*                                                                             *
*  Retour      : Bilan des recherches.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_flat_format_get_main_address(GFlatFormat *format, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *base;                       /* Format de base du format    */

    base = G_BIN_FORMAT(format);

    g_rw_lock_reader_lock(&base->pt_lock);

    result = (base->pt_count[DPL_ENTRY_POINT] > 0);

    if (result)
        init_vmpa(addr, 0, base->start_points[DPL_ENTRY_POINT][0]);

    g_rw_lock_reader_unlock(&base->pt_lock);

    return result;

}
