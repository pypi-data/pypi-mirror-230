
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.c - spécification d'un lecteur Kaitai
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


#include "parser.h"


#include "parser-int.h"



/* Initialise la classe des lecteurs de spécification Kaitai. */
static void g_kaitai_parser_class_init(GKaitaiParserClass *);

/* Initialise un lecteur de spécification Kaitai. */
static void g_kaitai_parser_init(GKaitaiParser *);

/* Supprime toutes les références externes. */
static void g_kaitai_parser_dispose(GKaitaiParser *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_parser_finalize(GKaitaiParser *);



/* Indique le type défini pour un lecteur de spécification Kaitai. */
G_DEFINE_TYPE(GKaitaiParser, g_kaitai_parser, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des lecteurs de spécification Kaitai.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_parser_class_init(GKaitaiParserClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_parser_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_parser_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parser = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un lecteur de spécification Kaitai.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_parser_init(GKaitaiParser *parser)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parser = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_parser_dispose(GKaitaiParser *parser)
{
    G_OBJECT_CLASS(g_kaitai_parser_parent_class)->dispose(G_OBJECT(parser));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parser = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_parser_finalize(GKaitaiParser *parser)
{
    G_OBJECT_CLASS(g_kaitai_parser_parent_class)->finalize(G_OBJECT(parser));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parser  = structure Kaitai en cours de parcours.             *
*                locals  = variables locales pour les résolutions de types.   *
*                content = données binaires à analyser et traduire.           *
*                pos     = tête de lecture courante. [OUT]                    *
*                record  = noeud d'arborescence d'éléments rencontrés. [OUT]  *
*                                                                             *
*  Description : Parcourt un contenu binaire selon des spécifications Kaitai. *
*                                                                             *
*  Retour      : Bilan de l'opératon : true pour continuer, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_parser_parse_content(GKaitaiParser *parser, kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    GKaitaiParserClass *class;              /* Classe de l'instance        */

    class = G_KAITAI_PARSER_GET_CLASS(parser);

    result = class->parse(parser, locals, content, pos, record);

    if (result)
        remember_last_record(locals, *record);

    return result;

}
