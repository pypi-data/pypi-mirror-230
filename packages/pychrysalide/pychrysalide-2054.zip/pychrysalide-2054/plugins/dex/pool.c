
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pool.c - extraction des informations issues des tables globales
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#include "pool.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>
#include <core/global.h>
#include <core/nproc.h>
#include <format/strsym.h>
#include <mangling/demangler.h>


#include "dex-int.h"
#include "loading.h"
#include "routine.h"



/* Table des ressources pour format Dex (instance) */
struct _GDexPool
{
    GObject parent;                         /* A laisser en premier        */

    GDexFormat *format;                     /* Format de rattachement      */

    GBinSymbol **strings;                   /* Symboles pour les chaînes   */
    GDataType **types;                      /* Types partagés pour Dalvik  */
    GBinVariable **fields;                  /* Champs de données partagés  */
    GDexMethod **methods;                   /* Méthodes déclarées          */
    GDexClass **classes;                    /* Classes retrouvées          */

};

/* Table des ressources pour format Dex (classe) */
struct _GDexPoolClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Procède à l'initialisation des tables de ressources pour Dex. */
static void g_dex_pool_class_init(GDexPoolClass *);

/* Procède à l'initialisation d'une table de ressources Dex. */
static void g_dex_pool_init(GDexPool *);

