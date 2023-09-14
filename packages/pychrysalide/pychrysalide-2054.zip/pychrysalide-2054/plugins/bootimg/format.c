
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.h - support du format BOOT.img
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "format.h"


#include <string.h>


#include <i18n.h>
#include <analysis/contents/memory.h>


#include "format-int.h"



/* Initialise la classe des formats d'exécutables ELF. */
static void g_bootimg_format_class_init(GBootImgFormatClass *);

/* Initialise une instance de format d'exécutable ELF. */
static void g_bootimg_format_init(GBootImgFormat *);

/* Supprime toutes les références externes. */
static void g_bootimg_format_dispose(GBootImgFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_bootimg_format_finalize(GBootImgFormat *);

/* Indique la désignation interne du format. */
static char *g_bootimg_format_get_key(const GBootImgFormat *);

/* Fournit une description humaine du format. */
static char *g_bootimg_format_get_description(const GBootImgFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_bootimg_format_analyze(GBootImgFormat *, wgroup_id_t, GtkStatusStack *);



/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à traiter.                         *
*                                                                             *
*  Description : Valide un contenu comme étant un format Elf.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_bootimg_format(const GBinContent *content)
{
    bool result;                            /* Bilan à faire remonter      */
    vmpa2t addr;                            /* Tête de lecture initiale    */
    char magic[BOOT_MAGIC_SIZE];            /* Idenfiant standard          */

    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &addr, BOOT_MAGIC_SIZE, (bin_t *)magic);

    if (result)
        result = (memcmp(magic, BOOT_MAGIC, BOOT_MAGIC_SIZE) == 0);

    return result;

}


/* Indique le type défini pour un format d'image BOOT.img. */
G_DEFINE_TYPE(GBootImgFormat, g_bootimg_format, G_TYPE_KNOWN_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables ELF.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bootimg_format_class_init(GBootImgFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_bootimg_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_bootimg_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_bootimg_format_get_key;
    known->get_desc = (known_get_desc_fc)g_bootimg_format_get_description;
    known->analyze = (known_analyze_fc)g_bootimg_format_analyze;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable ELF.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bootimg_format_init(GBootImgFormat *format)
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

static void g_bootimg_format_dispose(GBootImgFormat *format)
{
    G_OBJECT_CLASS(g_bootimg_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_bootimg_format_finalize(GBootImgFormat *format)
{
    G_OBJECT_CLASS(g_bootimg_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Prend en charge un nouveau format ELF.                       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBootImgFormat *g_bootimg_format_new(GBinContent *content)
{
    GBootImgFormat *result;                     /* Structure à retourner       */

    if (!check_bootimg_format(content))
        return NULL;

    result = g_object_new(G_TYPE_BOOTIMG_FORMAT, NULL);

    g_known_format_set_content(G_KNOWN_FORMAT(result), content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format à consulter.                  *
*                                                                             *
*  Description : Indique la désignation interne du format.                    *
*                                                                             *
*  Retour      : Désignation du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_bootimg_format_get_key(const GBootImgFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("bootimg");

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

static char *g_bootimg_format_get_description(const GBootImgFormat *format)
{
    char *result;                           /* Description à retourner     */

    result = strdup("Android Boot Image");

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

static bool g_bootimg_format_analyze(GBootImgFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */

    result = read_bootimg_header(format, &format->header);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Présente l'entête BOOT.img du format chargé.                 *
*                                                                             *
*  Retour      : Pointeur vers la description principale.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const boot_img_hdr *g_bootimg_format_get_header(const GBootImgFormat *format)
{
    const boot_img_hdr *result;             /* Structure à retourner       */

    result = &format->header;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Fournit le noyau inclus dans une image de démarrage.         *
*                                                                             *
*  Retour      : Nouveau contenu binaire ou NULL en cas d'absence.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_bootimg_format_get_kernel(const GBootImgFormat *format)
{
    GBinContent *result;                    /* Contenu à renvoyer          */
    phys_t offset;                          /* Départ de la zone à traiter */
    phys_t size;                            /* Taille de la zone à traiter */
    vmpa2t pos;                             /* Position de lecture         */
    GBinContent *content;                   /* Contenu binaire à lire      */
    const bin_t *data;                      /* Donnée du contenu nouveau   */

    result = NULL;

    if (format->header.kernel_addr == 0) goto no_kernel;

    offset = 1 * format->header.page_size;

    size = format->header.kernel_size;

    init_vmpa(&pos, offset, VMPA_NO_VIRTUAL);

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    data = g_binary_content_get_raw_access(content, &pos, size);
    if (data == NULL) goto no_data;

    result = g_memory_content_new(data, size);

 no_data:

    g_object_unref(G_OBJECT(content));

 no_kernel:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Fournit le disque en RAM inclus dans une image de démarrage. *
*                                                                             *
*  Retour      : Nouveau contenu binaire ou NULL en cas d'absence.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_bootimg_format_get_ramdisk(const GBootImgFormat *format)
{
    GBinContent *result;                    /* Contenu à renvoyer          */
    phys_t offset;                          /* Départ de la zone à traiter */
    phys_t size;                            /* Taille de la zone à traiter */
    vmpa2t pos;                             /* Position de lecture         */
    GBinContent *content;                   /* Contenu binaire à lire      */
    const bin_t *data;                      /* Donnée du contenu nouveau   */

    result = NULL;

    if (format->header.ramdisk_addr == 0) goto no_ramdisk;

    offset = format->header.kernel_size / format->header.page_size;

    if (format->header.kernel_size % format->header.page_size != 0)
        offset++;

    offset = (1 + offset) * format->header.page_size;

    size = format->header.ramdisk_size;

    init_vmpa(&pos, offset, VMPA_NO_VIRTUAL);

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    data = g_binary_content_get_raw_access(content, &pos, size);
    if (data == NULL) goto no_data;

    result = g_memory_content_new(data, size);

 no_data:

    g_object_unref(G_OBJECT(content));

 no_ramdisk:

    return result;

}
