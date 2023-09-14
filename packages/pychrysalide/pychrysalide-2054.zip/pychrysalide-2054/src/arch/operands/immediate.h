
/* Chrysalide - Outil d'analyse de fichiers binaires
 * immediate.h - prototypes pour les opérandes représentant des valeurs numériques
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_IMMEDIATE_H
#define _ARCH_OPERANDS_IMMEDIATE_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>


#include "../archbase.h"
#include "../operand.h"
#include "../../analysis/content.h"



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _ImmOpFlag
{
    IOF_ZERO_PADDING_BY_DEFAULT = AOF_USER_FLAG(0), /* Bourrage avec 0 par défaut ?*/
    IOF_ZERO_PADDING = AOF_USER_FLAG(1),    /* Bourrage avec 0 ?           */

} ImmOpFlag;

/* Grande ligne d'un format d'affichage */
typedef enum _ImmOperandDisplay
{
    IOD_BIN,                                /* Impression en binaire       */
    IOD_OCT,                                /* Impression en octal         */
    IOD_DEC,                                /* Impression en décimal       */
    IOD_HEX,                                /* Impression en hexadécimal   */
    IOD_CHAR,                               /* Impression en base 26       */

    IOD_COUNT

} ImmOperandDisplay;

#define IOD_LAST_VALID IOD_CHAR


#define G_TYPE_IMM_OPERAND            g_imm_operand_get_type()
#define G_IMM_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_IMM_OPERAND, GImmOperand))
#define G_IS_IMM_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_IMM_OPERAND))
#define G_IMM_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_IMM_OPERAND, GImmOperandClass))
#define G_IS_IMM_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_IMM_OPERAND))
#define G_IMM_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_IMM_OPERAND, GImmOperandClass))


/* Définition d'un opérande de valeur numérique (instance) */
typedef struct _GImmOperand GImmOperand;

/* Définition d'un opérande de valeur numérique (classe) */
typedef struct _GImmOperandClass GImmOperandClass;


/* Indique le type défini pour un opérande d'architecture. */
GType g_imm_operand_get_type(void);

/* Crée un opérande réprésentant une valeur numérique. */
GArchOperand *_g_imm_operand_new_from_data(MemoryDataSize, const GBinContent *, vmpa2t *, bool *, SourceEndian);

#define g_imm_operand_new_from_data(size, content, addr, endian) \
    _g_imm_operand_new_from_data(size, content, addr, NULL, endian)

/* Crée un opérande réprésentant une valeur numérique. */
GArchOperand *g_imm_operand_new_from_value(MemoryDataSize, uint64_t);

/* Renseigne la taille de la valeur indiquée à la construction. */
MemoryDataSize g_imm_operand_get_size(const GImmOperand *);

/* Fournit la valeur portée par une opérande numérique. */
bool g_imm_operand_get_value(const GImmOperand *, MemoryDataSize, ...);

/* Fournit la valeur brute représentée par l'opérande. */
uint64_t g_imm_operand_get_raw_value(const GImmOperand *);

/* Définit la nouvelle valeur de l'opérande à une valeur. */
void g_imm_operand_set_value(GImmOperand *, MemoryDataSize, uint64_t);

/* Définit le format textuel par défaut de la valeur. */
void g_imm_operand_set_default_display(GImmOperand *, ImmOperandDisplay);

/* Indique le format textuel par défaut de la valeur. */
ImmOperandDisplay g_imm_operand_get_default_display(const GImmOperand *);

/* Définit la grande ligne du format textuel de la valeur. */
void g_imm_operand_set_display(GImmOperand *, ImmOperandDisplay);

/* Indique la grande ligne du format textuel de la valeur. */
ImmOperandDisplay g_imm_operand_get_display(const GImmOperand *);

/* Indique le signe d'une valeur immédiate. */
bool g_imm_operand_is_negative(const GImmOperand *);

/* Indique si une valeur immédiate est nulle ou non. */
bool g_imm_operand_is_null(const GImmOperand *);

/**
 * La taille d'impression d'un opérande n'est pas VMPA_MAX_SIZE,
 * mais 1 + 64 caractères + octet nul final en cas d'impression en binaire.
 */
#define IMM_MAX_SIZE 66

/* Construit la chaîne de caractères correspondant à l'opérande. */
size_t g_imm_operand_to_string(const GImmOperand *, char [IMM_MAX_SIZE]);

/* Convertit une valeur immédiate en position de type phys_t. */
bool g_imm_operand_to_phys_t(const GImmOperand *, phys_t *);

/* Convertit une valeur immédiate en adresse de type virt_t. */
bool g_imm_operand_to_virt_t(const GImmOperand *, virt_t *);

/* Convertit une valeur immédiate en valeur de type leb128_t. */
void g_imm_operand_as_leb128(const GImmOperand *, leb128_t *);

/* Convertit une valeur immédiate en valeur de type uleb128_t. */
void g_imm_operand_as_uleb128(const GImmOperand *, uleb128_t *);



#endif  /* _ARCH_OPERANDS_IMMEDIATE_H */
