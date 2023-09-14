
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - support des différents formats binaires
 *
 * Copyright (C) 2009-2020 Cyrille Bagard
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


#include "format.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "format-int.h"
#include "preload.h"
#include "../arch/processor.h"
#include "../common/sort.h"
#include "../core/demanglers.h"
#include "../plugins/pglist.h"



/* Initialise la classe des formats binaires génériques. */
static void g_binary_format_class_init(GBinFormatClass *);

/* Initialise une instance de format binaire générique. */
static void g_binary_format_init(GBinFormat *);

/* Supprime toutes les références externes. */
static void g_binary_format_dispose(GBinFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_binary_format_finalize(GBinFormat *);

/* Charge les plages de couvertures depuis une mémoire tampon. */
static bool g_binary_format_load_start_points(GBinFormat *, packed_buffer_t *);

/* Sauvegarde les points de départ enregistrés pour un format. */
static bool g_binary_format_store_start_points(GBinFormat *, packed_buffer_t *);



/* ---------------------- RASSEMBLEMENT ET GESTION DE SYMBOLES ---------------------- */


/* Retire un symbole de la collection du format binaire. */
static void _g_binary_format_remove_symbol(GBinFormat *, size_t);

/* Recherche le symbole associé à une adresse. */
static bool _g_binary_format_find_symbol(const GBinFormat *, const vmpa2t *, __compar_fn_t, size_t *, GBinSymbol **);

/* Recherche un symbole particulier. */
static bool __g_binary_format_find_symbol(const GBinFormat *, const void *, __compar_fn_t, size_t *, GBinSymbol **);



/* ------------------ CONSERVATION DES SOUCIS DURANT LE CHARGEMENT ------------------ */


/* Charge les erreurs de chargement depuis une mémoire tampon. */
static bool g_binary_format_load_errors(GBinFormat *, packed_buffer_t *);

/* Sauvegarde les erreurs de chargement dans une mémoire tampon. */
static bool g_binary_format_store_errors(GBinFormat *, packed_buffer_t *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Charge un format depuis une mémoire tampon. */
static bool g_binary_format_load(GBinFormat *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un format dans une mémoire tampon. */
static bool g_binary_format_store(GBinFormat *, GObjectStorage *, packed_buffer_t *);





/* Indique le type défini pour un format binaire générique. */
G_DEFINE_TYPE(GBinFormat, g_binary_format, G_TYPE_KNOWN_FORMAT);


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

static void g_binary_format_class_init(GBinFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_binary_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_binary_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->load = (load_known_fc)g_binary_format_load;
    known->store = (load_known_fc)g_binary_format_store;

    g_signal_new("symbol-added",
                 G_TYPE_BIN_FORMAT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinFormatClass, symbol_added),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

    g_signal_new("symbol-removed",
                 G_TYPE_BIN_FORMAT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinFormatClass, symbol_removed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

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

static void g_binary_format_init(GBinFormat *format)
{
    fmt_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_FORMAT_EXTRA(format);

    INIT_GOBJECT_EXTRA_LOCK(extra);

    g_rw_lock_init(&format->pt_lock);

    format->info = g_preload_info_new();

    format->demangler = NULL;

    g_rw_lock_init(&format->syms_lock);
#ifndef NDEBUG
    g_atomic_int_set(&format->sym_locked, 0);
#endif

    format->errors = NULL;
    format->error_count = 0;
    g_mutex_init(&format->error_mutex);
#ifndef NDEBUG
    g_atomic_int_set(&format->error_locked, 0);
#endif

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

static void g_binary_format_dispose(GBinFormat *format)
{
    size_t i;                               /* Boucle de parcours          */

    g_rw_lock_clear(&format->pt_lock);

    g_clear_object(&format->info);

    g_clear_object(&format->demangler);

    for (i = 0; i < format->sym_count; i++)
        g_clear_object(&format->symbols[i]);

    g_rw_lock_clear(&format->syms_lock);

    g_mutex_clear(&format->error_mutex);

    G_OBJECT_CLASS(g_binary_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_binary_format_finalize(GBinFormat *format)
{
    DisassPriorityLevel i;                  /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */

    for (i = 0; i < DPL_COUNT; i++)
        if (format->start_points[i] != NULL)
            free(format->start_points[i]);

    if (format->symbols != NULL)
        free(format->symbols);

    if (format->errors != NULL)
    {
        for (k = 0; k < format->error_count; k++)
            if (format->errors[k].desc != NULL)
                free(format->errors[k].desc);

        free(format->errors);

    }

    G_OBJECT_CLASS(g_binary_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format à venir modifier.                            *
*                flag   = drapeau d'information complémentaire à planter.     *
*                                                                             *
*  Description : Ajoute une information complémentaire à un format.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_set_flag(GBinFormat *format, FormatFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    fmt_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_FORMAT_EXTRA(format);

    LOCK_GOBJECT_EXTRA(extra);

    result = !(extra->flags & flag);

    extra->flags |= flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format à venir modifier.                            *
*                flag   = drapeau d'information complémentaire à planter.     *
*                                                                             *
*  Description : Retire une information complémentaire à un format.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_unset_flag(GBinFormat *format, FormatFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    fmt_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_FORMAT_EXTRA(format);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    extra->flags &= ~flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format à venir consulter.                           *
*                flag   = drapeau d'information à rechercher.                 *
*                                                                             *
*  Description : Détermine si un format possède un fanion particulier.        *
*                                                                             *
*  Retour      : Bilan de la détection.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_has_flag(const GBinFormat *format, FormatFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    fmt_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_FORMAT_EXTRA(format);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format à venir consulter.                           *
*                                                                             *
*  Description : Fournit les particularités du format.                        *
*                                                                             *
*  Retour      : Somme de tous les fanions associés au format.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

FormatFlag g_binary_format_get_flags(const GBinFormat *format)
{
    FormatFlag result;                      /* Fanions à retourner         */
    fmt_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_FORMAT_EXTRA(format);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & FFL_MASK);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Indique le boutisme employé par le format binaire analysé.   *
*                                                                             *
*  Retour      : Boutisme associé au format.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SourceEndian g_binary_format_get_endianness(const GBinFormat *format)
{
    SourceEndian result;                    /* Boutisme à retourner        */

    result = G_BIN_FORMAT_GET_CLASS(format)->get_endian(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                pt     = point de l'espace mémoire à considérer.             *
*                level  = indication de priorité et d'origine de l'adresse.   *
*                                                                             *
*  Description : Enregistre une adresse comme début d'une zone de code.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_register_code_point(GBinFormat *format, virt_t pt, DisassPriorityLevel level)
{
    assert(level < DPL_COUNT);

    g_rw_lock_writer_lock(&format->pt_lock);

    if (format->pt_count[level] == format->pt_allocated[level])
    {
        format->pt_allocated[level] += EXTRA_POINT_BLOCK;

        format->start_points[level] = realloc(format->start_points[level],
                                              format->pt_allocated[level] * sizeof(virt_t));

    }

    format->start_points[level][format->pt_count[level]++] = pt;

    g_rw_lock_writer_unlock(&format->pt_lock);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture concernée par la procédure.              *
*                pbuf = zone tampon à vider.                                  *
*                                                                             *
*  Description : Charge les plages de couvertures depuis une mémoire tampon.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_format_load_start_points(GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    DisassPriorityLevel i;                  /* Boucle de parcours #1       */
    uleb128_t count;                        /* Quantité de points présents */
    size_t k;                               /* Boucle de parcours #2       */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = true;

    g_rw_lock_writer_lock(&format->pt_lock);

    for (i = 0; i < DPL_COUNT && result; i++)
    {
        result = unpack_uleb128(&count, pbuf);
        if (!result) break;

        format->pt_allocated[i] = count;
        format->pt_count[i] = count;

        format->start_points[i] = calloc(format->pt_count[i], sizeof(virt_t));

        for (k = 0; k < format->pt_count[i] && result; k++)
        {
            result = unpack_uleb128(&value, pbuf);
            if (!result) break;

            format->start_points[i][k] = value;

        }

    }

    g_rw_lock_writer_unlock(&format->pt_lock);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                pbuf = zone tampon à remplir.                                *
*                                                                             *
*  Description : Sauvegarde les points de départ enregistrés pour un format.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_format_store_start_points(GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    DisassPriorityLevel i;                  /* Boucle de parcours #1       */
    size_t count;                           /* Quantité de points présents */
    size_t k;                               /* Boucle de parcours #2       */

    result = true;

    g_rw_lock_writer_lock(&format->pt_lock);

    for (i = 0; i < DPL_COUNT && result; i++)
    {
        count = format->pt_count[i];

        result = pack_uleb128((uleb128_t []){ count }, pbuf);

        for (k = 0; k < count && result; k++)
            result = pack_uleb128((uleb128_t []){ format->start_points[i][k] }, pbuf);

    }

    g_rw_lock_writer_unlock(&format->pt_lock);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                ctx    = contexte de désassemblage à préparer.               *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Intègre dans un contexte les informations tirées d'un format.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_preload_disassembling_context(GBinFormat *format, GProcContext *ctx, GtkStatusStack *status)
{
    g_preload_info_copy(format->info, G_PRELOAD_INFO(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                ctx    = contexte de désassemblage à préparer.               *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Définit les points de départ d'un contexte de désassemblage. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_activate_disassembling_context(GBinFormat *format, GProcContext *ctx, GtkStatusStack *status)
{
    DisassPriorityLevel i;                  /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */

    g_rw_lock_reader_lock(&format->pt_lock);

    for (i = 0; i < DPL_COUNT; i++)
        for (k = 0; k < format->pt_count[i]; k++)
            g_proc_context_push_drop_point(ctx, i, format->start_points[i][k]);

    g_rw_lock_reader_unlock(&format->pt_lock);

}



/* ---------------------------------------------------------------------------------- */
/*                                DECODAGE DE SYMBOLES                                */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format binaire à consulter pour l'opération.        *
*                                                                             *
*  Description : Fournit le décodeur de symboles privilégié pour un format.   *
*                                                                             *
*  Retour      : Décodeur préféré ou NULL s'il n'est pas renseigné.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCompDemangler *g_binary_format_get_demangler(const GBinFormat *format)
{
    GCompDemangler *result;                 /* Décodeur à retourner        */

    result = format->demangler;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format binaire à consulter pour l'opération.        *
*                desc   = chaîne de caractères à décoder.                     *
*                                                                             *
*  Description : Décode une chaîne de caractères donnée en type.              *
*                                                                             *
*  Retour      : Instance obtenue ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_binary_format_decode_type(const GBinFormat *format, const char *desc)
{
    GDataType *result;                      /* Construction à remonter     */
    GCompDemangler *demangler;              /* Accès plus lisible          */

    demangler = format->demangler;

    if (demangler != NULL)
        result = g_compiler_demangler_decode_type(demangler, desc);
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format binaire à consulter pour l'opération.        *
*                desc   = chaîne de caractères à décoder.                     *
*                                                                             *
*  Description : Décode une chaîne de caractères donnée en routine.           *
*                                                                             *
*  Retour      : Instance obtenue ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_binary_format_decode_routine(const GBinFormat *format, const char *desc)
{
    GBinRoutine *result;                    /* Construction à remonter     */
    GCompDemangler *demangler;              /* Accès plus lisible          */

    demangler = format->demangler;

    if (demangler != NULL)
        result = g_compiler_demangler_decode_routine(demangler, desc);
    else
        result = NULL;

    if (result == NULL)
    {
        result = g_binary_routine_new();
        g_binary_routine_set_name(result, strdup(desc));
    }

    return result;

}


/* ---------------------------------------------------------------------------------- */
/*                        RASSEMBLEMENT ET GESTION DE SYMBOLES                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture à manipuler.                           *
*                state  = nouvel état de l'accès aux symboles.                *
*                                                                             *
*  Description : Protège ou lève la protection de l'accès aux symboles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_lock_unlock_symbols_rd(GBinFormat *format, bool state)
{
#ifndef NDEBUG
    gint test;                              /* Test de valeur courante     */
#endif

    if (state)
    {
        g_rw_lock_reader_lock(&format->syms_lock);
#ifndef NDEBUG
        g_atomic_int_inc(&format->sym_locked);
#endif
    }
    else
    {
#ifndef NDEBUG
        test = g_atomic_int_add(&format->sym_locked, -1);
        assert(test > 0);
#endif
        g_rw_lock_reader_unlock(&format->syms_lock);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture à manipuler.                           *
*                state  = nouvel état de l'accès aux symboles.                *
*                                                                             *
*  Description : Protège ou lève la protection de l'accès aux symboles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_lock_unlock_symbols_wr(GBinFormat *format, bool state)
{
    if (state)
    {
        g_rw_lock_writer_lock(&format->syms_lock);
#ifndef NDEBUG
        g_atomic_int_set(&format->sym_locked, 1);
#endif
    }
    else
    {
#ifndef NDEBUG
        g_atomic_int_set(&format->sym_locked, 0);
#endif
        g_rw_lock_writer_unlock(&format->syms_lock);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture à consulter via la procédure.          *
*                                                                             *
*  Description : Assure qu'un verrou est bien posé pour l'accès aux symboles. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#ifndef NDEBUG
void g_binary_format_check_for_symbols_lock(const GBinFormat *format)
{
    assert(g_atomic_int_get(&format->sym_locked) > 0);

}
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture à consulter via la procédure.          *
*                                                                             *
*  Description : Fournit la marque de dernière modification des symboles.     *
*                                                                             *
*  Retour      : Marque de la dernière modification de la liste de symboles.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int g_binary_format_get_symbols_stamp(const GBinFormat *format)
{
    return format->sym_stamp;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format visé par la procédure.                       *
*                                                                             *
*  Description : Compte le nombre de symboles représentés.                    *
*                                                                             *
*  Retour      : Nombre de symboles présents.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_binary_format_count_symbols(const GBinFormat *format)
{
    assert(g_atomic_int_get(&format->sym_locked) > 0);

    return format->sym_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format visé par la procédure.                       *
*                index  = indice du symbole visé.                             *
*                                                                             *
*  Description : Fournit un symbole lié à un format.                          *
*                                                                             *
*  Retour      : Symbole conservé trouvé ou NULL si aucun.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_binary_format_get_symbol(const GBinFormat *format, size_t index)
{
    GBinSymbol *result;                     /* Symbole à retourner         */

    assert(g_atomic_int_get(&format->sym_locked) > 0);

    if (format->sym_count == 0)
        result = NULL;

    else
    {
        assert(index < format->sym_count);

        result = format->symbols[index];
        assert(result != NULL);

        g_object_ref(G_OBJECT(result));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à compléter.                  *
*                symbol = symbole à ajouter à la liste.                       *
*                                                                             *
*  Description : Ajoute un symbole à la collection du format binaire.         *
*                                                                             *
*  Retour      : true si le symbole était bien localisé et a été inséré.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_add_symbol(GBinFormat *format, GBinSymbol *symbol)
{
    bool result;                            /* Statut d'ajout à retourner  */
#ifndef NDEBUG
    const mrange_t *range;                  /* Couverture du symbole       */
    const vmpa2t *addr;                     /* Emplacement du symbole      */
#endif
    size_t index;                           /* Indice du point d'insertion */

    /**
     * Pour que les fonctions de recherche basées sur _g_binary_format_find_symbol()
     * fassent bien leur office, il faut que les symboles soient triés.
     *
     * Cependant, les localisations à satisfaire lors d'une recherche recontrent
     * un problème si les positions physiques ne sont pas renseignées. En effet
     * les adresses virtuelles en sont potentiellement décorrélées (c'est le cas
     * avec le format ELF par exemple, où les zones en mémoire ne suivent pas le
     * même ordre que les segments du binaire).
     *
     * Comme les comparaisons entre localisations se réalisent sur les éléments
     * renseignés communs, à commencer par la position physique si c'est possible,
     * une localisation s'appuyant uniquement sur une adresse virtuelle va être
     * analysée suivant une liste non triée d'adresses virtuelles.
     *
     * On corrige donc le tir si besoin est en forçant la comparaison via les
     * positions physiques.
     */

#ifndef NDEBUG
    range = g_binary_symbol_get_range(symbol);
    addr = get_mrange_addr(range);

    assert(has_phys_addr(addr) || g_binary_symbol_get_status(symbol) == SSS_DYNAMIC);
#endif

    g_binary_format_lock_unlock_symbols_wr(format, true);

    /**
     * Avec tous les traitements parallèles, il est possible que plusieurs chemins d'exécution
     * amènent à la création d'un même symbole.
     *
     * Plutôt que de verrouiller la liste des symboles en amont (et donc assez longtemps)
     * pour faire une vérification avant construction puis ajout, on préfère limiter
     * l'état figé à cette seule fonction, quitte à annuler le travail fourni pour la
     * construction du symbole dans les cas peu fréquents où le symbole était déjà en place.
     */

    result = bsearch_index(&symbol, format->symbols, format->sym_count,
                           sizeof(GBinSymbol *), (__compar_fn_t)g_binary_symbol_cmp, &index);

    if (!result)
    {
        format->symbols = _qinsert(format->symbols, &format->sym_count,
                                   sizeof(GBinSymbol *), &symbol, index);

        format->sym_stamp++;
        result = true;

    }
    else
        g_object_unref(G_OBJECT(symbol));

    g_binary_format_lock_unlock_symbols_wr(format, false);

    if (result)
        g_signal_emit_by_name(format, "symbol-added", symbol);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à compléter.                 *
*                symbols = ensemble de symboles à ajouter à la liste.         *
*                count   = taille de cet ensemble.                            *
*                                                                             *
*  Description : Ajoute plusieurs symboles à la collection du format binaire. *
*                                                                             *
*  Retour      : true si les symboles dûment localisés ont été insérés.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_add_symbols(GBinFormat *format, GBinSymbol **symbols, size_t count)
{
    bool result;                            /* Statut d'ajout à retourner  */
#ifndef NDEBUG
    phys_t last;                            /* Dernière position rencontrée*/
#endif
    size_t i;                               /* Boucle de parcours          */
#ifndef NDEBUG
    const mrange_t *range;                  /* Couverture du symbole       */
    const vmpa2t *addr;                     /* Emplacement du symbole      */
#endif
    size_t index;                           /* Indice du point d'insertion */

    /**
     * Pour que les fonctions de recherche basées sur _g_binary_format_find_symbol()
     * fassent bien leur office, il faut que les symboles soient triés.
     *
     * Cependant, les localisations à satisfaire lors d'une recherche recontrent
     * un problème si les positions physiques ne sont pas renseignées. En effet
     * les adresses virtuelles en sont potentiellement décorrélées (c'est le cas
     * avec le format ELF par exemple, où les zones en mémoire ne suivent pas le
     * même ordre que les segments du binaire).
     *
     * Comme les comparaisons entre localisations se réalisent sur les éléments
     * renseignés communs, à commencer par la position physique si c'est possible,
     * une localisation s'appuyant uniquement sur une adresse virtuelle va être
     * analysée suivant une liste non triée d'adresses virtuelles.
     *
     * On corrige donc le tir si besoin est en forçant la comparaison via les
     * positions physiques.
     */

#ifndef NDEBUG
    last = VMPA_NO_PHYSICAL;

    for (i = 0; i < count; i++)
    {
        range = g_binary_symbol_get_range(symbols[i]);
        addr = get_mrange_addr(range);

        assert(has_phys_addr(addr) || g_binary_symbol_get_status(symbols[i]) == SSS_DYNAMIC);

        if (has_phys_addr(addr))
        {
            assert(last == VMPA_NO_PHYSICAL || last <= get_phy_addr(addr));
            last = get_phy_addr(addr);
        }

    }
#endif

    g_binary_format_lock_unlock_symbols_wr(format, true);

    /**
     * Avec tous les traitements parallèles, il est possible que plusieurs chemins d'exécution
     * amènent à la création d'un même symbole.
     *
     * Plutôt que de verrouiller la liste des symboles en amont (et donc assez longtemps)
     * pour faire une vérification avant construction puis ajout, on préfère limiter
     * l'état figé à cette seule fonction, quitte à annuler le travail fourni pour la
     * construction du symbole dans les cas peu fréquents où le symbole était déjà en place.
     */

    result = bsearch_index(&symbols[0], format->symbols, format->sym_count,
                           sizeof(GBinSymbol *), (__compar_fn_t)g_binary_symbol_cmp, &index);

    if (!result)
    {
        for (i = 0; i < count; i++)
            g_object_ref(G_OBJECT(symbols[i]));

        format->symbols = _qinsert_batch(format->symbols, &format->sym_count,
                                         sizeof(GBinSymbol *), symbols, count, index);

        format->sym_stamp++;
        result = true;

    }

    g_binary_format_lock_unlock_symbols_wr(format, false);

    if (result)
        for (i = 0; i < count; i++)
            g_signal_emit_by_name(format, "symbol-added", symbols[i]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à compléter.                  *
*                index  = indice du symbole à retirer de la liste.            *
*                                                                             *
*  Description : Retire un symbole de la collection du format binaire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _g_binary_format_remove_symbol(GBinFormat *format, size_t index)
{
    assert(g_atomic_int_get(&format->sym_locked) == 1);

    assert(index < format->sym_count);

    g_object_unref(G_OBJECT(format->symbols[index]));

    if ((index + 1) < format->sym_count)
        memmove(&format->symbols[index], &format->symbols[index + 1],
                (format->sym_count - index - 1) * sizeof(GBinSymbol *));

    format->symbols = realloc(format->symbols, --format->sym_count * sizeof(GBinSymbol *));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à compléter.                  *
*                symbol = symbole à retirer de la liste.                      *
*                                                                             *
*  Description : Retire un symbole de la collection du format binaire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_remove_symbol(GBinFormat *format, GBinSymbol *symbol)
{
    bool found;                             /* Jeton de présence           */
    size_t index;                           /* Indice du point de retrait  */

    g_object_ref(G_OBJECT(symbol));

    g_binary_format_lock_unlock_symbols_wr(format, true);

    found = bsearch_index(&symbol, format->symbols, format->sym_count,
                          sizeof(GBinSymbol *), (__compar_fn_t)g_binary_symbol_cmp, &index);

    if (found)
        _g_binary_format_remove_symbol(format, index);

    g_binary_format_lock_unlock_symbols_wr(format, false);

    if (found)
        g_signal_emit_by_name(format, "symbol-removed", symbol);

    g_object_unref(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                label  = étiquette à retrouver lors des recherches.          *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                                                                             *
*  Description : Recherche le symbole correspondant à une étiquette.          *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_find_symbol_by_label(GBinFormat *format, const char *label, GBinSymbol **symbol)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    char *cur_lbl;                          /* Etiquette courante          */

    result = false;

    g_binary_format_lock_symbols_rd(format);

    for (i = 0; i < format->sym_count && !result; i++)
    {
        cur_lbl = g_binary_symbol_get_label(format->symbols[i]);
        if (cur_lbl == NULL) continue;

        if (strcmp(label, cur_lbl) == 0)
        {
            *symbol = format->symbols[i];
            g_object_ref(G_OBJECT(*symbol));

            result = true;

        }

        free(cur_lbl);

    }

    g_binary_format_unlock_symbols_rd(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse à cibler lors des recherches.               *
*                fn     = méthode de comparaison des symboles.                *
*                index  = indice de l'éventuel symbole trouvé ou NULL. [OUT]  *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                                                                             *
*  Description : Recherche le symbole associé à une adresse.                  *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_binary_format_find_symbol(const GBinFormat *format, const vmpa2t *addr, __compar_fn_t fn, size_t *index, GBinSymbol **symbol)
{
    /**
     * Pour ce qui est des justifications quant à la vérification suivante,
     * se référer aux commentaires placés dans g_binary_format_add_symbol().
     */

    assert(has_phys_addr(addr));

    return __g_binary_format_find_symbol(format, addr, fn, index, symbol);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                key    = clef fournie pour distinguer les éléments.          *
*                fn     = méthode de comparaison des symboles.                *
*                index  = indice de l'éventuel symbole trouvé ou NULL. [OUT]  *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                                                                             *
*  Description : Recherche un symbole particulier.                            *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool __g_binary_format_find_symbol(const GBinFormat *format, const void *key, __compar_fn_t fn, size_t *index, GBinSymbol **symbol)
{
    bool result;                            /* Bilan à retourner           */
    void *found;                            /* Résultat de recherches      */

    assert(g_atomic_int_get(&format->sym_locked) > 0);

    found = bsearch(key, format->symbols, format->sym_count, sizeof(GBinSymbol *), fn);

    if (found != NULL)
    {
        if (index != NULL)
            *index = (GBinSymbol **)found - format->symbols;

        if (symbol != NULL)
        {
            *symbol = *(GBinSymbol **)found;
            g_object_ref(G_OBJECT(*symbol));
        }

        result = true;

    }

    else
    {
        if (symbol != NULL)
            *symbol = NULL;

        result = false;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse à cibler lors des recherches.               *
*                index  = indice de l'éventuel symbole trouvé. [OUT]          *
*                                                                             *
*  Description : Recherche l'indice du symbole correspondant à une adresse.   *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_find_symbol_index_at(GBinFormat *format, const vmpa2t *addr, size_t *index)
{
    bool result;                            /* Bilan à retourner           */

    int find_symbol(const vmpa2t *addr, const GBinSymbol **sym)
    {
        const mrange_t *range;              /* Espace mémoire parcouru     */

        range = g_binary_symbol_get_range(*sym);

        return cmp_vmpa(addr, get_mrange_addr(range));

    }

    g_binary_format_lock_symbols_rd(format);

    result = _g_binary_format_find_symbol(format, addr, (__compar_fn_t)find_symbol, index, NULL);

    g_binary_format_unlock_symbols_rd(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse à cibler lors des recherches.               *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                                                                             *
*  Description : Recherche le symbole correspondant à une adresse.            *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_find_symbol_at(GBinFormat *format, const vmpa2t *addr, GBinSymbol **symbol)
{
    bool result;                            /* Bilan à retourner           */

    int find_symbol(const vmpa2t *addr, const GBinSymbol **sym)
    {
        const mrange_t *range;              /* Espace mémoire parcouru     */

        range = g_binary_symbol_get_range(*sym);

        return cmp_vmpa(addr, get_mrange_addr(range));

    }

    g_binary_format_lock_symbols_rd(format);

    result = _g_binary_format_find_symbol(format, addr, (__compar_fn_t)find_symbol, NULL, symbol);

    g_binary_format_unlock_symbols_rd(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse à cibler lors des recherches.               *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                                                                             *
*  Description : Recherche le symbole contenant une adresse.                  *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_find_symbol_for(GBinFormat *format, const vmpa2t *addr, GBinSymbol **symbol)
{
    bool result;                            /* Bilan à retourner           */

    int find_symbol(const vmpa2t *addr, const GBinSymbol **sym)
    {
        const mrange_t *range;              /* Espace mémoire parcouru     */

        range = g_binary_symbol_get_range(*sym);

        return cmp_mrange_with_vmpa(range, addr);

    }

    g_binary_format_lock_symbols_rd(format);

    result = _g_binary_format_find_symbol(format, addr, (__compar_fn_t)find_symbol, NULL, symbol);

    g_binary_format_unlock_symbols_rd(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse à cibler lors des recherches.               *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                                                                             *
*  Description : Recherche le symbole suivant celui lié à une adresse.        *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_find_next_symbol_at(GBinFormat *format, const vmpa2t *addr, GBinSymbol **symbol)
{
    bool result;                            /* Bilan à retourner           */
    size_t index;                           /* Indice à considérer         */

    int find_symbol(const vmpa2t *addr, const GBinSymbol **sym)
    {
        const mrange_t *range;              /* Espace mémoire parcouru     */

        range = g_binary_symbol_get_range(*sym);

        return cmp_mrange_with_vmpa(range, addr);

    }

    g_binary_format_lock_symbols_rd(format);

    result = _g_binary_format_find_symbol(format, addr, (__compar_fn_t)find_symbol, &index, NULL);

    if (result && (index + 1) < format->sym_count)
    {
        *symbol = format->symbols[index + 1];
        g_object_ref(G_OBJECT(*symbol));

    }

    else
    {
        *symbol = NULL;
        result = false;
    }

    g_binary_format_unlock_symbols_rd(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                range  = zone à cibler lors des recherches.                  *
*                index  = indice de l'éventuel symbole trouvé. [OUT]          *
*                                                                             *
*  Description : Recherche le premier symbole inclus dans une zone mémoire.   *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_find_first_symbol_inside(GBinFormat *format, const mrange_t *range, size_t *index)
{
    bool result;                            /* Bilan à retourner           */
    const GBinSymbol *prev;                 /* Symbole précédent           */
    const mrange_t *srange;                 /* Espace mémoire associé      */
    int ret;                                /* Bilan de comparaison        */

    int find_symbol(const mrange_t *ref_range, const GBinSymbol **sym)
    {
        const mrange_t *sym_range;          /* Espace mémoire parcouru     */

        int ret;

        sym_range = g_binary_symbol_get_range(*sym);

        ret = cmp_mrange_with_vmpa(ref_range, get_mrange_addr(sym_range));

        ret *= -1;

        return ret;

    }

    g_rw_lock_reader_lock(&format->syms_lock);

    result = __g_binary_format_find_symbol(format, range, (__compar_fn_t)find_symbol, index, NULL);

    if (result)
        while (*index > 0)
        {
            prev = format->symbols[*index - 1];
            srange = g_binary_symbol_get_range(prev);

            ret = cmp_mrange_with_vmpa(range, get_mrange_addr(srange));
            assert(ret <= 0);

            if (ret < 0) break;
            else (*index)--;

        }

    g_rw_lock_reader_unlock(&format->syms_lock);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse à cibler lors des recherches.               *
*                strict = indication de tolérance acceptée.                   *
*                symbol = éventuel symbole trouvé à déréfenrencer. [OUT]      *
*                diff   = décalage entre l'adresse et le symbole. [OUT]       *
*                                                                             *
*  Description : Recherche le symbole correspondant à une adresse.            *
*                                                                             *
*  Retour      : true si l'opération a été un succès, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_resolve_symbol(GBinFormat *format, const vmpa2t *addr, bool strict, GBinSymbol **symbol, phys_t *diff)
{
     bool result;                            /* Bilan à retourner           */
     const mrange_t *range;                  /* Espace mémoire parcouru     */

     if (strict)
         result = g_binary_format_find_symbol_at(format, addr, symbol);
     else
         result = g_binary_format_find_symbol_for(format, addr, symbol);

     if (result)
     {
         range = g_binary_symbol_get_range(*symbol);
         *diff = compute_vmpa_diff(get_mrange_addr(range), addr);

         assert(!strict || *diff == 0);

     }

     else
         *diff = 0;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    CONSERVATION DES SOUCIS DURANT LE CHARGEMENT                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture à manipuler.                           *
*                state  = nouvel état de l'accès aux erreurs relevées.        *
*                                                                             *
*  Description : Protège ou lève la protection de l'accès aux erreurs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_lock_unlock_errors(GBinFormat *format, bool state)
{
    if (state)
    {
        g_mutex_lock(&format->error_mutex);
#ifndef NDEBUG
        g_atomic_int_set(&format->error_locked, 1);
#endif
    }
    else
    {
#ifndef NDEBUG
        g_atomic_int_set(&format->error_locked, 0);
#endif
        g_mutex_unlock(&format->error_mutex);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture concernée par la procédure.            *
*                index  = indice du problème visé.                            *
*                type   = type d'erreur retrouvée.                            *
*                addr   = localisation associée.                              *
*                desc   = éventuelle description humaine de description.      *
*                                                                             *
*  Description : Etend la liste des soucis détectés avec de nouvelles infos.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_format_add_error(GBinFormat *format, BinaryFormatError type, const vmpa2t *addr, const char *desc)
{
    fmt_error *error;                       /* Raccourci de confort        */

    g_binary_format_lock_errors(format);

    format->errors = realloc(format->errors, ++format->error_count * sizeof(fmt_error));

    error = &format->errors[format->error_count - 1];

    error->type = type;

    copy_vmpa(&error->addr, addr);

    if (desc != NULL)
        error->desc = strdup(desc);
    else
        error->desc = NULL;

    g_binary_format_unlock_errors(format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture à consulter durant la procédure.       *
*                                                                             *
*  Description : Indique le nombre d'erreurs relevées au niveau assembleur.   *
*                                                                             *
*  Retour      : Nombre d'erreurs en stock.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_binary_format_count_errors(GBinFormat *format)
{
    size_t result;                          /* Quantité à retourner        */

    assert(g_atomic_int_get(&format->error_locked) == 1);

    result = format->error_count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = architecture concernée par la procédure.            *
*                index  = indice du problème visé.                            *
*                type   = type d'erreur retrouvée. [OUT]                      *
*                addr   = localisation associée. [OUT]                        *
*                desc   = éventuelle description humaine de description. [OUT]*
*                                                                             *
*  Description : Fournit les éléments concernant un soucis détecté.           *
*                                                                             *
*  Retour      : Validité des informations renseignées.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_format_get_error(GBinFormat *format, size_t index, BinaryFormatError *type, vmpa2t *addr, char **desc)
{
    bool result;                            /* Bilan à retourner           */
    fmt_error *error;                       /* Raccourci de confort        */

    assert(g_atomic_int_get(&format->error_locked) == 1);

    result = (index < format->error_count);

    assert(result);

    if (result)
    {
        error = &format->errors[index];

        *type = error->type;

        copy_vmpa(addr, &error->addr);

        if (error->desc != NULL)
            *desc = strdup(error->desc);
        else
            *desc = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format de binaire concerné par la procédure.        *
*                pbuf   = zone tampon à vider.                                *
*                                                                             *
*  Description : Charge les erreurs de chargement depuis une mémoire tampon.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_format_load_errors(GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    size_t i;                               /* Boucle de parcours          */
    fmt_error *error;                       /* Raccourci de confort        */
    rle_string str;                         /* Chaîne à charger            */

    g_binary_format_lock_errors(format);

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    format->error_count = value;

    format->errors = calloc(format->error_count, sizeof(fmt_error));

    for (i = 0; i < format->error_count && result; i++)
    {
        error = &format->errors[i];

        result = unpack_uleb128(&value, pbuf);
        if (!result) break;

        error->type = value;

        result = unpack_vmpa(&error->addr, pbuf);
        if (!result) break;

        setup_empty_rle_string(&str);

        result = unpack_rle_string(&str, pbuf);
        if (!result) break;

        if (get_rle_string(&str) != NULL)
            error->desc = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

 exit:

    g_binary_format_unlock_errors(format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format de binaire concerné par la procédure.        *
*                pbuf   = zone tampon à remplir.                              *
*                                                                             *
*  Description : Sauvegarde les erreurs de chargement dans une mémoire tampon.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_format_store_errors(GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    fmt_error *error;                       /* Raccourci de confort        */
    rle_string str;                         /* Chaîne à conserver          */

    g_binary_format_lock_errors(format);

    result = pack_uleb128((uleb128_t []){ format->error_count }, pbuf);

    for (i = 0; i < format->error_count && result; i++)
    {
        error = &format->errors[i];

        result = pack_uleb128((uleb128_t []){ error->type }, pbuf);
        if (!result) break;

        result = pack_vmpa(&error->addr, pbuf);
        if (!result) break;

        init_static_rle_string(&str, error->desc);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    g_binary_format_unlock_errors(format);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
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

static bool g_binary_format_load(GBinFormat *format, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    fmt_extra_data_t *extra;                /* Données insérées à consulter*/
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    rle_string str;                         /* Chaîne à charger            */

    extra = GET_BIN_FORMAT_EXTRA(format);

    LOCK_GOBJECT_EXTRA(extra);

    result = unpack_uleb128(&value, pbuf);

    if (result)
        extra->flags = value;

    UNLOCK_GOBJECT_EXTRA(extra);

    if (result)
        result = g_binary_format_load_start_points(format, pbuf);

    if (result)
    {
        setup_empty_rle_string(&str);

        result = unpack_rle_string(&str, pbuf);

        if (result)
            result = (get_rle_string(&str) != NULL);

        if (result)
            format->demangler = get_compiler_demangler_for_key(get_rle_string(&str));

        if (result)
            result = (format->demangler != NULL);

        exit_rle_string(&str);

    }





    if (result)
        result = g_binary_format_load_errors(format, pbuf);

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

static bool g_binary_format_store(GBinFormat *format, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    fmt_extra_data_t *extra;                /* Données insérées à consulter*/
    char *key;                              /* Désignation du décodeur     */
    rle_string str;                         /* Chaîne à conserver          */

    extra = GET_BIN_FORMAT_EXTRA(format);

    LOCK_GOBJECT_EXTRA(extra);

    result = pack_uleb128((uleb128_t []){ extra->flags }, pbuf);

    UNLOCK_GOBJECT_EXTRA(extra);

    if (result)
        result = g_binary_format_store_start_points(format, pbuf);

    if (result)
    {
        key = g_compiler_demangler_get_key(format->demangler);
        init_dynamic_rle_string(&str, key);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }






    if (result)
        result = g_binary_format_store_errors(format, pbuf);

    return result;

}
