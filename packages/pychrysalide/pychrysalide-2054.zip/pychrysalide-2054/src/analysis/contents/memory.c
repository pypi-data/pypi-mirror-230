
/* Chrysalide - Outil d'analyse de fichiers binaires
 * memory.c - chargement de données binaires à partir de la mémoire
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


#include "memory.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <unistd.h>


#include <i18n.h>


#include "memory-int.h"
#include "../content-int.h"
#include "../db/misc/rlestr.h"
#include "../storage/serialize-int.h"
#include "../../common/extstr.h"
#include "../../core/logs.h"



/* -------------------------- ENSEMBLE DE DONNEES BINAIRES -------------------------- */


/* Initialise la classe des contenus de données en mémoire. */
static void g_memory_content_class_init(GMemoryContentClass *);

/* Initialise une instance de contenu de données en mémoire. */
static void g_memory_content_init(GMemoryContent *);

/* Procède à l'initialisation de l'interface de lecture. */
static void g_memory_content_interface_init(GBinContentInterface *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_memory_content_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_memory_content_dispose(GMemoryContent *);

/* Procède à la libération totale de la mémoire. */
static void g_memory_content_finalize(GMemoryContent *);



/* ---------------------- INTERACTIONS AVEC UN CONTENU BINAIRE ---------------------- */


/* Associe un ensemble d'attributs au contenu binaire. */
static void g_memory_content_set_attributes(GMemoryContent *, GContentAttributes *);

/* Fournit l'ensemble des attributs associés à un contenu. */
static GContentAttributes *g_memory_content_get_attributes(const GMemoryContent *);

/* Donne l'origine d'un contenu binaire. */
static GBinContent *g_memory_content_get_root(GMemoryContent *);

/* Fournit le nom associé au contenu binaire. */
static char *g_memory_content_describe(const GMemoryContent *, bool);

/* Fournit une empreinte unique (SHA256) pour les données. */
static void g_memory_content_compute_checksum(GMemoryContent *, GChecksum *);

/* Détermine le nombre d'octets lisibles. */
static phys_t g_memory_content_compute_size(const GMemoryContent *);

/* Détermine la position initiale d'un contenu. */
static void g_memory_content_compute_start_pos(const GMemoryContent *, vmpa2t *);

/* Détermine la position finale d'un contenu. */
static void g_memory_content_compute_end_pos(const GMemoryContent *, vmpa2t *);

/* Avance la tête de lecture d'une certaine quantité de données. */
static bool g_memory_content_seek(const GMemoryContent *, vmpa2t *, phys_t);

/* Donne accès à une portion des données représentées. */
static const bin_t *g_memory_content_get_raw_access(const GMemoryContent *, vmpa2t *, phys_t);

/* Fournit une portion des données représentées. */
static bool g_memory_content_read_raw(const GMemoryContent *, vmpa2t *, phys_t, bin_t *);

/* Lit un nombre non signé sur quatre bits. */
static bool g_memory_content_read_u4(const GMemoryContent *, vmpa2t *, bool *, uint8_t *);

/* Lit un nombre non signé sur un octet. */
static bool g_memory_content_read_u8(const GMemoryContent *, vmpa2t *, uint8_t *);

/* Lit un nombre non signé sur deux octets. */
static bool g_memory_content_read_u16(const GMemoryContent *, vmpa2t *, SourceEndian, uint16_t *);

/* Lit un nombre non signé sur quatre octets. */
static bool g_memory_content_read_u32(const GMemoryContent *, vmpa2t *, SourceEndian, uint32_t *);

/* Lit un nombre non signé sur huit octets. */
static bool g_memory_content_read_u64(const GMemoryContent *, vmpa2t *, SourceEndian, uint64_t *);

/* Lit un nombre non signé encodé au format LEB128. */
static bool g_memory_content_read_uleb128(const GMemoryContent *, vmpa2t *, uleb128_t *);

/* Lit un nombre signé encodé au format LEB128. */
static bool g_memory_content_read_leb128(const GMemoryContent *, vmpa2t *, leb128_t *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_memory_content_load(GMemoryContent *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_memory_content_store(const GMemoryContent *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            ENSEMBLE DE DONNEES BINAIRES                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les contenus de données en mémoire. */
G_DEFINE_TYPE_WITH_CODE(GMemoryContent, g_memory_content, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_BIN_CONTENT, g_memory_content_interface_init)
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_memory_content_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contenus de données en mémoire.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_class_init(GMemoryContentClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_memory_content_dispose;
    object->finalize = (GObjectFinalizeFunc)g_memory_content_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contenu de données en mémoire.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_init(GMemoryContent *content)
{
    GContentAttributes *empty;              /* Jeu d'attributs vide        */

    content->attribs = NULL;

    empty = g_content_attributes_new("", NULL);

    g_binary_content_set_attributes(G_BIN_CONTENT(content), empty);

    g_object_unref(G_OBJECT(empty));

    content->data = NULL;
    content->length = 0;
    content->allocated = false;

    content->full_desc = strdup("In-memory content");
    content->desc = strdup("In-memory content");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de lecture.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_interface_init(GBinContentInterface *iface)
{
    iface->set_attribs = (set_content_attributes)g_memory_content_set_attributes;
    iface->get_attribs = (get_content_attributes)g_memory_content_get_attributes;

    iface->get_root = (get_content_root_fc)g_memory_content_get_root;

    iface->describe = (describe_content_fc)g_memory_content_describe;

    iface->compute_checksum = (compute_checksum_fc)g_memory_content_compute_checksum;

    iface->compute_size = (compute_size_fc)g_memory_content_compute_size;
    iface->compute_start_pos = (compute_start_pos_fc)g_memory_content_compute_start_pos;
    iface->compute_end_pos = (compute_end_pos_fc)g_memory_content_compute_end_pos;

    iface->seek = (seek_fc)g_memory_content_seek;

    iface->get_raw_access = (get_raw_access_fc)g_memory_content_get_raw_access;

    iface->read_raw = (read_raw_fc)g_memory_content_read_raw;
    iface->read_u4 = (read_u4_fc)g_memory_content_read_u4;
    iface->read_u8 = (read_u8_fc)g_memory_content_read_u8;
    iface->read_u16 = (read_u16_fc)g_memory_content_read_u16;
    iface->read_u32 = (read_u32_fc)g_memory_content_read_u32;
    iface->read_u64 = (read_u64_fc)g_memory_content_read_u64;

    iface->read_uleb128 = (read_uleb128_fc)g_memory_content_read_uleb128;
    iface->read_leb128 = (read_leb128_fc)g_memory_content_read_leb128;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de sérialisation.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_memory_content_load;
    iface->store = (store_serializable_object_cb)g_memory_content_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_dispose(GMemoryContent *content)
{
    g_clear_object(&content->attribs);

    G_OBJECT_CLASS(g_memory_content_parent_class)->dispose(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_finalize(GMemoryContent *content)
{
    if (content->allocated)
    {
        if (content->data != NULL)
            free(content->data);
    }

    if (content->desc != NULL)
        free(content->desc);

    if (content->full_desc != NULL)
        free(content->full_desc);

    G_OBJECT_CLASS(g_memory_content_parent_class)->finalize(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = données du contenu volatile.                          *
*                size = quantité de ces données.                              *
*                                                                             *
*  Description : Charge en mémoire le contenu de données brutes.              *
*                                                                             *
*  Retour      : Représentation de contenu à manipuler ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_memory_content_new(const bin_t *data, phys_t size)
{
    GMemoryContent *result;                 /* Structure à retourner       */
    bin_t *allocated;                       /* Zone de réception           */

    allocated = malloc(size);
    if (allocated == NULL)
    {
        LOG_ERROR_N("malloc");
        return NULL;
    }

    memcpy(allocated, data, size);

    result = g_object_new(G_TYPE_MEMORY_CONTENT, NULL);

    result->data = allocated;
    result->length = size;
    result->allocated = true;

    return G_BIN_CONTENT(result);

}



/* ---------------------------------------------------------------------------------- */
/*                        INTERACTIONS AVEC UN CONTENU BINAIRE                        */
/* ---------------------------------------------------------------------------------- */


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

static void g_memory_content_set_attributes(GMemoryContent *content, GContentAttributes *attribs)
{
    g_clear_object(&content->attribs);

    content->attribs = attribs;
    g_object_ref(G_OBJECT(attribs));

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

static GContentAttributes *g_memory_content_get_attributes(const GMemoryContent *content)
{
    GContentAttributes *result;             /* Instance à retourner        */

    result = content->attribs;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

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

static GBinContent *g_memory_content_get_root(GMemoryContent *content)
{
    GBinContent *result;                    /* Contenu en place à renvoyer */

    result = G_BIN_CONTENT(content);

    g_object_ref(G_OBJECT(result));

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

static char *g_memory_content_describe(const GMemoryContent *content, bool full)
{
    char *result;                           /* Description à retourner     */

    result = (full ? content->full_desc : content->desc);

    if (result != NULL)
        result = strdup(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content  = contenu binaire à venir lire.                     *
*                checksum = empreinte de zone mémoire à compléter.            *
*                                                                             *
*  Description : Calcule une empreinte unique (SHA256) pour les données.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_memory_content_compute_checksum(GMemoryContent *content, GChecksum *checksum)
{
    g_checksum_update(checksum, content->data, content->length);

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

static phys_t g_memory_content_compute_size(const GMemoryContent *content)
{
    phys_t result;                          /* Quantité trouvée à retourner*/

    result = content->length;

    return result;

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

static void g_memory_content_compute_start_pos(const GMemoryContent *content, vmpa2t *pos)
{
    init_vmpa(pos, 0, VMPA_NO_VIRTUAL);

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

static void g_memory_content_compute_end_pos(const GMemoryContent *content, vmpa2t *pos)
{
    g_memory_content_compute_start_pos(content, pos);

    advance_vmpa(pos, content->length);

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

static bool g_memory_content_seek(const GMemoryContent *content, vmpa2t *addr, phys_t length)
{
    bool result;                            /* Bilan à retourner           */
    phys_t offset;                          /* Emplacement de départ       */

    result = false;

    offset = get_phy_addr(addr);

    if (length > content->length)
        goto done;

    if (offset > (content->length - length))
        goto done;

    advance_vmpa(addr, length);

    result = true;

 done:

    return result;

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

static const bin_t *g_memory_content_get_raw_access(const GMemoryContent *content, vmpa2t *addr, phys_t length)
{
    const bin_t *result;                    /* Données utiles à renvoyer   */
    phys_t offset;                          /* Emplacement de départ       */
    bool allowed;                           /* Capacité d'avancer ?        */

    offset = get_phy_addr(addr);

    allowed = g_memory_content_seek(content, addr, length);

    result = (allowed ? &content->data[offset] : NULL);

    return result;

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

static bool g_memory_content_read_raw(const GMemoryContent *content, vmpa2t *addr, phys_t length, bin_t *out)
{
    bool result;                            /* Bilan à remonter            */
    const bin_t *data;                      /* Pointeur vers données utiles*/

    data = g_memory_content_get_raw_access(content, addr, length);

    if (data != NULL)
    {
        result = true;
        memcpy(out, data, length);
    }
    else
        result = false;

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

static bool g_memory_content_read_u4(const GMemoryContent *content, vmpa2t *addr, bool *low, uint8_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    result = read_u4(val, content->data, &pos, content->length, low);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

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

static bool g_memory_content_read_u8(const GMemoryContent *content, vmpa2t *addr, uint8_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */
    phys_t length;                          /* Taille de la surface dispo. */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    length = length;

    result = read_u8(val, content->data, &pos, content->length);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

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

static bool g_memory_content_read_u16(const GMemoryContent *content, vmpa2t *addr, SourceEndian endian, uint16_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    result = read_u16(val, content->data, &pos, content->length, endian);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

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

static bool g_memory_content_read_u32(const GMemoryContent *content, vmpa2t *addr, SourceEndian endian, uint32_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    result = read_u32(val, content->data, &pos, content->length, endian);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

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

static bool g_memory_content_read_u64(const GMemoryContent *content, vmpa2t *addr, SourceEndian endian, uint64_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    result = read_u64(val, content->data, &pos, content->length, endian);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

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

static bool g_memory_content_read_uleb128(const GMemoryContent *content, vmpa2t *addr, uleb128_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    result = read_uleb128(val, content->data, &pos, content->length);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

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

static bool g_memory_content_read_leb128(const GMemoryContent *content, vmpa2t *addr, leb128_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    phys_t pos;                             /* Tête de lecture courante    */

    pos = get_phy_addr(addr);

    if (pos == VMPA_NO_PHYSICAL)
        return false;

    result = read_leb128(val, content->data, &pos, content->length);

    if (result)
        advance_vmpa(addr, pos - get_phy_addr(addr));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_memory_content_load(GMemoryContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t length;                       /* Quantité de données à suivre*/
    rle_string str;                         /* Chaîne à charger            */

    result = unpack_uleb128(&length, pbuf);

    if (result)
    {
        content->data = malloc(length);
        result = (content->data != NULL);

        content->allocated = true;

    }

    if (result)
    {
        content->length = length;
        result = extract_packed_buffer(pbuf, content->data, length, false);
    }

    setup_empty_rle_string(&str);

    if (result)
        result = unpack_rle_string(&str, pbuf);

    if (result)
    {
        result = (get_rle_string(&str) != NULL);

        if (result)
            content->full_desc = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

    if (result)
        result = unpack_rle_string(&str, pbuf);

    if (result)
    {
        result = (get_rle_string(&str) != NULL);

        if (result)
            content->desc = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_memory_content_store(const GMemoryContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à conserver          */

    result = pack_uleb128((uleb128_t []){ content->length }, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, content->data, content->length, false);

    if (result)
    {
        init_static_rle_string(&str, content->full_desc);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    if (result)
    {
        init_static_rle_string(&str, content->desc);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    return result;

}