/* Supprime toutes les références externes. */
static void g_dex_pool_dispose(GDexPool *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_pool_finalize(GDexPool *);



/* Détermine le type d'une table des ressources pour format Dex. */
G_DEFINE_TYPE(GDexPool, g_dex_pool, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GLib à initialiser.              *
*                                                                             *
*  Description : Procède à l'initialisation des tables de ressources pour Dex.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_pool_class_init(GDexPoolClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_pool_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_pool_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = composant GLib à initialiser.                         *
*                                                                             *
*  Description : Procède à l'initialisation d'une table de ressources Dex.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_pool_init(GDexPool *pool)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_pool_dispose(GDexPool *pool)
{
    G_OBJECT_CLASS(g_dex_pool_parent_class)->dispose(G_OBJECT(pool));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_pool_finalize(GDexPool *pool)
{
    G_OBJECT_CLASS(g_dex_pool_parent_class)->finalize(G_OBJECT(pool));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = représentation interne du format Dex à consulter.   *
*                                                                             *
*  Description : Crée une nouvelle table de ressources pour format Dex.       *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexPool *g_dex_pool_new(GDexFormat *format)
{
    GDexPool *result;                       /* Composant à retourner       */

    result = g_object_new(G_TYPE_DEX_POOL, NULL);

    result->format = format;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool   = table de ressources pour format Dex  à compléter.   *
*                gid    = groupe de travail impliqué.                         *
                 status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire l'ensemble des chaînes du format DEX.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_load_all_string_symbols(GDexPool *pool, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    uint32_t run_size;                      /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t msg;                      /* Message de progression      */
    guint i;                                /* Boucle de parcours          */
    uint32_t begin;                         /* Début de bloc de traitement */
    uint32_t end;                           /* Fin d'un bloc de traitement */
    GDexLoading *loading;                   /* Tâche de chargement à lancer*/

    result = true;

    /* Préparation du réceptacle */

    count = g_dex_pool_count_strings(pool);

    pool->strings = calloc(count, sizeof(GBinSymbol *));

    /* Lancement des chargements */

    run_size = compute_run_size(count, &runs_count);

    queue = get_work_queue();

    msg = gtk_status_stack_add_activity(status, _("Loading all strings from the Dex pool..."), count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = count;
        else
            end = begin + run_size;

        loading = g_dex_loading_new(G_OBJECT(pool), begin, end, msg,
                                    (dex_loading_cb)g_dex_pool_get_string_symbol, &result);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(loading), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    /* Insertion en tant que symboles */

    if (result)
        result = g_binary_format_add_symbols(G_BIN_FORMAT(pool->format), pool->strings, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = table de resources pour format Dex à consulter.       *
*                                                                             *
*  Description : Compte le nombre de chaînes de caractères dans une table DEX.*
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_dex_pool_count_strings(const GDexPool *pool)
{
    uint32_t result;                        /* Quantité à retourner        */

    result = pool->format->header.string_ids_size;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index de la chaîne recherchée.                       *
*                mark  = marque la chaîne comme structurelle si définie.      *
*                range = éventuelle couverture à renseigner ou NULL. [OUT]    *
*                                                                             *
*  Description : Extrait une chaîne de caractères d'une table DEX.            *
*                                                                             *
*  Retour      : Chaîne de caractères trouvée ou NULL en cas d'erreur.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_dex_pool_get_string(const GDexPool *pool, uint32_t index, bool *mark, mrange_t *range)
{
    uint32_t count;                         /* Nombre d'éléments présents  */
    GDexFormat *format;                     /* Format associé à la table   */
    off_t pos;                              /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */
    string_id_item str_id;                  /* Identifiant de chaîne       */
    vmpa2t inter;                           /* Position intermédiaire      */
    string_data_item str_data;              /* Description de chaîne       */
    phys_t diff;                            /* Avancée de tête de lecture  */

    count = g_dex_pool_count_strings(pool);

    if (index >= count)
        return NULL;

    format = pool->format;

    pos = format->header.string_ids_off + index * sizeof(string_id_item);
    init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

    if (!read_dex_string_id_item(format, &addr, &str_id))
        return NULL;

    pos = str_id.string_data_off;
    init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

    if (!read_dex_string_data_item(format, &addr, &inter, &str_data))
        return NULL;

    if (mark != NULL)
    {
        assert(*mark);

        assert(pool->strings[index] != NULL);
        g_string_symbol_set_structural(G_STR_SYMBOL(pool->strings[index]), true);

    }

    if (range != NULL)
    {
        diff = compute_vmpa_diff(&inter, &addr);

        init_mrange(range, &inter, diff);

    }

    return (const char *)str_data.data;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index de la chaîne recherchée.                       *
*                                                                             *
*  Description : Extrait un symbole de chaîne d'une table DEX.                *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_dex_pool_get_string_symbol(GDexPool *pool, uint32_t index)
{
    GBinSymbol *result;                     /* Instance à retourner        */
    uint32_t count;                         /* Nombre d'éléments présents  */
    mrange_t range;                         /* Emplacement de la chaîne    */
    const char *string;                     /* Chaîne de caractères liée   */
    GBinFormat *base;                       /* Autre version du format     */
    GBinSymbol *new;                        /* Nouveau symbol créé         */

    result = NULL;

    count = g_dex_pool_count_strings(pool);

    if (index >= count)
        goto gssfdp_error;

    if (pool->strings[index] == NULL)
    {
        string = g_dex_pool_get_string(pool, index, NULL, &range);
        if (string == NULL) goto gssfdp_error;

        base = G_BIN_FORMAT(pool->format);

        new = g_string_symbol_new_read_only(SET_MUTF_8, G_KNOWN_FORMAT(base), &range);

        if (new != NULL)
            g_string_symbol_build_label(G_STR_SYMBOL(new), base);

        pool->strings[index] = new;

    }

    result = pool->strings[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

 gssfdp_error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool   = table de ressources pour format Dex  à compléter.   *
*                gid    = groupe de travail impliqué.                         *
                 status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire l'ensemble des types du format DEX.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_load_all_types(GDexPool *pool, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    uint32_t run_size;                      /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t msg;                      /* Message de progression      */
    guint i;                                /* Boucle de parcours          */
    uint32_t begin;                         /* Début de bloc de traitement */
    uint32_t end;                           /* Fin d'un bloc de traitement */
    GDexLoading *loading;                   /* Tâche de chargement à lancer*/

    result = true;

    /* Préparation du réceptacle */

    count = g_dex_pool_count_types(pool);

    pool->types = calloc(count, sizeof(GDataType *));

    /* Lancement des chargements */

    run_size = compute_run_size(count, &runs_count);

    queue = get_work_queue();

    msg = gtk_status_stack_add_activity(status, _("Loading all types from the Dex pool..."), count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = count;
        else
            end = begin + run_size;

        loading = g_dex_loading_new(G_OBJECT(pool), begin, end, msg,
                                    (dex_loading_cb)g_dex_pool_get_type_, &result);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(loading), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = table de resources pour format Dex à consulter.       *
*                                                                             *
*  Description : Compte le nombre de types dans une table DEX.                *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_dex_pool_count_types(const GDexPool *pool)
{
    uint32_t result;                        /* Quantité à retourner        */

    result = pool->format->header.type_ids_size;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool    = table de resources pour format Dex à consulter.    *
*                index   = index du type recherché.                           *
*                type_id = élément ciblé à constituer. [OUT]                  *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'un type Dex.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_get_raw_type(GDexPool *pool, uint32_t index, type_id_item *type_id)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    GDexFormat *format;                     /* Format associé à la table   */
    phys_t pos;                             /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */

    result = false;

    count = g_dex_pool_count_types(pool);

    if (index < count)
    {
        format = pool->format;

        pos = format->header.type_ids_off + index * sizeof(type_id_item);
        init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

        result = read_dex_type_id_item(format, &addr, type_id);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index du type recherché.                             *
*                                                                             *
*  Description : Extrait une représentation de type d'une table DEX.          *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_dex_pool_get_type_(GDexPool *pool, uint32_t index)
{
    GDataType *result;                      /* Instance à retourner        */
    type_id_item type_id;                   /* Définition de la classe     */
    const char *desc;                       /* Description de type         */

    result = NULL;

    if (pool->types[index] == NULL)
    {
        if (!g_dex_pool_get_raw_type(pool, index, &type_id))
            goto no_type_id;

        desc = g_dex_pool_get_string(pool, type_id.descriptor_idx, (bool []) { true }, NULL);
        if (desc == NULL) goto type_error;

        pool->types[index] = g_binary_format_decode_type(G_BIN_FORMAT(pool->format), desc);

    }

    result = pool->types[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

 type_error:

 no_type_id:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool   = table de ressources pour format Dex  à compléter.   *
*                gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire l'ensemble des champs du format DEX.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_load_all_fields(GDexPool *pool, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    uint32_t run_size;                      /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t msg;                      /* Message de progression      */
    guint i;                                /* Boucle de parcours          */
    uint32_t begin;                         /* Début de bloc de traitement */
    uint32_t end;                           /* Fin d'un bloc de traitement */
    GDexLoading *loading;                   /* Tâche de chargement à lancer*/

    result = true;

    /* Préparation du réceptacle */

    count = g_dex_pool_count_fields(pool);

    pool->fields = calloc(count, sizeof(GBinVariable *));

    /* Lancement des chargements */

    run_size = compute_run_size(count, &runs_count);

    queue = get_work_queue();

    msg = gtk_status_stack_add_activity(status, _("Loading all fields from the Dex pool..."),
                                        count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = count;
        else
            end = begin + run_size;

        loading = g_dex_loading_new(G_OBJECT(pool), begin, end, msg,
                                    (dex_loading_cb)g_dex_pool_get_field, &result);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(loading), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = table de resources pour format Dex à consulter.       *
*                                                                             *
*  Description : Compte le nombre de champs dans une table DEX.               *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_dex_pool_count_fields(const GDexPool *pool)
{
    uint32_t result;                        /* Quantité à retourner        */

    result = pool->format->header.field_ids_size;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool     = table de resources pour format Dex à consulter.   *
*                index    = index du type recherché.                          *
*                field_id = élément ciblé à constituer. [OUT]                 *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'un champ Dex.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_get_raw_field(GDexPool *pool, uint32_t index, field_id_item *field_id)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    GDexFormat *format;                     /* Format associé à la table   */
    phys_t pos;                             /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */

    result = false;

    count = g_dex_pool_count_fields(pool);

    if (index < count)
    {
        format = pool->format;

        pos = format->header.field_ids_off + index * sizeof(field_id_item);
        init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

        result = read_dex_field_id_item(format, &addr, field_id);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index du champ recherché.                            *
*                                                                             *
*  Description : Extrait une représentation de champ d'une table DEX.         *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinVariable *g_dex_pool_get_field(GDexPool *pool, uint32_t index)
{
    GBinVariable *result;                   /* Instance à retourner        */
    field_id_item field_id;                 /* Description du champ        */
    GDataType *type;                        /* Type du champ               */
    const char *name;                       /* Désignation humaine         */
    GBinVariable *field;                    /* Instance nouvelle à définir */
    GDataType *owner;                       /* Propriétaire du champ       */

    result = NULL;

    if (pool->fields[index] == NULL)
    {
        if (!g_dex_pool_get_raw_field(pool, index, &field_id))
            goto no_field_id;

        type = g_dex_pool_get_type_(pool, field_id.type_idx);
        if (type == NULL) goto type_error;

        name = g_dex_pool_get_string(pool, field_id.name_idx, (bool []) { true }, NULL);
        if (name == NULL) goto bad_name;

        field = g_binary_variable_new(type);
        g_binary_variable_set_name(field, name);

        if (field_id.class_idx != NO_INDEX)
        {
            owner = g_dex_pool_get_type_(pool, field_id.class_idx);
            if (owner == NULL) goto bad_owner;

            g_binary_variable_set_owner(field, owner);

        }

        pool->fields[index] = field;

    }

    result = pool->fields[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

 type_error:

 no_field_id:

    return result;

 bad_owner:

    g_object_unref(G_OBJECT(field));

 bad_name:

    g_object_unref(G_OBJECT(type));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = table de resources pour format Dex à consulter.       *
*                                                                             *
*  Description : Compte le nombre de prototypes dans une table DEX.           *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_dex_pool_count_prototypes(const GDexPool *pool)
{
    uint32_t result;                        /* Quantité à retourner        */

    result = pool->format->header.proto_ids_size;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool     = table de resources pour format Dex à consulter.   *
*                index    = index de la routine recherchée.                   *
*                proto_id = élément ciblé à constituer. [OUT]                 *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'une routine Dex.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_get_raw_prototype(GDexPool *pool, uint32_t index, proto_id_item *proto_id)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    GDexFormat *format;                     /* Format associé à la table   */
    phys_t pos;                             /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */

    result = false;

    count = g_dex_pool_count_prototypes(pool);

    if (index < count)
    {
        format = pool->format;

        pos = format->header.proto_ids_off + index * sizeof(proto_id_item);
        init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

        result = read_dex_proto_id_item(format, &addr, proto_id);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index de la routine recherchée.                      *
*                                                                             *
*  Description : Extrait une représentation de routine d'une table DEX.       *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_dex_pool_get_prototype(GDexPool *pool, uint32_t index)
{
    GBinRoutine *result;                    /* Instance à retourner        */
    proto_id_item proto_id;                 /* Prototype de routine        */
    GDataType *type;                        /* Type de retour              */
    phys_t pos;                             /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */
    type_list args;                         /* Liste des arguments         */
    uint32_t i;                             /* Boucle de parcours          */
    GBinVariable *arg;                      /* Argument reconstitué        */

    result = NULL;

    /**
     * Les prototypes sont personnalisés après chargement.
     * Donc on ne peut pas conserver de version globale comme pour
     * les autres éléments de la table des constantes.
     */

    if (!g_dex_pool_get_raw_prototype(pool, index, &proto_id))
        goto no_proto_id;

    /**
     * On choisit d'ignorer le champ proto_id.shorty_idx : c'est un descripteur
     * qui doit correspondre au retour et aux paramètres précisés avec les
     * autres champs de la structure, donc l'information paraît redondante.
     */

    /**
     * On marque cependant la chaîne de description comme étant structurelle.
     */

    assert(pool->strings[proto_id.shorty_idx] != NULL);
    g_string_symbol_set_structural(G_STR_SYMBOL(pool->strings[proto_id.shorty_idx]), true);

    /* Type de retour */

    type = g_dex_pool_get_type_(pool, proto_id.return_type_idx);
    if (type == NULL) goto type_error;

    result = G_BIN_ROUTINE(g_dex_routine_new());

    g_binary_routine_set_return_type(result, type);

    /* Liste des arguments, s'il y a */

    pos = proto_id.parameters_off;

    if (pos > 0)
    {
        init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

        if (!read_dex_type_list(pool->format, &addr, &args))
            goto arg_error;

        for (i = 0; i < args.size; i++)
        {
            type = g_dex_pool_get_type_(pool, args.list[i].type_idx);
            if (type == NULL) goto arg_error;

            arg = g_binary_variable_new(type);
            g_binary_routine_add_arg(result, arg);

        }

    }

    return result;

 arg_error:

    if (result != NULL)
        g_object_unref(G_OBJECT(result));

 type_error:

 no_proto_id:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool   = table de ressources pour format Dex  à compléter.   *
*                gid    = groupe de travail impliqué.                         *
                 status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge toutes les classes listées dans le contenu binaire.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_load_all_methods(GDexPool *pool, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    uint32_t run_size;                      /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t msg;                      /* Message de progression      */
    guint i;                                /* Boucle de parcours          */
    uint32_t begin;                         /* Début de bloc de traitement */
    uint32_t end;                           /* Fin d'un bloc de traitement */
    GDexLoading *loading;                   /* Tâche de chargement à lancer*/

    /**
     * Il existe deux voies pour récupérer une méthode :
     *
     *    - depuis 'method_id_item', qui précise classe d'appartenance, prototype
     *      et nom.
     *
     *    - depuis 'encoded_method', qui contient une définition 'method_id_item',
     *      ainsi que des attributs propres à la méthode visée.
     *
     * Techniquement, il peut donc y avoir plusieurs variations d'un même
     * 'method_id_item' selon différents 'encoded_method'.
     *
     * Dans la pratique, c'est hautement improbable : une méthode ne peut pas
     * être privée et publique  par exemple, ou renvoyer vers différents code.
     *
     * Donc on se permet d'associer une unique méthode par 'method_id_item',
     * et de précharger le tout.
     */

    result = true;

    /* Préparation du réceptacle */

    count = pool->format->header.method_ids_size;

    pool->methods = calloc(count, sizeof(GDexMethod *));

    /* Lancement des chargements */

    run_size = compute_run_size(count, &runs_count);

    queue = get_work_queue();

    msg = gtk_status_stack_add_activity(status, _("Loading all methods from the Dex pool..."), count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = count;
        else
            end = begin + run_size;

        loading = g_dex_loading_new(G_OBJECT(pool), begin, end, msg,
                                    (dex_loading_cb)g_dex_pool_get_method, &result);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(loading), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = table de resources pour format Dex à consulter.       *
*                                                                             *
*  Description : Compte le nombre de méthodes dans une table DEX.             *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_dex_pool_count_methods(const GDexPool *pool)
{
    uint32_t result;                        /* Quantité à retourner        */

    result = pool->format->header.method_ids_size;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool     = table de resources pour format Dex à consulter.   *
*                index    = index du type recherché.                          *
*                field_id = élément ciblé à constituer. [OUT]                 *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'une méthode Dex.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_get_raw_method(GDexPool *pool, uint32_t index, method_id_item *method_id)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    GDexFormat *format;                     /* Format associé à la table   */
    phys_t pos;                             /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */

    result = false;

    count = g_dex_pool_count_methods(pool);

    if (index < count)
    {
        format = pool->format;

        pos = format->header.method_ids_off + index * sizeof(method_id_item);
        init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

        result = read_dex_method_id_item(format, &addr, method_id);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index de la méthode recherchée.                      *
*                                                                             *
*  Description : Extrait une représentation de méthode d'une table DEX.       *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_pool_get_method(GDexPool *pool, uint32_t index)
{
    GDexMethod *result;                     /* Instance à retourner        */
    method_id_item method_id;               /* Définition de la méthode    */

    result = NULL;

    if (pool->methods[index] == NULL)
    {
        if (!g_dex_pool_get_raw_method(pool, index, &method_id))
            goto no_method_id;

        pool->methods[index] = g_dex_method_new_callable(pool->format, &method_id);

    }

    result = pool->methods[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

 no_method_id:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool   = table de ressources pour format Dex  à compléter.   *
*                gid    = groupe de travail impliqué.                         *
                 status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge toutes les classes listées dans le contenu binaire.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_load_all_classes(GDexPool *pool, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    uint32_t run_size;                      /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t msg;                      /* Message de progression      */
    guint i;                                /* Boucle de parcours #1       */
    uint32_t begin;                         /* Début de bloc de traitement */
    uint32_t end;                           /* Fin d'un bloc de traitement */
    GDexLoading *loading;                   /* Tâche de chargement à lancer*/
    GBinSymbol **symbols;                   /* Symboles présents à injecter*/
    size_t scount;                          /* Quantité de ces symboles    */
    uint32_t j;                             /* Boucle de parcours #2       */
    size_t k;                               /* Boucle de parcours #3       */
    bool need_sort;                         /* Tri des symboles nécessaire */
    phys_t last;                            /* Dernière position rencontrée*/
    const mrange_t *range;                  /* Couverture du symbole       */
    const vmpa2t *addr;                     /* Emplacement du symbole      */

    result = true;

    /* Préparation du réceptacle */

    count = pool->format->header.class_defs_size;

    pool->classes = calloc(count, sizeof(GDexClass *));

    /* Lancement des chargements */

    run_size = compute_run_size(count, &runs_count);

    queue = get_work_queue();

    msg = gtk_status_stack_add_activity(status, _("Loading all classes from the Dex pool..."), count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = count;
        else
            end = begin + run_size;

        loading = g_dex_loading_new(G_OBJECT(pool), begin, end, msg,
                                    (dex_loading_cb)g_dex_pool_get_class, &result);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(loading), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    /* Insertion en tant que symboles */

    if (result)
    {
        symbols = NULL;
        scount = 0;

        for (j = 0; j < count && result; j++)
            result = g_dex_class_get_collect_symbols(pool->classes[j], &symbols, &scount);

        if (result)
        {
            /**
             * Si le format DEX impose un ordre croissant dans les identifiants
             * des méthodes d'une classe (champ method_idx de la structure
             * encoded_method), cela ne conduit pas forcément à :
             *   - à disposer de champs code_off eux-même ordonnés ;
             *   - à retrouver des ordonnancements d'une classe à une autre.
             *
             * Un tri est donc forcé ici s'il s'avère nécessaire.
             */

            need_sort = false;
            last = VMPA_NO_PHYSICAL;

            for (k = 0; k < scount && !need_sort; k++)
            {
                range = g_binary_symbol_get_range(symbols[k]);
                addr = get_mrange_addr(range);

                need_sort = (last != VMPA_NO_PHYSICAL && last > get_phy_addr(addr));

                last = get_phy_addr(addr);

            }

            if (need_sort)
                qsort(symbols, count, sizeof(GBinSymbol *), (__compar_fn_t)g_binary_symbol_cmp);

            result = g_binary_format_add_symbols(G_BIN_FORMAT(pool->format), symbols, count);

        }

        for (k = 0; k < scount; k++)
            g_object_unref(symbols[k]);

        if (symbols != NULL)
            free(symbols);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool = table de resources pour format Dex à consulter.       *
*                                                                             *
*  Description : Dénombre le nombre de classes trouvées.                      *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_dex_pool_count_classes(const GDexPool *pool)
{
    uint32_t result;                        /* Quantité à retourner        */

    result = pool->format->header.class_defs_size;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool      = table de resources pour format Dex à consulter.  *
*                index     = index du type recherché.                         *
*                class_def = élément ciblé à constituer. [OUT]                *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'une classe Dex.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_pool_get_raw_class(GDexPool *pool, uint32_t index, class_def_item *class_def)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t count;                         /* Nombre d'éléments présents  */
    GDexFormat *format;                     /* Format associé à la table   */
    phys_t pos;                             /* Tête de lecture             */
    vmpa2t addr;                            /* Tête de lecture générique   */

    result = false;

    count = g_dex_pool_count_classes(pool);

    if (index < count)
    {
        format = pool->format;

        pos = format->header.class_defs_off + index * sizeof(class_def_item);
        init_vmpa(&addr, pos, VMPA_NO_VIRTUAL);

        result = read_dex_class_def_item(format, &addr, class_def);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pool  = table de resources pour format Dex à consulter.      *
*                index = index de la classe recherchée.                       *
*                                                                             *
*  Description : Extrait une représentation de classe d'une table DEX.        *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexClass *g_dex_pool_get_class(GDexPool *pool, uint32_t index)
{
    GDexClass *result;                      /* Instance à retourner        */
    class_def_item class_def;               /* Définition de la classe     */

    result = NULL;

    if (pool->classes[index] == NULL)
    {
        if (!g_dex_pool_get_raw_class(pool, index, &class_def))
            goto no_class_def;

        pool->classes[index] = g_dex_class_new(pool->format, &class_def);

    }

    result = pool->classes[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

 no_class_def:

    return result;

}
