
/* Chrysalide - Outil d'analyse de fichiers binaires
 * it.c - manipulation des informations de l'instruction TI
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


#include "it.h"


#include <assert.h>


#include <common/sort.h>
#include <core/columns.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _a7itcop_extra_data_t
{
    operand_extra_data_t parent;            /* A laisser en premier        */

    ArmCondCode firstcond;                  /* Condition première          */
    uint8_t mask;                           /* Masque de l'interprétation  */

} a7itcop_extra_data_t;


/* Définition d'un opérande organisant l'application d'une instruction IT (instance) */
struct _GArmV7ITCondOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_ARMV7_ITCOND_OP_EXTRA(op) ((a7itcop_extra_data_t *)&((GArchOperand *)op)->extra)

#else

#   define GET_ARMV7_ITCOND_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), a7itcop_extra_data_t)

#endif


/* Définition d'un opérande organisant l'application d'une instruction IT (classe) */
struct _GArmV7ITCondOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/* Initialise la classe des conditions d'application d'IT. */
static void g_armv7_itcond_operand_class_init(GArmV7ITCondOperandClass *);

/* Initialise une instance de conditions d'application d'IT. */
static void g_armv7_itcond_operand_init(GArmV7ITCondOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_itcond_operand_dispose(GArmV7ITCondOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_itcond_operand_finalize(GArmV7ITCondOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_itcond_operand_compare(const GArmV7ITCondOperand *, const GArmV7ITCondOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_itcond_operand_print(const GArmV7ITCondOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_itcond_operand_hash(const GArmV7ITCondOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_itcond_operand_load(GArmV7ITCondOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_itcond_operand_store(GArmV7ITCondOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour l'application d'une instruction IT. */
G_DEFINE_TYPE(GArmV7ITCondOperand, g_armv7_itcond_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des conditions d'application d'IT.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_itcond_operand_class_init(GArmV7ITCondOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_itcond_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_itcond_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_armv7_itcond_operand_compare;

    operand->print = (operand_print_fc)g_armv7_itcond_operand_print;

    operand->hash = (operand_hash_fc)g_armv7_itcond_operand_hash;

    operand->load = (load_operand_fc)g_armv7_itcond_operand_load;
    operand->store = (store_operand_fc)g_armv7_itcond_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de conditions d'application d'IT.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_itcond_operand_init(GArmV7ITCondOperand *operand)
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

static void g_armv7_itcond_operand_dispose(GArmV7ITCondOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_itcond_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_itcond_operand_finalize(GArmV7ITCondOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_itcond_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : firstcond = valeur brute de la condition d'exécution.        *
*                mask      = masque d'interprétation pour l'instruction.      *
*                                                                             *
*  Description : Crée un opérande lié à une instruction IT.                   *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_itcond_operand_new(uint8_t firstcond, uint8_t mask)
{
    GArmV7ITCondOperand *result;            /* Structure à retourner       */
    a7itcop_extra_data_t *extra;            /* Données insérées à modifier */

    if (firstcond > ACC_NV)
        return NULL;

    result = g_object_new(G_TYPE_ARMV7_ITCOND_OPERAND, NULL);

    extra = GET_ARMV7_ITCOND_OP_EXTRA(result);

    extra->firstcond = firstcond;
    extra->mask = mask;

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Fournit la condition associée à l'opérande.                  *
*                                                                             *
*  Retour      : Condition classique pour ARMv7.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ArmCondCode g_armv7_itcond_operand_get_firstcond(const GArmV7ITCondOperand *operand)
{
    ArmCondCode result;                     /* Condition à renvoyer        */
    a7itcop_extra_data_t *extra;            /* Données insérées à modifier */

    extra = GET_ARMV7_ITCOND_OP_EXTRA(operand);

    result = extra->firstcond;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Fournit le masque d'interprétation de la condition.          *
*                                                                             *
*  Retour      : Masque de bits.                                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint8_t g_armv7_itcond_operand_get_mask(const GArmV7ITCondOperand *operand)
{
    uint8_t result;                         /* Valeur à retourner          */
    a7itcop_extra_data_t *extra;            /* Données insérées à modifier */

    extra = GET_ARMV7_ITCOND_OP_EXTRA(operand);

    result = extra->mask;

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

static int g_armv7_itcond_operand_compare(const GArmV7ITCondOperand *a, const GArmV7ITCondOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    a7itcop_extra_data_t *ea;               /* Données insérées à consulter*/
    a7itcop_extra_data_t *eb;               /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_ARMV7_ITCOND_OP_EXTRA(a);
    eb = GET_ARMV7_ITCOND_OP_EXTRA(b);

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = sort_boolean(ea->firstcond, eb->firstcond);

    if (result == 0)
        result = sort_unsigned_long(ea->mask, eb->mask);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_itcond_operand_parent_class);
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

static void g_armv7_itcond_operand_print(const GArmV7ITCondOperand *operand, GBufferLine *line)
{
    a7itcop_extra_data_t *extra;            /* Données insérées à consulter*/
    const char *kw;                         /* Mot clef à imprimer         */

    extra = GET_ARMV7_ITCOND_OP_EXTRA(operand);

    switch (extra->firstcond)
    {
        case ACC_EQ: kw = "EQ"; break;
        case ACC_NE: kw = "NE"; break;
        case ACC_HS: kw = "HS"; break;
        case ACC_LO: kw = "LO"; break;
        case ACC_MI: kw = "MI"; break;
        case ACC_PL: kw = "PL"; break;
        case ACC_VS: kw = "VS"; break;
        case ACC_VC: kw = "VC"; break;
        case ACC_HI: kw = "HI"; break;
        case ACC_LS: kw = "LS"; break;
        case ACC_GE: kw = "GE"; break;
        case ACC_LT: kw = "LT"; break;
        case ACC_GT: kw = "GT"; break;
        case ACC_LE: kw = "LE"; break;
        case ACC_AL: kw = NULL; break;
        case ACC_NV: kw = "NV"; break;

        default:    /* Pour GCC... */
            assert(false);
            kw = NULL;
            break;

    }

    if (kw != NULL)
        g_buffer_line_append_text(line, DLC_ASSEMBLY, kw, 2, RTT_KEY_WORD, NULL);

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

static guint g_armv7_itcond_operand_hash(const GArmV7ITCondOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    a7itcop_extra_data_t *extra;            /* Données internes à manipuler*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_ARMV7_ITCOND_OP_EXTRA(operand);

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_itcond_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= extra->firstcond;

    result ^= extra->mask;

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

static bool g_armv7_itcond_operand_load(GArmV7ITCondOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    a7itcop_extra_data_t *extra;            /* Données insérées à modifier */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_itcond_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        extra = GET_ARMV7_ITCOND_OP_EXTRA(operand);

        result = unpack_uleb128(&value, pbuf);

        if (result)
            extra->firstcond = value;

        if (result)
            result = extract_packed_buffer(pbuf, &extra->mask, sizeof(uint8_t), false);

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

static bool g_armv7_itcond_operand_store(GArmV7ITCondOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7itcop_extra_data_t *extra;            /* Données insérées à modifier */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_itcond_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        extra = GET_ARMV7_ITCOND_OP_EXTRA(operand);

        result = pack_uleb128((uleb128_t []){ extra->firstcond }, pbuf);

        if (result)
            result = extend_packed_buffer(pbuf, &extra->mask, sizeof(uint8_t), false);

    }

    return result;

}
