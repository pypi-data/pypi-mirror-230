
/* Chrysalide - Outil d'analyse de fichiers binaires
 * uint.c - lecture d'un mot à partir de données binaires
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


#include "uint.h"


#include <assert.h>


#include "uint-int.h"
#include "../exprs/literal.h"
#include "../../../common/extstr.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des lectures de valeurs entières. */
static void g_scan_uint_function_class_init(GScanUintFunctionClass *);

/* Initialise une instance de lecture de valeur entière. */
static void g_scan_uint_function_init(GScanUintFunction *);

/* Supprime toutes les références externes. */
static void g_scan_uint_function_dispose(GScanUintFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_uint_function_finalize(GScanUintFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_uint_function_get_name(const GScanUintFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_uint_function_run_call(GScanUintFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une lecture de mot à partir de données binaires. */
G_DEFINE_TYPE(GScanUintFunction, g_scan_uint_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des lectures de valeurs entières.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_uint_function_class_init(GScanUintFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_uint_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_uint_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_uint_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_uint_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de lecture de valeur entière.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_uint_function_init(GScanUintFunction *func)
{
    func->size = MDS_UNDEFINED;
    func->endian = SRE_LITTLE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_uint_function_dispose(GScanUintFunction *func)
{
    G_OBJECT_CLASS(g_scan_uint_function_parent_class)->dispose(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_uint_function_finalize(GScanUintFunction *func)
{
    G_OBJECT_CLASS(g_scan_uint_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : size = taille du mot à venir lire dans les données.          *
*                                                                             *
*  Description : Constitue une fonction de lecture de valeur entière.         *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_uint_function_new(MemoryDataSize size, SourceEndian endian)
{
    GRegisteredItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_UINT_FUNCTION, NULL);

    if (!g_scan_uint_function_create(G_SCAN_UINT_FUNCTION(result), size, endian))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = encadrement d'un parcours de correspondances.         *
*                size = taille du mot à venir lire dans les données.          *
*                                                                             *
*  Description : Met en place un nouvelle fonction de lecture d'entiers.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_uint_function_create(GScanUintFunction *func, MemoryDataSize size, SourceEndian endian)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    func->size = size;
    func->endian = endian;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément d'appel à consulter.                          *
*                                                                             *
*  Description : Indique le nom associé à une expression d'évaluation.        *
*                                                                             *
*  Retour      : Désignation humaine de l'expression d'évaluation.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_scan_uint_function_get_name(const GScanUintFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    switch (item->size & ~MDS_SIGN)
    {
        case MDS_8_BITS_UNSIGNED:
            result = strdup("int8");
            break;

        case MDS_16_BITS_UNSIGNED:
            result = strdup("int16");
            break;

        case MDS_32_BITS_UNSIGNED:
            result = strdup("int32");
            break;

        case MDS_64_BITS_UNSIGNED:
            result = strdup("int64");
            break;

        default:
            assert(false);
            result = NULL;
            break;

    }

    if (result)
    {
        if (!MDS_IS_SIGNED(item->size))
            result = strprep(result, "u");

        if (item->endian == SRE_BIG)
            result = stradd(result, "be");

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = élément d'appel à consulter.                         *
*                args  = liste d'éventuels arguments fournis.                 *
*                count = taille de cette liste.                               *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                out   = zone d'enregistrement de la résolution opérée. [OUT] *
*                                                                             *
*  Description : Réduit une expression à une forme plus simple.               *
*                                                                             *
*  Retour      : Réduction correspondante, expression déjà réduite, ou NULL.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_uint_function_run_call(GScanUintFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    unsigned long long offset;              /* Position du mot ciblé       */
    GBinContent *content;                   /* Contenu à manipuler         */
    vmpa2t pos;                             /* Tête de lecture             */
    uint8_t val_s8;                          /* Valeur entière sur 8 bits   */
    uint8_t val_u8;                          /* Valeur entière sur 8 bits   */
    uint16_t val_s16;                        /* Valeur entière sur 16 bits  */
    uint16_t val_u16;                        /* Valeur entière sur 16 bits  */
    uint32_t val_s32;                        /* Valeur entière sur 32 bits  */
    uint32_t val_u32;                        /* Valeur entière sur 32 bits  */
    uint64_t val_s64;                        /* Valeur entière sur 64 bits  */
    uint64_t val_u64;                        /* Valeur entière sur 64 bits  */

    result = (count == 1 && G_IS_SCAN_LITERAL_EXPRESSION(args[0]));
    if (!result) goto exit;

    result = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[0]), &offset);
    if (!result) goto exit;

    content = g_scan_context_get_content(ctx);

    g_binary_content_compute_start_pos(content, &pos);
    advance_vmpa(&pos, offset);

    switch (item->size)
    {
        case MDS_8_BITS_SIGNED:
            result = g_binary_content_read_s8(content, &pos, &val_s8);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_SIGNED_INTEGER,
                                                              (long long []){ val_s8 }));
            break;

        case MDS_8_BITS_UNSIGNED:
            result = g_binary_content_read_u8(content, &pos, &val_u8);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER,
                                                              (unsigned long long []){ val_u8 }));
            break;

        case MDS_16_BITS_SIGNED:
            result = g_binary_content_read_s16(content, &pos, item->endian, &val_s16);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_SIGNED_INTEGER,
                                                              (long long []){ val_s16 }));
            break;

        case MDS_16_BITS_UNSIGNED:
            result = g_binary_content_read_u16(content, &pos, item->endian, &val_u16);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER,
                                                              (unsigned long long []){ val_u16 }));
            break;

        case MDS_32_BITS_SIGNED:
            result = g_binary_content_read_s32(content, &pos, item->endian, &val_s32);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_SIGNED_INTEGER,
                                                              (long long []){ val_s32 }));
            break;

        case MDS_32_BITS_UNSIGNED:
            result = g_binary_content_read_u32(content, &pos, item->endian, &val_u32);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER,
                                                              (unsigned long long []){ val_u32 }));
            break;

        case MDS_64_BITS_SIGNED:
            result = g_binary_content_read_s64(content, &pos, item->endian, &val_s64);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_SIGNED_INTEGER,
                                                              (long long []){ val_s64 }));
            break;

        case MDS_64_BITS_UNSIGNED:
            result = g_binary_content_read_u64(content, &pos, item->endian, &val_u64);
            if (result)
                *out = G_OBJECT(g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER,
                                                              (unsigned long long []){ val_u64 }));
            break;

        default:
            break;

    }

    g_object_unref(G_OBJECT(content));

 exit:

    return result;

}
