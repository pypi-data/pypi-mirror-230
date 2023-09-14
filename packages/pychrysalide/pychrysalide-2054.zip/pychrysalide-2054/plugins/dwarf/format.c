
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dwarf.c - support du format Dwarf
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


#include "format.h"


#include <i18n.h>
#include <common/cpp.h>
#include <format/format.h>


#include "def.h"
#include "format-int.h"
#include "info.h"
#include "utils.h"



/* Initialise la classe des formats de débogage DWARF. */
static void g_dwarf_format_class_init(GDwarfFormatClass *);

/* Initialise une instance de format de débogage DWARF. */
static void g_dwarf_format_init(GDwarfFormat *);

/* Supprime toutes les références externes. */
static void g_dwarf_format_dispose(GDwarfFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_dwarf_format_finalize(GDwarfFormat *);

/* Indique la désignation interne du format. */
static char *g_dwarf_format_get_key(const GDwarfFormat *);

/* Fournit une description humaine du format. */
static char *g_dwarf_format_get_description(const GDwarfFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_dwarf_format_analyze(GDwarfFormat *, wgroup_id_t, GtkStatusStack *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = exécutable auquel on peut tenter de se raccrocher.  *
*                                                                             *
*  Description : Valide un contenu comme étant un format Dwarf.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbgFormat *check_dwarf_format(GExeFormat *format)
{
    GDbgFormat *result;                     /* Eventuel format à renvoyer  */
    bool matched;                           /* Correspondance probable     */
    size_t i;                               /* Boucle de parcours #1       */

    static const char *section_names[] = {
        ".debug_abbrev",
        ".debug_info"
    };

    matched = true;

    for (i = 0; i < ARRAY_SIZE(section_names) && matched; i++)
        matched = g_exe_format_get_section_range_by_name(format, section_names[i], UNUSED_MRANGE_PTR);

    if (matched)
        result = g_dwarf_format_new(format);
    else
        result = NULL;

    return result;

}


/* Indique le type défini pour un format de débogage générique. */
G_DEFINE_TYPE(GDwarfFormat, g_dwarf_format, G_TYPE_DBG_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats de débogage DWARF.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dwarf_format_class_init(GDwarfFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de format connu     */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dwarf_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dwarf_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_dwarf_format_get_key;
    known->get_desc = (known_get_desc_fc)g_dwarf_format_get_description;
    known->analyze = (known_analyze_fc)g_dwarf_format_analyze;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format de débogage DWARF.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dwarf_format_init(GDwarfFormat *format)
{

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

static void g_dwarf_format_dispose(GDwarfFormat *format)
{
    G_OBJECT_CLASS(g_dwarf_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_dwarf_format_finalize(GDwarfFormat *format)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < format->info_count; i++)
        if (format->info[i] != NULL)
            delete_dwarf_die(format->info[i]);

    if (format->info != NULL)
        free(format->info);

    G_OBJECT_CLASS(g_dwarf_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent  = éventuel format exécutable déjà chargé.            *
                                                                              *
*  Description : Prend en charge un nouveau format DWARF.                     *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbgFormat *g_dwarf_format_new(GExeFormat *parent)
{
    GDwarfFormat *result;                   /* Structure à retourner       */
    GBinContent *content;                   /* Contenu binaire à lire      */

    result = g_object_new(G_TYPE_DWARF_FORMAT, NULL);

    g_debuggable_format_attach_executable(G_DBG_FORMAT(result), parent);

    content = G_KNOWN_FORMAT(parent)->content;

    G_KNOWN_FORMAT(result)->content = content;
    g_object_ref(G_OBJECT(content));

    return G_DBG_FORMAT(result);

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

static char *g_dwarf_format_get_key(const GDwarfFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("dwarf");

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

static char *g_dwarf_format_get_description(const GDwarfFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("DWARF Debugging Information Format");

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

static bool g_dwarf_format_analyze(GDwarfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */

    result = load_dwarf_debug_information(format, gid, status);

    return result;

}
