
/* Chrysalide - Outil d'analyse de fichiers binaires
 * restricted.c - chargement de données binaires à partir d'un contenu restreint
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


#include "restricted.h"


#include <assert.h>
#include <string.h>


#include "../content-int.h"
#include "../db/misc/rlestr.h"
#include "../storage/serialize-int.h"
#include "../../common/extstr.h"
#include "../../core/logs.h"



/* -------------------------- ENSEMBLE DE DONNEES BINAIRES -------------------------- */


/* Contenu de données binaires issues d'un contenu restreint (instance) */
struct _GRestrictedContent
{
    GObject parent;                         /* A laisser en premier        */

    GBinContent *internal;                  /* Contenu de sous-traitance   */

    mrange_t range;                         /* Restriction de couverture   */

};

/* Contenu de données binaires issues d'un contenu restreint (classe) */
struct _GRestrictedContentClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des contenus de données binaires. */
static void g_restricted_content_class_init(GRestrictedContentClass *);

/* Initialise une instance de contenu de données binaires. */
static void g_restricted_content_init(GRestrictedContent *);

/* Procède à l'initialisation de l'interface de lecture. */
static void g_restricted_content_interface_init(GBinContentInterface *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_restricted_content_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_restricted_content_dispose(GRestrictedContent *);

/* Procède à la libération totale de la mémoire. */
static void g_restricted_content_finalize(GRestrictedContent *);



/* ---------------------- INTERACTIONS AVEC UN CONTENU BINAIRE ---------------------- */


/* Associe un ensemble d'attributs au contenu binaire. */
static void g_restricted_content_set_attributes(GRestrictedContent *, GContentAttributes *);

/* Fournit l'ensemble des attributs associés à un contenu. */
static GContentAttributes *g_restricted_content_get_attributes(const GRestrictedContent *);

/* Donne l'origine d'un contenu binaire. */
static GBinContent *g_restricted_content_get_root(GRestrictedContent *);

/* Fournit le nom associé au contenu binaire. */
static char *g_restricted_content_describe(const GRestrictedContent *, bool);

/* Calcule une empreinte unique (SHA256) pour les données. */
static void g_restricted_content_compute_checksum(GRestrictedContent *, GChecksum *);

/* Détermine le nombre d'octets lisibles. */
static phys_t g_restricted_content_compute_size(const GRestrictedContent *);

/* Détermine la position initiale d'un contenu. */
static void g_restricted_content_compute_start_pos(const GRestrictedContent *, vmpa2t *);

/* Détermine la position finale d'un contenu. */
static void g_restricted_content_compute_end_pos(const GRestrictedContent *, vmpa2t *);

/* Avance la tête de lecture d'une certaine quantité de données. */
static bool g_restricted_content_seek(const GRestrictedContent *, vmpa2t *, phys_t);

/* Donne accès à une portion des données représentées. */
static const bin_t *g_restricted_content_get_raw_access(const GRestrictedContent *, vmpa2t *, phys_t);

/* Fournit une portion des données représentées. */
static bool g_restricted_content_read_raw(const GRestrictedContent *, vmpa2t *, phys_t, bin_t *);

/* Lit un nombre non signé sur quatre bits. */
static bool g_restricted_content_read_u4(const GRestrictedContent *, vmpa2t *, bool *, uint8_t *);

/* Lit un nombre non signé sur un octet. */
static bool g_restricted_content_read_u8(const GRestrictedContent *, vmpa2t *, uint8_t *);

/* Lit un nombre non signé sur deux octets. */
static bool g_restricted_content_read_u16(const GRestrictedContent *, vmpa2t *, SourceEndian, uint16_t *);

/* Lit un nombre non signé sur quatre octets. */
static bool g_restricted_content_read_u32(const GRestrictedContent *, vmpa2t *, SourceEndian, uint32_t *);

/* Lit un nombre non signé sur huit octets. */
static bool g_restricted_content_read_u64(const GRestrictedContent *, vmpa2t *, SourceEndian, uint64_t *);

/* Lit un nombre non signé encodé au format LEB128. */
static bool g_restricted_content_read_uleb128(const GRestrictedContent *, vmpa2t *, uleb128_t *);

/* Lit un nombre signé encodé au format LEB128. */
static bool g_restricted_content_read_leb128(const GRestrictedContent *, vmpa2t *, leb128_t *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_restricted_content_load(GRestrictedContent *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_restricted_content_store(const GRestrictedContent *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            ENSEMBLE DE DONNEES BINAIRES                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les contenus de données. */
G_DEFINE_TYPE_WITH_CODE(GRestrictedContent, g_restricted_content, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_BIN_CONTENT, g_restricted_content_interface_init)
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_restricted_content_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contenus de données binaires.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_restricted_content_class_init(GRestrictedContentClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_restricted_content_dispose;
    object->finalize = (GObjectFinalizeFunc)g_restricted_content_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contenu de données binaires.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_restricted_content_init(GRestrictedContent *content)
{
    vmpa2t dummy;                           /* Localisation nulle          */

    content->internal = NULL;

    init_vmpa(&dummy, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);
    init_mrange(&content->range, &dummy, 0);

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

static void g_restricted_content_interface_init(GBinContentInterface *iface)
{
    iface->set_attribs = (set_content_attributes)g_restricted_content_set_attributes;
    iface->get_attribs = (get_content_attributes)g_restricted_content_get_attributes;

    iface->get_root = (get_content_root_fc)g_restricted_content_get_root;

    iface->describe = (describe_content_fc)g_restricted_content_describe;

    iface->compute_checksum = (compute_checksum_fc)g_restricted_content_compute_checksum;

    iface->compute_size = (compute_size_fc)g_restricted_content_compute_size;
    iface->compute_start_pos = (compute_start_pos_fc)g_restricted_content_compute_start_pos;
    iface->compute_end_pos = (compute_end_pos_fc)g_restricted_content_compute_end_pos;

    iface->seek = (seek_fc)g_restricted_content_seek;

    iface->get_raw_access = (get_raw_access_fc)g_restricted_content_get_raw_access;

    iface->read_raw = (read_raw_fc)g_restricted_content_read_raw;
    iface->read_u4 = (read_u4_fc)g_restricted_content_read_u4;
    iface->read_u8 = (read_u8_fc)g_restricted_content_read_u8;
    iface->read_u16 = (read_u16_fc)g_restricted_content_read_u16;
    iface->read_u32 = (read_u32_fc)g_restricted_content_read_u32;
    iface->read_u64 = (read_u64_fc)g_restricted_content_read_u64;

    iface->read_uleb128 = (read_uleb128_fc)g_restricted_content_read_uleb128;
    iface->read_leb128 = (read_leb128_fc)g_restricted_content_read_leb128;

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

static void g_restricted_content_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_restricted_content_load;
    iface->store = (store_serializable_object_cb)g_restricted_content_store;

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

static void g_restricted_content_dispose(GRestrictedContent *content)
{
    g_clear_object(&content->internal);

    G_OBJECT_CLASS(g_restricted_content_parent_class)->dispose(G_OBJECT(content));

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

static void g_restricted_content_finalize(GRestrictedContent *content)
{
    G_OBJECT_CLASS(g_restricted_content_parent_class)->finalize(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire où puiser les données à fournir.   *
*                range   = espace de restrictions pour les accès.             *
*                                                                             *
*  Description : Charge en mémoire le contenu d'un contenu restreint.         *
*                                                                             *
*  Retour      : Représentation de contenu à manipuler ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_restricted_content_new(GBinContent *content, const mrange_t *range)
{
    GRestrictedContent *result;              /* Structure à retourner      */

    result = g_object_new(G_TYPE_RESTRICTED_CONTENT, NULL);

    result->internal = content;
    g_object_ref(G_OBJECT(result->internal));

    copy_mrange(&result->range, range);

    return G_BIN_CONTENT(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire où puiser les données à fournir.   *
*                range   = espace de restrictions pour les accès.             *
*                                                                             *
*  Description : Charge en mémoire le contenu d'un contenu restreint.         *
*                                                                             *
*  Retour      : Représentation de contenu à manipuler ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_restricted_content_new_ro(const GBinContent *content, const mrange_t *range)
{
    GRestrictedContent *result;              /* Structure à retourner      */

    result = g_object_new(G_TYPE_RESTRICTED_CONTENT, NULL);

    result->internal = (GBinContent *)content;
    g_object_ref(G_OBJECT(result->internal));

    copy_mrange(&result->range, range);

    return G_BIN_CONTENT(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                range   = espace de restrictions pour les accès. [OUT]       *
*                                                                             *
*  Description : Indique l'espace de restriction appliqué à un contenu.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_restricted_content_get_range(const GRestrictedContent *content, mrange_t *range)
{
    copy_mrange(range, &content->range);

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

static void g_restricted_content_set_attributes(GRestrictedContent *content, GContentAttributes *attribs)
{
    g_binary_content_set_attributes(content->internal, attribs);

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

static GContentAttributes *g_restricted_content_get_attributes(const GRestrictedContent *content)
{
    GContentAttributes *result;             /* Instance à retourner        */

    result = g_binary_content_get_attributes(content->internal);

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

static GBinContent *g_restricted_content_get_root(GRestrictedContent *content)
{
    GBinContent *result;                    /* Contenu en place à renvoyer */

    result = g_binary_content_get_root(content->internal);

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

static char *g_restricted_content_describe(const GRestrictedContent *content, bool full)
{
    char *result;                           /* Description à retourner     */
    VMPA_BUFFER(start_str);                 /* Zone de départ en texte     */
    vmpa2t end;                             /* Position de fin             */
    VMPA_BUFFER(end_str);                   /* Zone de départ en texte     */
    char *suffix;                           /* Construction d'un appendice */
    int ret;                                /* Bilan de construction       */

    result = g_binary_content_describe(content->internal, full);

    vmpa2_to_string(get_mrange_addr(&content->range), MDS_UNDEFINED, start_str, NULL);

    compute_mrange_end_addr(&content->range, &end);

    vmpa2_to_string(&end, MDS_UNDEFINED, end_str, NULL);

    ret = asprintf(&suffix, "[%s:%s]", start_str, end_str);

    if (ret == -1)
        LOG_ERROR_N("asprintf");

    else
    {
        if (result != NULL)
            result = stradd(result, " ");

        result = stradd(result, suffix);

        free(suffix);

    }

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

static void g_restricted_content_compute_checksum(GRestrictedContent *content, GChecksum *checksum)
{
    vmpa2t start;                           /* Point de départ             */
    phys_t i;                               /* Boucle de parcours          */
    vmpa2t iter;                            /* Tête de lecture             */
    const bin_t *byte;                      /* Octet de données à intégrer */

    copy_vmpa(&start, get_mrange_addr(&content->range));

    for (i = 0; i < get_mrange_length(&content->range); i++)
    {
        copy_vmpa(&iter, &start);
        advance_vmpa(&iter, i);

        byte = g_binary_content_get_raw_access(G_BIN_CONTENT(content->internal), &iter, 1);

        if (byte != NULL)
            g_checksum_update(checksum, byte, 1);

    }

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

static phys_t g_restricted_content_compute_size(const GRestrictedContent *content)
{
    phys_t result;                          /* Quantité trouvée à retourner*/

    result = get_mrange_length(&content->range);

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

static void g_restricted_content_compute_start_pos(const GRestrictedContent *content, vmpa2t *pos)
{
    copy_vmpa(pos, get_mrange_addr(&content->range));

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

static void g_restricted_content_compute_end_pos(const GRestrictedContent *content, vmpa2t *pos)
{
    compute_mrange_end_addr(&content->range, pos);

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

static bool g_restricted_content_seek(const GRestrictedContent *content, vmpa2t *addr, phys_t length)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_seek(content->internal, addr, length);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static const bin_t *g_restricted_content_get_raw_access(const GRestrictedContent *content, vmpa2t *addr, phys_t length)
{
    const bin_t *result;                    /* Données utiles à renvoyer   */
    mrange_t requested;                     /* Espace demandé en lecture   */

    init_mrange(&requested, addr, length);

    if (!mrange_contains_mrange(&content->range, &requested))
    {
        result = NULL;
        goto bad_range;
    }

    result = g_binary_content_get_raw_access(content->internal, addr, length);

 bad_range:

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

static bool g_restricted_content_read_raw(const GRestrictedContent *content, vmpa2t *addr, phys_t length, bin_t *out)
{
    bool result;                            /* Bilan à remonter            */
    const bin_t *data;                      /* Pointeur vers données utiles*/

    data = g_restricted_content_get_raw_access(content, addr, length);

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

static bool g_restricted_content_read_u4(const GRestrictedContent *content, vmpa2t *addr, bool *low, uint8_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */
    bool old_low;                           /* Côté de l'octet traité      */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);
    old_low = *low;

    result = g_binary_content_read_u4(content->internal, addr, low, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        *low = old_low;
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_read_u8(const GRestrictedContent *content, vmpa2t *addr, uint8_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_read_u8(content->internal, addr, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_read_u16(const GRestrictedContent *content, vmpa2t *addr, SourceEndian endian, uint16_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_read_u16(content->internal, addr, endian, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_read_u32(const GRestrictedContent *content, vmpa2t *addr, SourceEndian endian, uint32_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_read_u32(content->internal, addr, endian, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_read_u64(const GRestrictedContent *content, vmpa2t *addr, SourceEndian endian, uint64_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_read_u64(content->internal, addr, endian, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_read_uleb128(const GRestrictedContent *content, vmpa2t *addr, uleb128_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_read_uleb128(content->internal, addr, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_read_leb128(const GRestrictedContent *content, vmpa2t *addr, leb128_t *val)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    vmpa2t old;                             /* Copie de sauvegarde         */

    if (!mrange_contains_addr(&content->range, addr))
    {
        result = false;
        goto bad_range;
    }

    copy_vmpa(&old, addr);

    result = g_binary_content_read_leb128(content->internal, addr, val);

    if (result && !mrange_contains_addr_inclusive(&content->range, addr))
    {
        copy_vmpa(addr, &old);
        result = false;
    }

 bad_range:

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

static bool g_restricted_content_load(GRestrictedContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    content->internal = G_BIN_CONTENT(g_object_storage_unpack_object(storage, "contents", pbuf));
    result = (content->internal != NULL);

    if (result)
        result = unpack_mrange(&content->range, pbuf);

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

static bool g_restricted_content_store(const GRestrictedContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = g_object_storage_pack_object(storage, "contents", G_SERIALIZABLE_OBJECT(content->internal), pbuf);

    if (result)
        result = pack_mrange(&content->range, pbuf);

    return result;

}
