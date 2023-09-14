
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.c - gestion générique des opérandes
 *
 * Copyright (C) 2008-2020 Cyrille Bagard
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


#include "operand.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "operand-int.h"
#include "storage.h"
#include "../analysis/storage/serialize-int.h"
#include "../common/fnv1a.h"
#include "../common/sort.h"
#include "../core/logs.h"
#include "../glibext/singleton-int.h"



/* ------------------------ DEFINITION D'OPERANDE QUELCONQUE ------------------------ */


/* Initialise la classe générique des opérandes. */
static void g_arch_operand_class_init(GArchOperandClass *);

/* Initialise une instance d'opérande d'architecture. */
static void g_arch_operand_init(GArchOperand *);

/* Procède à l'initialisation de l'interface de singleton. */
static void g_arch_operand_singleton_init(GSingletonCandidateInterface *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_arch_operand_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_arch_operand_dispose(GArchOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_arch_operand_finalize(GArchOperand *);

/* Compare un opérande avec un autre. */
static int _g_arch_operand_compare(const GArchOperand *, const GArchOperand *, bool);



/* ------------------------ CONTROLE DU VOLUME DES INSTANCES ------------------------ */


/* Fournit une liste de candidats embarqués par un candidat. */
GArchOperand **g_arch_operand_list_inner_instances(const GArchOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
void g_arch_operand_update_inner_instances(GArchOperand *, GArchOperand **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint _g_arch_operand_hash(const GArchOperand *, bool);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_arch_operand_hash(const GArchOperand *);

/* Détermine si deux candidats à l'unicité sont identiques. */
static gboolean g_arch_operand_is_equal(const GArchOperand *, const GArchOperand *);

/* Marque un candidat comme figé. */
static void g_arch_operand_set_read_only(GArchOperand *);

/* Indique si le candidat est figé. */
static bool g_arch_operand_is_read_only(GArchOperand *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool _g_arch_operand_load(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_arch_operand_load(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool _g_arch_operand_store(GArchOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_arch_operand_store(GArchOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                          DEFINITION D'OPERANDE QUELCONQUE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un opérande d'architecture. */
G_DEFINE_TYPE_WITH_CODE(GArchOperand, g_arch_operand, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_SINGLETON_CANDIDATE, g_arch_operand_singleton_init)
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_arch_operand_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe générique des opérandes.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_class_init(GArchOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_arch_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_arch_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)_g_arch_operand_compare;

    operand->hash = _g_arch_operand_hash;

    operand->load = (load_operand_fc)_g_arch_operand_load;
    operand->store = (store_operand_fc)_g_arch_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande d'architecture.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_init(GArchOperand *operand)
{
    operand_extra_data_t *extra;            /* Données insérées à modifier */

    extra = GET_ARCH_OP_EXTRA(operand);

    INIT_GOBJECT_EXTRA_LOCK(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de singleton.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_singleton_init(GSingletonCandidateInterface *iface)
{
    iface->list_inner = (list_inner_instances_fc)g_arch_operand_list_inner_instances;
    iface->update_inner = (update_inner_instances_fc)g_arch_operand_update_inner_instances;

    iface->hash = (hash_candidate_fc)g_arch_operand_hash;
    iface->is_equal = (is_candidate_equal_fc)g_arch_operand_is_equal;

    iface->set_ro = (set_candidate_ro_fc)g_arch_operand_set_read_only;
    iface->is_ro = (is_candidate_ro_fc)g_arch_operand_is_read_only;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de sérialisation.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_arch_operand_load;
    iface->store = (store_serializable_object_cb)g_arch_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_dispose(GArchOperand *operand)
{
    G_OBJECT_CLASS(g_arch_operand_parent_class)->dispose(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_finalize(GArchOperand *operand)
{
    G_OBJECT_CLASS(g_arch_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a    = premier opérande à consulter.                         *
*                b    = second opérande à consulter.                          *
*                lock = précise le besoin en verrouillage.                    *
*                                                                             *
*  Description : Compare un opérande avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int _g_arch_operand_compare(const GArchOperand *a, const GArchOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    operand_extra_data_t *ea;               /* Données insérées à consulter*/
    operand_extra_data_t *eb;               /* Données insérées à consulter*/

    assert(!lock);

    ea = GET_ARCH_OP_EXTRA(a);
    eb = GET_ARCH_OP_EXTRA(b);

    result = sort_unsigned_long(ea->flags, eb->flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier opérande à consulter.                            *
*                b = second opérande à consulter.                             *
*                                                                             *
*  Description : Compare un opérande avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_arch_operand_compare(const GArchOperand *a, const GArchOperand *b)
{
    int result;                             /* Bilan à faire remonter      */
    GType type_a;                           /* Type de l'object A          */
    GType type_b;                           /* Type de l'object B          */

    type_a = G_OBJECT_TYPE(G_OBJECT(a));
    type_b = G_OBJECT_TYPE(G_OBJECT(b));

    assert(sizeof(GType) <= sizeof(unsigned long));

    result = sort_unsigned_long(type_a, type_b);

    if (result == 0)
        result = G_ARCH_OPERAND_GET_CLASS(a)->compare(a, b, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                target  = instruction à venir retrouver.                     *
*                                                                             *
*  Description : Détermine le chemin conduisant à un opérande interne.        *
*                                                                             *
*  Retour      : Chemin d'accès à l'opérande ou NULL en cas d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_arch_operand_find_inner_operand_path(const GArchOperand *operand, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */
    GArchOperandClass *class;               /* Classe associée à l'objet   */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    if (class->find_inner != NULL)
        result = class->find_inner(operand, target);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                path  = chemin d'accès à un opérande à retrouver.            *
*                                                                             *
*  Description : Obtient l'opérande correspondant à un chemin donné.          *
*                                                                             *
*  Retour      : Opérande trouvé ou NULL en cas d'échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_arch_operand_get_inner_operand_from_path(const GArchOperand *operand, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */
    GArchOperandClass *class;               /* Classe associée à l'objet   */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    if (class->get_inner != NULL)
        result = class->get_inner(operand, path);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à traiter.                                *
*                line    = ligne tampon où imprimer l'opérande donné.         *
*                                                                             *
*  Description : Traduit un opérande en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_operand_print(const GArchOperand *operand, GBufferLine *line)
{
    G_ARCH_OPERAND_GET_CLASS(operand)->print(operand, line);

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                binary  = informations relatives au binaire chargé.          *
*                                                                             *
*  Description : Construit un petit résumé concis de l'opérande.              *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_arch_operand_build_tooltip(const GArchOperand *operand, const GLoadedBinary *binary)
{
    char *result;                           /* Description à retourner     */
    GArchOperandClass *class;               /* Classe associée à l'objet   */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    if (class->build_tooltip != NULL)
        result = class->build_tooltip(operand, binary);
    else
        result = NULL;

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à venir modifier.                         *
*                flag    = drapeau d'information complémentaire à planter.    *
*                lock    = indique un besoin de verrouillage des données.     *
*                                                                             *
*  Description : Ajoute une information complémentaire à un opérande.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_arch_operand_set_flag(GArchOperand *operand, ArchOperandFlag flag, bool lock)
{
    bool result;                            /* Bilan à retourner           */
    operand_extra_data_t *extra;            /* Données insérées à modifier */

    assert(flag <= AOF_HIGH_USER);

    extra = GET_ARCH_OP_EXTRA(operand);

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    result = !(extra->flags & flag);

    extra->flags |= flag;

    if (lock)
        UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à venir modifier.                         *
*                flag    = drapeau d'information complémentaire à planter.    *
*                                                                             *
*  Description : Ajoute une information complémentaire à un opérande.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_set_flag(GArchOperand *operand, ArchOperandFlag flag)
{
    bool result;                            /* Bilan à retourner           */

    result = _g_arch_operand_set_flag(operand, flag, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à venir modifier.                         *
*                flag    = drapeau d'information complémentaire à planter.    *
*                lock    = indique un besoin de verrouillage des données.     *
*                                                                             *
*  Description : Retire une information complémentaire à un opérande.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_arch_operand_unset_flag(GArchOperand *operand, ArchOperandFlag flag, bool lock)
{
    bool result;                            /* Bilan à retourner           */
    operand_extra_data_t *extra;            /* Données insérées à modifier */

    assert(flag <= AOF_HIGH_USER);

    extra = GET_ARCH_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    extra->flags &= ~flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à venir modifier.                         *
*                flag    = drapeau d'information complémentaire à planter.    *
*                                                                             *
*  Description : Retire une information complémentaire à un opérande.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_unset_flag(GArchOperand *operand, ArchOperandFlag flag)
{
    bool result;                            /* Bilan à retourner           */

    result = _g_arch_operand_unset_flag(operand, flag, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à venir consulter.                        *
*                flag    = drapeau d'information à rechercher.                *
*                                                                             *
*  Description : Détermine si un opérande possède un fanion particulier.      *
*                                                                             *
*  Retour      : Bilan de la détection.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_has_flag(const GArchOperand *operand, ArchOperandFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    operand_extra_data_t *extra;            /* Données insérées à modifier */

    assert(flag <= AOF_HIGH_USER);

    extra = GET_ARCH_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à venir consulter.                        *
*                                                                             *
*  Description : Fournit les particularités de l'opérande.                    *
*                                                                             *
*  Retour      : Somme de tous les fanions associés à l'opérande.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ArchOperandFlag g_arch_operand_get_flags(const GArchOperand *operand)
{
    ArchOperandFlag result;                 /* Fanions à retourner         */
    operand_extra_data_t *extra;            /* Données insérées à modifier */

    extra = GET_ARCH_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->flags;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          CONTROLE DU VOLUME DES INSTANCES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                count   = quantité d'instances à l'unicité internes.         *
*                                                                             *
*  Description : Fournit une liste de candidats embarqués par un candidat.    *
*                                                                             *
*  Retour      : Liste de candidats internes ou NULL si aucun.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand **g_arch_operand_list_inner_instances(const GArchOperand *operand, size_t *count)
{
    GArchOperand **result;                  /* Instances à retourner       */
    GArchOperandClass *class;               /* Classe associée à l'objet   */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    if (class->list_inner == NULL)
    {
        *count = 0;
        result = NULL;
    }

    else
        result = class->list_inner(operand, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand   = objet dont l'instance se veut unique.            *
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

void g_arch_operand_update_inner_instances(GArchOperand *operand, GArchOperand **instances, size_t count)
{
    GArchOperandClass *class;               /* Classe associée à l'objet   */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    if (class->update_inner == NULL)
        assert(class->list_inner == NULL);

    else
    {
        assert(class->list_inner != NULL);
        class->update_inner(operand, instances, count);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                lock    = précise le besoin en verrouillage.                 *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint _g_arch_operand_hash(const GArchOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    const char *name;                       /* Désignation du type d'object*/
    fnv64_t name_hash;                      /* Empreinte du nom            */
    operand_extra_data_t *extra;            /* Données insérées à modifier */

    assert(!lock);

    name = G_OBJECT_TYPE_NAME(G_OBJECT(operand));
    name_hash = fnv_64a_hash(name);

    result = (name_hash & 0xffffffff);
    result ^= (name_hash >> 32);

    extra = GET_ARCH_OP_EXTRA(operand);

    result ^= extra->flags;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_arch_operand_hash(const GArchOperand *operand)
{
    guint result;                           /* Valeur à retourner          */
    GArchOperandClass *class;               /* Classe associée à l'objet   */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    result = class->hash(operand, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                other   = second élément à analyser.                         *
*                                                                             *
*  Description : Détermine si deux candidats à l'unicité sont identiques.     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean g_arch_operand_is_equal(const GArchOperand *operand, const GArchOperand *other)
{
    gboolean result;                        /* Bilan à renvoyer            */
    int ret;                                /* Bilan d'une comparaison     */

    ret = g_arch_operand_compare(operand, other);

    result = (ret == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                                                                             *
*  Description : Marque un candidat comme figé.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_operand_set_read_only(GArchOperand *operand)
{
    g_arch_operand_set_flag(operand, AOF_READ_ONLY);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                                                                             *
*  Description : Indique si le candidat est figé.                             *
*                                                                             *
*  Retour      : true si le contenu du candidat ne peut plus être modifié.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_operand_is_read_only(GArchOperand *operand)
{
    bool result;                            /* Etat à retourner            */

    result = g_arch_operand_has_flag(operand, AOF_READ_ONLY);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_arch_operand_load(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    operand_extra_data_t *extra;            /* Données insérées à consulter*/
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    extra = GET_ARCH_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = unpack_uleb128(&value, pbuf);

    if (result)
        extra->flags = value;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_operand_load(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *class;               /* Classe à activer            */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    result = class->load(operand, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_arch_operand_store(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    operand_extra_data_t *extra;            /* Données insérées à consulter*/

    extra = GET_ARCH_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = pack_uleb128((uleb128_t []){ extra->flags }, pbuf);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_operand_store(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *class;               /* Classe à activer            */

    class = G_ARCH_OPERAND_GET_CLASS(operand);

    result = class->store(operand, storage, pbuf);

    return result;

}
