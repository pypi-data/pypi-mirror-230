
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.c - aide à la création d'opérandes Dalvik
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


#include "operand.h"


#include <assert.h>
#include <malloc.h>
#include <stdarg.h>


#include <arch/operands/immediate.h>
#include <arch/operands/register.h>



/* Liste de tous les types d'opérandes */
typedef enum _DalvikOperandID
{
    DOI_INVALID,

    DOI_REGISTER_4,
    DOI_REGISTER_8,
    DOI_REGISTER_16,

    DOI_IMMEDIATE_4,
    DOI_IMMEDIATE_8,
    DOI_IMMEDIATE_16,
    DOI_IMMEDIATE_32,
    DOI_IMMEDIATE_64,
    DOI_IMMEDIATE_H16,

    DOI_POOL_CONST,
    DOI_POOL_CONST_WIDE,

    DOI_TARGET_8,
    DOI_TARGET_16,
    DOI_TARGET_32

} DalvikOperandID;


/* Crée un opérande visant une instruction Dalvik. */
static GArchOperand *dalvik_build_target_operand(const GBinContent *, vmpa2t *, MemoryDataSize , SourceEndian, const vmpa2t *);

/* Procède à la lecture d'opérandes pour une instruction. */
static bool dalvik_read_basic_operands(GArchInstruction *, GDexFormat *, const GBinContent *, vmpa2t *, bool *, SourceEndian, DalvikOperandType, ...);

/* Procède à la lecture d'opérandes pour une instruction. */
static bool dalvik_read_fixed_operands(GArchInstruction *, GDexFormat *, const GBinContent *, vmpa2t *, bool *, SourceEndian, DalvikOperandType);

/* Procède à la lecture d'opérandes pour une instruction. */
static bool dalvik_read_variatic_operands(GArchInstruction *, GDexFormat *, const GBinContent *, vmpa2t *, bool *, SourceEndian, DalvikOperandType);



/******************************************************************************
*                                                                             *
*  Paramètres  : content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                size    = taille de l'opérande.                              *
*                endian  = ordre des bits dans la source.                     *
*                base    = adresse de référence pour le calcul.               *
*                                                                             *
*  Description : Crée un opérande visant une instruction Dalvik.              *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchOperand *dalvik_build_target_operand(const GBinContent *content, vmpa2t *pos, MemoryDataSize size, SourceEndian endian, const vmpa2t *base)
{
    GArchOperand *result;                   /* Structure à retourner       */
    phys_t offset;                          /* Emplacement de base         */
    int8_t val8;                            /* Valeur sur 8 bits           */
    int16_t val16;                          /* Valeur sur 16 bits          */
    int32_t val32;                          /* Valeur sur 32 bits          */
    bool test;                              /* Bilan de lecture            */
    phys_t address;                         /* Adresse finale visée        */

    offset = get_phy_addr(base);

    switch (size)
    {
        case MDS_8_BITS_SIGNED:
            test = g_binary_content_read_s8(content, pos, &val8);
            address = offset + val8 * sizeof(uint16_t);
            break;
        case MDS_16_BITS_SIGNED:
            test = g_binary_content_read_s16(content, pos, endian, &val16);
            address = offset + val16 * sizeof(uint16_t);
            break;
        case MDS_32_BITS_SIGNED:
            test = g_binary_content_read_s32(content, pos, endian, &val32);
            address = offset + val32 * sizeof(uint16_t);
            break;
        default:
            test = false;
            break;
    }

    if (!test)
        return NULL;

    result = g_imm_operand_new_from_value(MDS_32_BITS, address);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction dont la définition est incomplète.[OUT]*
