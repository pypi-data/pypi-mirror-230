
/* Chrysalide - Outil d'analyse de fichiers binaires
 * singleton.c - réduction du nombre d'instances d'un même type
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "singleton.h"


#include <assert.h>


#include "singleton-int.h"



/* ------------------ INTERFACE POUR CANDIDAT A UNE CENTRALISATION ------------------ */

/* Procède à l'initialisation de l'interface de rassemblement. */
static void g_singleton_candidate_default_init(GSingletonCandidateInterface *);

/* Met à jour une liste de candidats embarqués par un candidat. */
static void g_singleton_candidate_update_inner_instances(GSingletonCandidate *, GSingletonCandidate **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint _g_singleton_candidate_hash(GSingletonCandidate *, GList **);

/* Détermine si deux candidats à l'unicité sont identiques. */
static gboolean _g_singleton_candidate_is_equal(GSingletonCandidate *, GSingletonCandidate *, GList **);

/* Marque un candidat comme figé. */
static void _g_singleton_candidate_set_read_only(GSingletonCandidate *, GList **);



/* ------------------------- COLLECTION D'INSTANCES UNIQUES ------------------------- */


/* Définition d'un compacteur d'instances de types (instance) */
struct _GSingletonFactory
{
    GObject parent;                         /* A laisser en premier        */

    GHashTable *table;                      /* Suivi des conservations     */
    GMutex access;                          /* Verrou pour la concurrence  */

};

/* Définition d'un compacteur d'instances de types (classe) */
struct _GSingletonFactoryClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des compacteurs d'instances de types. */
static void g_singleton_factory_class_init(GSingletonFactoryClass *);

/* Initialise une instance de compacteur d'instances de types. */
static void g_singleton_factory_init(GSingletonFactory *);

/* Supprime toutes les références externes. */
static void g_singleton_factory_dispose(GSingletonFactory *);

/* Procède à la libération totale de la mémoire. */
static void g_singleton_factory_finalize(GSingletonFactory *);



/* ---------------------------------------------------------------------------------- */
/*                    INTERFACE POUR CANDIDAT A UNE CENTRALISATION                    */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type d'une interface pour la lecture de binaire. */
G_DEFINE_INTERFACE(GSingletonCandidate, g_singleton_candidate, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de rassemblement.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_singleton_candidate_default_init(GSingletonCandidateInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                count     = quantité d'instances à l'unicité internes.       *
*                                                                             *
*  Description : Fournit une liste de candidats embarqués par un candidat.    *
*                                                                             *
*  Retour      : Liste de candidats internes ou NULL si aucun.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSingletonCandidate **g_singleton_candidate_list_inner_instances(const GSingletonCandidate *candidate, size_t *count)
{
    GSingletonCandidate **result;           /* Instances à retourner       */
    GSingletonCandidateIface *iface;        /* Interface utilisée          */

    iface = G_SINGLETON_CANDIDATE_GET_IFACE(candidate);

    if (iface->list_inner == NULL)
    {
        *count = 0;
        result = NULL;
    }

    else
        result = iface->list_inner(candidate, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                instances = liste de candidats internes devenus singletons.  *
*                count     = quantité d'instances à l'unicité internes.       *
*                                                                             *
*  Description : Met à jour une liste de candidats embarqués par un candidat. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_singleton_candidate_update_inner_instances(GSingletonCandidate *candidate, GSingletonCandidate **instances, size_t count)
{
    GSingletonCandidateIface *iface;        /* Interface utilisée          */

    iface = G_SINGLETON_CANDIDATE_GET_IFACE(candidate);

    if (iface->update_inner == NULL)
        assert(iface->list_inner == NULL);

    else
    {
        assert(iface->list_inner != NULL);
        iface->update_inner(candidate, instances, count);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                processed = liste de candidats déjà traités.                 *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint _g_singleton_candidate_hash(GSingletonCandidate *candidate, GList **processed)
{
    guint result;                           /* Valeur à retourner          */
    GList *skip;                            /* Détection de boucle         */
    GSingletonCandidateIface *iface;        /* Interface utilisée          */
    GSingletonCandidate **children;         /* Instances internes          */
    size_t count;                           /* Quantité de ces instances   */
    size_t i;                               /* Boucle de parcours          */

    skip = g_list_find(*processed, candidate);

    if (skip != NULL)
        result = 0;

    else
    {
        iface = G_SINGLETON_CANDIDATE_GET_IFACE(candidate);

        result = iface->hash(candidate);

        *processed = g_list_append(*processed, candidate);

        children = g_singleton_candidate_list_inner_instances(candidate, &count);

        for (i = 0; i < count; i++)
        {
            result ^= _g_singleton_candidate_hash(children[i], processed);
            g_object_unref(G_OBJECT(children[i]));
        }

        if (children != NULL)
            free(children);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

guint g_singleton_candidate_hash(GSingletonCandidate *candidate)
{
    guint result;                           /* Valeur à retourner          */
    GList *processed;                       /* Suivi des traitements       */

    processed = NULL;

    result = _g_singleton_candidate_hash(candidate, &processed);

    assert(processed != NULL);

    g_list_free(processed);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                other     = second élément à analyser.                       *
*                processed = liste de candidats déjà traités.                 *
*                                                                             *
*  Description : Détermine si deux candidats à l'unicité sont identiques.     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean _g_singleton_candidate_is_equal(GSingletonCandidate *candidate, GSingletonCandidate *other, GList **processed)
{
    gboolean result;                        /* Bilan à renvoyer            */
    GList *skip;                            /* Détection de boucle         */
    GSingletonCandidateIface *iface;        /* Interface utilisée          */
    GSingletonCandidate **children[2];      /* Instances internes          */
    size_t count[2];                        /* Quantité de ces instances   */
    size_t i;                               /* Boucle de parcours          */

    skip = g_list_find(processed[0], candidate);

    if (skip != NULL)
        result = (g_list_find(processed[1], other) != NULL);

    else
    {
        iface = G_SINGLETON_CANDIDATE_GET_IFACE(candidate);

        result = iface->is_equal(candidate, other);

        processed[0] = g_list_append(processed[0], candidate);
        processed[1] = g_list_append(processed[1], other);

        if (!result)
            goto done;

        children[0] = g_singleton_candidate_list_inner_instances(candidate, &count[0]);
        children[1] = g_singleton_candidate_list_inner_instances(other, &count[1]);

        if (count[0] != count[1])
        {
            for (i = 0; i < count[0]; i++)
                g_object_unref(G_OBJECT(children[0][i]));

            for (i = 0; i < count[1]; i++)
                g_object_unref(G_OBJECT(children[1][i]));

        }

        else
        {
            for (i = 0; i < count[0] && result; i++)
            {
                result = _g_singleton_candidate_is_equal(children[0][i], children[1][i], processed);
                g_object_unref(G_OBJECT(children[0][i]));
                g_object_unref(G_OBJECT(children[1][i]));
            }

            for (; i < count[0]; i++)
            {
                g_object_unref(G_OBJECT(children[0][i]));
                g_object_unref(G_OBJECT(children[1][i]));
            }

            if (children[0] != NULL)
                free(children[0]);

            if (children[1] != NULL)
                free(children[1]);

        }

    }

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                other     = second élément à analyser.                       *
*                                                                             *
*  Description : Détermine si deux candidats à l'unicité sont identiques.     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gboolean g_singleton_candidate_is_equal(GSingletonCandidate *candidate, GSingletonCandidate *other)
{
    gboolean result;                        /* Bilan à renvoyer            */
    GList *processed[2];                    /* Suivi des traitements       */

    processed[0] = NULL;
    processed[1] = NULL;

    result = _g_singleton_candidate_is_equal(candidate, other, processed);

    assert(processed[0] != NULL);
    assert(processed[1] != NULL);

    g_list_free(processed[0]);
    g_list_free(processed[1]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                processed = liste de candidats déjà traités.                 *
*                                                                             *
*  Description : Marque un candidat comme figé.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _g_singleton_candidate_set_read_only(GSingletonCandidate *candidate, GList **processed)
{
    GList *skip;                            /* Détection de boucle         */
    GSingletonCandidateIface *iface;        /* Interface utilisée          */
    GSingletonCandidate **children;         /* Instances internes          */
    size_t count;                           /* Quantité de ces instances   */
    size_t i;                               /* Boucle de parcours          */

    skip = g_list_find(*processed, candidate);

    if (skip == NULL)
    {
        iface = G_SINGLETON_CANDIDATE_GET_IFACE(candidate);

        iface->set_ro(candidate);

        *processed = g_list_append(*processed, candidate);

        children = g_singleton_candidate_list_inner_instances(candidate, &count);

        for (i = 0; i < count; i++)
        {
            _g_singleton_candidate_set_read_only(candidate, processed);
            g_object_unref(G_OBJECT(children[i]));
        }

        if (children != NULL)
            free(children);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                                                                             *
*  Description : Marque un candidat comme figé.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_singleton_candidate_set_read_only(GSingletonCandidate *candidate)
{
    GList *processed;                       /* Suivi des traitements       */

    processed = NULL;

    _g_singleton_candidate_set_read_only(candidate, &processed);

    assert(processed != NULL);

    g_list_free(processed);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                                                                             *
*  Description : Indique si le candidat est figé.                             *
*                                                                             *
*  Retour      : true si le contenu du candidat ne peut plus être modifié.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_singleton_candidate_is_read_only(const GSingletonCandidate *candidate)
{
    bool result;                            /* Etat à retourner            */
    GSingletonCandidateIface *iface;        /* Interface utilisée          */

    iface = G_SINGLETON_CANDIDATE_GET_IFACE(candidate);

    result = iface->is_ro(candidate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           COLLECTION D'INSTANCES UNIQUES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une mémoire de types d'objets. */
G_DEFINE_TYPE(GSingletonFactory, g_singleton_factory, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des compacteurs d'instances de types.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_singleton_factory_class_init(GSingletonFactoryClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_singleton_factory_dispose;
    object->finalize = (GObjectFinalizeFunc)g_singleton_factory_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : factory = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de compacteur d'instances de types.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_singleton_factory_init(GSingletonFactory *factory)
{
    factory->table = g_hash_table_new_full((GHashFunc)g_singleton_candidate_hash,
                                           (GEqualFunc)g_singleton_candidate_is_equal,
                                           g_object_unref, NULL);

    g_mutex_init(&factory->access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : factory = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_singleton_factory_dispose(GSingletonFactory *factory)
{
    if (factory->table != NULL)
    {
        g_hash_table_unref(factory->table);
        factory->table = NULL;
    }

    G_OBJECT_CLASS(g_singleton_factory_parent_class)->dispose(G_OBJECT(factory));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : factory = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_singleton_factory_finalize(GSingletonFactory *factory)
{
    g_mutex_clear(&factory->access);

    G_OBJECT_CLASS(g_singleton_factory_parent_class)->finalize(G_OBJECT(factory));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un compacteur d'instances de types.                     *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSingletonFactory *g_singleton_factory_new(void)
{
    GSingletonFactory *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_SINGLETON_FACTORY, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : factory   = gestionnaire d'instances uniques à consulter.    *
*                candidate = instance à conserver ou oublier.                 *
*                                                                             *
*  Description : Fournit l'instance unique correspondant à un objet.          *
*                                                                             *
*  Retour      : Instance unique à utiliser.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSingletonCandidate *g_singleton_factory_get_instance(GSingletonFactory *factory, GSingletonCandidate *candidate)
{
    GSingletonCandidate *result;            /* Instance unique à retourner */
    size_t count;                           /* Quantité d'objets internes  */
    GSingletonCandidate **instances;        /* Liste d'instances internes  */
    GSingletonCandidate **updated;          /* Nouvelle liste d'instances  */
    bool need_update;                       /* Mise à jour nécessaire      */
    size_t i;                               /* Boucle de parcours          */
#ifndef NDEBUG
    gboolean status;                        /* Validation d'une opération  */
#endif

    /* Validation des objets internes éventuels */

    instances = g_singleton_candidate_list_inner_instances(candidate, &count);

    if (count > 0)
    {
        updated = malloc(count * sizeof(GSingletonCandidate *));
        need_update = false;

        for (i = 0; i < count; i++)
        {
            updated[i] = g_singleton_factory_get_instance(factory, instances[i]);
            need_update |= (instances[i] != updated[i]);
        }

        if (need_update)
            g_singleton_candidate_update_inner_instances(candidate, updated, count);

        for (i = 0; i < count; i++)
        {
            g_object_unref(G_OBJECT(updated[i]));
            g_object_unref(G_OBJECT(instances[i]));
        }

        free(updated);

    }

    if (instances != NULL)
        free(instances);

    /* Récupération de l'instance principale */

    g_mutex_lock(&factory->access);

    if (g_hash_table_contains(factory->table, candidate))
    {
#ifndef NDEBUG
        status = g_hash_table_lookup_extended(factory->table, candidate, (void **)&result, NULL);
        assert(status);
#else
        g_hash_table_lookup_extended(factory->table, candidate, (void **)&result, NULL);
#endif

    }

    else
    {
        g_object_ref(G_OBJECT(candidate));

#ifndef NDEBUG
        status = g_hash_table_add(factory->table, candidate);
        assert(status);
#else
        g_hash_table_add(factory->table, candidate);
#endif

        g_singleton_candidate_set_read_only(candidate);

        result = candidate;

    }

    g_object_ref(G_OBJECT(result));

    g_mutex_unlock(&factory->access);

    return result;

}
