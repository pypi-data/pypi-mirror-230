
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encapsulated.c - chargement de données binaires à partir d'un fichier
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


#include "encapsulated.h"


#include <malloc.h>
#include <string.h>


#include "../content-int.h"
#include "../db/misc/rlestr.h"
#include "../storage/serialize-int.h"
#include "../../common/extstr.h"



/* -------------------------- ENSEMBLE DE DONNEES BINAIRES -------------------------- */


/* Contenu de issu d'un contenu plus global (instance) */
struct _GEncapsContent
{
    GObject parent;                         /* A laisser en premier        */

    GBinContent *base;                      /* Base offrant une extraction */
    char *path;                             /* Chemin vers le contenu ciblé*/
    GBinContent *endpoint;                  /* Contenu ciblé               */

    char *full_desc;                        /* Description de l'ensemble   */
    char *desc;                             /* Description de l'ensemble   */

};

/* Contenu de issu d'un contenu plus global (classe) */
struct _GEncapsContentClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des contenus de données encapsulés. */
static void g_encaps_content_class_init(GEncapsContentClass *);

/* Initialise une instance de contenu de données encapsulé. */
static void g_encaps_content_init(GEncapsContent *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_encaps_content_serializable_init(GSerializableObjectInterface *);

/* Procède à l'initialisation de l'interface de lecture. */
static void g_encaps_content_interface_init(GBinContentInterface *);

/* Supprime toutes les références externes. */
static void g_encaps_content_dispose(GEncapsContent *);

/* Procède à la libération totale de la mémoire. */
static void g_encaps_content_finalize(GEncapsContent *);



/* ---------------------- INTERACTIONS AVEC UN CONTENU BINAIRE ---------------------- */


/* Associe un ensemble d'attributs au contenu binaire. */
static void g_encaps_content_set_attributes(GEncapsContent *, GContentAttributes *);

/* Fournit l'ensemble des attributs associés à un contenu. */
static GContentAttributes *g_encaps_content_get_attributes(const GEncapsContent *);

/* Donne l'origine d'un contenu binaire. */
static GBinContent *g_encaps_content_get_root(GEncapsContent *);

/* Fournit le nom associé au contenu binaire. */
static char *g_encaps_content_describe(const GEncapsContent *, bool);

/* Fournit une empreinte unique (SHA256) pour les données. */
static void g_encaps_content_compute_checksum(GEncapsContent *, GChecksum *);

/* Détermine le nombre d'octets lisibles. */
static phys_t g_encaps_content_compute_size(const GEncapsContent *);

/* Détermine la position initiale d'un contenu. */
static void g_encaps_content_compute_start_pos(const GEncapsContent *, vmpa2t *);

/* Détermine la position finale d'un contenu. */
static void g_encaps_content_compute_end_pos(const GEncapsContent *, vmpa2t *);

/* Avance la tête de lecture d'une certaine quantité de données. */
static bool g_encaps_content_seek(const GEncapsContent *, vmpa2t *, phys_t);

/* Donne accès à une portion des données représentées. */
static const bin_t *g_encaps_content_get_raw_access(const GEncapsContent *, vmpa2t *, phys_t);

/* Fournit une portion des données représentées. */
static bool g_encaps_content_read_raw(const GEncapsContent *, vmpa2t *, phys_t, bin_t *);

/* Lit un nombre non signé sur quatre bits. */
static bool g_encaps_content_read_u4(const GEncapsContent *, vmpa2t *, bool *, uint8_t *);

/* Lit un nombre non signé sur un octet. */
static bool g_encaps_content_read_u8(const GEncapsContent *, vmpa2t *, uint8_t *);

/* Lit un nombre non signé sur deux octets. */
static bool g_encaps_content_read_u16(const GEncapsContent *, vmpa2t *, SourceEndian, uint16_t *);

/* Lit un nombre non signé sur quatre octets. */
static bool g_encaps_content_read_u32(const GEncapsContent *, vmpa2t *, SourceEndian, uint32_t *);

/* Lit un nombre non signé sur huit octets. */
static bool g_encaps_content_read_u64(const GEncapsContent *, vmpa2t *, SourceEndian, uint64_t *);

/* Lit un nombre non signé encodé au format LEB128. */
static bool g_encaps_content_read_uleb128(const GEncapsContent *, vmpa2t *, uleb128_t *);

/* Lit un nombre signé encodé au format LEB128. */
static bool g_encaps_content_read_leb128(const GEncapsContent *, vmpa2t *, leb128_t *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_encaps_content_load(GEncapsContent *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_encaps_content_store(const GEncapsContent *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            ENSEMBLE DE DONNEES BINAIRES                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les contenus encapsulés. */
G_DEFINE_TYPE_WITH_CODE(GEncapsContent, g_encaps_content, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_BIN_CONTENT, g_encaps_content_interface_init)
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_encaps_content_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contenus de données encapsulés.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_encaps_content_class_init(GEncapsContentClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_encaps_content_dispose;
    object->finalize = (GObjectFinalizeFunc)g_encaps_content_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contenu de données encapsulé.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_encaps_content_init(GEncapsContent *content)
{
    content->base = NULL;
    content->path = NULL;
    content->endpoint = NULL;

    content->full_desc = NULL;
    content->desc = NULL;

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

static void g_encaps_content_interface_init(GBinContentInterface *iface)
{
    iface->set_attribs = (set_content_attributes)g_encaps_content_set_attributes;
    iface->get_attribs = (get_content_attributes)g_encaps_content_get_attributes;

    iface->get_root = (get_content_root_fc)g_encaps_content_get_root;

    iface->describe = (describe_content_fc)g_encaps_content_describe;

    iface->compute_checksum = (compute_checksum_fc)g_encaps_content_compute_checksum;

    iface->compute_size = (compute_size_fc)g_encaps_content_compute_size;
    iface->compute_start_pos = (compute_start_pos_fc)g_encaps_content_compute_start_pos;
    iface->compute_end_pos = (compute_end_pos_fc)g_encaps_content_compute_end_pos;

    iface->seek = (seek_fc)g_encaps_content_seek;

    iface->get_raw_access = (get_raw_access_fc)g_encaps_content_get_raw_access;

    iface->read_raw = (read_raw_fc)g_encaps_content_read_raw;
    iface->read_u4 = (read_u4_fc)g_encaps_content_read_u4;
    iface->read_u8 = (read_u8_fc)g_encaps_content_read_u8;
    iface->read_u16 = (read_u16_fc)g_encaps_content_read_u16;
    iface->read_u32 = (read_u32_fc)g_encaps_content_read_u32;
    iface->read_u64 = (read_u64_fc)g_encaps_content_read_u64;

    iface->read_uleb128 = (read_uleb128_fc)g_encaps_content_read_uleb128;
    iface->read_leb128 = (read_leb128_fc)g_encaps_content_read_leb128;

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

static void g_encaps_content_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_encaps_content_load;
    iface->store = (store_serializable_object_cb)g_encaps_content_store;

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

static void g_encaps_content_dispose(GEncapsContent *content)
{
    g_clear_object(&content->base);

    g_clear_object(&content->endpoint);

    G_OBJECT_CLASS(g_encaps_content_parent_class)->dispose(G_OBJECT(content));

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

static void g_encaps_content_finalize(GEncapsContent *content)
{
    if (content->desc != NULL)
        free(content->desc);

    if (content->full_desc != NULL)
        free(content->full_desc);

    G_OBJECT_CLASS(g_encaps_content_parent_class)->finalize(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base     = contenu binaire d'où réaliser une extraction.     *
*                path     = chemin vers le contenu finalement ciblé.          *
*                endpoint = contenu final rendu accessible.                   *
*                                                                             *
*  Description : Charge en mémoire un contenu binaire encapsulé.              *
*                                                                             *
*  Retour      : Représentation de contenu à manipuler ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_encaps_content_new(GBinContent *base, const char *path, GBinContent *endpoint)
{
    GEncapsContent *result;                 /* Structure à retourner      */

    result = g_object_new(G_TYPE_ENCAPS_CONTENT, NULL);

    g_object_ref(base);
    g_object_ref(endpoint);

    result->base = base;
    result->path = strdup(path);
    result->endpoint = endpoint;

    /* Description complète */

    result->full_desc = g_binary_content_describe(result->base, true);

    result->full_desc = stradd(result->full_desc, G_DIR_SEPARATOR_S);

    result->full_desc = stradd(result->full_desc, path);

    /* Description partielle */

    result->desc = strdup(path);

    return G_BIN_CONTENT(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir consulter.                 *
*                                                                             *
*  Description : Indique la base d'un contenu binaire encapsulé.              *
*                                                                             *
*  Retour      : Instance de contenu binaire ou NULL si aucune.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_encaps_content_get_base(const GEncapsContent *content)
{
    GBinContent *result;                    /* Contenu binaire à renvoyer  */

    result = content->base;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir consulter.                 *
*                                                                             *
*  Description : Fournit le chemin vers le contenu interne représenté.        *
*                                                                             *
*  Retour      : Chemin d'accès au contenu binaire.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_encaps_content_get_path(const GEncapsContent *content)
{
    char *result;                           /* Chemin d'accès à retourner  */

    result = content->path;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir consulter.                 *
*                                                                             *
*  Description : Indique le contenu binaire embarqué dans une encapsulation.  *
*                                                                             *
*  Retour      : Instance de contenu binaire ou NULL si aucune.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_encaps_content_get_endpoint(const GEncapsContent *content)
{
    GBinContent *result;                    /* Contenu binaire à renvoyer  */

    result = content->endpoint;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

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

static void g_encaps_content_set_attributes(GEncapsContent *content, GContentAttributes *attribs)
{
    g_binary_content_set_attributes(content->endpoint, attribs);

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

static GContentAttributes *g_encaps_content_get_attributes(const GEncapsContent *content)
{
    GContentAttributes *result;             /* Instance à retourner        */

    result = g_binary_content_get_attributes(content->endpoint);

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

static GBinContent *g_encaps_content_get_root(GEncapsContent *content)
{
    GBinContent *result;                    /* Contenu en place à renvoyer */

    result = g_binary_content_get_root(content->base);

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

static char *g_encaps_content_describe(const GEncapsContent *content, bool full)
{
    char *result;                           /* Description à retourner     */

    if (full)
        result = strdup(content->full_desc);
    else
        result = strdup(content->desc);

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

static void g_encaps_content_compute_checksum(GEncapsContent *content, GChecksum *checksum)
{
    GBinContentIface *iface;                /* Interface utilisée          */

    iface = G_BIN_CONTENT_GET_IFACE(content->endpoint);

    iface->compute_checksum(content->endpoint, checksum);

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

static phys_t g_encaps_content_compute_size(const GEncapsContent *content)
{
    phys_t result;                          /* Quantité trouvée à retourner*/

    result = g_binary_content_compute_size(content->endpoint);

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

static void g_encaps_content_compute_start_pos(const GEncapsContent *content, vmpa2t *pos)
{
    g_binary_content_compute_start_pos(content->endpoint, pos);

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

static void g_encaps_content_compute_end_pos(const GEncapsContent *content, vmpa2t *pos)
{
    g_binary_content_compute_end_pos(content->endpoint, pos);

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

static bool g_encaps_content_seek(const GEncapsContent *content, vmpa2t *addr, phys_t length)
{
    bool result;                            /* Bilan d'opération à renvoyer*/

    result = g_binary_content_seek(content->endpoint, addr, length);

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

static const bin_t *g_encaps_content_get_raw_access(const GEncapsContent *content, vmpa2t *addr, phys_t length)
{
    const bin_t *result;                    /* Accès brut à retourner      */

    result = g_binary_content_get_raw_access(content->endpoint, addr, length);

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

static bool g_encaps_content_read_raw(const GEncapsContent *content, vmpa2t *addr, phys_t length, bin_t *out)
{
    bool result;                            /* Bilan à remonter            */

    result = g_binary_content_read_raw(content->endpoint, addr, length, out);

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

static bool g_encaps_content_read_u4(const GEncapsContent *content, vmpa2t *addr, bool *low, uint8_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_u4(content->endpoint, addr, low, val);

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

static bool g_encaps_content_read_u8(const GEncapsContent *content, vmpa2t *addr, uint8_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_u8(content->endpoint, addr, val);

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

static bool g_encaps_content_read_u16(const GEncapsContent *content, vmpa2t *addr, SourceEndian endian, uint16_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_u16(content->endpoint, addr, endian, val);

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

static bool g_encaps_content_read_u32(const GEncapsContent *content, vmpa2t *addr, SourceEndian endian, uint32_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_u32(content->endpoint, addr, endian, val);

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

static bool g_encaps_content_read_u64(const GEncapsContent *content, vmpa2t *addr, SourceEndian endian, uint64_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_u64(content->endpoint, addr, endian, val);

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

static bool g_encaps_content_read_uleb128(const GEncapsContent *content, vmpa2t *addr, uleb128_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_uleb128(content->endpoint, addr, val);

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

static bool g_encaps_content_read_leb128(const GEncapsContent *content, vmpa2t *addr, leb128_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */

    result = g_binary_content_read_leb128(content->endpoint, addr, val);

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

static bool g_encaps_content_load(GEncapsContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à charger            */

    content->base = G_BIN_CONTENT(g_object_storage_unpack_object(storage, "contents", pbuf));
    result = (content->base != NULL);

    setup_empty_rle_string(&str);

    if (result)
        result = unpack_rle_string(&str, pbuf);

    if (result)
    {
        result = (get_rle_string(&str) != NULL);

        if (result)
            content->path = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

    if (result)
    {
        content->endpoint = G_BIN_CONTENT(g_object_storage_unpack_object(storage, "contents", pbuf));
        result = (content->endpoint != NULL);
    }

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

static bool g_encaps_content_store(const GEncapsContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à conserver          */

    result = g_object_storage_pack_object(storage, "contents", G_SERIALIZABLE_OBJECT(content->base), pbuf);

    if (result)
    {
        init_static_rle_string(&str, content->path);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    if (result)
        result = g_object_storage_pack_object(storage, "contents", G_SERIALIZABLE_OBJECT(content->endpoint), pbuf);

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
