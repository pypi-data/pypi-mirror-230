
/* Chrysalide - Outil d'analyse de fichiers binaires
 * raw.c - instructions pures vues de l'esprit
 *
 * Copyright (C) 2014-2020 Cyrille Bagard
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


#include "raw.h"


#include <assert.h>
#include <ctype.h>
#include <string.h>


#include <i18n.h>


#include "../instruction-int.h"
#include "../operands/immediate.h"
#include "../operands/target.h"
#include "../../core/columns.h"



/* ------------------------- INSTRUCTION INCONNUE / DONNEES ------------------------- */


/* Définition générique d'une instruction brute d'architecture (instance) */
struct _GRawInstruction
{
    GArchInstruction parent;                /* A laisser en premier        */

};

/* Définition générique d'une instruction brute d'architecture (classe) */
struct _GRawInstructionClass
{
    GArchInstructionClass parent;           /* A laisser en premier        */

};


/* Initialise la classe des instructions brutes d'architecture. */
static void g_raw_instruction_class_init(GRawInstructionClass *);

/* Initialise une instance d'instruction brute d'architecture. */
static void g_raw_instruction_init(GRawInstruction *);

/* Supprime toutes les références externes. */
static void g_raw_instruction_dispose(GRawInstruction *);

/* Procède à la libération totale de la mémoire. */
static void g_raw_instruction_finalize(GRawInstruction *);

