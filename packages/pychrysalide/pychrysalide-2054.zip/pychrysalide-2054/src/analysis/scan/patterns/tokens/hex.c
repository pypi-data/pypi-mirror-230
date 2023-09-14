
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.c - recherche de morceaux de binaire
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "hex.h"


#include <malloc.h>
#include <string.h>


#include "hex-int.h"



/* ----------------------- RECHERCHE D'UN MOTIF DE TEXTE BRUT ----------------------- */


/* Initialise la classe des recherches de texte brut. */
static void g_scan_hex_bytes_class_init(GScanHexBytesClass *klass);

/* Initialise une instance de recherche de texte brut. */
static void g_scan_hex_bytes_init(GScanHexBytes *);

/* Supprime toutes les références externes. */
static void g_scan_hex_bytes_dispose(GScanHexBytes *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_hex_bytes_finalize(GScanHexBytes *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Affiche un motif de recherche au format texte. */
static void g_scan_hex_bytes_output_to_text(const GScanHexBytes *, GScanContext *, int);

/* Affiche un motif de recherche au format JSON. */
static void g_scan_hex_bytes_output_to_json(const GScanHexBytes *, GScanContext *, const sized_string_t *, unsigned int, int);



/* ---------------------------------------------------------------------------------- */
/*                         RECHERCHE D'UN MOTIF DE TEXTE BRUT                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une suite d'octets à retrouver dans un binaire. */
G_DEFINE_TYPE(GScanHexBytes, g_scan_hex_bytes, G_TYPE_STRING_TOKEN);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des recherches de texte brut.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_hex_bytes_class_init(GScanHexBytesClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GSearchPatternClass *pattern;           /* Version de classe ancêtre   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_hex_bytes_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_hex_bytes_finalize;

    pattern = G_SEARCH_PATTERN_CLASS(klass);

    pattern->to_text = (output_pattern_to_text_fc)g_scan_hex_bytes_output_to_text;
    pattern->to_json = (output_pattern_to_json_fc)g_scan_hex_bytes_output_to_json;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bytes = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de recherche de texte brut.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_hex_bytes_init(GScanHexBytes *bytes)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bytes = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_hex_bytes_dispose(GScanHexBytes *bytes)
{
    G_OBJECT_CLASS(g_scan_hex_bytes_parent_class)->dispose(G_OBJECT(bytes));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bytes = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_hex_bytes_finalize(GScanHexBytes *bytes)
{
    G_OBJECT_CLASS(g_scan_hex_bytes_parent_class)->finalize(G_OBJECT(bytes));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root  = représentation du motif à recherche.                 *
*                private  = donne une vocation privée au motif de recherche.  *
*                                                                             *
*  Description : Construit un gestionnaire de recherche de texte brut.        *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSearchPattern *g_scan_hex_bytes_new(GScanTokenNode *root, bool private)
{
    GSearchPattern *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_HEX_BYTES, NULL);

    if (!g_scan_hex_bytes_create(G_SCAN_HEX_BYTES(result), root, private))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bytes = encadrement de motif à initialiser pleinement.       *
*                root  = représentation du motif à recherche.                 *
*                private  = donne une vocation privée au motif de recherche.  *
*                                                                             *
*  Description : Met en place un gestionnaire de recherche de binaire.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_hex_bytes_create(GScanHexBytes *bytes, GScanTokenNode *root, bool private)
{
    bool result;                            /* Bilan à retourner           */

    result = g_string_token_create(G_STRING_TOKEN(bytes), root, false, private);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context = contexte de l'analyse à mener.                     *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche un motif de recherche au format texte.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_hex_bytes_output_to_text(const GScanHexBytes *pattern, GScanContext *context, int fd)
{
    G_SEARCH_PATTERN_CLASS(g_scan_hex_bytes_parent_class)->to_text(G_SEARCH_PATTERN(pattern), context, fd);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context  = contexte de l'analyse à mener.                    *
*                padding  = éventuel bourrage initial à placer ou NULL.       *
*                level    = profondeur actuelle.                              *
*                fd       = canal d'écriture.                                 *
*                                                                             *
*  Description : Affiche un motif de recherche au format JSON.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_hex_bytes_output_to_json(const GScanHexBytes *pattern, GScanContext *context, const sized_string_t *padding, unsigned int level, int fd)
{
    G_SEARCH_PATTERN_CLASS(g_scan_hex_bytes_parent_class)->to_json(G_SEARCH_PATTERN(pattern), context, padding, level, fd);

    /* TODO */

}
