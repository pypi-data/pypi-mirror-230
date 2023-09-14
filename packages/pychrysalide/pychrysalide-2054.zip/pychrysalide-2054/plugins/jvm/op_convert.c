
/* Chrysalide - Outil d'analyse de fichiers binaires
 * op_convert.c - décodage des conversions entre types de base
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "opcodes.h"


#include "instruction.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'd2f'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_d2f(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_D2F);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'd2i'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_d2i(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_D2I);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'd2l'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_d2l(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_D2L);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'f2d'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_f2d(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_F2D);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'f2i'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_f2i(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_F2I);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'f2l'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_f2l(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_F2L);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'i2b'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_i2b(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_I2B);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'i2c'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_i2c(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_I2C);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'i2d'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_i2d(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_I2D);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'i2f'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_i2f(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_I2F);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'i2l'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_i2l(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_I2L);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'i2s'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_i2s(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_I2S);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'l2d'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_l2d(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_L2D);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'l2i'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_l2i(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_L2I);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'l2f'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_l2f(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_L2F);

    return result;

}