/* Indique l'encodage d'une instruction de façon détaillée. */
static const char *g_raw_instruction_get_encoding(const GRawInstruction *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *g_raw_instruction_get_keyword(const GRawInstruction *);



/* -------------------- CONSERVATION SUR DISQUE DES INSTRUCTIONS -------------------- */


/* Charge une instruction depuis une mémoire tampon. */
static bool g_raw_instruction_unserialize(GRawInstruction *, GAsmStorage *, GBinFormat *, packed_buffer_t *);

/* Sauvegarde une instruction dans une mémoire tampon. */
static bool g_raw_instruction_serialize(GRawInstruction *, GAsmStorage *, packed_buffer_t *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Ajoute à un tampon GLib le contenu de l'instance spécifiée. */
static void g_raw_instruction_print(GRawInstruction *, GBufferLine *, size_t, size_t, const GBinContent *);



/* ---------------------------------------------------------------------------------- */
/*                           INSTRUCTION INCONNUE / DONNEES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une instruction inconnue d'architecture. */
G_DEFINE_TYPE(GRawInstruction, g_raw_instruction, G_TYPE_ARCH_INSTRUCTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions brutes d'architecture. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_raw_instruction_class_init(GRawInstructionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_raw_instruction_dispose;
    object->finalize = (GObjectFinalizeFunc)g_raw_instruction_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->get_encoding = (get_instruction_encoding_fc)g_raw_instruction_get_encoding;
    instr->get_keyword = (get_instruction_keyword_fc)g_raw_instruction_get_keyword;

    instr->unserialize = (unserialize_instruction_fc)g_raw_instruction_unserialize;
    instr->serialize = (serialize_instruction_fc)g_raw_instruction_serialize;

    instr->print = (print_instruction_fc)g_raw_instruction_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction brute d'architecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_raw_instruction_init(GRawInstruction *instr)
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

static void g_raw_instruction_dispose(GRawInstruction *instr)
{
    G_OBJECT_CLASS(g_raw_instruction_parent_class)->dispose(G_OBJECT(instr));

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

static void g_raw_instruction_finalize(GRawInstruction *instr)
{
    G_OBJECT_CLASS(g_raw_instruction_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr  = position à associer à l'instruction.                 *
*                size  = taille de l'opérande souhaitée.                      *
*                value = valeur sur x bits à venir récupérer.                 *
*                                                                             *
*  Description : Crée une instruction de type 'db/dw/etc' simple.             *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_raw_instruction_new_from_value(const vmpa2t *addr, MemoryDataSize size, uint64_t value)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    GArchOperand *operand;                  /* Octet non décodé à afficher */
    mrange_t range;                         /* Couverture de l'instruction */

    result = g_object_new(G_TYPE_RAW_INSTRUCTION, NULL);

    operand = g_imm_operand_new_from_value(size, value);
    if (operand == NULL) goto error;

    g_arch_operand_set_flag(operand, IOF_ZERO_PADDING_BY_DEFAULT | IOF_ZERO_PADDING);

    g_arch_instruction_attach_extra_operand(result, operand);

    switch (size)
    {
        case MDS_8_BITS_UNSIGNED:
        case MDS_8_BITS_SIGNED:
            init_mrange(&range, addr, 1);
            break;

        case MDS_16_BITS_UNSIGNED:
        case MDS_16_BITS_SIGNED:
            init_mrange(&range, addr, 2);
            break;

        case MDS_32_BITS_UNSIGNED:
        case MDS_32_BITS_SIGNED:
            init_mrange(&range, addr, 4);
            break;

        case MDS_64_BITS_UNSIGNED:
        case MDS_64_BITS_SIGNED:
            init_mrange(&range, addr, 8);
            break;

        default:
            assert(false);
            goto error;
            break;

    }

    g_arch_instruction_set_range(result, &range);

    return result;

 error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = flux de données à analyser.                        *
*                addr    = position courante dans ce flux. [OUT]              *
*                                                                             *
*  Description : Crée une instruction de type 'db/dw/etc' pour un uleb128.    *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_raw_instruction_new_uleb128(const GBinContent *content, vmpa2t *addr)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    vmpa2t start;                           /* Départ original de lecture  */
    uleb128_t value;                        /* Valeur uleb128 à représenter*/
    phys_t diff;                            /* Couverture de la lecture    */
    MemoryDataSize leb_size;                /* Taille de la valeur         */
    GArchOperand *operand;                  /* Octet non décodé à afficher */
    mrange_t range;                         /* Couverture de l'instruction */

    result = NULL;

    copy_vmpa(&start, addr);

    if (!g_binary_content_read_uleb128(content, addr, &value))
        goto error;

    diff = compute_vmpa_diff(&start, addr);

    leb_size = MDS_FROM_BYTES(diff);
    assert(leb_size != MDS_UNDEFINED);

    result = g_object_new(G_TYPE_RAW_INSTRUCTION, NULL);

    init_mrange(&range, &start, diff);
    g_arch_instruction_set_range(result, &range);

    operand = g_imm_operand_new_from_value(leb_size, (uint64_t)value);
    if (operand == NULL) goto error;

    g_arch_operand_set_flag(operand, IOF_ZERO_PADDING_BY_DEFAULT | IOF_ZERO_PADDING);

    g_arch_instruction_attach_extra_operand(result, operand);

    return result;

 error:

    g_clear_object(&result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = flux de données à analyser.                        *
*                addr    = position courante dans ce flux. [OUT]              *
*                                                                             *
*  Description : Crée une instruction de type 'db/dw/etc' pour un sleb128.    *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_raw_instruction_new_sleb128(const GBinContent *content, vmpa2t *addr)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    vmpa2t start;                           /* Départ original de lecture  */
    uleb128_t value;                        /* Valeur uleb128 à représenter*/
    phys_t diff;                            /* Couverture de la lecture    */
    MemoryDataSize leb_size;                /* Taille de la valeur         */
    GArchOperand *operand;                  /* Octet non décodé à afficher */
    mrange_t range;                         /* Couverture de l'instruction */

    result = NULL;

    copy_vmpa(&start, addr);

    if (!g_binary_content_read_uleb128(content, addr, &value))
        goto error;

    diff = compute_vmpa_diff(&start, addr);

    leb_size = MDS_FROM_BYTES(diff) | MDS_SIGN;
    assert(leb_size != MDS_SIGN);

    result = g_object_new(G_TYPE_RAW_INSTRUCTION, NULL);

    init_mrange(&range, &start, diff);
    g_arch_instruction_set_range(result, &range);

    operand = g_imm_operand_new_from_value(leb_size, (uint64_t)value);
    if (operand == NULL) goto error;

    g_arch_operand_set_flag(operand, IOF_ZERO_PADDING_BY_DEFAULT | IOF_ZERO_PADDING);

    g_arch_instruction_attach_extra_operand(result, operand);

    return result;

 error:

    g_clear_object(&result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = flux de données à analyser.                        *
*                size    = taille de chacun des éléments à représenter.       *
*                count   = nombre de ces éléments.                            *
*                addr    = position courante dans ce flux. [OUT]              *
*                endian  = ordre des bits dans la source.                     *
*                                                                             *
*  Description : Crée une instruction de type 'db/dw/etc' étendue.            *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_raw_instruction_new_array(const GBinContent *content, MemoryDataSize size, size_t count, vmpa2t *addr, SourceEndian endian)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    vmpa2t old;                             /* Sauvegarde de la position   */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *operand;                  /* Octet non décodé à afficher */
    mrange_t range;                         /* Couverture de l'instruction */

    /* Par soucis de cohérence */
    if (count == 0) return NULL;

    result = g_object_new(G_TYPE_RAW_INSTRUCTION, NULL);

    copy_vmpa(&old, addr);

    for (i = 0; i < count; i++)
    {
        operand = g_imm_operand_new_from_data(size, content, addr, endian);
        if (operand == NULL) goto error;

        g_arch_operand_set_flag(operand, IOF_ZERO_PADDING_BY_DEFAULT | IOF_ZERO_PADDING);

        g_arch_instruction_attach_extra_operand(result, operand);

    }

    init_mrange(&range, &old, compute_vmpa_diff(addr, &old));

    g_arch_instruction_set_range(result, &range);

    return result;

 error:

    g_object_unref(G_OBJECT(result));

    return NULL;

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

static const char *g_raw_instruction_get_encoding(const GRawInstruction *instr)
{
    const char *result;                     /* Description à retourner     */

    if (g_raw_instruction_is_string(instr))
        result = _("String");
    else
        result = _("Raw");

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

static const char *g_raw_instruction_get_keyword(const GRawInstruction *instr)
{
    GArchOperand *operand;                  /* Octet décodé à afficher     */
    MemoryDataSize size;                    /* Taille de valeur associée   */

    static char *defines[] = { "dn", "db", "dw", "dd", "dq" };

    operand = g_arch_instruction_get_operand(G_ARCH_INSTRUCTION(instr), 0);

    if (G_IS_TARGET_OPERAND(operand))
        size = g_target_operand_get_size(G_TARGET_OPERAND(operand));
    else
        size = g_imm_operand_get_size(G_IMM_OPERAND(operand));

    g_object_unref(G_OBJECT(operand));

    return defines[MDS_RANGE(size)];

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

static bool g_raw_instruction_unserialize(GRawInstruction *instr, GAsmStorage *storage, GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    uint8_t boolean;                        /* Valeur booléenne            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_raw_instruction_parent_class);

    result = parent->unserialize(G_ARCH_INSTRUCTION(instr), storage, format, pbuf);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);

        if (result)
            g_raw_instruction_mark_as_padding(instr, (boolean == 1));

    }

    if (result)
    {
        result = extract_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);

        if (result)
            g_raw_instruction_mark_as_string(instr, (boolean == 1));

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

static bool g_raw_instruction_serialize(GRawInstruction *instr, GAsmStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    uint8_t boolean;                        /* Valeur booléenne            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_raw_instruction_parent_class);

    result = parent->serialize(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
    {
        boolean = (g_raw_instruction_is_padding(instr) ? 1 : 0);
        result = extend_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);
    }

    if (result)
    {
        boolean = (g_raw_instruction_is_string(instr) ? 1 : 0);
        result = extend_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);
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

static void g_raw_instruction_print(GRawInstruction *instr, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    GArchInstruction *base;                 /* Autre version de l'instance */
    phys_t max_displayed_len;               /* Quantité de code affichée   */
    const char *key;                        /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */
    char *string;                           /* Chaîne reconstituée         */
    size_t iter;                            /* Tête d'écriture             */
    bool first;                             /* Mémorise une énumération    */
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à manipuler        */
    GImmOperand *imm;                       /* Version opérande de valeur  */
    char byte;                              /* Octet à afficher (ou pas)   */
#ifndef NDEBUG
    bool status;                            /* Bilan d'une récupération    */
#endif

    base = G_ARCH_INSTRUCTION(instr);

    /* Localisation */

    g_buffer_line_fill_phys(line, DLC_PHYSICAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&base->range));

    g_buffer_line_fill_virt(line, DLC_VIRTUAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&base->range));

    /* Contenu */

    if (g_raw_instruction_is_padding(instr))
        max_displayed_len = 0;

    else if (g_raw_instruction_is_string(instr))
        max_displayed_len = 1;

    else
    {
        max_displayed_len = get_mrange_length(&base->range);
        max_displayed_len /= g_arch_instruction_count_operands(base);
    }

    g_buffer_line_fill_content(line, DLC_BINARY, content, &base->range, max_displayed_len);

    /* Zone du code d'assemblage */

    key = g_arch_instruction_get_keyword(base);
    klen = strlen(key);

    g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, key, klen, RTT_INSTRUCTION, NULL);

    if (g_raw_instruction_is_padding(instr))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "...", 3, RTT_RAW, NULL);

    else
    {
        string = NULL;
        iter = 0;

        first = true;

        g_arch_instruction_lock_operands(base);

        count = _g_arch_instruction_count_operands(base);

        for (i = 0; i < count; i++)
        {
            op = _g_arch_instruction_get_operand(base, i);

            if (!G_IS_IMM_OPERAND(op))
                goto grip_fallback;

            imm = G_IMM_OPERAND(op);

            if (g_imm_operand_get_size(imm) != MDS_8_BITS)
                goto grip_fallback;

            if (!g_raw_instruction_is_string(instr) && g_imm_operand_get_display(imm) != IOD_CHAR)
                goto grip_fallback;

#ifndef NDEBUG
            status = g_imm_operand_get_value(imm, MDS_8_BITS, &byte);
            assert(status);
#else
            g_imm_operand_get_value(imm, MDS_8_BITS, &byte);
#endif

            /* Si le caractère doit apparaître en hexadécimal... */

            if (!isprint(byte))
                goto grip_fallback;

            /* Impression de l'octet */

            if (string == NULL)
            {
                string = (char *)calloc(count + 3, sizeof(char));

                strcpy(string, "\"");
                iter = 1;

            }

            string[iter++] = byte;

            g_object_unref(G_OBJECT(op));

            continue;

 grip_fallback:

            /* Si une chaîne précède */

            if (string != NULL && iter > 1)
            {
                if (!first)
                {
                    g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
                    g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);
                }
                else
                    first = false;

                string[iter++] = '"';

                g_buffer_line_append_text(line, DLC_ASSEMBLY, string, iter, RTT_STRING, NULL);

                iter = 1;

            }

            /* Intégration en tant qu'opérande classique */

            if (!first)
            {
                g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
                g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);
            }
            else
                first = false;

            g_arch_operand_print(op, line);

            g_object_unref(G_OBJECT(op));

        }

        /* Si au final une chaîne traine encore */

        if (string != NULL && iter > 1)
        {
            if (!first)
            {
                g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
                g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);
            }

            string[iter++] = '"';

            g_buffer_line_append_text(line, DLC_ASSEMBLY, string, iter, RTT_STRING, NULL);

        }

        g_arch_instruction_unlock_operands(base);

        if (string != NULL)
            free(string);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr      = instruction à traiter.                          *
*                is_padding = nouveau statut à associer au contenu.           *
*                                                                             *
*  Description : Marque l'instruction comme ne contenant que du bourrage.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_raw_instruction_mark_as_padding(GRawInstruction *instr, bool is_padding)
{
    if (is_padding)
        g_arch_instruction_set_flag(G_ARCH_INSTRUCTION(instr), RIF_PADDING);
    else
        g_arch_instruction_unset_flag(G_ARCH_INSTRUCTION(instr), RIF_PADDING);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr      = instruction à traiter.                          *
*                is_padding = nouveau statut à associer au contenu.           *
*                                                                             *
*  Description : Indique si le contenu de l'instruction est du bourrage.      *
*                                                                             *
*  Retour      : Statut du contenu de l'instruction.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_raw_instruction_is_padding(const GRawInstruction *instr)
{
    bool result;                            /* Indication à retourner      */

    result = g_arch_instruction_has_flag(G_ARCH_INSTRUCTION(instr), RIF_PADDING);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr     = instruction à traiter.                           *
*                is_string = nouveau statut à associer au contenu.            *
*                                                                             *
*  Description : Marque l'instruction comme contenant une chaîne de texte.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_raw_instruction_mark_as_string(GRawInstruction *instr, bool is_string)
{
    if (is_string)
        g_arch_instruction_set_flag(G_ARCH_INSTRUCTION(instr), RIF_STRING);
    else
        g_arch_instruction_unset_flag(G_ARCH_INSTRUCTION(instr), RIF_STRING);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr     = instruction à traiter.                           *
*                is_string = nouveau statut à associer au contenu.            *
*                                                                             *
*  Description : Indique si le contenu de l'instruction est un texte.         *
*                                                                             *
*  Retour      : Statut du contenu de l'instruction.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_raw_instruction_is_string(const GRawInstruction *instr)
{
    bool result;                            /* Indication à retourner      */

    result = g_arch_instruction_has_flag(G_ARCH_INSTRUCTION(instr), RIF_STRING);

    return result;

}
