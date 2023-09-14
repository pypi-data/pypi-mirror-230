
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dt.c - possibilité de créer de nouveaux types de façon dynamique
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


#include "dt.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../plugins/pglist.h"



/* ------------------------- MODULE DE GESTION DES NOUVEAUX ------------------------- */


#define G_TYPE_DYNAMIC_TYPES            g_dynamic_types_get_type()
#define G_DYNAMIC_TYPES(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DYNAMIC_TYPES, GDynamicTypes))
#define G_IS_DYNAMIC_TYPES(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DYNAMIC_TYPES))
#define G_DYNAMIC_TYPES_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DYNAMIC_TYPES, GDynamicTypesClass))
#define G_IS_DYNAMIC_TYPES_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DYNAMIC_TYPES))
#define G_DYNAMIC_TYPES_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DYNAMIC_TYPES, GDynamicTypesClass))


/* Mémorisation des caractéristiques de type */
typedef struct _type_dyn_info_t
{
    GType type;                             /* Identifiant unique obtenu   */

    GClassInitFunc cinit;                   /* Phase d'initialisation #1   */
    gconstpointer data;                     /* Eventuelles données utiles  */

    GInstanceInitFunc init;                 /* Phase d'initialisation #2   */

} type_dyn_info_t;

/* Description de fichier binaire (instance) */
typedef struct _GDynamicTypes
{
    GObject parent;                         /* A laisser en premier        */

    type_dyn_info_t **info;                 /* Liste d'informations utiles */
    size_t count;                           /* Taille de cette liste       */

} GDynamicTypes;

/* Description de fichier binaire (classe) */
typedef struct _GDynamicTypesClass
{
    GObjectClass parent;                    /* A laisser en premier        */

} GDynamicTypesClass;


/* Indique le type défini pour une gestion de types dynamique. */
static GType g_dynamic_types_get_type(void);

/* Initialise la classe de gestion de types dynamique. */
static void g_dynamic_types_class_init(GDynamicTypesClass *);

/* Initialise une gestion de types dynamique. */
static void g_dynamic_types_init(GDynamicTypes *);

/* Procède à l'initialisation de l'interface de typage nouveau. */
static void g_dynamic_types_interface_init(GTypePluginClass *);

/* Supprime toutes les références externes. */
static void g_dynamic_types_dispose(GDynamicTypes *);

/* Procède à la libération totale de la mémoire. */
static void g_dynamic_types_finalize(GDynamicTypes *);

/* Crée un nouveau gestionnaire de nouveaux types. */
static GDynamicTypes *g_dynamic_types_new(void);

/* Marque une augmentation des utilisations. */
static void g_dynamic_types_use(GDynamicTypes *);

/* Marque une diminution des utilisations. */
static void g_dynamic_types_unuse(GDynamicTypes *);

/* Complète la définition d'un type dynamiquement. */
static void g_dynamic_types_complete_type(GDynamicTypes *, GType, GTypeInfo *, GTypeValueTable *);

/* Retrouve les informations concernant un type dynamique. */
static type_dyn_info_t *g_dynamic_types_find(const GDynamicTypes *, GType);

/* Fournit un identifiant GLib pour un nouveau type. */
static GType g_dynamic_types_register_type(GDynamicTypes *, GType, const char *, GClassInitFunc, gconstpointer, GInstanceInitFunc);



/* ----------------------- ACCOMPAGNEMENTS DES NOUVEAUX TYPES ----------------------- */


/* Encadrement des nouveaux types dérivés */
static GDynamicTypes *_chrysalide_dtypes = NULL;



/* ---------------------------------------------------------------------------------- */
/*                           MODULE DE GESTION DES NOUVEAUX                           */
/* ---------------------------------------------------------------------------------- */

