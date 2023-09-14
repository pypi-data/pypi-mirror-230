
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.c - aides auxiliaires relatives aux registres Dalvik
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "register.h"


#include <assert.h>


#include "register-int.h"
#include "../storage.h"



/* ------------------------- REGISTRE SOUS FORME D'OPERANDE ------------------------- */


/* Initialise la classe des opérandes de registre. */
static void g_register_operand_class_init(GRegisterOperandClass *);

/* Initialise une instance d'opérande de registre. */
static void g_register_operand_init(GRegisterOperand *);

/* Supprime toutes les références externes. */
static void g_register_operand_dispose(GRegisterOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_register_operand_finalize(GRegisterOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_register_operand_compare(const GRegisterOperand *, const GRegisterOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_register_operand_print(const GRegisterOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_register_operand_hash(const GRegisterOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_register_operand_load(GRegisterOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_register_operand_store(GRegisterOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                           REGISTRE SOUS FORME D'OPERANDE                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un opérande de registre Dalvik. */
G_DEFINE_TYPE(GRegisterOperand, g_register_operand, G_TYPE_ARCH_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes de registre Dalvik.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_register_operand_class_init(GRegisterOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_register_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_register_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_register_operand_compare;
    operand->print = (operand_print_fc)g_register_operand_print;

    operand->hash = (operand_hash_fc)g_register_operand_hash;

    operand->load = (load_operand_fc)g_register_operand_load;
    operand->store = (store_operand_fc)g_register_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande de registre Dalvik.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_register_operand_init(GRegisterOperand *operand)
{
    operand->reg = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_register_operand_dispose(GRegisterOperand *operand)
{
    g_clear_object(&operand->reg);

    G_OBJECT_CLASS(g_register_operand_parent_class)->dispose(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_register_operand_finalize(GRegisterOperand *operand)
{
    G_OBJECT_CLASS(g_register_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande représentant un registre.                 *
*                                                                             *
*  Description : Fournit le registre associé à l'opérande.                    *
*                                                                             *
*  Retour      : Représentation interne du registre.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchRegister *g_register_operand_get_register(const GRegisterOperand *operand)
{
    GArchRegister *result;                  /* Instance à retourner        */

    result = operand->reg;

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

static int g_register_operand_compare(const GRegisterOperand *a, const GRegisterOperand *b, bool lock)
{
    int result;                             /* Bilan à retourner           */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    result = g_arch_register_compare(a->reg, b->reg);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_register_operand_parent_class);
        result = class->compare(G_ARCH_OPERAND(a), G_ARCH_OPERAND(b), false);
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

static void g_register_operand_print(const GRegisterOperand *operand, GBufferLine *line)
{
    g_arch_register_print(operand->reg, line);

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

static guint g_register_operand_hash(const GRegisterOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    GArchOperandClass *class;               /* Classe parente normalisée   */
    GArchRegister *reg;                     /* Registre visé par l'opérande*/

    class = G_ARCH_OPERAND_CLASS(g_register_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    reg = g_register_operand_get_register(operand);

    result ^= g_arch_register_hash(reg);

    g_object_unref(G_OBJECT(reg));

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

static bool g_register_operand_load(GRegisterOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    GSerializableObject *reg;               /* Registre manipulé           */

    parent = G_ARCH_OPERAND_CLASS(g_register_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        reg = g_object_storage_unpack_object(storage, "registers", pbuf);

        result = (reg != NULL);

        if (result)
            operand->reg = G_ARCH_REGISTER(reg);

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

static bool g_register_operand_store(GRegisterOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */ 
    GSerializableObject *reg;               /* Registre manipulé           */

    parent = G_ARCH_OPERAND_CLASS(g_register_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        reg = G_SERIALIZABLE_OBJECT(operand->reg);
        result = g_object_storage_pack_object(storage, "registers", reg, pbuf);
    }

    return result;

}
