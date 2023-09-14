
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - gestion des instructions de la ARM
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


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <analysis/db/misc/rlestr.h>
#include <common/extstr.h>
#include <core/logs.h>


#include "instruction-int.h"



/* Initialise la classe des instructions ARM. */
static void g_arm_instruction_class_init(GArmInstructionClass *);

/* Initialise une instance de instruction ARM. */
static void g_arm_instruction_init(GArmInstruction *);

/* Supprime toutes les références externes. */
static void g_arm_instruction_dispose(GArmInstruction *);

/* Procède à la libération totale de la mémoire. */
static void g_arm_instruction_finalize(GArmInstruction *);



/* -------------------- CONSERVATION SUR DISQUE DES INSTRUCTIONS -------------------- */


/* Charge une instruction depuis une mémoire tampon. */
static bool g_arm_instruction_unserialize(GArmInstruction *, GAsmStorage *, GBinFormat *, packed_buffer_t *);

/* Sauvegarde une instruction dans une mémoire tampon. */
static bool g_arm_instruction_serialize(GArmInstruction *, GAsmStorage *, packed_buffer_t *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_arm_instruction_load(GArmInstruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_arm_instruction_store(GArmInstruction *, GObjectStorage *, packed_buffer_t *);



/* Indique le type défini pour une représentation d'une instruction ARM. */
G_DEFINE_TYPE(GArmInstruction, g_arm_instruction, G_TYPE_ARCH_INSTRUCTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions ARM.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_instruction_class_init(GArmInstructionClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object_class = G_OBJECT_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_arm_instruction_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_arm_instruction_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->unserialize = (unserialize_instruction_fc)g_arm_instruction_unserialize;
    instr->serialize = (serialize_instruction_fc)g_arm_instruction_serialize;

    instr->load = (load_instruction_fc)g_arm_instruction_load;
    instr->store = (store_instruction_fc)g_arm_instruction_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction ARM.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_instruction_init(GArmInstruction *instr)
{
    instr->suffix = NULL;
    instr->cached_keyword = NULL;

    instr->cond = ACC_AL;

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

static void g_arm_instruction_dispose(GArmInstruction *instr)
{
    G_OBJECT_CLASS(g_arm_instruction_parent_class)->dispose(G_OBJECT(instr));

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

static void g_arm_instruction_finalize(GArmInstruction *instr)
{
    if (instr->suffix != NULL)
        free(instr->suffix);

    if (instr->cached_keyword != NULL)
        free(instr->cached_keyword);

    G_OBJECT_CLASS(g_arm_instruction_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction quelconque à modifier.                  *
*                suffix = chaîne de caractères fournie en complément.         *
*                                                                             *
*  Description : Etend la désignation d'un nom d'instruction.                 *
*                                                                             *
*  Retour      : true.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arm_instruction_extend_keyword(GArmInstruction *instr, const char *suffix)
{
    instr->suffix = stradd(instr->suffix, suffix);

    if (instr->cached_keyword != NULL)
    {
        free(instr->cached_keyword);
        instr->cached_keyword = NULL;
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction ARM à mettre à jour.                     *
*                cond  = condition d'exécution de l'instruction.              *
*                                                                             *
*  Description : Définit les conditions d'exécution d'une instruction ARM.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arm_instruction_set_cond(GArmInstruction *instr, ArmCondCode cond)
{
    bool result;                            /* Bilan à retourner           */
    const char *suffix;                     /* Eventuelle marque à ajouter */

    instr->cond = cond;

    switch (cond)
    {
        case ACC_EQ: suffix = "eq"; break;
        case ACC_NE: suffix = "ne"; break;
        case ACC_HS: suffix = "hs"; break;
        case ACC_LO: suffix = "lo"; break;
        case ACC_MI: suffix = "mi"; break;
        case ACC_PL: suffix = "pl"; break;
        case ACC_VS: suffix = "vs"; break;
        case ACC_VC: suffix = "vc"; break;
        case ACC_HI: suffix = "hi"; break;
        case ACC_LS: suffix = "ls"; break;
        case ACC_GE: suffix = "ge"; break;
        case ACC_LT: suffix = "lt"; break;
        case ACC_GT: suffix = "gt"; break;
        case ACC_LE: suffix = "le"; break;
        case ACC_AL: suffix = NULL; break;
        case ACC_NV: suffix = "nv"; break;

        default:    /* Pour GCC... */
            assert(false);
            suffix = NULL;
            break;

    }

    if (suffix != NULL)
        result = g_arm_instruction_extend_keyword(instr, suffix);

    else
        result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction ARM à consulter.                         *
*                                                                             *
*  Description : Indique les conditions d'exécution d'une instruction ARM.    *
*                                                                             *
*  Retour      : Condition d'exécution de l'instruction.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ArmCondCode g_arm_instruction_get_cond(const GArmInstruction *instr)
{
    return instr->cond;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION SUR DISQUE DES INSTRUCTIONS                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à consulter.              *
*                storage = mécanisme de sauvegarde à manipuler.               *
*                format  = format binaire chargé associé à l'architecture.    *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Charge une instruction depuis une mémoire tampon.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arm_instruction_unserialize(GArmInstruction *instr, GAsmStorage *storage, GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    unsigned char len;                      /* Taille de textes            */
    char *text;                             /* Texte reconstitué           */

    parent = G_ARCH_INSTRUCTION_CLASS(g_arm_instruction_parent_class);

    result = parent->unserialize(G_ARCH_INSTRUCTION(instr), storage, format, pbuf);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &len, sizeof(unsigned char), false);

        if (result && len > 0)
        {
            text = (char *)malloc(len);

            if (result)
                result = extract_packed_buffer(pbuf, text, len, false);

            if (result)
                result = g_arm_instruction_extend_keyword(instr, text);

            free(text);

        }

    }

    if (result)
        result = extract_packed_buffer(pbuf, &instr->cond, sizeof(ArmCondCode), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à consulter.              *
*                storage = mécanisme de sauvegarde à manipuler.               *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde une instruction dans une mémoire tampon.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arm_instruction_serialize(GArmInstruction *instr, GAsmStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    size_t len;                             /* Taille de textes            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_arm_instruction_parent_class);

    result = parent->serialize(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        if (instr->suffix == NULL)
            result = extend_packed_buffer(pbuf, (unsigned char []) { 0 }, sizeof(unsigned char), false);

        else
        {
            len = strlen(instr->suffix) + 1;
            assert(len > 1);

            if (len > (2 << (sizeof(unsigned char) * 8 - 1)))
            {
                log_variadic_message(LMT_ERROR, "ARM suffix too long: '%s' (%zu bytes)", instr->suffix, len);
                result = false;
            }

            else
                result = extend_packed_buffer(pbuf, (unsigned char []) { len }, sizeof(unsigned char), false);

            if (result)
                result = extend_packed_buffer(pbuf, instr->suffix, len, false);

        }

    }

    if (result)
        result = extend_packed_buffer(pbuf, &instr->cond, sizeof(ArmCondCode), true);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
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

static bool g_arm_instruction_load(GArmInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    rle_string str;                         /* Chaîne à charger            */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    parent = G_ARCH_INSTRUCTION_CLASS(g_arm_instruction_parent_class);

    result = parent->load(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        setup_empty_rle_string(&str);

        result = unpack_rle_string(&str, pbuf);

        if (result)
        {
            result = (get_rle_string(&str) != NULL);

            if (result)
                result = g_arm_instruction_extend_keyword(instr, get_rle_string(&str));

            exit_rle_string(&str);

        }

    }

    if (result)
    {
        result = unpack_uleb128(&value, pbuf);

        if (result)
            instr->cond = value;

    }

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

static bool g_arm_instruction_store(GArmInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    rle_string str;                         /* Chaîne à conserver          */

    parent = G_ARCH_INSTRUCTION_CLASS(g_arm_instruction_parent_class);

    result = parent->store(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        init_static_rle_string(&str, instr->suffix);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    if (result)
        result = pack_uleb128((uleb128_t []){ instr->cond }, pbuf);

    return result;

}
