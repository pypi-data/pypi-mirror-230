
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proxy.c - opérandes renvoyant vers des éléments non architecturaux
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "proxy.h"


#include "proxy-int.h"



/* ------------------ OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES ------------------ */


/* Initialise la classe des opérandes renvoyant vers un élément. */
static void g_proxy_operand_class_init(GProxyOperandClass *);

/* Initialise une instance d'opérande renvoyant vers un élément. */
static void g_proxy_operand_init(GProxyOperand *);

/* Supprime toutes les références externes. */
static void g_proxy_operand_dispose(GProxyOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_proxy_operand_finalize(GProxyOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_proxy_operand_compare(const GProxyOperand *, const GProxyOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_proxy_operand_print(const GProxyOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_proxy_operand_hash(const GProxyOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_proxy_operand_load(GProxyOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_proxy_operand_store(GProxyOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                    OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES                    */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un opérande de valeur numérique. */
G_DEFINE_TYPE(GProxyOperand, g_proxy_operand, G_TYPE_ARCH_OPERAND);



/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes renvoyant vers un élément.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_proxy_operand_class_init(GProxyOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_proxy_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_proxy_operand_finalize;

    operand->compare = (operand_compare_fc)g_proxy_operand_compare;
    operand->print = (operand_print_fc)g_proxy_operand_print;

    operand->hash = (operand_hash_fc)g_proxy_operand_hash;

    operand->load = (load_operand_fc)g_proxy_operand_load;
    operand->store = (store_operand_fc)g_proxy_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande renvoyant vers un élément.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_proxy_operand_init(GProxyOperand *operand)
{

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

static void g_proxy_operand_dispose(GProxyOperand *operand)
{
    if (operand->feeder != NULL)
        g_object_unref(G_OBJECT(operand->feeder));

    G_OBJECT_CLASS(g_proxy_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_proxy_operand_finalize(GProxyOperand *operand)
{
    G_OBJECT_CLASS(g_proxy_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : feeder = fournisseur sur lequel s'appuyer.                   *
*                                                                             *
*  Description : Crée un opérande renvoyant vers un élément non architectural.*
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_proxy_operand_new(GProxyFeeder *feeder)
{
    GProxyOperand *result;                    /* Opérande à retourner        */

    result = g_object_new(G_TYPE_PROXY_OPERAND, NULL);

    result->feeder = feeder;

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Fournit le fournisseur représenté par l'opérande.            *
*                                                                             *
*  Retour      : Fournisseur associé à l'opérande.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GProxyFeeder *g_proxy_operand_get_feeder(const GProxyOperand *operand)
{
    GProxyFeeder *result;                   /* Instance à retourner        */

    result = operand->feeder;

    g_object_ref(G_OBJECT(result));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


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

static int g_proxy_operand_compare(const GProxyOperand *a, const GProxyOperand *b, bool lock)
{
    int result;                             /* Bilan à retourner           */
    operand_extra_data_t *ea;               /* Données insérées à consulter*/
    operand_extra_data_t *eb;               /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(a));
    eb = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(b));

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = g_proxy_feeder_compare(a->feeder, b->feeder);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_proxy_operand_parent_class);
        result = class->compare(G_ARCH_OPERAND(a), G_ARCH_OPERAND(b), false);
    }

    if (lock)
    {
        UNLOCK_GOBJECT_EXTRA(eb);
        UNLOCK_GOBJECT_EXTRA(ea);
    }

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

static void g_proxy_operand_print(const GProxyOperand *operand, GBufferLine *line)
{
    g_proxy_feeder_print(operand->feeder, line);

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

static guint g_proxy_operand_hash(const GProxyOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    operand_extra_data_t *extra;            /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_proxy_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= g_direct_hash(operand->feeder);

    if (lock)
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

static bool g_proxy_operand_load(GProxyOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    GSerializableObject *feeder;            /* Fournisseur manipulé        */

    parent = G_ARCH_OPERAND_CLASS(g_proxy_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        feeder = g_object_storage_unpack_object(storage, "operands", pbuf);

        result = (feeder != NULL);

        if (result)
            operand->feeder = G_PROXY_FEEDER(feeder);

    }

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

static bool g_proxy_operand_store(GProxyOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */ 
    GSerializableObject *feeder;            /* Fournisseur manipulé        */

    parent = G_ARCH_OPERAND_CLASS(g_proxy_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        feeder = G_SERIALIZABLE_OBJECT(operand->feeder);
        result = g_object_storage_pack_object(storage, "operands", feeder, pbuf);
    }

    return result;

}
