
/* Chrysalide - Outil d'analyse de fichiers binaires
 * class.c - manipulation des classes du format DEX
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


#include "class.h"


#include <malloc.h>
#include <string.h>


#include "dex-int.h"
#include "pool.h"



/* Classe issue du code source (instance) */
struct _GDexClass
{
    GObject parent;                         /* A laisser en premier        */

    GDexFormat *format;                     /* Lien vers la table globale  */

    class_def_item definition;              /* Définition de la classe     */
    bool has_data;                          /* Indicateur de présence      */
    class_data_item data;                   /* Contenu de la classe        */

    GDexField **static_fields;              /* Champs statiques            */
    size_t sfields_count;                   /* Quantité de ces champs      */
    GDexField **instance_fields;            /* Champs propres à la classe  */
    size_t ifields_count;                   /* Quantité de ces champs      */

    GDexMethod **direct_methods;            /* Méthodes propres            */
    size_t dmethods_count;                  /* Quantité de ces méthodes    */
    GDexMethod **virtual_methods;           /* Méthodes virtuelles         */
    size_t vmethods_count;                  /* Quantité de ces méthodes    */

};

/* Classe issue du code source (classe) */
struct _GDexClassClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Procède à l'initialisation d'une classe issue du code source. */
static void g_dex_class_class_init(GDexClassClass *);

/* Procède à l'initialisation d'une classe issue du code source. */
static void g_dex_class_init(GDexClass *);

