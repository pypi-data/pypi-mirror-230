
/* Chrysalide - Outil d'analyse de fichiers binaires
 * mclf.c - prise en compte du format binaire 'MCLF'
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#include "mclf.h"


#include <i18n.h>


#include "mclf-int.h"
#include "symbols.h"



/* Taille maximale d'une description */
#define MAX_PORTION_DESC 256



/* Initialise la classe des formats d'exécutables MCLF. */
static void g_mclf_format_class_init(GMCLFFormatClass *);

/* Initialise une instance de format d'exécutable MCLF. */
static void g_mclf_format_init(GMCLFFormat *);

/* Supprime toutes les références externes. */
static void g_mclf_format_dispose(GMCLFFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_mclf_format_finalize(GMCLFFormat *);

/* Indique la désignation interne du format. */
static char *g_mclf_format_get_key(const GMCLFFormat *);

/* Fournit une description humaine du format. */
static char *g_mclf_format_get_description(const GMCLFFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_mclf_format_analyze(GMCLFFormat *, wgroup_id_t, GtkStatusStack *);

/* Informe quant au boutisme utilisé. */
static SourceEndian g_mclf_format_get_endianness(const GMCLFFormat *);

/* Indique le type d'architecture visée par le format. */
static const char *g_mclf_format_get_target_machine(const GMCLFFormat *);

/* Etend la définition des portions au sein d'un binaire. */
static void g_mclf_format_refine_portions(GMCLFFormat *);



/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à traiter.                         *
*                                                                             *
*  Description : Valide un contenu comme étant un format Mobicore.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_mclf_format(const GBinContent *content)
{
    bool result;                            /* Bilan à faire remonter      */
    vmpa2t addr;                            /* Tête de lecture initiale    */
    char magic[4];                          /* Idenfiant standard          */

    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &addr, 4, (bin_t *)magic);

    if (result)
        result = (memcmp(magic, MC_SERVICE_HEADER_MAGIC_STR, 4) == 0);

    return result;

}


/* Indique le type défini pour un format d'exécutable MCLF. */
G_DEFINE_TYPE(GMCLFFormat, g_mclf_format, G_TYPE_EXE_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables MCLF.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_mclf_format_class_init(GMCLFFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de format connu     */
    GBinFormatClass *fmt;                   /* Version en format basique   */
    GExeFormatClass *exe;                   /* Version en exécutable       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_mclf_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_mclf_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_mclf_format_get_key;
    known->get_desc = (known_get_desc_fc)g_mclf_format_get_description;
    known->analyze = (known_analyze_fc)g_mclf_format_analyze;

    fmt = G_BIN_FORMAT_CLASS(klass);

    fmt->get_endian = (format_get_endian_fc)g_mclf_format_get_endianness;

    exe = G_EXE_FORMAT_CLASS(klass);

    exe->get_machine = (get_target_machine_fc)g_mclf_format_get_target_machine;
    exe->refine_portions = (refine_portions_fc)g_mclf_format_refine_portions;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable MCLF.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_mclf_format_init(GMCLFFormat *format)
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

static void g_mclf_format_dispose(GMCLFFormat *format)
{
    G_OBJECT_CLASS(g_mclf_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_mclf_format_finalize(GMCLFFormat *format)
{
    G_OBJECT_CLASS(g_mclf_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Prend en charge un nouveau format MCLF.                      *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GExeFormat *g_mclf_format_new(GBinContent *content)
{
    GMCLFFormat *result;                    /* Structure à retourner       */

    if (!check_mclf_format(content))
        return NULL;

    result = g_object_new(G_TYPE_MCLF_FORMAT, NULL);

    g_known_format_set_content(G_KNOWN_FORMAT(result), content);

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

static char *g_mclf_format_get_key(const GMCLFFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("mclf");

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

static char *g_mclf_format_get_description(const GMCLFFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("MobiCore Load Format");

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

static bool g_mclf_format_analyze(GMCLFFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GExeFormat *exe;                        /* Autre version du format     */

    result = false;

    exe = G_EXE_FORMAT(format);

    if (!read_mclf_header(format, &format->header, format->endian))
        goto error;

    g_executable_format_setup_portions(exe, status);

    if (!load_mclf_symbols(format))
        goto error;

    result = true;

 error:

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

static SourceEndian g_mclf_format_get_endianness(const GMCLFFormat *format)
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

static const char *g_mclf_format_get_target_machine(const GMCLFFormat *format)
{
    const char *result;                     /* Identifiant à retourner     */

    result = "armv7";

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Etend la définition des portions au sein d'un binaire.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_mclf_format_refine_portions(GMCLFFormat *format)
{
    GExeFormat *exe_format;                 /* Autre version du format     */
    phys_t offset;                          /* Position physique           */
    vmpa2t origin;                          /* Origine d'une définition    */
    vmpa2t addr;                            /* Emplacement dans le binaire */
    GBinPortion *new;                       /* Nouvelle portion définie    */
    char desc[MAX_PORTION_DESC];            /* Description d'une portion   */
    phys_t length;                          /* Taille de portion globale   */

    exe_format = G_EXE_FORMAT(format);

    /* Segment de code */

    offset = sizeof(uint32_t)   /* magic */             \
           + sizeof(uint32_t)   /* version */           \
           + sizeof(uint32_t)   /* flags */             \
           + sizeof(uint32_t)   /* mem_type */          \
           + sizeof(uint32_t)   /* service_type */      \
           + sizeof(uint32_t)   /* num_instances */     \
           + 16                 /* uuid */              \
           + sizeof(uint32_t)   /* driver_id */         \
           + sizeof(uint32_t);  /* num_threads */

    init_vmpa(&origin, offset, VMPA_NO_VIRTUAL);

    init_vmpa(&addr, 0, format->header.v1.text.start);

    new = g_binary_portion_new(BPC_CODE, &addr, format->header.v1.text.len);

    sprintf(desc, "%s \"%s\"", _("Segment"), "text");
    g_binary_portion_set_desc(new, desc);

    g_binary_portion_set_rights(new, PAC_WRITE | PAC_EXEC);

    g_exe_format_include_portion(exe_format, new, &origin);

    /* Segment de données */

    offset += sizeof(uint32_t)  /* start */             \
            + sizeof(uint32_t); /* len */

    init_vmpa(&origin, offset, VMPA_NO_VIRTUAL);

    init_vmpa(&addr, format->header.v1.text.len, format->header.v1.data.start);

    new = g_binary_portion_new(BPC_DATA, &addr, format->header.v1.data.len);

    sprintf(desc, "%s \"%s\"", _("Segment"), "data");
    g_binary_portion_set_desc(new, desc);

    g_binary_portion_set_rights(new, PAC_READ | PAC_WRITE);

    g_exe_format_include_portion(exe_format, new, &origin);

    /* Signature finale */

    length = g_binary_content_compute_size(G_KNOWN_FORMAT(format)->content);

    if (length > 521)
    {
        init_vmpa(&addr, length - 521, VMPA_NO_VIRTUAL);

        new = g_binary_portion_new(BPC_DATA, &addr, 521);

        sprintf(desc, "%s \"%s\"", _("Segment"), "sig");
        g_binary_portion_set_desc(new, desc);

        g_binary_portion_set_rights(new, PAC_READ | PAC_WRITE);

        g_exe_format_include_portion(exe_format, new, NULL);

    }

}
