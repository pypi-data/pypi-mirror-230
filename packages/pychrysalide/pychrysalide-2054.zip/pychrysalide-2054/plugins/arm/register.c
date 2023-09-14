
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.c - aides auxiliaires relatives aux registres ARM
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include <common/sort.h>


#include "register-int.h"



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Initialise la classe des registres ARM. */
static void g_arm_register_class_init(GArmRegisterClass *);

/* Initialise une instance de registre ARM. */
static void g_arm_register_init(GArmRegister *);

/* Supprime toutes les références externes. */
static void g_arm_register_dispose(GArmRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_arm_register_finalize(GArmRegister *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Produit une empreinte à partir d'un registre. */
static guint g_arm_register_hash(const GArmRegister *);

/* Compare un registre avec un autre. */
static int g_arm_register_compare(const GArmRegister *, const GArmRegister *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_arm_register_load(GArmRegister *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_arm_register_store(GArmRegister *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre ARM. */
G_DEFINE_TYPE(GArmRegister, g_arm_register, G_TYPE_ARCH_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres Arm.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_register_class_init(GArmRegisterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchRegisterClass *reg;                /* Classe de haut niveau       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_arm_register_dispose;
    object->finalize = (GObjectFinalizeFunc)g_arm_register_finalize;

    reg = G_ARCH_REGISTER_CLASS(klass);

    reg->hash = (reg_hash_fc)g_arm_register_hash;
    reg->compare = (reg_compare_fc)g_arm_register_compare;

    reg->load = (load_register_fc)g_arm_register_load;
    reg->store = (store_register_fc)g_arm_register_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre ARM.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_register_init(GArmRegister *reg)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_register_dispose(GArmRegister *reg)
{
    G_OBJECT_CLASS(g_arm_register_parent_class)->dispose(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_register_finalize(GArmRegister *reg)
{
    G_OBJECT_CLASS(g_arm_register_parent_class)->finalize(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre à consulter.                                  *
*                                                                             *
*  Description : Fournit l'indice d'un registre ARM.                          *
*                                                                             *
*  Retour      : Inditifiant représentant le registre.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint8_t g_arm_register_get_index(const GArmRegister *reg)
{
    return reg->index;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = opérande à consulter pour le calcul.                   *
*                                                                             *
*  Description : Produit une empreinte à partir d'un registre.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_arm_register_hash(const GArmRegister *reg)
{
    return reg->index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier opérande à consulter.                            *
*                b = second opérande à consulter.                             *
*                                                                             *
*  Description : Compare un registre avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_arm_register_compare(const GArmRegister *a, const GArmRegister *b)
{
    int result;                             /* Bilan à retourner           */

    result = sort_unsigned_long(a->index, b->index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg     = élément GLib à constuire.                          *
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

static bool g_arm_register_load(GArmRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *parent;             /* Classe parente à consulter  */

    parent = G_ARCH_REGISTER_CLASS(g_arm_register_parent_class);

    result = parent->load(G_ARCH_REGISTER(reg), storage, pbuf);

    if (result)
        result = extract_packed_buffer(pbuf, &reg->index, sizeof(uint8_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg     = élément GLib à consulter.                          *
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

static bool g_arm_register_store(GArmRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *parent;             /* Classe parente à consulter  */

    parent = G_ARCH_REGISTER_CLASS(g_arm_register_parent_class);

    result = parent->store(G_ARCH_REGISTER(reg), storage, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, &reg->index, sizeof(uint8_t), false);

    return result;

}
