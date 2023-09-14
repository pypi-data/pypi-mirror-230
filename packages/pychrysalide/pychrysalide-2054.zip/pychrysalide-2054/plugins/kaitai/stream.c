
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.c - données associées à un flux de données Kaitai
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "stream.h"


#include "stream-int.h"



/* Initialise la classe des flux de données pour Kaitai. */
static void g_kaitai_stream_class_init(GKaitaiStreamClass *);

/* Initialise un flux de données accessibles à Kaitai. */
static void g_kaitai_stream_init(GKaitaiStream *);

/* Supprime toutes les références externes. */
static void g_kaitai_stream_dispose(GKaitaiStream *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_stream_finalize(GKaitaiStream *);



/* Indique le type défini pour un flux de données manipulé par une lecture Kaitai. */
G_DEFINE_TYPE(GKaitaiStream, g_kaitai_stream, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des flux de données pour Kaitai.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_stream_class_init(GKaitaiStreamClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_stream_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_stream_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un flux de données accessibles à Kaitai.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_stream_init(GKaitaiStream *stream)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_stream_dispose(GKaitaiStream *stream)
{
    G_OBJECT_CLASS(g_kaitai_stream_parent_class)->dispose(G_OBJECT(stream));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_stream_finalize(GKaitaiStream *stream)
{
    G_OBJECT_CLASS(g_kaitai_stream_parent_class)->finalize(G_OBJECT(stream));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire parcouru par une analyse Kaitai.   *
*                pos     = tête de lecture courante.                          *
*                                                                             *
*  Description : Rassemble les éléments constituant un flux de données Kaitai.*
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiStream *g_kaitai_stream_new(GBinContent *content, const vmpa2t *pos)
{
    GKaitaiStream *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_STREAM, NULL);

    if (!g_kaitai_stream_create(result, content, pos))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = lecteur d'attribut Kaitai à initialiser pleinement.*
*                content = contenu binaire parcouru par une analyse Kaitai.   *
*                pos     = tête de lecture courante.                          *
*                                                                             *
*  Description : Met en place un flux de données pour Kaitai.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_stream_create(GKaitaiStream *stream, GBinContent *content, const vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    stream->content = content;
    g_object_ref(G_OBJECT(content));

    copy_vmpa(&stream->pos, pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream  = flux de données Kaitai à consulter.                *
*                                                                             *
*  Description : Indique le contenu de données binaires lié au flux Kaitai.   *
*                                                                             *
*  Retour      : Contenu binaire associé au flux de données.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_kaitai_stream_get_content(const GKaitaiStream *stream)
{
    GBinContent *result;                    /* Instance à renvoyer         */

    result = stream->content;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream  = flux de données Kaitai à consulter.                *
*                                                                             *
*  Description : Détermine si la fin des données a été atteinte.              *
*                                                                             *
*  Retour      : true si la tête de lecture est en position finale, ou false. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_stream_has_reached_eof(const GKaitaiStream *stream)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t end;                             /* Position finale du flux     */
    int ret;                                /* Bilan d'une comparaison     */

    g_binary_content_compute_end_pos(stream->content, &end);

    ret = cmp_vmpa_by_phy(&stream->pos, &end);

    result = (ret == 0);

    return result;

}
