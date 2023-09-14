
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - gestion générique des instructions
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


#include "instruction.h"


#include <assert.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "instruction-int.h"
#include "storage.h"
#include "../analysis/storage/serialize-int.h"
#include "../core/columns.h"
#include "../core/logs.h"
#include "../core/processors.h"
#include "../glibext/gbinarycursor.h"
#include "../glibext/linegen-int.h"



/* Initialise la classe générique des instructions. */
static void g_arch_instruction_class_init(GArchInstructionClass *);

/* Initialise une instance d'opérande d'architecture. */
static void g_arch_instruction_init(GArchInstruction *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_arch_instruction_generator_init(GLineGeneratorInterface *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_arch_instruction_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_arch_instruction_dispose(GArchInstruction *);

/* Procède à la libération totale de la mémoire. */
static void g_arch_instruction_finalize(GArchInstruction *);





/* Charge un contenu depuis une mémoire tampon. */
static bool g_arch_instruction_load_destinations(GArchInstruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde toutes les destinations d'une instruction. */
bool g_arch_instruction_store_destinations(GArchInstruction *, GObjectStorage *, packed_buffer_t *);





/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_arch_instruction_count_lines(const GArchInstruction *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_arch_instruction_compute_cursor(const GArchInstruction *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_arch_instruction_contain_cursor(const GArchInstruction *, size_t, size_t, const GLineCursor *);

#endif

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_arch_instruction_get_flags2(const GArchInstruction *, size_t, size_t);

/* Ajoute à un tampon GLib le contenu de l'instance spécifiée. */
static void _g_arch_instruction_print(GArchInstruction *, GBufferLine *, size_t, size_t, const GBinContent *);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_arch_instruction_print(GArchInstruction *, GBufferLine *, size_t, size_t, const GBinContent *);


/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool _g_arch_instruction_load(GArchInstruction *, GObjectStorage *, packed_buffer_t *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_arch_instruction_load(GArchInstruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool _g_arch_instruction_store(GArchInstruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_arch_instruction_store(GArchInstruction *, GObjectStorage *, packed_buffer_t *);



/* Indique le type défini pour une instruction d'architecture. */
G_DEFINE_TYPE_WITH_CODE(GArchInstruction, g_arch_instruction, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_arch_instruction_generator_init)
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_arch_instruction_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe générique des instructions.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_class_init(GArchInstructionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_arch_instruction_dispose;
    object->finalize = (GObjectFinalizeFunc)g_arch_instruction_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->print = (print_instruction_fc)_g_arch_instruction_print;

    instr->load = (load_instruction_fc)_g_arch_instruction_load;
    instr->store = (store_instruction_fc)_g_arch_instruction_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction d'architecture.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_init(GArchInstruction *instr)
{
    instr_extra_data_t *extra;              /* Données insérées à modifier */

    extra = GET_ARCH_INSTR_EXTRA(instr);

    INIT_GOBJECT_EXTRA_LOCK(extra);

    instr->operands = NULL;

    instr->from = NULL;
    instr->to = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_generator_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_arch_instruction_count_lines;
#ifdef INCLUDE_GTK_SUPPORT
    iface->compute = (linegen_compute_fc)g_arch_instruction_compute_cursor;
    iface->contain = (linegen_contain_fc)g_arch_instruction_contain_cursor;
#endif
    iface->get_flags = (linegen_get_flags_fc)g_arch_instruction_get_flags2;
    iface->print = (linegen_print_fc)g_arch_instruction_print;

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

static void g_arch_instruction_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_arch_instruction_load;
    iface->store = (store_serializable_object_cb)g_arch_instruction_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_dispose(GArchInstruction *instr)
{
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à manipuler        */

    g_arch_instruction_lock_operands(instr);

    count = _g_arch_instruction_count_operands(instr);

    for (i = 0; i < count; i++)
    {
        op = _g_arch_instruction_get_operand(instr, 0);

        rem_item_from_flat_array(&instr->operands, 0, sizeof(GArchOperand *));

        /**
         * Une fois pour l'obtention, une autre pour la libération !
         */
        g_object_unref(G_OBJECT(op));
        g_object_unref(G_OBJECT(op));

    }

    g_arch_instruction_unlock_operands(instr);

#ifndef NDEBUG
    g_arch_instruction_lock_src(instr);
    assert(count_flat_array_items(instr->from) == 0);
    g_arch_instruction_unlock_src(instr);
#endif

#ifndef NDEBUG
    g_arch_instruction_lock_dest(instr);
    assert(count_flat_array_items(instr->to) == 0);
    g_arch_instruction_unlock_dest(instr);
#endif

    G_OBJECT_CLASS(g_arch_instruction_parent_class)->dispose(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_finalize(GArchInstruction *instr)
{
    G_OBJECT_CLASS(g_arch_instruction_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à consulter.                  *
*                                                                             *
*  Description : Indique l'encodage d'une instruction de façon détaillée.     *
*                                                                             *
*  Retour      : Description humaine de l'encodage utilisé.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_arch_instruction_get_encoding(const GArchInstruction *instr)
{
    return G_ARCH_INSTRUCTION_GET_CLASS(instr)->get_encoding(instr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à modifier.                   *
*                flag  = drapeau d'information complémentaire à planter.      *
*                                                                             *
*  Description : Ajoute une information complémentaire à une instruction.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_set_flag(GArchInstruction *instr, ArchInstrFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    instr_extra_data_t *extra;              /* Données insérées à modifier */

    assert(flag <= AIF_HIGH_USER);

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = !(extra->flags & flag);

    extra->flags |= flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à modifier.                   *
*                flag  = drapeau d'information complémentaire à planter.      *
*                                                                             *
*  Description : Retire une information complémentaire à une instruction.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_unset_flag(GArchInstruction *instr, ArchInstrFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    instr_extra_data_t *extra;              /* Données insérées à modifier */

    assert(flag <= AIF_HIGH_USER);

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    extra->flags &= ~flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à consulter.                  *
*                flag  = drapeau d'information à rechercher.                  *
*                                                                             *
*  Description : Détermine si une instruction possède un fanion particulier.  *
*                                                                             *
*  Retour      : Bilan de la détection.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_has_flag(const GArchInstruction *instr, ArchInstrFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    instr_extra_data_t *extra;              /* Données insérées à modifier */

    assert(flag <= AIF_HIGH_USER);

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à modifier.                   *
*                                                                             *
*  Description : Fournit les informations complémentaires d'une instruction.  *
*                                                                             *
*  Retour      : Eventuels drapeaux d'information complémentaire à plantés.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ArchInstrFlag g_arch_instruction_get_flags(const GArchInstruction *instr)
{
    ArchInstrFlag result;                   /* Fanions à retourner         */
    instr_extra_data_t *extra;              /* Données insérées à modifier */

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->flags;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à consulter.                  *
*                uid   = identifiant unique par type d'instruction.           *
*                                                                             *
*  Description : Définit l'identifiant unique pour un ensemble d'instructions.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_set_unique_id(GArchInstruction *instr, itid_t uid)
{
    instr_extra_data_t *extra;              /* Données insérées à modifier */

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    extra->uid = uid;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à consulter.                  *
*                                                                             *
*  Description : Fournit l'identifiant unique pour un ensemble d'instructions.*
*                                                                             *
*  Retour      : Identifiant unique par type d'instruction et architecture.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itid_t g_arch_instruction_get_unique_id(const GArchInstruction *instr)
{
    itid_t result;                          /* Numéro à retourner          */
    instr_extra_data_t *extra;              /* Données insérées à consulter*/

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->uid;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction quelconque à traiter.                  *
*                type    = type de procédure à utiliser.                      *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = accès aux données du binaire d'origine.            *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_call_hook(GArchInstruction *instr, InstrProcessHook type, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchInstructionClass *class;           /* Classe des instructions     */

    class = G_ARCH_INSTRUCTION_GET_CLASS(instr);

    if (class->call_hook != NULL)
        class->call_hook(instr, type, proc, context, format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction quelconque à modifier.                 *
*                address = adresse virtuelle et/ou position physique.         *
*                length  = taille de l'instruction.                           *
*                                                                             *
*  Description : Définit la localisation d'une instruction.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_set_range(GArchInstruction *instr, const mrange_t *range)
{
    copy_mrange(&instr->range, range);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction quelconque à consulter.                *
*                                                                             *
*  Description : Fournit la place mémoire d'une instruction.                  *
*                                                                             *
*  Retour      : Zone mémoire couverte par l'instruction.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const mrange_t *g_arch_instruction_get_range(const GArchInstruction *instr)
{
    return &instr->range;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction quelconque à consulter.                *
*                offset  = position physique dans le code binaire/NULL. [OUT] *
*                length  = taille de l'instruction ou NULL. [OUT]             *
*                address = adresse virtuelle ou position physique/NULL. [OUT] *
*                                                                             *
*  Description : Fournit la localisation d'une instruction.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_get_location(const GArchInstruction *instr, off_t *offset, off_t *length, vmpa_t *address)
{
    //if (offset != NULL) *offset = instr->offset;
    //if (length != NULL) *length = instr->length;

    //if (address != NULL) *address = instr->address;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction à consulter.                            *
*                rregs  = liste des rgistres lus. [OUT]                       *
*                rcount = nombre de registres lus. [OUT]                      *
*                wregs  = liste des rgistres écrits. [OUT]                    *
*                wcount = nombre de registres écrits. [OUT]                   *
*                                                                             *
*  Description : Liste les registres lus et écrits par l'instruction.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Les compteurs de références sont à décrémenter après usage ! *
*                                                                             *
******************************************************************************/

void g_arch_instruction_get_rw_registers(const GArchInstruction *instr, GArchRegister ***rregs, size_t *rcount, GArchRegister ***wregs, size_t *wcount)
{
#if 0

    size_t i;                               /* Boucle de parcours          */

    *rregs = NULL;
    *rcount = 0;
    *wregs = NULL;
    *wcount = 0;

    instr->get_rw_regs(instr, rregs, rcount, wregs, wcount);

    for (i = 0; i < *rcount; i++)
        g_object_ref(G_OBJECT((*rregs)[i]));

    for (i = 0; i < *wcount; i++)
        g_object_ref(G_OBJECT((*wregs)[i]));

#endif

}



/* ---------------------------------------------------------------------------------- */
/*                             MANIPULATION DES OPERANDES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction à mettre à jour.                         *
*                                                                             *
*  Description : Verrouille les accès à la liste des opérandes.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_lock_operands(GArchInstruction *instr)
{
    lock_flat_array(&instr->operands);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction à mettre à jour.                         *
*                                                                             *
*  Description : Déverrouille les accès à la liste des opérandes.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_unlock_operands(GArchInstruction *instr)
{
    unlock_flat_array(&instr->operands);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instance à mettre à jour.                          *
*                operand = instruction à venir associer.                      *
*                                                                             *
*  Description : Attache un opérande supplémentaire à une instruction.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_attach_extra_operand(GArchInstruction *instr, GArchOperand *operand)
{
    GSingletonFactory *factory;             /* Unise à instances uniques   */
    GArchOperand *singleton;                /* Instance retenue            */

    factory = get_operands_factory();

    singleton = G_ARCH_OPERAND(g_singleton_factory_get_instance(factory, G_SINGLETON_CANDIDATE(operand)));

    g_object_unref(G_OBJECT(operand));
    g_object_unref(G_OBJECT(factory));

    g_arch_instruction_lock_operands(instr);

    add_item_to_flat_array(&instr->operands, &singleton, sizeof(GArchOperand *));

    g_arch_instruction_unlock_operands(instr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à consulter.                                *
*                                                                             *
*  Description : Indique la quantité d'opérandes présents dans l'instruction. *
*                                                                             *
*  Retour      : Nombre d'opérandes attachés.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t _g_arch_instruction_count_operands(const GArchInstruction *instr)
{
    size_t result;                          /* Décompte à retourner        */

    result = count_flat_array_items(instr->operands);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à consulter.                                *
*                index = indice de l'opérande concerné.                       *
*                                                                             *
*  Description : Fournit un opérande donné d'une instruction.                 *
*                                                                             *
*  Retour      : Opérande trouvée.                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *_g_arch_instruction_get_operand(const GArchInstruction *instr, size_t index)
{
    GArchOperand *result;                   /* Opérande à retourner        */
    GArchOperand **ptr;                     /* Adresse dans le tableau     */

    ptr = get_flat_array_item(instr->operands, index, sizeof(GArchOperand *));

    result = *ptr;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à mettre à jour.                            *
*                old   = ancienne opérande à détacher.                        *
*                new   = nouvelle opérande à attacher.                        *
*                                                                             *
*  Description : Remplace un opérande d'une instruction par un autre.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_arch_instruction_replace_operand(GArchInstruction *instr, GArchOperand *old, GArchOperand *new)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à manipuler        */

    result = false;

    count = _g_arch_instruction_count_operands(instr);

    for (i = 0; i < count && !result; i++)
    {
        op = _g_arch_instruction_get_operand(instr, i);

        result = (op == old);

        g_object_unref(G_OBJECT(op));

    }

    if (result)
    {
        rpl_item_in_flat_array(instr->operands, i - 1, &new, sizeof(GArchOperand *));

        g_object_unref(G_OBJECT(old));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instance à mettre à jour.                           *
*                target = instruction à venir dissocier.                      *
*                                                                             *
*  Description : Détache un opérande liée d'une instruction.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_arch_instruction_detach_operand(GArchInstruction *instr, GArchOperand *target)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à manipuler        */

    result = false;

    count = _g_arch_instruction_count_operands(instr);

    for (i = 0; i < count && !result; i++)
    {
        op = _g_arch_instruction_get_operand(instr, i);

        result = (op == target);

        g_object_unref(G_OBJECT(op));

    }

    if (result)
    {
        rem_item_from_flat_array(&instr->operands, i - 1, sizeof(GArchOperand *));

        g_object_unref(G_OBJECT(target));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instance à consulter.                               *
*                target = instruction à venir retrouver.                      *
*                                                                             *
*  Description : Détermine le chemin conduisant à un opérande.                *
*                                                                             *
*  Retour      : Chemin d'accès à l'opérande ou NULL en cas d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_arch_instruction_find_operand_path(GArchInstruction *instr, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à manipuler        */
    int ret;                                /* Bilan d'une construction    */
    char *sub_path;                         /* Sous-chemin emprunté        */

    result = NULL;

    g_arch_instruction_lock_operands(instr);

    count = _g_arch_instruction_count_operands(instr);

    /* Première passe : accès direct */

    for (i = 0; i < count && result == NULL; i++)
    {
        op = _g_arch_instruction_get_operand(instr, i);

        if (op == target)
        {
            ret = asprintf(&result, "%zu", i);
            if (ret == -1)
            {
                LOG_ERROR_N("asprintf");
                result = NULL;
            }
        }

        g_object_unref(G_OBJECT(op));

    }

    /* Seconde passe : accès profond */

    for (i = 0; i < count && result == NULL; i++)
    {
        op = _g_arch_instruction_get_operand(instr, i);

        sub_path = g_arch_operand_find_inner_operand_path(op, target);

        if (sub_path != NULL)
        {
            ret = asprintf(&result, "%zu:%s", i, sub_path);
            if (ret == -1)
            {
                LOG_ERROR_N("asprintf");
                result = NULL;
            }

            free(sub_path);

        }

        g_object_unref(G_OBJECT(op));

    }

    g_arch_instruction_unlock_operands(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à consulter.                                *
*                path  = chemin d'accès à un opérande à retrouver.            *
*                                                                             *
*  Description : Obtient l'opérande correspondant à un chemin donné.          *
*                                                                             *
*  Retour      : Opérande trouvé ou NULL en cas d'échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_arch_instruction_get_operand_from_path(GArchInstruction *instr, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */
    size_t index;                           /* Indice de l'opérande visé   */
    char *end;                              /* Poursuite du parcours ?     */
    GArchOperand *found;                    /* Opérande trouvé             */

    result = NULL;

    g_arch_instruction_lock_operands(instr);

    /* Recherche au premier niveau */

    index = strtoul(path, &end, 10);

    if ((index == ULONG_MAX && errno == ERANGE) || (index == 0 && errno == EINVAL))
    {
        LOG_ERROR_N("strtoul");
        goto done;
    }

    found = _g_arch_instruction_get_operand(instr, index);
    if (found == NULL) goto done;

    if (*end == '\0')
    {
        result = found;
        goto done;
    }

    /* Recherche en profondeur */

    assert(*end == ':');

    result = g_arch_operand_get_inner_operand_from_path(found, end + 1);

    g_object_unref(G_OBJECT(found));

 done:

    g_arch_instruction_unlock_operands(instr);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                     DEFINITION DES LIAISONS ENTRE INSTRUCTIONS                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction à mettre à jour.                         *
*                src   = sélection de l'extrémité à traiter.                  *
*                lock  = indique le sens du verrouillage à mener.             *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux liens.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_lock_unlock_links(GArchInstruction *instr, bool src, bool lock)
{
    flat_array_t **array;                   /* Choix du tableau ciblé      */

    array = (src ? &instr->from : &instr->to);

    if (lock)
        lock_flat_array(array);
    else
        unlock_flat_array(array);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                type  = type de lien à détecter.                             *
*                                                                             *
*  Description : Détermine si un type de lien existe dans une instruction.    *
*                                                                             *
*  Retour      : Bilan du statut courant de l'instruction.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_has_link(GArchInstruction *instr, InstructionLinkType type)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Nombre de liens à parcourir */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dlink;              /* Définition de destination   */

    result = false;

    g_arch_instruction_lock_dest(instr);

    count = g_arch_instruction_count_destinations(instr);

    for (i = 0; i < count && !result; i++)
    {
        dlink = g_arch_instruction_get_destination(instr, i);

        result = (dlink->type == type);

        unref_instr_link(dlink);

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                dest  = ligne visée par la liaison (côté destination).       *
*                                                                             *
*  Description : Détermine si un lien est déjà établi entre deux instructions.*
*                                                                             *
*  Retour      : Bilan de l'état actuel des liaisons.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_has_link_to(GArchInstruction *instr, const GArchInstruction *dest)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Nombre de liens à parcourir */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dlink;              /* Définition de destination   */

    result = false;

    g_arch_instruction_lock_dest(instr);

    count = g_arch_instruction_count_destinations(instr);

    for (i = 0; i < count && !result; i++)
    {
        dlink = g_arch_instruction_get_destination(instr, i);

        result = (dlink->linked == dest);

        unref_instr_link(dlink);

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                dest  = ligne visée par la liaison (côté destination).       *
*                type  = type de lien à construire.                           *
*                                                                             *
*  Description : Etablit un lien entre deux instructions.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_link_with(GArchInstruction *instr, GArchInstruction *dest, InstructionLinkType type)
{
    instr_link_t new_src;                   /* Nouveau lien à définir #1   */
    instr_link_t new_dst;                   /* Nouveau lien à définir #2   */

    /* Côté destination */

    new_src.linked = instr;
    new_src.type = type;

    ref_instr_link((&new_src));

    /* Côté point de départ */

    new_dst.linked = dest;
    new_dst.type = type;

    ref_instr_link((&new_dst));

    /* Ajout dans le respect d'une cohérence globale */

    g_arch_instruction_lock_src(dest);
    g_arch_instruction_lock_dest(instr);

    add_item_to_flat_array(&dest->from, &new_src, sizeof(instr_link_t));

    add_item_to_flat_array(&instr->to, &new_dst, sizeof(instr_link_t));

    g_arch_instruction_unlock_dest(instr);
    g_arch_instruction_unlock_src(dest);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                dest  = ligne visée par la liaison (côté destination).       *
*                old   = ancien type de lien construit.                       *
*                new   = nouveau type de lien à construire.                   *
*                                                                             *
*  Description : Change la nature d'un lien entre deux instructions.          *
*                                                                             *
*  Retour      : true pour une mise à jour réussie, false sinon.              *
*                                                                             *
*  Remarques   : Le verrou doit être posé sur les destinations de 'instr'.    *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_change_link(GArchInstruction *instr, GArchInstruction *dest, InstructionLinkType old, InstructionLinkType new)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Raccourci pour la lecture   */
    size_t i;                               /* Boucle de parcours          */
    instr_link_t *slink;                    /* Définition de source        */
    instr_link_t *dlink;                    /* Définition de destination   */

    result = false;

    /**
     * Note : pour la récupération des liens de sources et de destinations,
     * on n'utilise pas les fonctions g_arch_instruction_get_(source|destination)(),
     * qui renvoient un pointeur non modifiable.
     *
     * On a en effet besoin de modifier le type de lien.
     */


    g_arch_instruction_lock_src(dest);

    /* Côté destination */

    count = g_arch_instruction_count_sources(dest);

    for (i = 0; i < count; i++)
    {
        slink = get_flat_array_item(dest->from, i, sizeof(instr_link_t));

        if (slink->linked == instr && slink->type == old)
            break;

    }

    if (i == count)
        goto gaicl_exit;

    /* Côté point de départ */

    count = g_arch_instruction_count_destinations(instr);

    for (i = 0; i < count; i++)
    {
        dlink = get_flat_array_item(instr->to, i, sizeof(instr_link_t));

        if (dlink->linked == dest && dlink->type == old)
            break;

    }

    if (i == count)
        goto gaicl_exit;

    /* Si les deux extrémités sont raccord... */

    slink->type = new;

    dlink->type = new;

    result = true;

 gaicl_exit:

    g_arch_instruction_unlock_src(dest);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à traiter.    *
*                                                                             *
*  Description : Supprime tous les liens établis avec d'autres instructions.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_instruction_delete_all_links(GArchInstruction *instr)
{
    instr_link_t *link_src;                 /* Lien à supprimer #2         */
    GArchInstruction *other;                /* Instruction de l'autre bout */
    size_t count;                           /* Quantié de liens présents   */
    size_t i;                               /* Boucle de parcours          */
    instr_link_t *link_dst;                 /* Lien à supprimer #1         */

    /* Coté sources */

    g_arch_instruction_lock_src(instr);

    while (count_flat_array_items(instr->from) > 0)
    {
        link_src = get_flat_array_item(instr->from, 0, sizeof(instr_link_t));

        other = link_src->linked;

        g_arch_instruction_lock_dest(other);

        count = count_flat_array_items(other->to);

        for (i = 0; i < count; i++)
        {
            link_dst = get_flat_array_item(other->to, i, sizeof(instr_link_t));

            if (link_dst->linked == instr && link_dst->type == link_src->type)
            {
                unref_instr_link(link_dst);

                rem_item_from_flat_array(&other->to, i, sizeof(instr_link_t));

                break;

            }

        }

        assert(i < count);

        g_arch_instruction_unlock_dest(other);

        unref_instr_link(link_src);

        rem_item_from_flat_array(&instr->from, 0, sizeof(instr_link_t));

    }

    g_arch_instruction_unlock_src(instr);

    /* Coté destinations */

    g_arch_instruction_lock_dest(instr);

    while (count_flat_array_items(instr->to) > 0)
    {
        link_dst = get_flat_array_item(instr->to, 0, sizeof(instr_link_t));

        other = link_dst->linked;

        g_arch_instruction_lock_src(other);

        count = count_flat_array_items(other->from);

        for (i = 0; i < count; i++)
        {
            link_src = get_flat_array_item(other->from, i, sizeof(instr_link_t));

            if (link_src->linked == instr && link_src->type == link_dst->type)
            {
                unref_instr_link(link_src);

                rem_item_from_flat_array(&other->from, i, sizeof(instr_link_t));

                break;

            }

        }

        assert(i < count);

        g_arch_instruction_unlock_src(other);

        unref_instr_link(link_dst);

        rem_item_from_flat_array(&instr->to, 0, sizeof(instr_link_t));

    }

    g_arch_instruction_unlock_dest(instr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                                                                             *
*  Description : Fournit la quantité d'instructions pointant vers une autre.  *
*                                                                             *
*  Retour      : Nombre de ces origines.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_arch_instruction_count_sources(const GArchInstruction *instr)
{
    size_t result;                          /* Nombre de liens à renvoyer  */

    result = count_flat_array_items(instr->from);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                index = indice de l'élément à retrouver.                     *
*                                                                             *
*  Description : Fournit les détails d'une origine d'une instruction donnée.  *
*                                                                             *
*  Retour      : Lien déterminé vers une instruction d'origine.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const instr_link_t *g_arch_instruction_get_source(GArchInstruction *instr, size_t index)
{
    instr_link_t *result;                   /* Détails présents à renvoyer */

    result = get_flat_array_item(instr->from, index, sizeof(instr_link_t));

    ref_instr_link(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                count = quantié de liens présents. [OUT]                     *
*                                                                             *
*  Description : Fournit tous les détails d'origine d'une instruction donnée. *
*                                                                             *
*  Retour      : Liens vers des instructions d'origine à libérer.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_link_t *g_arch_instruction_get_sources(GArchInstruction *instr, size_t *count)
{
    instr_link_t *result;                   /* Détails présents à renvoyer */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *link;               /* Lien à fournir              */

    g_arch_instruction_lock_src(instr);

    *count = g_arch_instruction_count_sources(instr);

    if (*count == 0)
        result = NULL;

    else
    {
        result = (instr_link_t *)malloc(*count * sizeof(instr_link_t));

        for (i = 0; i < *count; i++)
        {
            link = g_arch_instruction_get_source(instr, i);
            memcpy(&result[i], link, sizeof(instr_link_t));
        }

    }

    g_arch_instruction_unlock_src(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                                                                             *
*  Description : Donne le nombre d'instructions non naturellement suivantes.  *
*                                                                             *
*  Retour      : Nombre de ces destinations.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_arch_instruction_count_destinations(const GArchInstruction *instr)
{
    size_t result;                          /* Nombre de liens à renvoyer  */

    result = count_flat_array_items(instr->to);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                index = indice de l'élément à retrouver.                     *
*                                                                             *
*  Description : Fournit les détails d'une destination d'une instruction.     *
*                                                                             *
*  Retour      : Lien déterminé vers une instruction de destination.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const instr_link_t *g_arch_instruction_get_destination(GArchInstruction *instr, size_t index)
{
    instr_link_t *result;                   /* Détails présents à renvoyer */

    result = get_flat_array_item(instr->to, index, sizeof(instr_link_t));

    ref_instr_link(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                type  = type de lien recherché.                              *
*                                                                             *
*  Description : Fournit la destination d'une instruction et d'un type donné. *
*                                                                             *
*  Retour      : Instruction de destination trouvée ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_arch_instruction_get_given_destination(GArchInstruction *instr, InstructionLinkType type)
{
    GArchInstruction *result;               /* Résultat à remonter         */
    size_t count;                           /* Nombre de liens à parcourir */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dest;               /* Destination à étudier       */

    result = NULL;

    g_arch_instruction_lock_dest(instr);

    count = g_arch_instruction_count_destinations(instr);

    for (i = 0; i < count && result == NULL; i++)
    {
        dest = g_arch_instruction_get_destination(instr, i);

        if (dest->type == type)
        {
            result = dest->linked;
            g_object_ref(G_OBJECT(result));
        }

        unref_instr_link(dest);

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont les informations sont à consulter.  *
*                count = quantié de liens présents. [OUT]                     *
*                                                                             *
*  Description : Fournit tous les détails de destination d'une instruction.   *
*                                                                             *
*  Retour      : Liens vers des instructions de destination à libérer.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_link_t *g_arch_instruction_get_destinations(GArchInstruction *instr, size_t *count)
{
    instr_link_t *result;                   /* Détails présents à renvoyer */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *link;               /* Lien à fournir              */

    g_arch_instruction_lock_dest(instr);

    *count = g_arch_instruction_count_destinations(instr);

    if (*count == 0)
        result = NULL;

    else
    {
        result = (instr_link_t *)malloc(*count * sizeof(instr_link_t));

        for (i = 0; i < *count; i++)
        {
            link = g_arch_instruction_get_destination(instr, i);
            memcpy(&result[i], link, sizeof(instr_link_t));
        }

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à constuire.                          *
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

static bool g_arch_instruction_load_destinations(GArchInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t count;                        /* Nombre de liens à charger   */
    uleb128_t i;                            /* Boucle de parcours          */
    GArchInstruction *linked;               /* Lien vers une instruction   */
    uleb128_t type;                         /* Valeur ULEB128 à charger    */

    g_arch_instruction_lock_dest(instr);

    result = unpack_uleb128(&count, pbuf);

    for (i = 0; i < count && result; i++)
    {
        linked = G_ARCH_INSTRUCTION(g_object_storage_unpack_object(storage, "instructions", pbuf));
        if (linked == NULL)
        {
            result = false;
            break;
        }

        result = unpack_uleb128(&type, pbuf);
        if (!result)
        {
            g_object_unref(G_OBJECT(linked));
            break;
        }

        g_arch_instruction_link_with(instr, linked, type);
        g_object_unref(G_OBJECT(linked));

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction dont les informations sont à consulter.*
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde toutes les destinations d'une instruction.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_instruction_store_destinations(GArchInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Nombre d'éléments à traiter */
    size_t kept;                            /* Nombre de liens conservés   */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *link;               /* Lien vers une instruction   */

    g_arch_instruction_lock_dest(instr);

    count = g_arch_instruction_count_destinations(instr);

    /**
     * Le type de lien ILT_REF n'est mis en place que lors de la création
     * d'opérandes de type G_TYPE_TARGET_OPERAND, et sera donc remis en place
     * dynamiquement lors de la restauration de ces derniers.
     */

    kept = 0;

    for (i = 0; i < count; i++)
    {
        link = g_arch_instruction_get_destination(instr, i);

        if (link->type != ILT_REF)
            kept++;

        unref_instr_link(link);

    }

    result = pack_uleb128((uleb128_t []){ kept }, pbuf);

    for (i = 0; i < count && result; i++)
    {
        link = g_arch_instruction_get_destination(instr, i);

        if (link->type != ILT_REF)
        {
            result = g_object_storage_pack_object(storage, "instructions",
                                                  G_SERIALIZABLE_OBJECT(link->linked), pbuf);

            if (result)
                result = pack_uleb128((uleb128_t []){ link->type }, pbuf);

        }

        unref_instr_link(link);

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       CONVERSIONS DU FORMAT DES INSTRUCTIONS                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction d'assemblage à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'instruction manipulée.            *
*                                                                             *
*  Retour      : Mot clef de bas niveau.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_arch_instruction_get_keyword(GArchInstruction *instr)
{
    const char *result;                     /* Désignation à retourner     */

    result = G_ARCH_INSTRUCTION_GET_CLASS(instr)->get_keyword(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction d'assemblage à consulter.                *
*                                                                             *
*  Description : Construit un petit résumé concis de l'instruction.           *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_arch_instruction_build_tooltip(const GArchInstruction *instr)
{
    char *result;                           /* Description à retourner     */
    GArchInstructionClass *class;           /* Classe des instructions     */

    class = G_ARCH_INSTRUCTION_GET_CLASS(instr);

    if (class->build_tooltip != NULL)
        result = class->build_tooltip(instr);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction d'assemblage à consulter.                *
*                                                                             *
*  Description : Fournit une description pour l'instruction manipulée.        *
*                                                                             *
*  Retour      : Chaîne de caractères avec balises éventuelles.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_arch_instruction_get_description(const GArchInstruction *instr)
{
    const char *result;                     /* Description à retourner     */

    result = G_ARCH_INSTRUCTION_GET_CLASS(instr)->get_desc(instr);

    return result;
  
}



/* ---------------------------------------------------------------------------------- */
/*                          OFFRE DE CAPACITES DE GENERATION                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = générateur à consulter.                              *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_arch_instruction_count_lines(const GArchInstruction *instr)
{
    return 1;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = générateur à consulter.                             *
*                x      = position géographique sur la ligne concernée.       *
*                index  = indice de cette même ligne dans le tampon global.   *
*                repeat = indice d'utilisations successives du générateur.    *
*                cursor = emplacement à constituer. [OUT]                     *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_compute_cursor(const GArchInstruction *instr, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    *cursor = g_binary_cursor_new();

    g_binary_cursor_update(G_BINARY_CURSOR(*cursor), get_mrange_addr(&instr->range));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = générateur à consulter.                             *
*                index  = indice de cette même ligne dans le tampon global.   *
*                repeat = indice d'utilisations successives du générateur.    *
*                cursor = emplacement à analyser.                             *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_arch_instruction_contain_cursor(const GArchInstruction *instr, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Conclusion à retourner      */
    vmpa2t addr;                            /* Autre emplacement à comparer*/

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    result = cmp_mrange_with_vmpa(&instr->range, &addr);

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = générateur à consulter.                             *
*                index  = indice de cette même ligne dans le tampon global.   *
*                repeat = indice d'utilisations successives du générateur.    *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BufferLineFlags g_arch_instruction_get_flags2(const GArchInstruction *instr, size_t index, size_t repeat)
{
    return BLF_HAS_CODE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à représenter.            *
*                line    = ligne de rendu à compléter.                        *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                content = éventuel contenu binaire brut à imprimer.          *
*                                                                             *
*  Description : Ajoute à un tampon GLib le contenu de l'instance spécifiée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _g_arch_instruction_print(GArchInstruction *instr, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    const char *key;                        /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à manipuler        */

    g_buffer_line_fill_phys(line, DLC_PHYSICAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&instr->range));

    g_buffer_line_fill_virt(line, DLC_VIRTUAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&instr->range));

    g_buffer_line_fill_content(line, DLC_BINARY, content, &instr->range, VMPA_NO_PHYSICAL);

    /* Instruction proprement dite */

    key = g_arch_instruction_get_keyword(instr);
    klen = strlen(key);

    g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, key, klen, RTT_INSTRUCTION, G_OBJECT(instr));

    /* Liste des opérandes */

    g_arch_instruction_lock_operands(instr);

    count = _g_arch_instruction_count_operands(instr);

    if (count > 0)
    {
        op = _g_arch_instruction_get_operand(instr, 0);
        g_arch_operand_print(op, line);
        g_object_unref(G_OBJECT(op));

        for (i = 1; i < count; i++)
        {
            g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
            g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);

            op = _g_arch_instruction_get_operand(instr, i);

            g_arch_operand_print(op, line);

            g_object_unref(G_OBJECT(op));

        }

    }

    g_arch_instruction_unlock_operands(instr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = générateur à utiliser pour l'impression.           *
*                line    = ligne de rendu à compléter.                        *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                content = éventuel contenu binaire brut à imprimer.          *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_instruction_print(GArchInstruction *instr, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    G_ARCH_INSTRUCTION_GET_CLASS(instr)->print(instr, line, index, repeat, content);

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à constuire.                          *
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

static bool _g_arch_instruction_load(GArchInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    instr_extra_data_t *extra;              /* Données insérées à consulter*/
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    uleb128_t count;                        /* Nombre d'éléments à traiter */
    uleb128_t i;                            /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à traiter          */

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = unpack_uleb128(&value, pbuf);

    if (result)
        extra->uid = value;

    if (result)
    {
        result = unpack_uleb128(&value, pbuf);

        if (result)
            extra->flags = value;

    }

    UNLOCK_GOBJECT_EXTRA(extra);

    if (result)
        result = unpack_mrange(&instr->range, pbuf);

    if (result)
    {
        result = unpack_uleb128(&count, pbuf);

        for (i = 0; i < count && result; i++)
        {
            op = G_ARCH_OPERAND(g_object_storage_unpack_object(storage, "operands", pbuf));
            result = (op != NULL);

            if (result)
                g_arch_instruction_attach_extra_operand(instr, op);

        }

    }

    if (result)
        result = g_arch_instruction_load_destinations(instr, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à constuire.                          *
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

static bool g_arch_instruction_load(GArchInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *class;           /* Classe à activer            */

    class = G_ARCH_INSTRUCTION_GET_CLASS(instr);

    result = class->load(instr, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à consulter.                          *
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

static bool _g_arch_instruction_store(GArchInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    instr_extra_data_t *extra;              /* Données insérées à consulter*/
    size_t count;                           /* Nombre d'éléments à traiter */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à traiter          */

    extra = GET_ARCH_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = pack_uleb128((uleb128_t []){ extra->uid }, pbuf);

    if (result)
        result = pack_uleb128((uleb128_t []){ extra->flags }, pbuf);

    UNLOCK_GOBJECT_EXTRA(extra);

    if (result)
        result = pack_mrange(&instr->range, pbuf);

    if (result)
    {
        g_arch_instruction_lock_operands(instr);

        count = _g_arch_instruction_count_operands(instr);

        result = pack_uleb128((uleb128_t []){ count }, pbuf);

        for (i = 0; i < count && result; i++)
        {
            op = _g_arch_instruction_get_operand(instr, i);

            result = g_object_storage_pack_object(storage, "operands", G_SERIALIZABLE_OBJECT(op), pbuf);

            g_object_unref(G_OBJECT(op));

        }

        g_arch_instruction_unlock_operands(instr);

    }

    if (result)
        result = g_arch_instruction_store_destinations(instr, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à consulter.                          *
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

static bool g_arch_instruction_store(GArchInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *class;           /* Classe à activer            */

    class = G_ARCH_INSTRUCTION_GET_CLASS(instr);

    result = class->store(instr, storage, pbuf);

    return result;

}
