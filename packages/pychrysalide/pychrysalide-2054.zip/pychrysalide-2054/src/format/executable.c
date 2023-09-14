
/* Chrysalide - Outil d'analyse de fichiers binaires
 * executable.c - support des formats d'exécutables
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#include "executable.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>


#include <i18n.h>


#include "executable-int.h"
#include "format.h"
#include "../core/logs.h"
#include "../plugins/pglist.h"



/* Initialise la classe des formats d'exécutables génériques. */
static void g_executable_format_class_init(GExeFormatClass *);

/* Initialise une instance de format d'exécutable générique. */
static void g_executable_format_init(GExeFormat *);

/* Supprime toutes les références externes. */
static void g_executable_format_dispose(GExeFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_executable_format_finalize(GExeFormat *);



/* Indique le type défini pour un format d'exécutable générique. */
G_DEFINE_TYPE(GExeFormat, g_executable_format, G_TYPE_BIN_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables génériques.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_executable_format_class_init(GExeFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_executable_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_executable_format_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable générique.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_executable_format_init(GExeFormat *format)
{
    g_mutex_init(&format->mutex);

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

static void g_executable_format_dispose(GExeFormat *format)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < format->debugs_count; i++)
        g_clear_object(&format->debugs[i]);

    for (i = 0; i < format->user_count; i++)
        g_clear_object(&format->user_portions[i]);

    g_clear_object(&format->portions);

    g_mutex_clear(&format->mutex);

    G_OBJECT_CLASS(g_executable_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_executable_format_finalize(GExeFormat *format)
{
    if (format->debugs != NULL)
        free(format->debugs);

    if (format->user_portions != NULL)
        free(format->user_portions);

    G_OBJECT_CLASS(g_executable_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à compléter.                  *
*                info   = informations de débogage à lier.                    *
*                                                                             *
*  Description : Rajoute des informations de débogage à un exécutable.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_exe_format_add_debug_info(GExeFormat *format, GDbgFormat *info)
{
    const char *desc;                       /* Description humaine associée*/

    desc = g_known_format_get_description(G_KNOWN_FORMAT(info));

    if (desc == NULL)
        log_simple_message(LMT_WARNING, _("Unnamed debug information"));
    else
        log_variadic_message(LMT_INFO, _("Found debug information: %s"), desc);

    format->debugs = realloc(format->debugs, ++format->debugs_count * sizeof(GDbgFormat *));

    format->debugs[format->debugs_count - 1] = info;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Compte le nombre de formats de débogage liés à l'exécutable. *
*                                                                             *
*  Retour      : Nombre de formats de débogage attachés.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_exe_format_count_debug_info(const GExeFormat *format)
{
    return format->debugs_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                index  = indice des informations à transmettre.              *
*                                                                             *
*  Description : Fournit un format de débogage attaché à l'exécutable.        *
*                                                                             *
*  Retour      : Informations de débogage attachées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbgFormat *g_exe_format_get_debug_info(const GExeFormat *format, size_t index)
{
    GDbgFormat *result;                     /* Format à retourner          */

    if (index >= format->debugs_count)
        result = NULL;

    else
    {
        result = format->debugs[index];
        g_object_ref(G_OBJECT(result));
    }

    return result;

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

const char *g_exe_format_get_target_machine(const GExeFormat *format)
{
    return G_EXE_FORMAT_GET_CLASS(format)->get_machine(format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse principale trouvée si possible. [OUT]       *
*                                                                             *
*  Description : Fournit l'adresse principale associée à un format.           *
*                                                                             *
*  Retour      : Bilan des recherches.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_get_main_address(GExeFormat *format, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *base;                       /* Version d'instance parente  */

    result = false;

    if (G_EXE_FORMAT_GET_CLASS(format)->get_main_addr != NULL)
        result = G_EXE_FORMAT_GET_CLASS(format)->get_main_addr(format, addr);

    if (!result)
    {
        base = G_BIN_FORMAT(format);

        g_rw_lock_reader_lock(&base->pt_lock);

        if (base->pt_count[DPL_ENTRY_POINT] > 0)
            result = g_exe_format_translate_address_into_vmpa(format, base->start_points[DPL_ENTRY_POINT][0], addr);

        g_rw_lock_reader_unlock(&base->pt_lock);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à traiter.                                 *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Crée les portions potentiellement utiles aux traductions.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_executable_format_setup_portions(GExeFormat *format, GtkStatusStack *status)
{
    vmpa2t addr;                            /* Emplacement vide de sens    */
    phys_t length;                          /* Taille de portion globale   */
    GExeFormatClass *class;                 /* Classe de l'instance        */
    size_t i;                               /* Boucle de parcours          */

    /**
     * Avant de lire l'entête du format, on ne sait pas où on se trouve !
     */
    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    length = g_binary_content_compute_size(G_KNOWN_FORMAT(format)->content);

    format->portions = g_binary_portion_new(BPC_RAW, &addr, length);

    class = G_EXE_FORMAT_GET_CLASS(format);

    if (class->refine_portions != NULL)
        class->refine_portions(format);

    for (i = 0; i < format->user_count; i++)
    {
        g_object_ref(G_OBJECT(format->user_portions[i]));
        g_exe_format_include_portion(format, format->user_portions[i], NULL);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à traiter.                                 *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Effectue les ultimes opérations de chargement d'un binaire.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_executable_format_complete_loading(GExeFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t count;                           /* Qté d'infos supplémentaires */
    size_t i;                               /* Boucle de parcours          */
    GDbgFormat *dbg;                        /* Informations de débogage    */

    result = true;

    attach_debug_format(format);

    count = g_exe_format_count_debug_info(format);

    for (i = 0; i < count && result; i++)
    {
        dbg = g_exe_format_get_debug_info(format, i);

        result = g_known_format_analyze(G_KNOWN_FORMAT(dbg), gid, status);

        g_object_unref(G_OBJECT(dbg));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à modifier.            *
*                portion = portion à inclure dans les définitions du format.  *
*                                                                             *
*  Description : Enregistre une portion artificielle pour le format.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_exe_format_register_user_portion(GExeFormat *format, GBinPortion *portion)
{
    g_mutex_lock(&format->mutex);

    format->user_portions = realloc(format->user_portions, ++format->user_count * sizeof(GBinPortion *));

    format->user_portions[format->user_count - 1] = portion;

    g_mutex_unlock(&format->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à modifier.            *
*                portion = portion à inclure dans les définitions du format.  *
*                origin  = source de définition de la portion fournie.        *
*                                                                             *
*  Description : Procède à l'enregistrement d'une portion dans un format.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_exe_format_include_portion(GExeFormat *format, GBinPortion *portion, const vmpa2t *origin)
{
    phys_t available;                       /* Taille totale du bianire    */
    const mrange_t *range;                  /* Emplacement de la portion   */
    phys_t start;                           /* Début de zone de la portion */
    vmpa2t no_origin;                       /* Emplacement inconnu         */
    char *msg;                              /* Description d'une erreur    */
    phys_t remaining;                       /* Taille maximale envisageable*/
    bool truncated;                         /* Modification faite ?        */

    available = g_binary_content_compute_size(G_KNOWN_FORMAT(format)->content);

    range = g_binary_portion_get_range(portion);

    start = get_phy_addr(get_mrange_addr(range));

    if (get_mrange_length(range) == 0)
    {
        log_variadic_message(LMT_BAD_BINARY, _("The binary portion '%s' is empty and thus useless... Discarding!"),
                             g_binary_portion_get_desc(portion));

        g_object_unref(G_OBJECT(portion));

    }

    else if (start >= available)
    {
        if (origin == NULL)
        {
            init_vmpa(&no_origin, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);
            origin = &no_origin;
        }

        asprintf(&msg, _("Defined binary portion '%s' is out of the file scope... Discarding!"),
                 g_binary_portion_get_desc(portion));

        g_binary_format_add_error(G_BIN_FORMAT(format), BFE_STRUCTURE, origin, msg);

        free(msg);

        g_object_unref(G_OBJECT(portion));

    }

    else
    {
        remaining = available - start;

        truncated = g_binary_portion_limit_range(portion, remaining);

        if (truncated)
            log_variadic_message(LMT_BAD_BINARY, _("Truncated binary portion '%s' to fit the binary content size!"),
                                 g_binary_portion_get_desc(portion));

        g_mutex_lock(&format->mutex);

        g_binary_portion_include(format->portions, portion);

        g_mutex_unlock(&format->mutex);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Fournit la première couche des portions composent le binaire.*
*                                                                             *
*  Retour      : Arborescence des différentes portions binaires.              *
*                                                                             *
*  Remarques   : Le compteur de références de l'instance renvoyée doit être   *
*                décrémenté après usage.                                      *
*                                                                             *
******************************************************************************/

GBinPortion *g_exe_format_get_portions(GExeFormat *format)
{
    GBinPortion *result;                    /* Instance à retourner        */

    g_mutex_lock(&format->mutex);

    result = format->portions;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    g_mutex_unlock(&format->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                off    = position physique à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une position physique. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_translate_offset_into_vmpa(GExeFormat *format, phys_t off, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = G_EXE_FORMAT_GET_CLASS(format)->translate_phys(format, off, pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse virtuelle à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une adresse virtuelle. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_translate_address_into_vmpa(GExeFormat *format, virt_t addr, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = G_EXE_FORMAT_GET_CLASS(format)->translate_virt(format, addr, pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                name   = nom de la section recherchée.                       *
*                range  = emplacement en mémoire à renseigner. [OUT]          *
*                                                                             *
*  Description : Fournit l'emplacement d'une section donnée.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_exe_format_get_section_range_by_name(const GExeFormat *format, const char *name, mrange_t *range)
{
    bool result;                            /* Bilan à retourner           */
    GExeFormatClass *class;                 /* Classe de l'instance        */

    class = G_EXE_FORMAT_GET_CLASS(format);

    if (class->get_range_by_name == NULL)
        result = false;

    else
        result = class->get_range_by_name(format, name, range);

    return result;

}
