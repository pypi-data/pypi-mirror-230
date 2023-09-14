
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - gestion des instructions de la VM Dalvik
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


#include "instruction.h"


#include <string.h>


#include <arch/instruction-int.h>
#include <arch/register-int.h>


#include "instruction-int.h"



/* Initialise la classe des instructions pour Dalvik. */
static void g_dalvik_instruction_class_init(GDalvikInstructionClass *);

/* Initialise une instance d'opérande d'architecture Dalvik. */
static void g_dalvik_instruction_init(GDalvikInstruction *);

/* Supprime toutes les références externes. */
static void g_dalvik_instruction_dispose(GDalvikInstruction *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_instruction_finalize(GDalvikInstruction *);

/* Indique l'encodage d'une instruction de façon détaillée. */
static const char *g_dalvik_instruction_get_encoding(const GDalvikInstruction *);

/* Construit un petit résumé concis de l'instruction. */
static char *g_dalvik_instruction_build_tooltip(const GDalvikInstruction *);



/* Indique le type défini pour une instruction d'architecture Dalvik. */
G_DEFINE_TYPE(GDalvikInstruction, g_dalvik_instruction, G_TYPE_ARCH_INSTRUCTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions pour Dalvik.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_instruction_class_init(GDalvikInstructionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_instruction_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_instruction_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->get_encoding = (get_instruction_encoding_fc)g_dalvik_instruction_get_encoding;
    instr->build_tooltip = (build_instruction_tooltip_fc)g_dalvik_instruction_build_tooltip;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction d'architecture Dalvik. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_instruction_init(GDalvikInstruction *instr)
{

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

static void g_dalvik_instruction_dispose(GDalvikInstruction *instr)
{
    G_OBJECT_CLASS(g_dalvik_instruction_parent_class)->dispose(G_OBJECT(instr));

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

static void g_dalvik_instruction_finalize(GDalvikInstruction *instr)
{
    G_OBJECT_CLASS(g_dalvik_instruction_parent_class)->finalize(G_OBJECT(instr));

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

static const char *g_dalvik_instruction_get_encoding(const GDalvikInstruction *instr)
{
    const char *result;                     /* Description à retourner     */

    /**
     * Solution de repli pour les pseudo-instructions.
     */

    result = "Dalvik";

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction Dalvik à consulter.                      *
*                                                                             *
*  Description : Construit un petit résumé concis de l'instruction.           *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_dalvik_instruction_build_tooltip(const GDalvikInstruction *instr)
{
    char *result;                           /* Description à retourner     */

    result = NULL;

    return result;

}
