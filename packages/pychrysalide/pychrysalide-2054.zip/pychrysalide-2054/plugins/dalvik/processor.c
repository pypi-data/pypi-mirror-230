
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - manipulation du processeur de la VM Dalvik
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "processor.h"


#include <assert.h>


#include <plugins/dex/format.h>


#include "instruction.h"
#include "processor-int.h"
#include "pseudo/fill.h"
#include "pseudo/identifiers.h"
#include "pseudo/switch.h"



/* Initialise la classe des processeurs de VM Dalvik. */
static void g_dalvik_processor_class_init(GDalvikProcessorClass *);

/* Initialise une instance de processeur de VM Dalvik. */
static void g_dalvik_processor_init(GDalvikProcessor *);

/* Supprime toutes les références externes. */
static void g_dalvik_processor_dispose(GDalvikProcessor *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_processor_finalize(GDalvikProcessor *);

/* Fournit la taille de l'espace mémoire d'une architecture. */
static MemoryDataSize g_dalvik_processor_get_memory_size(const GDalvikProcessor *);

/* Fournit la taille min. des instructions d'une architecture. */
static MemoryDataSize g_dalvik_processor_get_instruction_min_size(const GDalvikProcessor *);

/* Indique si l'architecture possède un espace virtuel ou non. */
static bool g_dalvik_processor_has_virtual_space(const GDalvikProcessor *);

/* Fournit un contexte pour l'exécution du processeur Dalvik. */
static GDalvikContext *g_dalvik_processor_get_context(const GDalvikProcessor *);



/* Indique le type défini par la GLib pour le processeur DALVIK. */
G_DEFINE_TYPE(GDalvikProcessor, g_dalvik_processor, G_TYPE_ARCH_PROCESSOR);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des processeurs de VM Dalvik.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_processor_class_init(GDalvikProcessorClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchProcessorClass *proc;              /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_processor_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_processor_finalize;

    proc = G_ARCH_PROCESSOR_CLASS(klass);

    proc->get_memsize = (get_processor_memsize_fc)g_dalvik_processor_get_memory_size;
    proc->get_inssize = (get_processor_inssize_fc)g_dalvik_processor_get_instruction_min_size;
    proc->has_vspace = (has_processor_vspace_fc)g_dalvik_processor_has_virtual_space;

    proc->get_ctx = (get_processor_context_fc)g_dalvik_processor_get_context;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de processeur de VM Dalvik.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_processor_init(GDalvikProcessor *proc)
{
    G_ARCH_PROCESSOR(proc)->endianness = SRE_LITTLE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_processor_dispose(GDalvikProcessor *proc)
{
    G_OBJECT_CLASS(g_dalvik_processor_parent_class)->dispose(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_processor_finalize(GDalvikProcessor *proc)
{
    G_OBJECT_CLASS(g_dalvik_processor_parent_class)->finalize(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la taille de l'espace mémoire d'une architecture.    *
*                                                                             *
*  Retour      : Taille de l'espace mémoire.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static MemoryDataSize g_dalvik_processor_get_memory_size(const GDalvikProcessor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */

    result = MDS_32_BITS;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la taille min. des instructions d'une architecture.  *
*                                                                             *
*  Retour      : Taille d'encodage des instructions.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static MemoryDataSize g_dalvik_processor_get_instruction_min_size(const GDalvikProcessor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */

    result = MDS_16_BITS;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Indique si l'architecture possède un espace virtuel ou non.  *
*                                                                             *
*  Retour      : true si un espace virtuel existe, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_dalvik_processor_has_virtual_space(const GDalvikProcessor *proc)
{
    bool result;                            /* Indication à retourner      */

    result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture, spectatrice ici.                        *
*                                                                             *
*  Description : Fournit un contexte pour l'exécution du processeur Dalvik.   *
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDalvikContext *g_dalvik_processor_get_context(const GDalvikProcessor *proc)
{
    return g_dalvik_context_new();

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = architecture visée par la procédure.               *
*                data    = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                end     = limite des données à analyser.                     *
*                addr    = adresse virtuelle de l'instruction.                *
*                low8    = 8 bits de poids faible déjà lus.                   *
*                handled = dit si une pseudo-instruction était bien là. [OUT] *
*                                                                             *
*  Description : Décode une pseudo-instruction dans un flux de données.       *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL si aucune trouvée.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_dalvik_processor_disassemble_pseudo(const GArchProcessor *proc, GDalvikContext *ctx, const GBinContent *content, vmpa2t *pos, uint8_t low8, bool *handled)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    vmpa2t tmp;                             /* Position modifiable         */
    uint8_t high8;                          /* Nouvelle octet à venir lire */
    uint16_t ident;                         /* Valeur lue dans le code     */

    /* Définition facultative, mais bon... */
    *handled = false;

    result = NULL;

    /* Vérification astucieuse et rapide...*/
    if (low8 != 0x00 /* DOP_NOP */)
        goto gdpdp_exit;

    copy_vmpa(&tmp, pos);

    if (!g_binary_content_read_u8(content, &tmp, &high8))
        goto gdpdp_exit;

    ident = high8 << 8 | low8;

    switch (ident)
    {
        case DPO_PACKED_SWITCH:
        case DPO_SPARSE_SWITCH:
            result = g_dalvik_switch_instr_new(ident, ctx, content, &tmp);
            *handled = true;
            break;

        case DPO_FILL_ARRAY_DATA:
            result = g_dalvik_fill_instr_new(ident, ctx, content, &tmp);
            *handled = true;
            break;

        default:
            result = NULL;
            break;

    }

    if (result != NULL)
        copy_vmpa(pos, &tmp);

 gdpdp_exit:

    return result;

}
