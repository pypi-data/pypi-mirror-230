
/* Chrysalide - Outil d'analyse de fichiers binaires
 * value.c - conservation d'une correspondance entre attribut et binaire
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


#include "value.h"


#include <assert.h>
#include <stdarg.h>
#include <string.h>


#include "value-int.h"
#include "../parsers/attribute.h"



/* -------------------- DEFINITION D'UNE CORRESPONDANCE UNITAIRE -------------------- */


/* Initialise la classe des valeurs purement calculées. */
static void g_record_value_class_init(GRecordValueClass *);

/* Initialise une correspondance entre attribut et binaire. */
static void g_record_value_init(GRecordValue *);

/* Supprime toutes les références externes. */
static void g_record_value_dispose(GRecordValue *);

/* Procède à la libération totale de la mémoire. */
static void g_record_value_finalize(GRecordValue *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Calcule ou fournit la zone couverte par une correspondance. */
static void g_record_value_get_range(const GRecordValue *, mrange_t *);



/* ---------------------------------------------------------------------------------- */
/*                      DEFINITION D'UNE CORRESPONDANCE UNITAIRE                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une valeur calculée selon des correspondances établies. */
G_DEFINE_TYPE(GRecordValue, g_record_value, G_TYPE_MATCH_RECORD);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des valeurs purement calculées.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_value_class_init(GRecordValueClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GMatchRecordClass *record;              /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_record_value_dispose;
    object->finalize = (GObjectFinalizeFunc)g_record_value_finalize;

    record = G_MATCH_RECORD_CLASS(klass);

    record->get_range = (get_record_range_fc)g_record_value_get_range;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une correspondance entre attribut et binaire.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_value_init(GRecordValue *value)
{
    init_record_scope(&value->locals, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_value_dispose(GRecordValue *value)
{
    reset_record_scope(&value->locals);

    G_OBJECT_CLASS(g_record_value_parent_class)->dispose(G_OBJECT(value));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_value_finalize(GRecordValue *value)
{
    G_OBJECT_CLASS(g_record_value_parent_class)->finalize(G_OBJECT(value));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst   = analyseur à l'origine de la correspondance.         *
*                locals = correspondances courantes pour résolutions.         *
*                                                                             *
*  Description : Crée une nouvelle valeur calculée à partir d'une instance.   *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRecordValue *g_record_value_new(GKaitaiInstance *inst, const kaitai_scope_t *locals)
{
    GRecordValue *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_RECORD_VALUE, NULL);

    if (!g_record_value_create(result, inst, locals))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value  = correspondance à initialiser pleinement.            *
*                inst   = analyseur à l'origine de la correspondance.         *
*                locals = correspondances courantes pour résolutions.         *
*                                                                             *
*  Description : Met en place une valeur calculée à partir d'une instance.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_value_create(GRecordValue *value, GKaitaiInstance *inst, const kaitai_scope_t *locals)
{
    bool result;                            /* Bilan à retourner           */

    result = g_match_record_create(G_MATCH_RECORD(value), G_KAITAI_PARSER(inst), NULL);

    if (result)
        copy_record_scope(&value->locals, locals);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = correspondance à consulter.                          *
*                value = valeur à sauvegarder sous une forme générique. [OUT] *
*                                                                             *
*  Description : Détermine la valeur d'un élément Kaitai calculé.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_value_compute_value(const GRecordValue *value, resolved_value_t *out)
{
    bool result;                            /* Bilan à retourner           */
    GKaitaiParser *parser;                  /* Instance liée à l'élément   */

    parser = g_match_record_get_creator(G_MATCH_RECORD(value));
    assert(G_IS_KAITAI_ATTRIBUTE(parser));

    result = g_kaitai_instance_compute_value(G_KAITAI_INSTANCE(parser),
                                             &value->locals,
                                             out);

    g_object_unref(G_OBJECT(parser));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = correspondance à consulter.                          *
*                value = valeur à sauvegarder sous une forme générique. [OUT] *
*                                                                             *
*  Description : Détermine et ajuste la valeur d'un élément Kaitai calculé.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_value_compute_and_aggregate_value(const GRecordValue *value, resolved_value_t *out)
{
    bool result;                            /* Bilan à retourner           */
    GKaitaiParser *parser;                  /* Instance liée à l'élément   */
    sized_string_t converted;               /* Conversion finale ?         */

    parser = g_match_record_get_creator(G_MATCH_RECORD(value));
    assert(G_IS_KAITAI_ATTRIBUTE(parser));

    result = g_kaitai_instance_compute_value(G_KAITAI_INSTANCE(parser),
                                             &value->locals,
                                             out);

    g_object_unref(G_OBJECT(parser));

    if (result)
    {
        /**
         * Lorsque c'est possible, les tableaux Kaitai sont transformés en série
         * d'octets.
         *
         * Même si les tableaux ont une grande portée en interne des règles
         * Kaitai (par exemple pour constituer une table de constantes de
         * référence), il en est différemment à l'extérieur du processus de
         * traitement : les tableaux sont le plus souvent destinés à manipuler
         * les octets représentés directement (par exemple :
         * "contents: [0xca, 0xfe, 0xba, 0xbe]").
         *
         * Pour les valeurs d'instance dont le type n'est pas explicite,
         * le choix est fait de tenter de simplifier la vie de l'utilisateur
         * en lui fournissant directement les octets qu'il attend probablement
         * plutôt qu'un tableau contenant des octets à extraire.
         */

        if (out->type == GVT_ARRAY)
        {
            if (g_kaitai_array_convert_to_bytes(out->array, &converted))
            {
                EXIT_RESOLVED_VALUE(*out);

                out->bytes = converted;
                out->type = GVT_BYTES;

            }

        }

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : value  = correspondance à consulter.                         *
*                range = zone de couverture déterminée. [OUT]                 *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_value_get_range(const GRecordValue *value, mrange_t *range)
{
    copy_mrange(range, UNUSED_MRANGE_PTR);

}