/* Supprime toutes les références externes. */
static void g_dex_class_dispose(GDexClass *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_class_finalize(GDexClass *);



/* Détermine le type d'une classe issue du code source. */
G_DEFINE_TYPE(GDexClass, g_dex_class, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GLib à initialiser.              *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe issue du code source.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_class_class_init(GDexClassClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_class_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_class_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = composant GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe issue du code source.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_class_init(GDexClass *class)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_class_dispose(GDexClass *class)
{
    size_t i;                               /* Boucle de parcours          */

    if (class->static_fields != NULL)
        for (i = 0; i < class->sfields_count; i++)
            if (class->static_fields[i] != NULL)
                g_object_unref(G_OBJECT(class->static_fields[i]));

    if (class->instance_fields != NULL)
        for (i = 0; i < class->ifields_count; i++)
            if (class->instance_fields[i] != NULL)
                g_object_unref(G_OBJECT(class->instance_fields[i]));

    if (class->direct_methods != NULL)
        for (i = 0; i < class->dmethods_count; i++)
            if (class->direct_methods[i] != NULL)
                g_object_unref(G_OBJECT(class->direct_methods[i]));

    if (class->virtual_methods != NULL)
        for (i = 0; i < class->vmethods_count; i++)
            if (class->virtual_methods[i] != NULL)
                g_object_unref(G_OBJECT(class->virtual_methods[i]));

    g_object_unref(G_OBJECT(class->format));

    G_OBJECT_CLASS(g_dex_class_parent_class)->dispose(G_OBJECT(class));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_class_finalize(GDexClass *class)
{
    if (class->has_data)
        reset_dex_class_data_item(&class->data);

    if (class->static_fields != NULL)
        free(class->static_fields);

    if (class->instance_fields != NULL)
        free(class->instance_fields);

    if (class->direct_methods != NULL)
        free(class->direct_methods);

    if (class->virtual_methods != NULL)
        free(class->virtual_methods);

    G_OBJECT_CLASS(g_dex_class_parent_class)->finalize(G_OBJECT(class));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = représentation interne du format DEX à consulter.   *
*                def    = définitions générales associées à la classe.        *
*                                                                             *
*  Description : Crée une nouvelle représentation de classe issue de code.    *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexClass *g_dex_class_new(GDexFormat *format, const class_def_item *def)
{
    GDexClass *result;                      /* Composant à retourner       */
    vmpa2t addr;                            /* Tête de lecture générique   */
    class_data_item data;                   /* Contenu de la classe        */
    uleb128_t index;                        /* Conservation du dernier id  */
    uleb128_t i;                            /* Boucle de parcours          */
    GDexField *field;                       /* Champ chargé                */
    GDexMethod *method;                     /* Méthode chargée             */

    result = g_object_new(G_TYPE_DEX_CLASS, NULL);

    result->format = format;
    g_object_ref(G_OBJECT(format));

    result->definition = *def;
    result->has_data = (def->class_data_off != 0);

    /* Interface vide ? */
    if (!result->has_data)
    {
        result->dmethods_count = 0;
        result->direct_methods = NULL;

        result->vmethods_count = 0;
        result->virtual_methods = NULL;

        goto gdcn_done;

    }

    init_vmpa(&addr, def->class_data_off, VMPA_NO_VIRTUAL);

    if (!read_dex_class_data_item(format, &addr, &data))
        goto gdcn_bad_item;

    result->data = data;

    /**
     * Chargement des champs de classe.
     */

    index = 0;

    result->sfields_count = data.static_fields_size;
    result->static_fields = (GDexField **)calloc(result->sfields_count, sizeof(GDexField *));

    for (i = 0; i < result->sfields_count; i++)
    {
        field = g_dex_field_new(format, &data.static_fields[i], &index);
        if (field == NULL) goto gdcn_bad_field;

        result->static_fields[i] = field;

    }

    index = 0;

    result->ifields_count = data.instance_fields_size;
    result->instance_fields = (GDexField **)calloc(result->ifields_count, sizeof(GDexField *));

    for (i = 0; i < result->ifields_count; i++)
    {
        field = g_dex_field_new(format, &data.instance_fields[i], &index);
        if (field == NULL) goto gdcn_bad_field;

        result->instance_fields[i] = field;

    }

    /**
     * Chargement des méthodes de classe.
     */

    index = 0;

    result->dmethods_count = data.direct_methods_size;
    result->direct_methods = (GDexMethod **)calloc(result->dmethods_count, sizeof(GDexMethod *));

    for (i = 0; i < result->dmethods_count; i++)
    {
        method = g_dex_method_new_defined(format, &data.direct_methods[i], &index);
        if (method == NULL) goto gdcn_bad_method;

        result->direct_methods[i] = method;

    }

    index = 0;

    result->vmethods_count = data.virtual_methods_size;
    result->virtual_methods = (GDexMethod **)calloc(result->vmethods_count, sizeof(GDexMethod *));

    for (i = 0; i < result->vmethods_count; i++)
    {
        method = g_dex_method_new_defined(format, &data.virtual_methods[i], &index);
        if (method == NULL) goto gdcn_bad_method;

        result->virtual_methods[i] = method;

    }

 gdcn_done:

    return result;

 gdcn_bad_method:

 gdcn_bad_field:

 gdcn_bad_item:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                                                                             *
*  Description : Fournit la définition brute d'une classe.                    *
*                                                                             *
*  Retour      : Données brutes issues du binaire chargé.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const class_def_item *g_dex_class_get_definition(const GDexClass *class)
{
    return &class->definition;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                                                                             *
*  Description : Fournit la définition brute des données d'une classe.        *
*                                                                             *
*  Retour      : Données brutes issues du binaire chargé.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const class_data_item *g_dex_class_get_data(const GDexClass *class)
{
    return (class->has_data ? &class->data : NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                                                                             *
*  Description : Indique le type Android d'une classe.                        *
*                                                                             *
*  Retour      : Type de classe ou NULL en cas d'erreur.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_dex_class_get_class_type(const GDexClass *class)
{
    GDataType *result;                      /* Type à renvoyer             */
    GDexPool *pool;                         /* Table de ressources         */

    pool = g_dex_format_get_pool(class->format);

    result = g_dex_pool_get_type_(pool, class->definition.class_idx);

    g_object_unref(G_OBJECT(pool));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                                                                             *
*  Description : Indique le type Android parent d'une classe.                 *
*                                                                             *
*  Retour      : Type de classe ou NULL en cas d'erreur.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_dex_class_get_superclass_type(const GDexClass *class)
{
    GDataType *result;                      /* Type à renvoyer             */
    GDexPool *pool;                         /* Table de ressources         */

    pool = g_dex_format_get_pool(class->format);

    result = g_dex_pool_get_type_(pool, class->definition.superclass_idx);

    g_object_unref(G_OBJECT(pool));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                count = taille de la liste constituée. [OUT]                 *
*                                                                             *
*  Description : Indique le type Android des interfaces d'une classe.         *
*                                                                             *
*  Retour      : Types d'interfaces ou NULL si aucune.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType **g_dex_class_get_interface_types(const GDexClass *class, size_t *count)
{
    GDataType **result;                     /* Types à renvoyer            */
    vmpa2t addr;                            /* Tête de lecture générique   */
    type_list interfaces;                   /* Liste des interfaces        */
    bool status;                            /* Bilan d'une lecture         */
    GDexPool *pool;                         /* Table de ressources         */
    size_t i;                               /* Boucle de parcours          */

    if (class->definition.interfaces_off == 0)
    {
        *count = 0;
        result = NULL;
    }

    else
    {
        init_vmpa(&addr, class->definition.interfaces_off, VMPA_NO_VIRTUAL);

        status = read_dex_type_list(class->format, &addr, &interfaces);

        if (status)
        {
            *count = interfaces.size;
            result = malloc(*count * sizeof(GDataType *));

            pool = g_dex_format_get_pool(class->format);

            for (i = 0; i < *count; i++)
                result[i] = g_dex_pool_get_type_(pool, interfaces.list[i].type_idx);

            g_object_unref(G_OBJECT(pool));

        }

        else
        {
            *count = 0;
            result = NULL;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class    = informations chargées à consulter.                *
*                instance = précise la nature des champs ciblés.              *
*                                                                             *
*  Description : Dénombre les champs de classe chargés d'une classe donnée.   *
*                                                                             *
*  Retour      : Quantité de champs trouvés.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_dex_class_count_fields(const GDexClass *class, bool instance)
{
    size_t result;                          /* Compte à retourner          */

    if (instance)
        result = class->ifields_count;
    else
        result = class->sfields_count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class    = informations chargées à consulter.                *
*                instance = précise la nature des champs ciblés.              *
*                index    = indique l'indice du champ désiré.                 *
*                                                                             *
*  Description : Fournit un champ chargé correspondant à une classe donnée.   *
*                                                                             *
*  Retour      : Champ intégré ou NULL.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexField *g_dex_class_get_field(const GDexClass *class, bool instance, size_t index)
{
    GDexField *result;                      /* Instance à renvoyer         */

    if (instance)
        result = class->instance_fields[index];
    else
        result = class->static_fields[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class   = informations chargées à consulter.                 *
*                virtual = précise la nature des méthodes ciblées.            *
*                                                                             *
*  Description : Dénombre les méthodes chargées d'un type donné.              *
*                                                                             *
*  Retour      : Quantité de méthodes trouvées.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_dex_class_count_methods(const GDexClass *class, bool virtual)
{
    size_t result;                          /* Compte à retourner          */

    if (virtual)
        result = class->vmethods_count;
    else
        result = class->dmethods_count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class   = informations chargées à consulter.                 *
*                virtual = précise la nature des méthodes ciblées.            *
*                index   = indique l'indice de la méthode désirée.            *
*                                                                             *
*  Description : Fournit une méthode chargée correspondant à un type donné.   *
*                                                                             *
*  Retour      : Méthode intégrée ou NULL.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_class_get_method(const GDexClass *class, bool virtual, size_t index)
{
    GDexMethod *result;                     /* Instance à renvoyer         */

    if (virtual)
    {
        if (index < class->vmethods_count)
            result = class->virtual_methods[index];
        else
            result = NULL;
    }
    else
    {
        if (index < class->dmethods_count)
            result = class->direct_methods[index];
        else
            result = NULL;
    }

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class   = informations chargées à consulter.                 *
*                symbols = liste de symboles complétée. [OUT]                 *
*                count   = taille de cette liste. [OUT]                       *
*                                                                             *
*  Description : Etablit une liste de tous les symboles d'une classe.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_class_get_collect_symbols(const GDexClass *class, GBinSymbol ***symbols, size_t *count)
{
    bool result;                            /* Bilan à retourner           */
    GDexPool *pool;                         /* Table de ressources         */
    GDataType *ctype;                       /* Type créé par la classe     */
    size_t slots_used;                      /* Compteur d'utilisations     */
    size_t i;                               /* Boucle de parcours          */
    GDexMethod *method;                     /* Méthode chargée             */
    GBinRoutine *routine;                   /* Version interne de méthode  */

    result = false;

    /* Contexte des méthodes */

    pool = g_dex_format_get_pool(class->format);

    ctype = g_dex_pool_get_type_(pool, class->definition.class_idx);

    g_object_unref(G_OBJECT(pool));

    if (ctype == NULL) goto unknown_type;

    /* Intégration des méthodes */

    *symbols = realloc(*symbols, (*count + class->dmethods_count + class->vmethods_count) * sizeof(GBinSymbol *));

    result = true;

    slots_used = 0;

    for (i = 0; i < class->dmethods_count; i++)
    {
        method = class->direct_methods[i];

        if (g_dex_method_has_dex_body(method))
        {
            routine = g_dex_method_get_routine(method);

            g_object_ref(G_OBJECT(ctype));
            g_binary_routine_set_namespace(routine, ctype, strdup("."));

            (*symbols)[*count + slots_used] = G_BIN_SYMBOL(routine);
            slots_used++;

        }

    }

    *count += slots_used;

    slots_used = 0;

    for (i = 0; i < class->vmethods_count; i++)
    {
        method = class->virtual_methods[i];

        if (g_dex_method_has_dex_body(method))
        {
            routine = g_dex_method_get_routine(method);

            g_object_ref(G_OBJECT(ctype));
            g_binary_routine_set_namespace(routine, ctype, strdup("."));

            (*symbols)[*count + slots_used] = G_BIN_SYMBOL(routine);
            slots_used++;

        }

    }

    *count += slots_used;

    g_object_unref(G_OBJECT(ctype));

 unknown_type:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = informations chargées à consulter.                  *
*                format = format permettant d'obtenir une adresse complète.   *
*                                                                             *
*  Description : Intègre la méthode en tant que portion de code.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_dex_class_include_as_portion(const GDexClass *class, GExeFormat *format)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < class->dmethods_count; i++)
        g_dex_method_include_as_portion(class->direct_methods[i], format);

    for (i = 0; i < class->vmethods_count; i++)
        g_dex_method_include_as_portion(class->virtual_methods[i], format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                addr  = adresse de la routine à retrouver.                   *
*                                                                             *
*  Description : Retrouve si possible la méthode associée à une adresse.      *
*                                                                             *
*  Retour      : Méthde retrouvée ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_class_find_method_by_address(const GDexClass *class, vmpa_t addr)
{
    GDexMethod *result;                     /* Trouvaille à retourner      */

#if 0
    size_t i;                               /* Boucle de parcours          */
    phys_t offset;                          /* Emplacement de méthode      */
#endif

    result = NULL;

#if 0 /* FIXME */
    /*

bool g_dex_method_get_offset(const GDexMethod *method, phys_t *offset)

    if (!g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), method->offset, &addr))
        return;

    */

    for (i = 0; i < class->dmethods_count && result == NULL; i++)
        if (addr == (vmpa_t)g_dex_method_get_offset(class->direct_methods[i]))
            result = class->direct_methods[i];

    for (i = 0; i < class->vmethods_count && result == NULL; i++)
        if (addr == (vmpa_t)g_dex_method_get_offset(class->virtual_methods[i]))
            result = class->virtual_methods[i];
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = informations chargées à consulter.                   *
*                                                                             *
*  Description : Retrouve si possible le nom du fichier source d'une classe.  *
*                                                                             *
*  Retour      : Nom du fichier trouvé ou NULL si aucun.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_dex_class_get_source_file(const GDexClass *class)
{
    const char *result;                     /* Trouvaille à renvoyer       */
    GDexPool *pool;                         /* Table de ressources         */

    pool = g_dex_format_get_pool(class->format);

    result = g_dex_pool_get_string(pool, class->definition.source_file_idx, (bool []) { true }, NULL);

    g_object_unref(G_OBJECT(pool));

    return result;

}
