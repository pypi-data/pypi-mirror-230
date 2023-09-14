
/* Chrysalide - Outil d'analyse de fichiers binaires
 * reglist.c - accès à la mémorie à partir d'un registre et d'un décalage
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


#include "reglist.h"


#include <assert.h>
#include <malloc.h>


#include <arch/register.h>
#include <arch/storage.h>
#include <common/sort.h>
#include <core/columns.h>


#include "../operand-int.h"
#include "../registers/basic.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Définition d'un opérande listant une série de registres ARM (instance) */
struct _GArmV7RegListOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

    GArmV7Register **registers;             /* Liste de registres intégrés */
    size_t count;                           /* Taille de cette liste       */

};


/* Définition d'un opérande listant une série de registres ARM (classe) */
struct _GArmV7RegListOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/* Initialise la classe des listes de registres ARM. */
static void g_armv7_reglist_operand_class_init(GArmV7RegListOperandClass *);

/* Initialise une instance de liste de registres ARM. */
static void g_armv7_reglist_operand_init(GArmV7RegListOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_reglist_operand_dispose(GArmV7RegListOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_reglist_operand_finalize(GArmV7RegListOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_reglist_operand_compare(const GArmV7RegListOperand *, const GArmV7RegListOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_reglist_operand_print(const GArmV7RegListOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_reglist_operand_hash(const GArmV7RegListOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_reglist_operand_load(GArmV7RegListOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_reglist_operand_store(GArmV7RegListOperand *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour une liste de registres ARM. */
G_DEFINE_TYPE(GArmV7RegListOperand, g_armv7_reglist_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des listes de registres ARM.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_reglist_operand_class_init(GArmV7RegListOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_reglist_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_reglist_operand_finalize;

    operand->compare = (operand_compare_fc)g_armv7_reglist_operand_compare;
    operand->print = (operand_print_fc)g_armv7_reglist_operand_print;

    operand->hash = (operand_hash_fc)g_armv7_reglist_operand_hash;

    operand->load = (load_operand_fc)g_armv7_reglist_operand_load;
    operand->store = (store_operand_fc)g_armv7_reglist_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de liste de registres ARM.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_reglist_operand_init(GArmV7RegListOperand *operand)
{
    operand->registers = NULL;
    operand->count = 0;

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

static void g_armv7_reglist_operand_dispose(GArmV7RegListOperand *operand)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < operand->count; i++)
        g_clear_object(&operand->registers[i]);

    G_OBJECT_CLASS(g_armv7_reglist_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_reglist_operand_finalize(GArmV7RegListOperand *operand)
{
    if (operand->registers != NULL)
        free(operand->registers);

    G_OBJECT_CLASS(g_armv7_reglist_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selected = masque de bits pour les registres à intégrer.     *
*                                                                             *
*  Description : Crée une liste vierge de registres ARM.                      *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_reglist_operand_new(uint16_t selected)
{
    GArmV7RegListOperand *result;           /* Structure à retourner       */
    uint8_t i;                              /* Boucle de parcours          */
    GArchRegister *reg;                     /* Nouveau registre à intégrer */

    result = g_object_new(G_TYPE_ARMV7_REGLIST_OPERAND, NULL);

    for (i = 0; i < 16; i++)
    {
        if ((selected & (1 << i)) == 0) continue;

        reg = g_armv7_basic_register_new(i);
        g_armv7_reglist_add_register(result, G_ARMV7_REGISTER(reg));

    }

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = liste de registres à compléter.                    *
*                reg     = nouveau registre à intégrer.                       *
*                                                                             *
*  Description : Ajoute un registre à une liste de registres ARM.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_armv7_reglist_add_register(GArmV7RegListOperand *operand, GArmV7Register *reg)
{
    operand->registers = realloc(operand->registers, ++operand->count * sizeof(GArmV7Register *));

    operand->registers[operand->count - 1] = reg;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Compte le nombre de registres ARM composant la liste.        *
*                                                                             *
*  Retour      : Nombre positif ou nul.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_armv7_reglist_count_registers(const GArmV7RegListOperand *operand)
{
    return operand->count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                index   = indice de l'élément à fournier.                    *
*                                                                             *
*  Description : Founit un élément donné d'une liste de registres ARM.        *
*                                                                             *
*  Retour      : Registre intégré à la liste manipulée.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArmV7Register *g_armv7_reglist_operand_get_register(const GArmV7RegListOperand *operand, size_t index)
{
    GArmV7Register *result;                 /* Instance à retourner        */

    assert(index < operand->count);

    result = operand->registers[index];

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = liste de registres à consulter.                    *
*                reg     = registre à rechercher.                             *
*                                                                             *
*  Description : Indique si un registre est présent dans une liste.           *
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_armv7_reglist_operand_has_register(const GArmV7RegListOperand *operand, const GArmV7Register *reg)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    for (i = 0; i < operand->count && !result; i++)
        result = (g_arch_register_compare(G_ARCH_REGISTER(operand->registers[i]), G_ARCH_REGISTER(reg)) == 0);

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

static int g_armv7_reglist_operand_compare(const GArmV7RegListOperand *a, const GArmV7RegListOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    size_t i;                               /* Boucle de parcours          */
    GArchRegister *ra;                      /* Registre de la liste A      */
    GArchRegister *rb;                      /* Registre de la liste B      */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    /* Création de l'objet... */
    if (b == NULL)
    {
        result = 1;
        goto done;
    }

    result = sort_unsigned_long(a->count, b->count);

    for (i = 0; i < a->count && result == 0; i++)
    {
        ra = G_ARCH_REGISTER(a->registers[i]);
        rb = G_ARCH_REGISTER(b->registers[i]);

        result = g_arch_register_compare(ra, rb);

    }

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_reglist_operand_parent_class);
        result = class->compare(G_ARCH_OPERAND(a), G_ARCH_OPERAND(b), false);
    }

 done:

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

static void g_armv7_reglist_operand_print(const GArmV7RegListOperand *operand, GBufferLine *line)
{
    size_t i;                               /* Boucle de parcours          */

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "{", 1, RTT_HOOK, NULL);

    for (i = 0; i < operand->count; i++)
    {
        if (i > 0)
        {
            g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
            g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);
        }

        g_arch_register_print(G_ARCH_REGISTER(operand->registers[i]), line);

    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "}", 1, RTT_HOOK, NULL);

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

static guint g_armv7_reglist_operand_hash(const GArmV7RegListOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    operand_extra_data_t *extra;            /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */
    size_t i;                               /* Boucle de parcours          */

    extra = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_reglist_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= operand->count;

    for (i = 0; i < operand->count; i++)
        result ^= g_arch_register_hash(G_ARCH_REGISTER(operand->registers[i]));

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

static bool g_armv7_reglist_operand_load(GArmV7RegListOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    size_t count;                           /* Quantité de registres       */
    size_t i;                               /* Boucle de parcours          */
    GSerializableObject *reg;               /* Registre de la liste        */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_reglist_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = extract_packed_buffer(pbuf, &count, sizeof(size_t), true);

    for (i = 0; i < count && result; i++)
    {
        reg = g_object_storage_unpack_object(storage, "registers", pbuf);

        result = (reg != NULL);

        if (result)
            g_armv7_reglist_add_register(operand, G_ARMV7_REGISTER(reg));

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

static bool g_armv7_reglist_operand_store(GArmV7RegListOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    size_t i;                               /* Boucle de parcours          */
    GSerializableObject *reg;               /* Registre de la liste        */

    parent = G_ARCH_OPERAND_CLASS(g_armv7_reglist_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, &operand->count, sizeof(size_t), true);

    for (i = 0; i < operand->count && result; i++)
    {
        reg = G_SERIALIZABLE_OBJECT(operand->registers[i]);
        result = g_object_storage_pack_object(storage, "registers", reg, pbuf);
    }

    return result;

}
