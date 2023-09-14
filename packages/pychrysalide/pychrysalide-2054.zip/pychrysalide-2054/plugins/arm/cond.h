
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encoding.h - prototypes pour le décodage des conditions d'exécution ARM
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


#ifndef _PLUGINS_ARM_ENCODING_H
#define _PLUGINS_ARM_ENCODING_H



/**
 * Les conditions d'exécutions sont partagées par les architectures ARM :
 *
 * ARMv7 Instruction Details
 * § A8.3 Conditional execution
 *
 * ARMv8 Instruction Set Overview.
 * § 4.3 Condition Codes.
 *
 */

/* Liste des conditions possibles */
typedef enum _ArmCondCode
{
    ACC_EQ = 0x0,                           /* Equal                       */
    ACC_NE = 0x1,                           /* Not equal                   */
    ACC_HS = 0x2,                           /* Unsigned higher or same     */
    ACC_LO = 0x3,                           /* Unsigned lower              */
    ACC_MI = 0x4,                           /* Minus                       */
    ACC_PL = 0x5,                           /* Plus or zero                */
    ACC_VS = 0x6,                           /* Overflow set                */
    ACC_VC = 0x7,                           /* Overflow clear              */
    ACC_HI = 0x8,                           /* Unsigned higher             */
    ACC_LS = 0x9,                           /* Unsigned lower or same      */
    ACC_GE = 0xa,                           /* Signed greater than or equal*/
    ACC_LT = 0xb,                           /* Signed less than            */
    ACC_GT = 0xc,                           /* Signed greater than         */
    ACC_LE = 0xd,                           /* Signed less than or equal   */
    ACC_AL = 0xe,                           /* Always                      */
    ACC_NV = 0xf,                           /* (Never)                     */

} ArmCondCode;



#endif  /* _PLUGINS_ARM_ENCODING_H */
