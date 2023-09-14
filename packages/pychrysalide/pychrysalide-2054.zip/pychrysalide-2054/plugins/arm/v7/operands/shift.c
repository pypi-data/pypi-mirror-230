
/* Chrysalide - Outil d'analyse de fichiers binaires
 * shift.c - décalages de valeurs
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


#include "shift.h"


#include <assert.h>
#include <stdio.h>
#include <string.h>


#include <common/sort.h>
#include <core/columns.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _a7shiftop_extra_data_t
{
    operand_extra_data_t parent;            /* A laisser en premier        */

    SRType shift_type;                      /* Type de décalage            */

} a7shiftop_extra_data_t;


/* Définition d'un opérande visant une opérande de décalage ARMv7 (instance) */
struct _GArmV7ShiftOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

    GArchOperand *shift_value;              /* Valeur du décalage          */

};


/* Définition d'un opérande visant une opérande de décalage ARMv7 (classe) */
struct _GArmV7ShiftOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_ARMV7_SHIFT_OP_EXTRA(op) ((a7shiftop_extra_data_t *)&((GArchOperand *)op)->extra)

#else

#   define GET_ARMV7_SHIFT_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), a7shiftop_extra_data_t)

#endif


/* Initialise la classe des opérandes de décalage ARMv7. */
static void g_armv7_shift_operand_class_init(GArmV7ShiftOperandClass *);

