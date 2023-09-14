
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - manipulation du processeur ARMv7
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


#include "arm.h"
#include "context.h"
#include "thumb_16.h"
#include "thumb_32.h"
#include "../processor-int.h"



/* Définition du processeur ARMv7 (instance) */
struct _GArmV7Processor
{
    GArmProcessor parent;                   /* Instance parente            */

};


/* Définition du processeur ARMv7 (classe) */
struct _GArmV7ProcessorClass
{
    GArmProcessorClass parent;              /* Classe parente              */

};


/* Initialise la classe des registres ARMv7. */
static void g_armv7_processor_class_init(GArmV7ProcessorClass *);

/* Initialise une instance de registre ARMv7. */
static void g_armv7_processor_init(GArmV7Processor *);

/* Supprime toutes les références externes. */
static void g_armv7_processor_dispose(GArmV7Processor *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_processor_finalize(GArmV7Processor *);

/* Fournit la désignation interne du processeur d'architecture. */
static char *g_armv7_processor_get_key(const GArmV7Processor *);

/* Fournit le nom humain de l'architecture visée. */
static char *g_armv7_processor_get_desc(const GArmV7Processor *);

/* Fournit la taille de l'espace mémoire d'une architecture. */
static MemoryDataSize g_armv7_processor_get_memory_size(const GArmV7Processor *);

/* Fournit la taille min. des instructions d'une architecture. */
static MemoryDataSize g_armv7_processor_get_instruction_min_size(const GArmV7Processor *);

/* Fournit un contexte pour l'exécution du processeur ARM. */
static GArmV7Context *g_armv7_processor_get_context(const GArmV7Processor *);

/* Décode une instruction dans un flux de données. */
static GArchInstruction *g_armv7_processor_disassemble(const GArmV7Processor *, GArmV7Context *, const GBinContent *, vmpa2t *, GExeFormat *);



/* Indique le type défini par la GLib pour le processeur ARMv7. */
G_DEFINE_TYPE(GArmV7Processor, g_armv7_processor, G_TYPE_ARM_PROCESSOR);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des processeurs ARMv7.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_processor_class_init(GArmV7ProcessorClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchProcessorClass *proc;              /* Encore une autre vision...  */

    object_class = G_OBJECT_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_processor_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_armv7_processor_finalize;

    proc = G_ARCH_PROCESSOR_CLASS(klass);

    proc->get_key = (get_processor_key_fc)g_armv7_processor_get_key;
    proc->get_desc = (get_processor_desc_fc)g_armv7_processor_get_desc;
    proc->get_memsize = (get_processor_memsize_fc)g_armv7_processor_get_memory_size;
    proc->get_inssize = (get_processor_inssize_fc)g_armv7_processor_get_instruction_min_size;

    proc->get_ctx = (get_processor_context_fc)g_armv7_processor_get_context;
    proc->disassemble = (disass_instr_fc)g_armv7_processor_disassemble;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de processeur ARMv7.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_processor_init(GArmV7Processor *proc)
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

static void g_armv7_processor_dispose(GArmV7Processor *proc)
{
    G_OBJECT_CLASS(g_armv7_processor_parent_class)->dispose(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_processor_finalize(GArmV7Processor *proc)
{
    G_OBJECT_CLASS(g_armv7_processor_parent_class)->finalize(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée le support de l'architecture ARMv7.                     *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArmV7Processor *g_armv7_processor_new(void)
{
    GArmV7Processor *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_PROCESSOR, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la désignation interne du processeur d'architecture. *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_armv7_processor_get_key(const GArmV7Processor *proc)
{
    char *result;                           /* Désignation à renvoyer      */

    result = strdup("armv7");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'architecture visée.               *
*                                                                             *
*  Retour      : Désignation humaine associée au processeur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_armv7_processor_get_desc(const GArmV7Processor *proc)
{
    char *result;                           /* Désignation à renvoyer      */

    result = strdup("ARM v7");

    return result;

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

static MemoryDataSize g_armv7_processor_get_memory_size(const GArmV7Processor *proc)
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

static MemoryDataSize g_armv7_processor_get_instruction_min_size(const GArmV7Processor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */

    result = MDS_32_BITS;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture, spectatrice ici.                        *
*                                                                             *
*  Description : Fournit un contexte pour l'exécution du processeur Arm.      *
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArmV7Context *g_armv7_processor_get_context(const GArmV7Processor *proc)
{
    return g_armv7_context_new();

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = architecture visée par la procédure.               *
*                ctx     = contexte lié à l'exécution du processeur.          *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                format  = format du fichier contenant le code.               *
*                                                                             *
*  Description : Désassemble une instruction dans un flux de données.         *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *g_armv7_processor_disassemble(const GArmV7Processor *proc, GArmV7Context *ctx, const GBinContent *content, vmpa2t *pos, GExeFormat *format)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    SourceEndian endian;                    /* Boutisme des données lues   */
    uint16_t raw16;                         /* Donnée 16 bits à analyser   */
    uint32_t raw32;                         /* Donnée 32 bits à analyser   */
    ArmV7InstrSet iset;                     /* Type de jeu d'instructions  */

    endian = G_ARCH_PROCESSOR(proc)->endianness;

    iset = g_armv7_context_find_encoding(ctx, get_virt_addr(pos));

    switch (iset)
    {
        case AV7IS_ARM:

            if (!g_binary_content_read_u32(content, pos, endian, &raw32))
                return NULL;

            result = process_armv7_arm_instruction_set_encoding(raw32);

            break;

        case AV7IS_THUMB:

            if (!g_binary_content_read_u16(content, pos, endian, &raw16))
                return NULL;

            switch (raw16 >> 11)
            {
                case 0b11101:
                case 0b11110:
                case 0b11111:

                    raw32 = raw16 << 16;

                    if (!g_binary_content_read_u16(content, pos, endian, &raw16))
                        return NULL;

                    raw32 |= raw16;

                    result = process_armv7_thumb_32_instruction_set_encoding(raw32);
                    break;

                default:
                    result = process_armv7_thumb_16_instruction_set_encoding(raw16);
                    break;

            }

            break;

        default:    /* Pour GCC... */
            assert(false);
            result = NULL;
            break;

    }

    return result;

}
