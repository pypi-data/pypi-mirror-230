
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.c - opérandes visant un registre ARMv7
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


#include "register.h"


#include <arch/operands/register-int.h>
#include <common/sort.h>
#include <core/columns.h>



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _a7regop_extra_data_t
{
    operand_extra_data_t parent;            /* A laisser en premier        */

    uint8_t alignment;                      /* Eventuel alignement         */

} a7regop_extra_data_t;


/* Définition d'un opérande visant un registre ARMv7 (instance) */
struct _GArmV7RegisterOperand
{
    GRegisterOperand parent;                /* Instance parente            */

};


/* Définition d'un opérande visant un registre ARMv7 (classe) */
struct _GArmV7RegisterOperandClass
{
    GRegisterOperandClass parent;           /* Classe parente              */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_ARMV7_REGISTER_OP_EXTRA(op) ((a7regop_extra_data_t *)&((GArchOperand *)op)->extra)

#else

#   define GET_ARMV7_REGISTER_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), a7regop_extra_data_t)

#endif


/* Initialise la classe des opérandes de registre ARMv7. */
static void g_armv7_register_operand_class_init(GArmV7RegisterOperandClass *);

/* Initialise une instance d'opérande de registre ARMv7. */
static void g_armv7_register_operand_init(GArmV7RegisterOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_register_operand_dispose(GArmV7RegisterOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_register_operand_finalize(GArmV7RegisterOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_register_operand_compare(const GArmV7RegisterOperand *, const GArmV7RegisterOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_register_operand_print(const GArmV7RegisterOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_register_operand_hash(const GArmV7RegisterOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_register_operand_load(GArmV7RegisterOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_register_operand_store(GArmV7RegisterOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un opérande de registre ARMv7. */
G_DEFINE_TYPE(GArmV7RegisterOperand, g_armv7_register_operand, G_TYPE_REGISTER_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes de registre ARMv7.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_register_operand_class_init(GArmV7RegisterOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_register_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_register_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_armv7_register_operand_compare;

    operand->print = (operand_print_fc)g_armv7_register_operand_print;

    operand->hash = (operand_hash_fc)g_armv7_register_operand_hash;

    operand->load = (load_operand_fc)g_armv7_register_operand_load;
    operand->store = (store_operand_fc)g_armv7_register_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande de registre ARMv7.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_register_operand_init(GArmV7RegisterOperand *operand)
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

static void g_armv7_register_operand_dispose(GArmV7RegisterOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_register_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_register_operand_finalize(GArmV7RegisterOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_register_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre déjà en place.                                *
*                                                                             *
*  Description : Crée un opérande visant un registre ARMv7.                   *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_register_operand_new(GArmV7Register *reg)
{
    GArmV7RegisterOperand *result;         /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_REGISTER_OPERAND, NULL);

    G_REGISTER_OPERAND(result)->reg = G_ARCH_REGISTER(reg);

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande représentant un registre.                 *
*                align   = alignement imposé au registre.                     *
*                                                                             *
*  Description : Définit un alignement à appliquer à l'opérande de registre.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_armv7_register_operand_define_alignement(GArmV7RegisterOperand *operand, unsigned int align)
{
    a7regop_extra_data_t *extra;            /* Données internes à manipuler*/

    extra = GET_ARMV7_REGISTER_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    extra->alignment = align;

    if (align > 0)
        _g_arch_operand_set_flag(G_ARCH_OPERAND(operand), A7ROF_HAS_ALIGNMENT, false);
    else
        _g_arch_operand_unset_flag(G_ARCH_OPERAND(operand), A7ROF_HAS_ALIGNMENT, false);

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande représentant un registre.                 *
*                wback   = indique si le registre est mis à jour après coup.  *
*                                                                             *
*  Description : Détermine si le registre est mis à jour après l'opération.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_armv7_register_operand_write_back(GArmV7RegisterOperand *operand, bool wback)
{
    g_arch_operand_set_flag(G_ARCH_OPERAND(operand), A7ROF_WRITE_BACK);

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

static int g_armv7_register_operand_compare(const GArmV7RegisterOperand *a, const GArmV7RegisterOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    a7regop_extra_data_t *ea;               /* Données insérées à consulter*/
    a7regop_extra_data_t *eb;               /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_ARMV7_REGISTER_OP_EXTRA(a);
    eb = GET_ARMV7_REGISTER_OP_EXTRA(b);

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = sort_unsigned_long(ea->alignment, eb->alignment);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_register_operand_parent_class);
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

static void g_armv7_register_operand_print(const GArmV7RegisterOperand *operand, GBufferLine *line)
{
    GArchOperandClass *parent;              /* Classe parente              */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_register_operand_parent_class);

    parent->print(G_ARCH_OPERAND(operand), line);

    if (g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7ROF_WRITE_BACK))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "!", 1, RTT_PUNCT, NULL);

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

static guint g_armv7_register_operand_hash(const GArmV7RegisterOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    a7regop_extra_data_t *extra;            /* Données internes à manipuler*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_ARMV7_REGISTER_OP_EXTRA(operand);

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_register_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= extra->alignment;

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

static bool g_armv7_register_operand_load(GArmV7RegisterOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7regop_extra_data_t *extra;            /* Données internes à manipuler*/

    parent = G_ARCH_OPERAND_CLASS(g_armv7_register_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result && g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7ROF_HAS_ALIGNMENT))
    {
        extra = GET_ARMV7_REGISTER_OP_EXTRA(operand);

        result = extract_packed_buffer(pbuf, &extra->alignment, sizeof(uint8_t), false);

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

static bool g_armv7_register_operand_store(GArmV7RegisterOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7regop_extra_data_t *extra;            /* Données internes à manipuler*/

    parent = G_ARCH_OPERAND_CLASS(g_armv7_register_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result && g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7ROF_HAS_ALIGNMENT))
    {
        extra = GET_ARMV7_REGISTER_OP_EXTRA(operand);

        result = extend_packed_buffer(pbuf, &extra->alignment, sizeof(uint8_t), false);

    }

    return result;

}
