
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fill.c - prise en charge de l'instruction spéciale fill-array-data
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#include "fill.h"


#include <assert.h>
#include <string.h> 


#include "identifiers.h"
#include "../instruction-int.h"



/* Définition générique d'une instruction d'architecture Dalvik (instance) */
struct _GDalvikFillInstr
{
    GDalvikInstruction parent;              /* A laisser en premier        */

    uint16_t item_width;                    /* Taille des éléments         */
    uint32_t array_size;                    /* Taille du tableau           */

};

/* Définition générique d'une instruction d'architecture Dalvik (classe) */
struct _GDalvikFillInstrClass
{
    GDalvikInstructionClass parent;         /* A laisser en premier        */

};



/* Initialise la classe générique des instructions. */
static void g_dalvik_fill_instr_class_init(GDalvikFillInstrClass *);

/* Initialise une instance d'opérande d'architecture. */
static void g_dalvik_fill_instr_init(GDalvikFillInstr *);

/* Supprime toutes les références externes. */
static void g_dalvik_fill_instr_dispose(GDalvikFillInstr *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_fill_instr_finalize(GDalvikFillInstr *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *g_dalvik_fill_instruction_get_keyword(const GDalvikFillInstr *);



/* Indique le type défini pour une pseudo-instruction Dalvik de remplissage. */
G_DEFINE_TYPE(GDalvikFillInstr, g_dalvik_fill_instr, G_TYPE_DALVIK_INSTRUCTION);


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

static void g_dalvik_fill_instr_class_init(GDalvikFillInstrClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_fill_instr_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_fill_instr_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->get_keyword = (get_instruction_keyword_fc)g_dalvik_fill_instruction_get_keyword;

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

static void g_dalvik_fill_instr_init(GDalvikFillInstr *instr)
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

static void g_dalvik_fill_instr_dispose(GDalvikFillInstr *instr)
{
    G_OBJECT_CLASS(g_dalvik_fill_instr_parent_class)->dispose(G_OBJECT(instr));

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

static void g_dalvik_fill_instr_finalize(GDalvikFillInstr *instr)
{
    G_OBJECT_CLASS(g_dalvik_fill_instr_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ident   = identifiant de l'instruction déjà lu.              *
*                ctx     = contexte lié à l'exécution du processeur.          *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                                                                             *
*  Description : Crée une pesudo-instruction Dalvik de remplissage.           *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_dalvik_fill_instr_new(uint16_t ident, GDalvikContext *ctx, const GBinContent *content, vmpa2t *pos)
{
    GDalvikFillInstr *result;               /* Structure à retourner       */
    phys_t consumed;                        /* Données consommées          */
    vmpa2t padding;                         /* Emplacement d'un bourrage   */

    assert(ident == DPO_FILL_ARRAY_DATA);

    result = g_object_new(G_TYPE_DALVIK_FILL_INSTR, NULL);

    g_arch_instruction_set_unique_id(G_ARCH_INSTRUCTION(result), DPO_FILL_ARRAY_DATA);

    if (!g_binary_content_read_u16(content, pos, SRE_LITTLE, &result->item_width))
        goto gdfin_bad;

    if (!g_binary_content_read_u32(content, pos, SRE_LITTLE, &result->array_size))
        goto gdfin_bad;

    consumed = result->item_width * result->array_size;

    if (!g_dalvik_context_register_array_data(ctx, pos, result->item_width, consumed))
        goto gdfin_bad;

    if (consumed % sizeof(uint16_t) != 0)
    {
        copy_vmpa(&padding, pos);
        advance_vmpa(&padding, consumed);

        if (!g_dalvik_context_register_array_data_padding(ctx, &padding))
        {
            /**
             * Si on a pu prendre le premier verrou, on devrait avoir l'assurance
             * de prendre le second !
             */
            assert(false);
        }



    }

    return G_ARCH_INSTRUCTION(result);

 gdfin_bad:

    g_object_unref(result);

    return NULL;

}


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

static const char *g_dalvik_fill_instruction_get_keyword(const GDalvikFillInstr *instr)
{
    const char *result;                     /* Désignation à retourner     */

    result = "array-data";

    return result;

}
