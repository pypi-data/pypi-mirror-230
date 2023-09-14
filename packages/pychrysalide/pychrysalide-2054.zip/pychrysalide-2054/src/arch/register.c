
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.c - aides auxiliaires relatives aux registres Dalvik
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#include "register-int.h"



/* ---------------------------- PUR REGISTRE DU MATERIEL ---------------------------- */


/* Initialise la classe des registres. */
static void g_arch_register_class_init(GArchRegisterClass *);

/* Initialise une instance de registre. */
static void g_arch_register_init(GArchRegister *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_arch_register_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_arch_register_dispose(GArchRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_arch_register_finalize(GArchRegister *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool _g_arch_register_load(GArchRegister *, GObjectStorage *, packed_buffer_t *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_arch_register_load(GArchRegister *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool _g_arch_register_store(GArchRegister *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_arch_register_store(GArchRegister *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                              PUR REGISTRE DU MATERIEL                              */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre. */
G_DEFINE_TYPE_WITH_CODE(GArchRegister, g_arch_register, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_arch_register_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_register_class_init(GArchRegisterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_arch_register_dispose;
    object->finalize = (GObjectFinalizeFunc)g_arch_register_finalize;

    klass->load = (load_register_fc)_g_arch_register_load;
    klass->store = (store_register_fc)_g_arch_register_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_register_init(GArchRegister *reg)
{

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

static void g_arch_register_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_arch_register_load;
    iface->store = (store_serializable_object_cb)g_arch_register_store;

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

static void g_arch_register_dispose(GArchRegister *reg)
{
    G_OBJECT_CLASS(g_arch_register_parent_class)->dispose(G_OBJECT(reg));

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

static void g_arch_register_finalize(GArchRegister *reg)
{
    G_OBJECT_CLASS(g_arch_register_parent_class)->finalize(G_OBJECT(reg));

}


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

guint g_arch_register_hash(const GArchRegister *reg)
{
    return G_ARCH_REGISTER_GET_CLASS(reg)->hash(reg);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier registre à consulter.                            *
*                b = second registre à consulter.                             *
*                                                                             *
*  Description : Compare un registre avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_arch_register_compare(const GArchRegister *a, const GArchRegister *b)
{
    return G_ARCH_REGISTER_GET_CLASS(a)->compare(a, b);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg  = registre à transcrire.                                *
*                line = ligne tampon où imprimer l'opérande donné.            *
*                                                                             *
*  Description : Traduit un registre en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_register_print(const GArchRegister *reg, GBufferLine *line)
{
    G_ARCH_REGISTER_GET_CLASS(reg)->print(reg, line);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre à consulter.                                  *
*                                                                             *
*  Description : Indique si le registre correspond à ebp ou similaire.        *
*                                                                             *
*  Retour      : true si la correspondance est avérée, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_register_is_base_pointer(const GArchRegister *reg)
{
    bool result;                            /* Bilan à renvoyer            */

    if (G_ARCH_REGISTER_GET_CLASS(reg)->is_bp != NULL)
        result = G_ARCH_REGISTER_GET_CLASS(reg)->is_bp(reg);
    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre à consulter.                                  *
*                                                                             *
*  Description : Indique si le registre correspond à esp ou similaire.        *
*                                                                             *
*  Retour      : true si la correspondance est avérée, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_register_is_stack_pointer(const GArchRegister *reg)
{
    bool result;                            /* Bilan à renvoyer            */

    if (G_ARCH_REGISTER_GET_CLASS(reg)->is_sp != NULL)
        result = G_ARCH_REGISTER_GET_CLASS(reg)->is_sp(reg);
    else
        result = false;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


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

static bool _g_arch_register_load(GArchRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

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

static bool g_arch_register_load(GArchRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *class;              /* Classe à activer            */

    class = G_ARCH_REGISTER_GET_CLASS(reg);

    result = class->load(reg, storage, pbuf);

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

static bool _g_arch_register_store(GArchRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

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

static bool g_arch_register_store(GArchRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *class;              /* Classe à activer            */

    class = G_ARCH_REGISTER_GET_CLASS(reg);

    result = class->store(reg, storage, pbuf);

    return result;

}
