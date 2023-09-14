
/* Chrysalide - Outil d'analyse de fichiers binaires
 * limitation.c - décalages de valeurs
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


#include "limitation.h"


#include <arch/operand-int.h>
#include <common/sort.h>
#include <core/columns.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _a7limop_extra_data_t
{
    operand_extra_data_t parent;            /* A laisser en premier        */

    BarrierLimitationType type;             /* Type de limitation          */

} a7limop_extra_data_t;


/* Définition d'un opérande déterminant une limitation de domaine et d'accès (instance) */
struct _GArmV7LimitationOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

};


/* Définition d'un opérande déterminant une limitation de domaine et d'accès (classe) */
struct _GArmV7LimitationOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_ARMV7_LIMITATION_OP_EXTRA(op) ((a7limop_extra_data_t *)&((GArchOperand *)op)->extra)

#else

#   define GET_ARMV7_LIMITATION_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), a7limop_extra_data_t)

#endif


/* Initialise la classe des co-processeurs ARM. */
static void g_armv7_limitation_operand_class_init(GArmV7LimitationOperandClass *);

/* Initialise une instance de co-processeur ARM. */
static void g_armv7_limitation_operand_init(GArmV7LimitationOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_limitation_operand_dispose(GArmV7LimitationOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_limitation_operand_finalize(GArmV7LimitationOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_limitation_operand_compare(const GArmV7LimitationOperand *, const GArmV7LimitationOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_limitation_operand_print(const GArmV7LimitationOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_limitation_operand_hash(const GArmV7LimitationOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_limitation_operand_load(GArmV7LimitationOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_limitation_operand_store(GArmV7LimitationOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour une limitation de domaine et d'accès. */
G_DEFINE_TYPE(GArmV7LimitationOperand, g_armv7_limitation_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des limitations de domaine et d'accès.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_limitation_operand_class_init(GArmV7LimitationOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_limitation_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_limitation_operand_finalize;

    operand->compare = (operand_compare_fc)g_armv7_limitation_operand_compare;

    operand->print = (operand_print_fc)g_armv7_limitation_operand_print;

    operand->hash = (operand_hash_fc)g_armv7_limitation_operand_hash;

    operand->load = (load_operand_fc)g_armv7_limitation_operand_load;
    operand->store = (store_operand_fc)g_armv7_limitation_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de limitation de domaine et d'accès. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_limitation_operand_init(GArmV7LimitationOperand *operand)
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

static void g_armv7_limitation_operand_dispose(GArmV7LimitationOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_limitation_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_limitation_operand_finalize(GArmV7LimitationOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_limitation_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = valeur brute de la limitation à considérer.            *
*                                                                             *
*  Description : Crée une représentation d'une limitation pour barrière.      *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_limitation_operand_new(uint8_t raw)
{
    GArmV7LimitationOperand *result;        /* Structure à retourner       */
    a7limop_extra_data_t *extra;            /* Données insérées à modifier */

    result = g_object_new(G_TYPE_ARMV7_LIMITATION_OPERAND, NULL);

    extra = GET_ARMV7_LIMITATION_OP_EXTRA(result);

    if (raw < 0b0010 || raw > 0b1111)
        extra->type = BLT_RESERVED;

    else
        extra->type = raw;

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Indique le type de limitation représentée.                   *
*                                                                             *
*  Retour      : Type de limitation d'accès et de domaine.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BarrierLimitationType g_armv7_limitation_operand_get_value(const GArmV7LimitationOperand *operand)
{
    BarrierLimitationType result;           /* Type à retourner            */
    a7limop_extra_data_t *extra;            /* Données insérées à consulter*/

    extra = GET_ARMV7_LIMITATION_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->type;

    UNLOCK_GOBJECT_EXTRA(extra);

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

static int g_armv7_limitation_operand_compare(const GArmV7LimitationOperand *a, const GArmV7LimitationOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    a7limop_extra_data_t *ea;               /* Données insérées à consulter*/
    a7limop_extra_data_t *eb;               /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_ARMV7_LIMITATION_OP_EXTRA(a);
    eb = GET_ARMV7_LIMITATION_OP_EXTRA(b);

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = sort_unsigned_long(ea->type, eb->type);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_limitation_operand_parent_class);
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

static void g_armv7_limitation_operand_print(const GArmV7LimitationOperand *operand, GBufferLine *line)
{
    BarrierLimitationType type;             /* Type porté par l'opérande   */

    type = g_armv7_limitation_operand_get_value(operand);

    switch (type)
    {
        case BLT_SY:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "SY", 2, RTT_KEY_WORD, NULL);
            break;

        case BLT_ST:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "ST", 2, RTT_KEY_WORD, NULL);
            break;

        case BLT_ISH:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "ISH", 3, RTT_KEY_WORD, NULL);
            break;

        case BLT_ISHST:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "ISHST", 5, RTT_KEY_WORD, NULL);
            break;

        case BLT_NSH:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "NSH", 3, RTT_KEY_WORD, NULL);
            break;

        case BLT_NSHST:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "NSHST", 5, RTT_KEY_WORD, NULL);
            break;

        case BLT_OSH:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "OSH", 3, RTT_KEY_WORD, NULL);
            break;

        case BLT_OSHST:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "OSHST", 5, RTT_KEY_WORD, NULL);
            break;

        default:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "(reserved)", 10, RTT_KEY_WORD, NULL);
            break;

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

static guint g_armv7_limitation_operand_hash(const GArmV7LimitationOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    a7limop_extra_data_t *extra;            /* Données internes à manipuler*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_ARMV7_LIMITATION_OP_EXTRA(operand);

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_limitation_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= extra->type;

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

static bool g_armv7_limitation_operand_load(GArmV7LimitationOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7limop_extra_data_t *extra;            /* Données insérées à modifier */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_limitation_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        extra = GET_ARMV7_LIMITATION_OP_EXTRA(operand);

        result = unpack_uleb128(&value, pbuf);

        if (result)
            extra->type = value;

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

static bool g_armv7_limitation_operand_store(GArmV7LimitationOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7limop_extra_data_t *extra;            /* Données insérées à modifier */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_limitation_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        extra = GET_ARMV7_LIMITATION_OP_EXTRA(operand);

        result = pack_uleb128((uleb128_t []){ extra->type }, pbuf);

    }

    return result;

}