/* Indique le type défini pour une gestion de types dynamique. */
G_DEFINE_TYPE_WITH_CODE(GDynamicTypes, g_dynamic_types, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_TYPE_PLUGIN, g_dynamic_types_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe de gestion de types dynamique.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_class_init(GDynamicTypesClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dynamic_types_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dynamic_types_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : types = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une gestion de types dynamique.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_init(GDynamicTypes *types)
{

}

/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de typage nouveau. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_interface_init(GTypePluginClass *iface)
{
    iface->use_plugin = (GTypePluginUse)g_dynamic_types_use;
    iface->unuse_plugin = (GTypePluginUnuse)g_dynamic_types_unuse;
    iface->complete_type_info = (GTypePluginCompleteTypeInfo)g_dynamic_types_complete_type;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : types = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_dispose(GDynamicTypes *types)
{
    G_OBJECT_CLASS(g_dynamic_types_parent_class)->dispose(G_OBJECT(types));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : types = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_finalize(GDynamicTypes *types)
{
    G_OBJECT_CLASS(g_dynamic_types_parent_class)->finalize(G_OBJECT(types));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau gestionnaire de nouveaux types.              *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDynamicTypes *g_dynamic_types_new(void)
{
    GDynamicTypes *result;                  /* Adresse à retourner         */

    result = g_object_new(G_TYPE_DYNAMIC_TYPES, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : types = gestionnaire de types courant.                       *
*                                                                             *
*  Description : Marque une augmentation des utilisations.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_use(GDynamicTypes *types)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : types = gestionnaire de types courant.                       *
*                                                                             *
*  Description : Marque une diminution des utilisations.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_unuse(GDynamicTypes *types)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : types = gestionnaire de types courant.                       *
*                type  = nouveau type GLib à traiter.                         *
*                info  = information concernant ce type à constituer. [OUT]   *
*                table = table de valeur à éventuellement initialiser. [OUT]  *
*                                                                             *
*  Description : Complète la définition d'un type dynamiquement.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dynamic_types_complete_type(GDynamicTypes *types, GType type, GTypeInfo *info, GTypeValueTable *table)
{
    type_dyn_info_t *nfo;                   /* Source d'inspiration        */
    GType parent;                           /* Type parent du type         */
    GTypeQuery query;                       /* Informations complémentaires*/

    /* Consultation */

    nfo = g_dynamic_types_find(types, type);
    assert(nfo != NULL);

    parent = g_type_parent(type);
    g_type_query(parent, &query);

    /* Définition */

    info->class_size = query.class_size;
    info->class_init = nfo->cinit;
    info->class_data = nfo->data;

    info->instance_size = query.instance_size;
    info->instance_init = nfo->init;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = type GLib parent.                                   *
*                type   = identifiant du type GLib à considérer.              *
*                                                                             *
*  Description : Retrouve les informations concernant un type dynamique.      *
*                                                                             *
*  Retour      : Structure contenant les informations associées au type.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static type_dyn_info_t *g_dynamic_types_find(const GDynamicTypes *types, GType target)
{
    type_dyn_info_t *result;                /* Informations à retourner    */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < types->count && result == NULL; i++)
        if (types->info[i]->type == target)
            result = types->info[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = type GLib parent.                                   *
*                name   = désignation du nouveau type.                        *
*                cinit  = procédure d'initialisation de la classe associée.   *
*                data   = éventuelles données à associer à la future classe.  *
*                init   = procédure d'initialisation pour chaque instance.    *
*                                                                             *
*  Description : Fournit un identifiant GLib pour un nouveau type.            *
*                                                                             *
*  Retour      : identifiant d'un nouveau type valide, ou 0.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GType g_dynamic_types_register_type(GDynamicTypes *types, GType parent, const char *name, GClassInitFunc cinit, gconstpointer data, GInstanceInitFunc init)
{
    GType result;                           /* Identifiant à retourner     */
    type_dyn_info_t *new;                   /* Mémorisation de paramètres  */

    /* Création d'un nouveau type adapté */

    result = g_type_register_dynamic(parent, name, G_TYPE_PLUGIN(types), 0);

    if (result == 0)
        goto exit;

    new = malloc(sizeof(type_dyn_info_t));

    new->type = result;

    new->cinit = cinit;
    new->data = data;

    new->init = init;

    /* Inscription définitive */

    types->info = realloc(types->info, ++types->count * sizeof(type_dyn_info_t *));

    types->info[types->count - 1] = new;

 exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         ACCOMPAGNEMENTS DES NOUVEAUX TYPES                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Lance le support de dérivations de types dans Chrysalide.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_chrysalide_dynamic_types(void)
{
    bool result;                            /* Bilan à retourner           */

    _chrysalide_dtypes = g_dynamic_types_new();

    result = (_chrysalide_dtypes != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Arrête le support de dérivations de types dans Chrysalide.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_chrysalide_dynamic_types(void)
{
    g_object_unref(G_OBJECT(_chrysalide_dtypes));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = type GLib parent.                                   *
*                name   = désignation du nouveau type.                        *
*                cinit  = procédure d'initialisation de la classe associée.   *
*                data   = éventuelles données à associer à la future classe.  *
*                init   = procédure d'initialisation pour chaque instance.    *
*                                                                             *
*  Description : Fournit un identifiant GLib pour un nouveau type.            *
*                                                                             *
*  Retour      : Identifiant d'un nouveau type valide, ou 0.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GType build_dynamic_type(GType parent, const char *name, GClassInitFunc cinit, gconstpointer data, GInstanceInitFunc init)
{
    GType result;                           /* Identifiant à retourner     */

    result = g_type_from_name(name);

    if (result == 0)
        result = g_dynamic_types_register_type(_chrysalide_dtypes, parent, name, cinit, data, init);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type d'instance à créer.                              *
*                                                                             *
*  Description : Crée un objet à partir d'un type, dynamique ou classique.    *
*                                                                             *
*  Retour      : Instance d'objet mise en place ou NULL en cas d'erreur.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gpointer create_object_from_type(GType type)
{
    GObject *result;                        /* Instance à retourner        */

    result = NULL;

    if (g_dynamic_types_find(_chrysalide_dtypes, type) != NULL)
        result = build_type_instance(type);

    else
        result = g_object_new(type, NULL);

    assert(result != NULL);

    return result;

}
