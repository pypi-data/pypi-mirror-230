
/* Chrysalide - Outil d'analyse de fichiers binaires
 * undefined.c - instructions au comportement non défini
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "undefined.h"


#include <assert.h>


#include <i18n.h>


#include "undefined-int.h"
#include "../../core/columns.h"



/* Initialise la classe des instructions non définies. */
static void g_undef_instruction_class_init(GUndefInstructionClass *);

/* Initialise une instance d'instruction non définie. */
static void g_undef_instruction_init(GUndefInstruction *);

/* Supprime toutes les références externes. */
static void g_undef_instruction_dispose(GUndefInstruction *);

/* Procède à la libération totale de la mémoire. */
static void g_undef_instruction_finalize(GUndefInstruction *);

/* Indique l'encodage d'une instruction de façon détaillée. */
static const char *g_undef_instruction_get_encoding(const GUndefInstruction *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *g_undef_instruction_get_keyword(const GUndefInstruction *);



/* -------------------- CONSERVATION SUR DISQUE DES INSTRUCTIONS -------------------- */


/* Charge une instruction depuis une mémoire tampon. */
static bool g_undef_instruction_unserialize(GUndefInstruction *, GAsmStorage *, GBinFormat *, packed_buffer_t *);

/* Sauvegarde une instruction dans une mémoire tampon. */
static bool g_undef_instruction_serialize(GUndefInstruction *, GAsmStorage *, packed_buffer_t *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Ajoute à un tampon GLib le contenu de l'instance spécifiée. */
static void g_undef_instruction_print(GUndefInstruction *, GBufferLine *, size_t, size_t, const GBinContent *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_undef_instruction_load(GUndefInstruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_undef_instruction_store(GUndefInstruction *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                           INSTRUCTION INCONNUE / DONNEES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une instruction au comportement non défini. */
G_DEFINE_TYPE(GUndefInstruction, g_undef_instruction, G_TYPE_ARCH_INSTRUCTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions non définies.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_undef_instruction_class_init(GUndefInstructionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_undef_instruction_dispose;
    object->finalize = (GObjectFinalizeFunc)g_undef_instruction_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->get_encoding = (get_instruction_encoding_fc)g_undef_instruction_get_encoding;
    instr->get_keyword = (get_instruction_keyword_fc)g_undef_instruction_get_keyword;

    instr->unserialize = (unserialize_instruction_fc)g_undef_instruction_unserialize;
    instr->serialize = (serialize_instruction_fc)g_undef_instruction_serialize;

    instr->print = (print_instruction_fc)g_undef_instruction_print;

    instr->load = (load_instruction_fc)g_undef_instruction_load;
    instr->store = (store_instruction_fc)g_undef_instruction_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction non définie.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_undef_instruction_init(GUndefInstruction *instr)
{
    GET_UNDEF_INSTR_EXTRA(instr)->behavior = IEB_UNDEFINED;

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

static void g_undef_instruction_dispose(GUndefInstruction *instr)
{
    G_OBJECT_CLASS(g_undef_instruction_parent_class)->dispose(G_OBJECT(instr));

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

static void g_undef_instruction_finalize(GUndefInstruction *instr)
{
    G_OBJECT_CLASS(g_undef_instruction_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : behavior = état réel du CPU après une passe de l'instruction.*
*                                                                             *
*  Description : Crée une instruction au comportement nominalement indéfini.  *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_undef_instruction_new(InstrExpectedBehavior behavior)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    undef_extra_data_t *extra;              /* Données insérées à modifier */

    result = g_object_new(G_TYPE_UNDEF_INSTRUCTION, NULL);

    extra = GET_UNDEF_INSTR_EXTRA(result);

    extra->behavior = behavior;

    return result;

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

static const char *g_undef_instruction_get_encoding(const GUndefInstruction *instr)
{
    const char *result;                     /* Description à retourner     */

    result = _("Undefined");

    return result;

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

const char *g_undef_instruction_get_keyword(const GUndefInstruction *instr)
{
    const char *result;                     /* Désignation à retourner     */
    undef_extra_data_t *extra;              /* Données insérées à consulter*/

    extra = GET_UNDEF_INSTR_EXTRA(instr);

    switch (extra->behavior)
    {
        case IEB_NOP:
            result = "nop";
            break;

        case IEB_UNDEFINED:
            result = "undefined";
            break;

        case IEB_UNPREDICTABLE:
            result = "unpredictable";
            break;

        case IEB_RESERVED:
            result = "reserved";
            break;

        default:
            assert(false);
            result = NULL;
            break;

    }

    return result;

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

static bool g_undef_instruction_unserialize(GUndefInstruction *instr, GAsmStorage *storage, GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    undef_extra_data_t *extra;              /* Données insérées à consulter*/
    uint8_t val;                            /* Champ de bits manipulé      */

    parent = G_ARCH_INSTRUCTION_CLASS(g_undef_instruction_parent_class);

    result = parent->unserialize(G_ARCH_INSTRUCTION(instr), storage, format, pbuf);

    if (result)
    {
        extra = GET_UNDEF_INSTR_EXTRA(instr);

        LOCK_GOBJECT_EXTRA(extra);

        result = extract_packed_buffer(pbuf, &val, sizeof(uint8_t), false);
        extra->behavior = val;

        UNLOCK_GOBJECT_EXTRA(extra);

    }

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

static bool g_undef_instruction_serialize(GUndefInstruction *instr, GAsmStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    undef_extra_data_t *extra;              /* Données insérées à consulter*/

    parent = G_ARCH_INSTRUCTION_CLASS(g_undef_instruction_parent_class);

    result = parent->serialize(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        extra = GET_UNDEF_INSTR_EXTRA(instr);

        LOCK_GOBJECT_EXTRA(extra);

        result = extend_packed_buffer(pbuf, (uint8_t []){ extra->behavior }, sizeof(uint8_t), false);

        UNLOCK_GOBJECT_EXTRA(extra);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          OFFRE DE CAPACITES DE GENERATION                          */
/* ---------------------------------------------------------------------------------- */


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

static void g_undef_instruction_print(GUndefInstruction *instr, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    GArchInstruction *base;                 /* Version de base             */
    const char *key;                        /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */

    base = G_ARCH_INSTRUCTION(instr);

    g_buffer_line_fill_phys(line, DLC_PHYSICAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&base->range));

    g_buffer_line_fill_virt(line, DLC_VIRTUAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&base->range));

    g_buffer_line_fill_content(line, DLC_BINARY, content, &base->range, VMPA_NO_PHYSICAL);

    /* Instruction proprement dite */

    key = g_arch_instruction_get_keyword(base);
    klen = strlen(key);

    g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, key, klen, RTT_ERROR, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction à consulter.                            *
*                                                                             *
*  Description : Indique le type de conséquences réél de l'instruction.       *
*                                                                             *
*  Retour      : Etat réel du CPU après l'exécution de l'instruction.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

InstrExpectedBehavior g_undef_instruction_get_behavior(const GUndefInstruction *instr)
{
    InstrExpectedBehavior result;           /* Comportement à retourner    */
    undef_extra_data_t *extra;              /* Données insérées à consulter*/

    extra = GET_UNDEF_INSTR_EXTRA(instr);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->behavior;

    UNLOCK_GOBJECT_EXTRA(extra);

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

static bool g_undef_instruction_load(GUndefInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    undef_extra_data_t *extra;              /* Données insérées à consulter*/
    uint8_t val;                            /* Champ de bits manipulé      */

    parent = G_ARCH_INSTRUCTION_CLASS(g_undef_instruction_parent_class);

    result = parent->load(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        extra = GET_UNDEF_INSTR_EXTRA(instr);

        LOCK_GOBJECT_EXTRA(extra);

        result = extract_packed_buffer(pbuf, &val, sizeof(uint8_t), false);
        extra->behavior = val;

        UNLOCK_GOBJECT_EXTRA(extra);

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

static bool g_undef_instruction_store(GUndefInstruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    undef_extra_data_t *extra;              /* Données insérées à consulter*/

    parent = G_ARCH_INSTRUCTION_CLASS(g_undef_instruction_parent_class);

    result = parent->store(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        extra = GET_UNDEF_INSTR_EXTRA(instr);

        LOCK_GOBJECT_EXTRA(extra);

        result = extend_packed_buffer(pbuf, (uint8_t []){ extra->behavior }, sizeof(uint8_t), false);

        UNLOCK_GOBJECT_EXTRA(extra);

    }

    return result;

}
