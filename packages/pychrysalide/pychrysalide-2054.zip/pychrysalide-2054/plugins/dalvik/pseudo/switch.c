
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switch.c - prise en charge des instructions spéciales (packed|sparse)switch
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


#include "switch.h"


#include <assert.h>
#include <malloc.h>


#include "identifiers.h"
#include "../instruction-int.h"



/* Définition générique d'une instruction d'architecture Dalvik (instance) */
struct _GDalvikSwitchInstr
{
    GDalvikInstruction parent;              /* A laisser en premier        */

    uint16_t switch_size;                   /* Taille du switch considéré  */

    int32_t *keys;                          /* Table de clefs              */
    int32_t *targets;                       /* Table des sauts relatifs    */

};

/* Définition générique d'une instruction d'architecture Dalvik (classe) */
struct _GDalvikSwitchInstrClass
{
    GDalvikInstructionClass parent;         /* A laisser en premier        */

};



/* Initialise la classe générique des instructions. */
static void g_dalvik_switch_instr_class_init(GDalvikSwitchInstrClass *);

/* Initialise une instance d'opérande d'architecture. */
static void g_dalvik_switch_instr_init(GDalvikSwitchInstr *);

/* Supprime toutes les références externes. */
static void g_dalvik_switch_instr_dispose(GDalvikSwitchInstr *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_switch_instr_finalize(GDalvikSwitchInstr *);

/* Lit toutes les valeurs associés aux branchements. */
static bool g_dalvik_switch_decode_data(GDalvikSwitchInstr *, const GBinContent *, const vmpa2t *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *g_dalvik_switch_instruction_get_keyword(const GDalvikSwitchInstr *);



/* Indique le type défini pour une pseudo-instruction Dalvik de remplissage. */
G_DEFINE_TYPE(GDalvikSwitchInstr, g_dalvik_switch_instr, G_TYPE_DALVIK_INSTRUCTION);


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

static void g_dalvik_switch_instr_class_init(GDalvikSwitchInstrClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_switch_instr_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_switch_instr_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->get_keyword = (get_instruction_keyword_fc)g_dalvik_switch_instruction_get_keyword;

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

static void g_dalvik_switch_instr_init(GDalvikSwitchInstr *instr)
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

static void g_dalvik_switch_instr_dispose(GDalvikSwitchInstr *instr)
{
    G_OBJECT_CLASS(g_dalvik_switch_instr_parent_class)->dispose(G_OBJECT(instr));

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

static void g_dalvik_switch_instr_finalize(GDalvikSwitchInstr *instr)
{
    if (instr->keys != NULL)
        free(instr->keys);

    if (instr->targets != NULL)
        free(instr->targets);

    G_OBJECT_CLASS(g_dalvik_switch_instr_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ident   = identifiant de l'instruction déjà lu.              *
*                ctx     = contexte lié à l'exécution du processeur.          *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                                                                             *
*  Description : Crée une pesudo-instruction Dalvik de branchement.           *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_dalvik_switch_instr_new(uint16_t ident, GDalvikContext *ctx, const GBinContent *content, vmpa2t *pos)
{
    GDalvikSwitchInstr *result;             /* Structure à retourner       */
    phys_t consumed;                        /* Données consommées          */

    assert(ident == DPO_PACKED_SWITCH || ident == DPO_SPARSE_SWITCH);

    result = g_object_new(G_TYPE_DALVIK_SWITCH_INSTR, NULL);

    g_arch_instruction_set_unique_id(G_ARCH_INSTRUCTION(result), ident);

    if (!g_binary_content_read_u16(content, pos, SRE_LITTLE, &result->switch_size))
        goto gdsin_bad;

    if (!g_dalvik_switch_decode_data(result, content, pos))
        goto gdsin_bad;

    if (ident == DPO_PACKED_SWITCH)
        consumed = (1 + result->switch_size) * sizeof(int32_t);
    else
        consumed = (2 * result->switch_size) * sizeof(int32_t);

    if (!g_dalvik_context_register_switch_data(ctx, pos, consumed))
        goto gdsin_bad;

    return G_ARCH_INSTRUCTION(result);

 gdsin_bad:

    g_object_unref(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à compléter.              *
*                content = flux de données à analyser.                        *
*                pos     = position de lecture courante dans ce flux.         *
*                                                                             *
*  Description : Lit toutes les valeurs associés aux branchements.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_dalvik_switch_decode_data(GDalvikSwitchInstr *instr, const GBinContent *content, const vmpa2t *pos)
{
    vmpa2t iter;                            /* Position modifiable         */
    itid_t uid;                             /* Identifiant unique          */
    int32_t first_key;                      /* Première clef               */
    uint16_t i;                             /* Boucle de parcours          */

    instr->keys = (int32_t *)calloc(instr->switch_size, sizeof(int32_t));
    instr->targets = (int32_t *)calloc(instr->switch_size, sizeof(int32_t));

    copy_vmpa(&iter, pos);

    uid = g_arch_instruction_get_unique_id(G_ARCH_INSTRUCTION(instr));

    if (uid == DPO_PACKED_SWITCH)
    {
        if (!g_binary_content_read_s32(content, &iter, SRE_LITTLE, &first_key))
            goto gdsdd_bad;

        for (i = 0; i < instr->switch_size; i++)
        {
            instr->keys[i] = first_key + i;

            if (!g_binary_content_read_s32(content, &iter, SRE_LITTLE, &instr->targets[i]))
                goto gdsdd_bad;

        }

    }

    else
    {
        for (i = 0; i < instr->switch_size; i++)
            if (!g_binary_content_read_s32(content, &iter, SRE_LITTLE, &instr->keys[i]))
                goto gdsdd_bad;

        for (i = 0; i < instr->switch_size; i++)
            if (!g_binary_content_read_s32(content, &iter, SRE_LITTLE, &instr->targets[i]))
                goto gdsdd_bad;

    }

    return true;

 gdsdd_bad:

    return false;

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

static const char *g_dalvik_switch_instruction_get_keyword(const GDalvikSwitchInstr *instr)
{
    const char *result;                     /* Désignation à retourner     */

    result = "switch-data";

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à compléter.              *
*                keys    = tableau renseignant les conditions de saut. [OUT]  *
*                targets = tableau renseignant les sauts relatifs. [OUT]      *
*                                                                             *
*  Description : Fournit les données associées à un branchement Dalvik.       *
*                                                                             *
*  Retour      : Taille des tableaux renseignés.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint16_t g_dalvik_switch_get_data(GDalvikSwitchInstr *instr, const int32_t **keys, const int32_t **targets)
{
    if (keys != NULL)
        *keys = instr->keys;

    if (targets != NULL)
        *targets = instr->targets;

    return instr->switch_size;

}
