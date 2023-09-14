
/* Chrysalide - Outil d'analyse de fichiers binaires
 * identifiers.h - définition d'identifiants uniques pour Dalvik
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


#ifndef _PLUGINS_DALVIK_PSEUDO_IDENTIFIERS_H
#define _PLUGINS_DALVIK_PSEUDO_IDENTIFIERS_H


/* Enumération de tous les pseudo-opcodes */
typedef enum _DalvikPseudoOpcodes
{
    DPO_PACKED_SWITCH   = 0x0100,           /* Switch aux clefs compactes  */
    DPO_SPARSE_SWITCH   = 0x0200,           /* Switch aux clefs éclatées   */
    DPO_FILL_ARRAY_DATA = 0x0300            /* Contenu de tableau          */

} DalvikPseudoOpcodes;



#endif  /* _PLUGINS_DALVIK_PSEUDO_IDENTIFIERS_H */
