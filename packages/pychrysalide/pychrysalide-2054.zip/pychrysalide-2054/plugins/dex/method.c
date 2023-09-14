
/* Chrysalide - Outil d'analyse de fichiers binaires
 * method.c - manipulation des methodes du format DEX
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "method.h"


#include <assert.h>
#include <stddef.h>
#include <string.h>


#include <i18n.h>


#include "dex-int.h"
#include "pool.h"
#include "routine.h"



/* Methode issue du code source (instance) */
struct _GDexMethod
{
    GObject parent;                         /* A laisser en premier        */

    GBinRoutine *routine;                   /* Représentation interne      */

    /**
     * Les champs suivants ne sont renseignés que pour les objets mis
     * en place à partir du constructeur g_dex_method_new_defined().
     */

#ifndef NDEBUG
    bool already_defined;                   /* Vérification d'unicité      */
#endif

    method_id_item id_item;                 /* Définition de la méthode    */
    encoded_method info;                    /* Propriétés de la méthode    */
    bool has_body;                          /* Indication de présence      */
    code_item body;                         /* Corps de la méthode         */
    off_t offset;                           /* Position du code            */

};

/* Methode issue du code source (classe) */
struct _GDexMethodClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Procède à l'initialisation d'une methode issue du code. */
static void g_dex_method_class_init(GDexMethodClass *);

/* Procède à l'initialisation d'une methode issue du code. */
static void g_dex_method_init(GDexMethod *);