*                format  = format du fichier contenant le code.               *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                low     = position éventuelle des 4 bits visés. [OUT]        *
*                endian  = boutisme lié au binaire accompagnant.              *
*                model   = type d'opérandes attendues.                        *
*                ...     = éventuels arguments complémentaires.               *
*                                                                             *
*  Description : Procède à la lecture d'opérandes pour une instruction.       *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool dalvik_read_basic_operands(GArchInstruction *instr, GDexFormat *format, const GBinContent *content, vmpa2t *pos, bool *low, SourceEndian endian, DalvikOperandType model, ...)
{
    bool result;                            /* Bilan à retourner           */
    DalvikOperandID *types;                 /* Liste des chargements       */
    DalvikOperandID *iter;                  /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande unique décodé      */
    uint16_t value16;                       /* Valeur sur 16 bits          */
    DalvikPoolType pool_type;               /* Type de table à manipuler   */
    va_list ap;                             /* Arguments complémentaires   */
    const vmpa2t *base;                     /* Base pour les sauts de code */

    result = true;

    /* Choix des opérandes à charger */

    switch (DALVIK_OP_BASE_MASK(model))
    {
        case DALVIK_OPT_10T:
            types = (DalvikOperandID []) {
                DOI_TARGET_8,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_11N:
            types = (DalvikOperandID []) {
                DOI_REGISTER_4,
                DOI_IMMEDIATE_4,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_11X:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_12X:
            types = (DalvikOperandID []) {
                DOI_REGISTER_4,
                DOI_REGISTER_4,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_20T:
            types = (DalvikOperandID []) {
                DOI_TARGET_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_21C:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_POOL_CONST,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_21H:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_IMMEDIATE_H16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_21S:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_IMMEDIATE_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_21T:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_TARGET_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_22B:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_REGISTER_8,
                DOI_IMMEDIATE_8,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_22C:
            types = (DalvikOperandID []) {
                DOI_REGISTER_4,
                DOI_REGISTER_4,
                DOI_POOL_CONST,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_22S:
            types = (DalvikOperandID []) {
                DOI_REGISTER_4,
                DOI_REGISTER_4,
                DOI_IMMEDIATE_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_22T:
            types = (DalvikOperandID []) {
                DOI_REGISTER_4,
                DOI_REGISTER_4,
                DOI_TARGET_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_22X:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_REGISTER_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_23X:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_REGISTER_8,
                DOI_REGISTER_8,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_30T:
            types = (DalvikOperandID []) {
                DOI_TARGET_32,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_31C:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_POOL_CONST_WIDE,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_31I:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_IMMEDIATE_32,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_31T:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_TARGET_32,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_32X:
            types = (DalvikOperandID []) {
                DOI_REGISTER_16,
                DOI_REGISTER_16,
                DOI_INVALID
            };
            break;

        case DALVIK_OPT_51L:
            types = (DalvikOperandID []) {
                DOI_REGISTER_8,
                DOI_IMMEDIATE_64,
                DOI_INVALID
            };
            break;

        default:
            types = (DalvikOperandID []) {
                DOI_INVALID
            };
            break;

    }

    /* Chargement des opérandes */

    for (iter = types; *iter != G_TYPE_INVALID && result; iter++)
    {
        op = NULL;  /* Nul de GCC */

        switch (*iter)
        {
            case DOI_REGISTER_4:
                op = g_dalvik_register_operand_new(content, pos, low, MDS_4_BITS, endian);
                break;

            case DOI_REGISTER_8:
                op = g_dalvik_register_operand_new(content, pos, NULL, MDS_8_BITS, endian);
                break;

            case DOI_REGISTER_16:
                op = g_dalvik_register_operand_new(content, pos, NULL, MDS_16_BITS, endian);
                break;

            case DOI_IMMEDIATE_4:
                op = _g_imm_operand_new_from_data(MDS_4_BITS, content, pos, low, endian);
                break;

            case DOI_IMMEDIATE_8:
                op = g_imm_operand_new_from_data(MDS_8_BITS, content, pos, endian);
                break;

            case DOI_IMMEDIATE_16:
                op = g_imm_operand_new_from_data(MDS_16_BITS, content, pos, endian);
                break;

            case DOI_IMMEDIATE_32:
                op = g_imm_operand_new_from_data(MDS_32_BITS, content, pos, endian);
                break;

            case DOI_IMMEDIATE_64:
                op = g_imm_operand_new_from_data(MDS_64_BITS, content, pos, endian);
                break;

            case DOI_IMMEDIATE_H16:
                result = g_binary_content_read_u16(content, pos, endian, &value16);
                if (result)
                    op = g_imm_operand_new_from_value(MDS_32_BITS_SIGNED, ((uint32_t)value16) << 16);
                break;

            case DOI_POOL_CONST:
                pool_type = DALVIK_OP_GET_POOL(model);
                op = g_dalvik_pool_operand_new(format, pool_type, content, pos, MDS_16_BITS, endian);
                break;

            case DOI_POOL_CONST_WIDE:
                pool_type = DALVIK_OP_GET_POOL(model);
                op = g_dalvik_pool_operand_new(format, pool_type, content, pos, MDS_32_BITS, endian);
                break;

            case DOI_TARGET_8:
                va_start(ap, model);
                base = va_arg(ap, const vmpa2t *);
                op = dalvik_build_target_operand(content, pos, MDS_8_BITS_SIGNED, endian, base);
                va_end(ap);
                break;

            case DOI_TARGET_16:
                va_start(ap, model);
                base = va_arg(ap, const vmpa2t *);
                op = dalvik_build_target_operand(content, pos, MDS_16_BITS_SIGNED, endian, base);
                va_end(ap);
                break;

            case DOI_TARGET_32:
                va_start(ap, model);
                base = va_arg(ap, const vmpa2t *);
                op = dalvik_build_target_operand(content, pos, MDS_32_BITS_SIGNED, endian, base);
                va_end(ap);
                break;

            default:
                op = NULL;
                break;

        }

        if (op == NULL) result = false;
        else g_arch_instruction_attach_extra_operand(instr, op);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction dont la définition est incomplète.[OUT]*
*                format  = format du fichier contenant le code.               *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                low     = position éventuelle des 4 bits visés. [OUT]        *
*                endian  = boutisme lié au binaire accompagnant.              *
*                model   = type d'opérandes attendues.                        *
*                                                                             *
*  Description : Procède à la lecture d'opérandes pour une instruction.       *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool dalvik_read_fixed_operands(GArchInstruction *instr, GDexFormat *format, const GBinContent *content, vmpa2t *pos, bool *low, SourceEndian endian, DalvikOperandType model)
{
    GArchOperand *opg;                      /* Opérande G décodé           */
    uint8_t a;                              /* Nbre. de registres utilisés */
    GArchOperand *target;                  /* Opérande visant la table #1 */
    GArchOperand *args;                     /* Liste des opérandes         */
    uint8_t i;                              /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande unique décodé      */

    opg = g_dalvik_register_operand_new(content, pos, low, MDS_4_BITS, endian);

    if (!g_binary_content_read_u4(content, pos, low, &a))
        goto err_va;

    if (a == 5 && opg == NULL)
        goto err_no_opg;

    target = g_dalvik_pool_operand_new(format, DALVIK_OP_GET_POOL(model), content, pos, MDS_16_BITS, endian);
    if (target == NULL) goto err_target;

    /* Mise en place des arguments */

    args = g_dalvik_args_operand_new();

    for (i = 0; i < MIN(a, 4); i++)
    {
        op = g_dalvik_register_operand_new(content, pos, low, MDS_4_BITS, endian);
        if (op == NULL) goto err_registers;

        g_dalvik_args_operand_add(G_DALVIK_ARGS_OPERAND(args), op);

    }

    /* Consommation pleine et entière */

    for (; i < 4; i++)
        if (!g_binary_content_read_u4(content, pos, low, (uint8_t []) { 0 }))
            goto err_padding;

    /* Rajout des éléments finaux déjà chargés */

    if (a == 5)
        g_dalvik_args_operand_add(G_DALVIK_ARGS_OPERAND(args), opg);

    else
    {
        if (opg != NULL)
            g_object_unref(G_OBJECT(opg));
    }

    g_arch_instruction_attach_extra_operand(instr, args);

    /* Rajout de la cible */

    g_arch_instruction_attach_extra_operand(instr, target);

    return true;

 err_padding:

 err_registers:

    g_object_unref(G_OBJECT(target));

 err_target:

    if (opg != NULL)
        g_object_unref(G_OBJECT(opg));

 err_no_opg:
 err_va:

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction dont la définition est incomplète.[OUT]*
*                format  = format du fichier contenant le code.               *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                low     = position éventuelle des 4 bits visés. [OUT]        *
*                endian  = boutisme lié au binaire accompagnant.              *
*                model   = type d'opérandes attendues.                        *
*                                                                             *
*  Description : Procède à la lecture d'opérandes pour une instruction.       *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool dalvik_read_variatic_operands(GArchInstruction *instr, GDexFormat *format, const GBinContent *content, vmpa2t *pos, bool *low, SourceEndian endian, DalvikOperandType model)
{
    uint8_t a;                              /* Nbre. de registres utilisés */
    uint16_t c;                             /* Indice de registre          */
    GArchOperand *target;                   /* Opérande visant la table    */
    GArchOperand *args;                     /* Liste des opérandes         */
    uint8_t i;                              /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande unique décodé      */

    if (!g_binary_content_read_u8(content, pos, &a))
        return false;

    target = g_dalvik_pool_operand_new(format, DALVIK_OP_GET_POOL(model), content, pos, MDS_16_BITS, endian);
    if (target == NULL) return false;

    if (!g_binary_content_read_u16(content, pos, endian, &c))
        return false;

    /* Mise en place des arguments */

    args = g_dalvik_args_operand_new();

    for (i = 0; i < a; i++)
    {
        op = g_dalvik_register_operand_new_from_existing(g_dalvik_register_new(c + i));
        if (op == NULL) goto drvo_registers;

        g_dalvik_args_operand_add(G_DALVIK_ARGS_OPERAND(args), op);

    }

    g_arch_instruction_attach_extra_operand(instr, args);

    /* Rajout de la cible */

    g_arch_instruction_attach_extra_operand(instr, target);

    return true;

 drvo_registers:

    g_object_unref(G_OBJECT(target));

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction dont la définition est incomplète.[OUT]*
*                format  = format du fichier contenant le code.               *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                endian  = boutisme lié au binaire accompagnant.              *
*                model   = type d'opérandes attendues.                        *
*                                                                             *
*  Description : Procède à la lecture d'opérandes pour une instruction.       *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool dalvik_read_operands(GArchInstruction *instr, GExeFormat *format, const GBinContent *content, vmpa2t *pos, SourceEndian endian, DalvikOperandType model)
{
    bool result;                            /* Bilan à retourner           */
    GDexFormat *dformat;                    /* Autre version du format     */
    bool low;                               /* Partie d'octets à lire      */
#ifndef NDEBUG
    vmpa2t old;                             /* Position avant traitements  */
#endif
    vmpa2t base;                            /* Base pour les sauts de code */
    vmpa2t *extra;                          /* Information complémentaire  */
#ifndef NDEBUG
    phys_t expected;                        /* Consommation attendue       */
    phys_t consumed;                        /* Consommation réelle         */
#endif

    result = true;

    dformat = G_DEX_FORMAT(format);

    low = true;

#ifndef NDEBUG

    copy_vmpa(&old, pos);

#endif

    /* Récupération de la base ? */

    if (DALVIK_OP_GET_MNEMONIC(model) == DALVIK_OP_MNEMONIC_1('t'))
    {
        extra = &base;

        copy_vmpa(extra, pos);
        deminish_vmpa(extra, 1);

    }
    else extra = NULL;

    /* Bourrage : ØØ|op ? */

    switch (DALVIK_OP_BASE_MASK(model))
    {
        case DALVIK_OPT_10X:
        case DALVIK_OPT_20T:
        case DALVIK_OPT_30T:
        case DALVIK_OPT_32X:
            result = g_binary_content_seek(content, pos, 1);
            break;

        default:
            break;

    }

    /* Décodage... */

    switch (DALVIK_OP_BASE_MASK(model))
    {
        case DALVIK_OPT_10T:
        case DALVIK_OPT_11N:
        case DALVIK_OPT_11X:
        case DALVIK_OPT_12X:
        case DALVIK_OPT_20T:
        case DALVIK_OPT_21C:
        case DALVIK_OPT_21H:
        case DALVIK_OPT_21S:
        case DALVIK_OPT_21T:
        case DALVIK_OPT_22B:
        case DALVIK_OPT_22C:
        case DALVIK_OPT_22S:
        case DALVIK_OPT_22T:
        case DALVIK_OPT_22X:
        case DALVIK_OPT_23X:
        case DALVIK_OPT_30T:
        case DALVIK_OPT_31C:
        case DALVIK_OPT_31I:
        case DALVIK_OPT_31T:
        case DALVIK_OPT_32X:
        case DALVIK_OPT_51L:
            result = dalvik_read_basic_operands(instr, dformat, content, pos, &low, endian, model, extra);
            break;

        case DALVIK_OPT_35C:
            result = dalvik_read_fixed_operands(instr, dformat, content, pos, &low, endian, model);
            break;

        case DALVIK_OPT_3RC:
            result = dalvik_read_variatic_operands(instr, dformat, content, pos, &low, endian, model);
            break;

        default:
            break;

    }

#ifndef NDEBUG

    /* Vérification d'implémentation */

    if (result)
    {
        expected = DALVIK_OP_GET_LEN(model) * 2;
        consumed = 1 + compute_vmpa_diff(&old, pos);

        assert(consumed == expected);

    }

#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction dont la définition est incomplète.      *
*                                                                             *
*  Description : Procède à la lecture d'opérandes pour une instruction.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void dalvik_mark_first_operand_as_written(GArchInstruction *instr)
{
    GArchOperand *operand;                  /* Première opérande visé      */

    operand = g_arch_instruction_get_operand(instr, 0);

    g_arch_operand_set_flag(operand, ROF_IS_WRITTEN);

    g_object_unref(G_OBJECT(operand));

}