/* Initialise une instance d'opérande de décalage ARMv7. */
static void g_armv7_shift_operand_init(GArmV7ShiftOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_shift_operand_dispose(GArmV7ShiftOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_shift_operand_finalize(GArmV7ShiftOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_shift_operand_compare(const GArmV7ShiftOperand *, const GArmV7ShiftOperand *, bool);

/* Détermine le chemin conduisant à un opérande interne. */
static char *g_armv7_shift_operand_find_inner_operand_path(const GArmV7ShiftOperand *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
static GArchOperand *g_armv7_shift_operand_get_inner_operand_from_path(const GArmV7ShiftOperand *, const char *);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_shift_operand_print(const GArmV7ShiftOperand *, GBufferLine *);

/* Fournit une liste de candidats embarqués par un candidat. */
static GArchOperand **g_armv7_shift_operand_list_inner_instances(const GArmV7ShiftOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
static void g_armv7_shift_operand_update_inner_instances(GArmV7ShiftOperand *, GArchOperand **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_shift_operand_hash(const GArmV7ShiftOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_shift_operand_load(GArmV7ShiftOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_shift_operand_store(GArmV7ShiftOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour une opérande de décalage ARMv7. */
G_DEFINE_TYPE(GArmV7ShiftOperand, g_armv7_shift_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes de décalage ARMv7.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_shift_operand_class_init(GArmV7ShiftOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_shift_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_shift_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_armv7_shift_operand_compare;
    operand->find_inner = (find_inner_operand_fc)g_armv7_shift_operand_find_inner_operand_path;
    operand->get_inner = (get_inner_operand_fc)g_armv7_shift_operand_get_inner_operand_from_path;

    operand->print = (operand_print_fc)g_armv7_shift_operand_print;

    operand->list_inner = (operand_list_inners_fc)g_armv7_shift_operand_list_inner_instances;
    operand->update_inner = (operand_update_inners_fc)g_armv7_shift_operand_update_inner_instances;
    operand->hash = (operand_hash_fc)g_armv7_shift_operand_hash;

    operand->load = (load_operand_fc)g_armv7_shift_operand_load;
    operand->store = (store_operand_fc)g_armv7_shift_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande de décalage ARMv7.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_shift_operand_init(GArmV7ShiftOperand *operand)
{
    operand->shift_value = NULL;

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

static void g_armv7_shift_operand_dispose(GArmV7ShiftOperand *operand)
{
    g_clear_object(&operand->shift_value);

    G_OBJECT_CLASS(g_armv7_shift_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_shift_operand_finalize(GArmV7ShiftOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_shift_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un réceptacle pour opérande de décalage ARMv7.          *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_shift_operand_new(SRType type, GArchOperand *value)
{
    GArmV7ShiftOperand *result;             /* Structure à retourner       */
    a7shiftop_extra_data_t *extra;          /* Données insérées à modifier */

    result = g_object_new(G_TYPE_ARMV7_SHIFT_OPERAND, NULL);

    extra = GET_ARMV7_SHIFT_OP_EXTRA(result);

    extra->shift_type = type;

    result->shift_value = value;

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Indique la forme de décalage représenté.                     *
*                                                                             *
*  Retour      : Type de décalage.                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SRType g_armv7_shift_operand_get_shift_type(const GArmV7ShiftOperand *operand)
{
    SRType result;                          /* Type à retourner            */
    a7shiftop_extra_data_t *extra;          /* Données insérées à consulter*/

    extra = GET_ARMV7_SHIFT_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->shift_type;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Founit la valeur utilisée pour un décalage.                  *
*                                                                             *
*  Retour      : Opérande en place.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_shift_operand_get_shift_value(const GArmV7ShiftOperand *operand)
{
    GArchOperand *result;                   /* Instance à retourner        */

    result = operand->shift_value;

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

static int g_armv7_shift_operand_compare(const GArmV7ShiftOperand *a, const GArmV7ShiftOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    a7shiftop_extra_data_t *ea;             /* Données insérées à consulter*/
    a7shiftop_extra_data_t *eb;             /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_ARMV7_SHIFT_OP_EXTRA(a);
    eb = GET_ARMV7_SHIFT_OP_EXTRA(b);

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = sort_unsigned_long(ea->shift_type, eb->shift_type);

    if (result == 0)
        result = g_arch_operand_compare(a->shift_value, b->shift_value);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_shift_operand_parent_class);
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

static char *g_armv7_shift_operand_find_inner_operand_path(const GArmV7ShiftOperand *operand, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */

    if (target == operand->shift_value)
        result = strdup("0");
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

static GArchOperand *g_armv7_shift_operand_get_inner_operand_from_path(const GArmV7ShiftOperand *operand, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */

    result = NULL;

    if (strncmp(path, "0", 1) == 0)
        switch (path[1])
        {
            case '\0':
                result = operand->shift_value;
                g_object_ref(G_OBJECT(result));
                break;

            case ':':
                result = g_arch_operand_get_inner_operand_from_path(operand->shift_value, path + 1);
                break;

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

static void g_armv7_shift_operand_print(const GArmV7ShiftOperand *operand, GBufferLine *line)
{
    SRType shift_type;                      /* Type porté par l'opérande   */

    shift_type = g_armv7_shift_operand_get_shift_type(operand);

    switch (shift_type)
    {
        case SRType_LSL:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "lsl", 3, RTT_KEY_WORD, NULL);
            break;
        case SRType_LSR:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "lsr", 3, RTT_KEY_WORD, NULL);
            break;
        case SRType_ASR:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "asr", 3, RTT_KEY_WORD, NULL);
            break;
        case SRType_ROR:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "ror", 3, RTT_KEY_WORD, NULL);
            break;
        case SRType_RRX:
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "rrx", 3, RTT_KEY_WORD, NULL);
            break;
    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);

    g_arch_operand_print(operand->shift_value, line);

}


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

static GArchOperand **g_armv7_shift_operand_list_inner_instances(const GArmV7ShiftOperand *operand, size_t *count)
{
    GArchOperand **result;                  /* Instances à retourner       */

    *count = 1;

    result = malloc(*count * sizeof(GArchOperand *));

    result[0] = operand->shift_value;
    g_object_ref(G_OBJECT(result[0]));

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

static void g_armv7_shift_operand_update_inner_instances(GArmV7ShiftOperand *operand, GArchOperand **instances, size_t count)
{
    assert(count == 1);

    g_clear_object(&operand->shift_value);

    operand->shift_value = instances[0];
    g_object_ref(G_OBJECT(instances[0]));

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

static guint g_armv7_shift_operand_hash(const GArmV7ShiftOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    a7shiftop_extra_data_t *extra;          /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */
    a7shiftop_extra_data_t *op_extra;       /* Données internes à manipuler*/

    extra = GET_ARMV7_SHIFT_OP_EXTRA(G_ARMV7_SHIFT_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_shift_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    op_extra = GET_ARMV7_SHIFT_OP_EXTRA(operand);

    result ^= op_extra->shift_type;

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

static bool g_armv7_shift_operand_load(GArmV7ShiftOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7shiftop_extra_data_t *extra;          /* Données insérées à modifier */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_shift_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        extra = GET_ARMV7_SHIFT_OP_EXTRA(operand);

        result = unpack_uleb128(&value, pbuf);

        if (result)
            extra->shift_type = value;

    }

    if (result)
        result = _g_arch_operand_load_inner_instances(G_ARCH_OPERAND(operand), storage, pbuf, 1);

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

static bool g_armv7_shift_operand_store(GArmV7ShiftOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    a7shiftop_extra_data_t *extra;          /* Données insérées à modifier */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_shift_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        extra = GET_ARMV7_SHIFT_OP_EXTRA(operand);

        result = pack_uleb128((uleb128_t []){ extra->shift_type }, pbuf);

    }

    if (result)
        result = _g_arch_operand_store_inner_instances(G_ARCH_OPERAND(operand), storage, pbuf, true);

    return result;

}