/* Supprime toutes les références externes. */
static void g_dex_method_dispose(GDexMethod *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_method_finalize(GDexMethod *);



/* Détermine le type d'une methode issue du code source. */
G_DEFINE_TYPE(GDexMethod, g_dex_method, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GLib à initialiser.              *
*                                                                             *
*  Description : Procède à l'initialisation des methodes issues du code.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_method_class_init(GDexMethodClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_method_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_method_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = composant GLib à initialiser.                       *
*                                                                             *
*  Description : Procède à l'initialisation d'une methode issue du code.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_method_init(GDexMethod *method)
{
#ifndef NDEBUG
    method->already_defined = false;
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_method_dispose(GDexMethod *method)
{
    if (method->routine != NULL)
        g_object_unref(G_OBJECT(method->routine));

    G_OBJECT_CLASS(g_dex_method_parent_class)->dispose(G_OBJECT(method));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_method_finalize(GDexMethod *method)
{
    if (method->has_body)
        reset_dex_code_item(&method->body);

    G_OBJECT_CLASS(g_dex_method_parent_class)->finalize(G_OBJECT(method));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = représentation interne du format DEX à consulter.   *
*                seed   = graine des informations à extraire.                 *
*                last   = dernier indice utilisé (à mettre à jour). [OUT]     *
*                                                                             *
*  Description : Crée une nouvelle représentation de methode issue de code.   *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_method_new_defined(GDexFormat *format, const encoded_method *seed, uleb128_t *last)
{
    GDexMethod *result;                     /* Composant à retourner       */
    GDexPool *pool;                         /* Table de ressources         */
    vmpa2t addr;                            /* Tête de lecture générique   */
    code_item item;                         /* Corps de la méthode         */
    phys_t ins_offset;                      /* Position physique du code   */
    mrange_t range;                         /* Emplacement du code associé */

    *last += seed->method_idx_diff;

    pool = g_dex_format_get_pool(format);

    result = g_dex_pool_get_method(pool, *last);

    g_object_unref(G_OBJECT(pool));

    if (result == NULL)
        return NULL;

#ifndef NDEBUG
    assert(!result->already_defined);
    result->already_defined = true;
#endif

    result->info = *seed;

    result->has_body = (seed->code_off > 0);

    if (result->has_body)
    {
        init_vmpa(&addr, seed->code_off, VMPA_NO_VIRTUAL);

        if (!read_dex_code_item(format, &addr, &item))
            goto gdmnd_bad_code_item;

        ins_offset = seed->code_off + offsetof(code_item, insns);

        if (!g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), ins_offset, &addr))
            goto gdmnd_bad_translation;

        result->body = item;

        result->offset = ins_offset;

        init_mrange(&range, &addr, item.insns_size * sizeof(uint16_t));
        g_binary_symbol_set_range(G_BIN_SYMBOL(result->routine), &range);

    }

    return result;

 gdmnd_bad_translation:

    reset_dex_code_item(&item);

 gdmnd_bad_code_item:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = représentation interne du format DEX à consulter.*
*                id_item = informations de base quant à la méthode.         *
*                                                                             *
*  Description : Crée une nouvelle représentation de methode vide.            *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_method_new_callable(GDexFormat *format, const method_id_item *id_item)
{
    GDexMethod *result;                     /* Composant à retourner       */
    GDexPool *pool;                         /* Table de ressources         */
    GDataType *ns;                          /* Espace d'appartenance       */
    const char *name;                       /* Nom de la routine finale    */
    GBinRoutine *routine;                   /* Routine représentée         */

    result = NULL;

    pool = g_dex_format_get_pool(format);

    ns = g_dex_pool_get_type_(pool, id_item->class_idx);

    name = g_dex_pool_get_string(pool, id_item->name_idx, (bool []) { true }, NULL);
    if (name == NULL) goto gdmne_exit;

    routine = g_dex_pool_get_prototype(pool, id_item->proto_idx);
    if (routine == NULL) goto gdmne_exit;

    if (ns != NULL)
        g_binary_routine_set_namespace(routine, ns, strdup("."));

    g_binary_routine_set_name(routine, strdup(name));

    result = g_object_new(G_TYPE_DEX_METHOD, NULL);

    result->routine = routine;

    g_dex_routine_attach_method(G_DEX_ROUTINE(routine), result);

    result->id_item = *id_item;

 gdmne_exit:

    g_object_unref(G_OBJECT(pool));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne de la méthode à consulter.   *
*                                                                             *
*  Description : Fournit les identifiants Dex concernant la méthode.          *
*                                                                             *
*  Retour      : Données brutes du binaire.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const method_id_item *g_dex_method_get_dex_id_item(const GDexMethod *method)
{
    return &method->id_item;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne de la méthode à consulter.   *
*                                                                             *
*  Description : Fournit les indications Dex concernant la méthode.           *
*                                                                             *
*  Retour      : Données brutes du binaire.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const encoded_method *g_dex_method_get_dex_info(const GDexMethod *method)
{
    return &method->info;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne de la méthode à consulter.   *
*                                                                             *
*  Description : Indique si du code est rattaché à une méthode Dex.           *
*                                                                             *
*  Retour      : true si la méthode n'est pas abstraite ni native.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_method_has_dex_body(const GDexMethod *method)
{
    return method->has_body;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne de la méthode à consulter.   *
*                                                                             *
*  Description : Fournit les indications Dex relatives au corps de la méthode.*
*                                                                             *
*  Retour      : Données brutes du binaire.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const code_item *g_dex_method_get_dex_body(const GDexMethod *method)
{
    return (method->has_body ? &method->body : NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne du format DEX à consulter.   *
*                                                                             *
*  Description : Fournit la routine Chrysalide correspondant à la méthode.    *
*                                                                             *
*  Retour      : Instance de routine mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_dex_method_get_routine(const GDexMethod *method)
{
    GBinRoutine *result;                    /* Instance à retourner        */

    result = method->routine;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne du format DEX à consulter.   *
*                format = format permettant d'obtenir une adresse complète.   *
*                                                                             *
*  Description : Intègre la méthode en tant que portion de code.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_dex_method_include_as_portion(const GDexMethod *method, GExeFormat *format)
{
    vmpa2t addr;                            /* Emplacement dans le binaire */
    GBinPortion *new;                       /* Nouvelle portion définie    */

    /* Si la taille est nulle, on ne fait rien */
    if (method->info.access_flags & ACC_NATIVE)
        return;

    if (!method->has_body)
        return;

    if (!g_exe_format_translate_offset_into_vmpa(format, method->offset, &addr))
        return;

    new = g_binary_portion_new(BPC_CODE, &addr, method->body.insns_size * sizeof(uint16_t));

    g_binary_portion_set_desc(new, _("Dalvik code"));

    g_binary_portion_set_rights(new, PAC_READ | PAC_EXEC);

    g_exe_format_include_portion(format, new, &method->info.origin);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne du format DEX à consulter.   *
*                offset = position physique à renseigner. [OUT]               *
*                                                                             *
*  Description : Indique la position de la méthode au sein du binaire.        *
*                                                                             *
*  Retour      : Validiter de la position dans le contenu binaire.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dex_method_get_offset(const GDexMethod *method, phys_t *offset)
{
    bool result;                            /* Indication à retourner      */

    result = method->has_body;

    if (result)
        *offset = method->offset;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = représentation interne du format DEX à consulter.   *
*                index  = indice de base comme seul indice.                   *
*                                                                             *
*  Description : Fournit des indications sur la nature d'une variable donnée. *
*                                                                             *
*  Retour      : Indentifiant complet d'une variable utilisée.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DexVariableIndex g_dex_method_get_variable(const GDexMethod *method, uint32_t index)
{
    const encoded_method *info;             /* Propriétés de la méthode    */
    const code_item *body;                  /* Corps de la méthode         */
    uint32_t pivot;                         /* Bascule pour les arguments  */

    assert(method->has_body);

    info = &method->info;
    body = &method->body;

    /* S'agit-il d'un argument ? */

    pivot = body->registers_size - body->ins_size;

    if (!(info->access_flags & ACC_STATIC))
        pivot++;

    if (index >= pivot)
        return (index - pivot) | DVI_ARGUMENT;

    /* S'agit-il de "this" ? */

    if (!(info->access_flags & ACC_STATIC)
        && index == (body->registers_size - body->ins_size))
        return DVI_THIS;

    /* Alors il s'agit d'une variable locale... */

    return index | DVI_LOCAL;

}
