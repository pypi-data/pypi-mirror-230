
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - support des différents formats binaires reconnus
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


#include "known.h"


#include <assert.h>


#include "known-int.h"
#include "../analysis/storage/serialize-int.h"
#include "../plugins/pglist.h"



/* ---------------------- DEFINITION DE LA BASE DE TOUT FORMAT ---------------------- */


/* Initialise la classe des formats binaires génériques. */
static void g_known_format_class_init(GKnownFormatClass *);

/* Initialise une instance de format binaire générique. */
static void g_known_format_init(GKnownFormat *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_known_format_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_known_format_dispose(GKnownFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_known_format_finalize(GKnownFormat *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un format depuis une mémoire tampon. */
static bool _g_known_format_load(GKnownFormat *, GObjectStorage *, packed_buffer_t *);

/* Charge un format depuis une mémoire tampon. */
static bool g_known_format_load(GKnownFormat *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un format dans une mémoire tampon. */
static bool _g_known_format_store(GKnownFormat *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un format dans une mémoire tampon. */
static bool g_known_format_store(GKnownFormat *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA BASE DE TOUT FORMAT                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un format binaire générique. */
G_DEFINE_TYPE_WITH_CODE(GKnownFormat, g_known_format, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_known_format_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats binaires génériques.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_known_format_class_init(GKnownFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_known_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_known_format_finalize;

    klass->load = (load_known_fc)_g_known_format_load;
    klass->store = (store_known_fc)_g_known_format_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format binaire générique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_known_format_init(GKnownFormat *format)
{
    format->content = NULL;

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

static void g_known_format_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_known_format_load;
    iface->store = (store_serializable_object_cb)g_known_format_store;

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

static void g_known_format_dispose(GKnownFormat *format)
{
    g_clear_object(&format->content);

    G_OBJECT_CLASS(g_known_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_known_format_finalize(GKnownFormat *format)
{
    G_OBJECT_CLASS(g_known_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Définit le contenu binaire à analyser.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_known_format_set_content(GKnownFormat *format, GBinContent *content)
{
    assert(format->content == NULL);

    g_object_ref_sink(G_OBJECT(content));

    format->content = content;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                                                                             *
*  Description : Fournit une référence vers le contenu binaire analysé.       *
*                                                                             *
*  Retour      : Gestionnaire de contenu binaire en place.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_known_format_get_content(const GKnownFormat *format)
{
    GBinContent *result;                    /* Instance à retourner        */

    result = format->content;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                                                                             *
*  Description : Indique la désignation interne du format.                    *
*                                                                             *
*  Retour      : Désignation du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_known_format_get_key(const GKnownFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = G_KNOWN_FORMAT_GET_CLASS(format)->get_key(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                                                                             *
*  Description : Fournit une description humaine du format.                   *
*                                                                             *
*  Retour      : Description du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_known_format_get_description(const GKnownFormat *format)
{
    char *result;                           /* Description à retourner     */

    result = G_KNOWN_FORMAT_GET_CLASS(format)->get_desc(format);

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

bool g_known_format_analyze(GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GKnownFormatClass *class;               /* Classe de l'instance        */

    handle_known_format_analysis(PGA_FORMAT_ANALYSIS_STARTED, format, gid, status);

    class = G_KNOWN_FORMAT_GET_CLASS(format);

    result = class->analyze(format, gid, status);

    handle_known_format_analysis(PGA_FORMAT_ANALYSIS_ENDED, format, gid, status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à manipuler.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Réalise un traitement post-désassemblage.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_known_format_complete_analysis(GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    GKnownFormatClass *class;               /* Classe de l'instance        */

    handle_known_format_analysis(PGA_FORMAT_POST_ANALYSIS_STARTED, format, gid, status);

    class = G_KNOWN_FORMAT_GET_CLASS(format);

    if (class->complete != NULL)
        class->complete(format, gid, status);

    handle_known_format_analysis(PGA_FORMAT_POST_ANALYSIS_ENDED, format, gid, status);

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un format depuis une mémoire tampon.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_known_format_load(GKnownFormat *format, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire rechargé    */

    content = G_BIN_CONTENT(g_object_storage_unpack_object(storage, "contents", pbuf));
    result = (content != NULL);

    if (result)
    {
        g_known_format_set_content(format, content);

        g_object_unref(G_OBJECT(content));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un format depuis une mémoire tampon.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_known_format_load(GKnownFormat *format, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GKnownFormatClass *class;               /* Classe à activer            */

    class = G_KNOWN_FORMAT_GET_CLASS(format);

    result = class->load(format, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un format dans une mémoire tampon.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_known_format_store(GKnownFormat *format, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    if (format->content == NULL)
        result = false;

    else
        result = g_object_storage_pack_object(storage, "contents", G_SERIALIZABLE_OBJECT(format->content), pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un format dans une mémoire tampon.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_known_format_store(GKnownFormat *format, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GKnownFormatClass *class;               /* Classe à activer            */

    class = G_KNOWN_FORMAT_GET_CLASS(format);

    result = class->store(format, storage, pbuf);

    return result;

}
