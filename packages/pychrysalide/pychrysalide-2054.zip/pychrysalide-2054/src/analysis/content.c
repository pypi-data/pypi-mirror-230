
/* Chrysalide - Outil d'analyse de fichiers binaires
 * content.c - lecture de données binaires quelconques
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "content.h"


#include <assert.h>
#include <string.h>


#include <i18n.h>


#include "content-int.h"



/* Procède à l'initialisation de l'interface de rassemblement. */
static void g_binary_content_default_init(GBinContentInterface *);



/* Détermine le type d'une interface pour la lecture de binaire. */
G_DEFINE_INTERFACE(GBinContent, g_binary_content, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de rassemblement.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_content_default_init(GBinContentInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à actualiser.                      *
*                attribs = jeu d'attributs à lier au contenu courant.         *
*                                                                             *
*  Description : Associe un ensemble d'attributs au contenu binaire.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_content_set_attributes(GBinContent *content, GContentAttributes *attribs)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    iface->set_attribs(content, attribs);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                                                                             *
*  Description : Fournit l'ensemble des attributs associés à un contenu.      *
*                                                                             *
*  Retour      : Jeu d'attributs liés au contenu courant.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentAttributes *g_binary_content_get_attributes(const GBinContent *content)
{
    GContentAttributes *result;             /* Instance à retourner        */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->get_attribs(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                                                                             *
*  Description : Donne l'origine d'un contenu binaire.                        *
*                                                                             *
*  Retour      : Contenu à l'origine du contenu courant.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_binary_content_get_root(GBinContent *content)
{
    GBinContent *result;                    /* Contenu en place à renvoyer */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->get_root(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                full    = précise s'il s'agit d'une version longue ou non.   *
*                                                                             *
*  Description : Fournit le nom associé au contenu binaire.                   *
*                                                                             *
*  Retour      : Nom de fichier avec chemin absolu au besoin.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_binary_content_describe(const GBinContent *content, bool full)
{
    char *result;                           /* Description à retourner     */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->describe(content, full);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                                                                             *
*  Description : Fournit une empreinte unique (SHA256) pour les données.      *
*                                                                             *
*  Retour      : Chaîne représentant l'empreinte du contenu binaire.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const gchar *g_binary_content_get_checksum(GBinContent *content)
{
    const gchar *result;                    /* Empreinte à retourner       */
    GChecksum *checksum;                    /* Calcul de l'empreinte       */
    GBinContentIface *iface;                /* Interface utilisée          */

    checksum = g_object_get_data(G_OBJECT(content), "checksum");

    if (checksum == NULL)
    {
        checksum = g_checksum_new(G_CHECKSUM_SHA256);
        assert(checksum != NULL);

        g_checksum_reset(checksum);

        iface = G_BIN_CONTENT_GET_IFACE(content);

        iface->compute_checksum(content, checksum);

        g_object_set_data_full(G_OBJECT(content), "checksum", checksum, (GDestroyNotify)g_checksum_free);

    }

    result = g_checksum_get_string(checksum);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                                                                             *
*  Description : Détermine le nombre d'octets lisibles.                       *
*                                                                             *
*  Retour      : Quantité représentée.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

phys_t g_binary_content_compute_size(const GBinContent *content)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    return iface->compute_size(content);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                pos     = position initiale. [OUT]                           *
*                                                                             *
*  Description : Détermine la position initiale d'un contenu.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_content_compute_start_pos(const GBinContent *content, vmpa2t *pos)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    return iface->compute_start_pos(content, pos);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                pos     = position finale (exclusive). [OUT]                 *
*                                                                             *
*  Description : Détermine la position finale d'un contenu.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_content_compute_end_pos(const GBinContent *content, vmpa2t *pos)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    return iface->compute_end_pos(content, pos);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                length  = quantité d'octets à provisionner.                  *
*                                                                             *
*  Description : Avance la tête de lecture d'une certaine quantité de données.*
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_seek(const GBinContent *content, vmpa2t *addr, phys_t length)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    return iface->seek(content, addr, length);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                length  = quantité d'octets à lire.                          *
*                                                                             *
*  Description : Donne accès à une portion des données représentées.          *
*                                                                             *
*  Retour      : Pointeur vers les données à lire ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const bin_t *g_binary_content_get_raw_access(const GBinContent *content, vmpa2t *addr, phys_t length)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    return iface->get_raw_access(content, addr, length);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                length  = quantité d'octets à lire.                          *
*                out     = réceptacle disponible pour ces données. [OUT]      *
*                                                                             *
*  Description : Fournit une portion des données représentées.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_raw(const GBinContent *content, vmpa2t *addr, phys_t length, bin_t *out)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_raw(content, addr, length, out);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                low     = position éventuelle des 4 bits visés. [OUT]        *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur quatre bits.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_u4(const GBinContent *content, vmpa2t *addr, bool *low, uint8_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_u4(content, addr, low, val);

    return result;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur un octet.                        *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_u8(const GBinContent *content, vmpa2t *addr, uint8_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_u8(content, addr, val);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur deux octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_u16(const GBinContent *content, vmpa2t *addr, SourceEndian endian, uint16_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_u16(content, addr, endian, val);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur quatre octets.                   *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_u32(const GBinContent *content, vmpa2t *addr, SourceEndian endian, uint32_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_u32(content, addr, endian, val);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur huit octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_u64(const GBinContent *content, vmpa2t *addr, SourceEndian endian, uint64_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_u64(content, addr, endian, val);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé encodé au format LEB128.             *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_uleb128(const GBinContent *content, vmpa2t *addr, uleb128_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_uleb128(content, addr, val);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre signé encodé au format LEB128.                 *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_content_read_leb128(const GBinContent *content, vmpa2t *addr, leb128_t *val)
{
    bool result;                            /* Bilan à remonter            */
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content);

    result = iface->read_leb128(content, addr, val);

    return result;

}
