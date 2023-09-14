
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - conservation d'une correspondance entre attribut et binaire
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


#include "item.h"


#include <assert.h>
#include <string.h>


#include "item-int.h"



/* -------------------- DEFINITION D'UNE CORRESPONDANCE UNITAIRE -------------------- */


/* Initialise la classe des correspondances attribut/binaire. */
static void g_record_item_class_init(GRecordItemClass *);

/* Initialise une correspondance entre attribut et binaire. */
static void g_record_item_init(GRecordItem *);

/* Supprime toutes les références externes. */
static void g_record_item_dispose(GRecordItem *);

/* Procède à la libération totale de la mémoire. */
static void g_record_item_finalize(GRecordItem *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Calcule ou fournit la zone couverte par une correspondance. */
static void g_record_item_get_range(const GRecordItem *, mrange_t *);



/* ---------------------------------------------------------------------------------- */
/*                      DEFINITION D'UNE CORRESPONDANCE UNITAIRE                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une correspondance entre un attribut et du binaire. */
G_DEFINE_TYPE(GRecordItem, g_record_item, G_TYPE_MATCH_RECORD);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des correspondances attribut/binaire.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_item_class_init(GRecordItemClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GMatchRecordClass *record;              /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_record_item_dispose;
    object->finalize = (GObjectFinalizeFunc)g_record_item_finalize;

    record = G_MATCH_RECORD_CLASS(klass);

    record->get_range = (get_record_range_fc)g_record_item_get_range;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une correspondance entre attribut et binaire.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_item_init(GRecordItem *item)
{
    copy_mrange(&item->range, UNUSED_MRANGE_PTR);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_item_dispose(GRecordItem *item)
{
    G_OBJECT_CLASS(g_record_item_parent_class)->dispose(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_item_finalize(GRecordItem *item)
{
    G_OBJECT_CLASS(g_record_item_parent_class)->finalize(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                range   = zone couverture par la correspondance.             *
*                endian  = boustime des données à respecter.                  *
*                                                                             *
*  Description : Crée une nouvelle correspondance entre attribut et binaire.  *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRecordItem *g_record_item_new(GKaitaiAttribute *attrib, GBinContent *content, const mrange_t *range, SourceEndian endian)
{
    GRecordItem *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_RECORD_ITEM, NULL);

    if (!g_record_item_create(result, attrib, content, range, endian))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item    = correspondance à initialiser pleinement.           *
*                attrib  = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                range   = zone couverte par la correspondance.               *
*                endian  = boustime des données à respecter.                  *
*                                                                             *
*  Description : Met en place une correspondance entre attribut et binaire.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_item_create(GRecordItem *item, GKaitaiAttribute *attrib, GBinContent *content, const mrange_t *range, SourceEndian endian)
{
    bool result;                            /* Bilan à retourner           */

    result = g_match_record_create(G_MATCH_RECORD(item), G_KAITAI_PARSER(attrib), content);

    if (result)
    {
        copy_mrange(&item->range, range);

        item->endian = endian;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = correspondance à consulter.                           *
*                out  = tableau d'octets retournés. [OUT]                     *
*                len  = taille de ce tableau alloué. [OUT]                    *
*                                                                             *
*  Description : Lit la série d'octets d'un élément Kaitai entier représenté. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_item_get_truncated_bytes(const GRecordItem *item, bin_t **out, size_t *len)
{
    bool result;                            /* Bilan à retourner           */
    GKaitaiParser *parser;                  /* Attribut associé à l'élément*/

    parser = g_match_record_get_creator(G_MATCH_RECORD(item));
    assert(G_IS_KAITAI_ATTRIBUTE(parser));

    result = g_kaitai_attribute_read_truncated_bytes(G_KAITAI_ATTRIBUTE(parser),
                                                     G_MATCH_RECORD(item)->content,
                                                     &item->range,
                                                     out, len);

    g_object_unref(G_OBJECT(parser));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = correspondance à consulter.                           *
*                out  = valeur à sauvegarder sous une forme générique. [OUT]  *
*                                                                             *
*  Description : Lit la valeur d'un élément Kaitai entier représenté.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_item_get_value(const GRecordItem *item, resolved_value_t *out)
{
    bool result;                            /* Bilan à retourner           */
    GKaitaiParser *parser;                  /* Attribut associé à l'élément*/

    parser = g_match_record_get_creator(G_MATCH_RECORD(item));
    assert(G_IS_KAITAI_ATTRIBUTE(parser));

    result = g_kaitai_attribute_read_value(G_KAITAI_ATTRIBUTE(parser),
                                           G_MATCH_RECORD(item)->content,
                                           &item->range,
                                           item->endian, out);

    g_object_unref(G_OBJECT(parser));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = correspondance à consulter.                          *
*                range = zone de couverture déterminée. [OUT]                 *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_item_get_range(const GRecordItem *item, mrange_t *range)
{
    copy_mrange(range, &item->range);

}
