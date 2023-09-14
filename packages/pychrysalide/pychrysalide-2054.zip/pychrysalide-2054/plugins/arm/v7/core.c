
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - chargement et déchargement des mécanismes internes de l'architecture ARMv7
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "core.h"


#include <core/processors.h>


#include "instruction.h"
#include "processor.h"
#include "operands/estate.h"
#include "operands/iflags.h"
#include "operands/it.h"
#include "operands/limitation.h"
#include "operands/maccess.h"
#include "operands/offset.h"
#include "operands/register.h"
#include "operands/reglist.h"
#include "operands/rotation.h"
#include "operands/shift.h"
#include "registers/banked.h"
#include "registers/basic.h"
#include "registers/coproc.h"
#include "registers/simd.h"
#include "registers/special.h"



/* Assure l'enregistrement de types pour les caches à charger. */
static void register_armv7_gtypes(void);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Assure l'enregistrement de types pour les caches à charger.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_armv7_gtypes(void)
{
    g_type_ensure(G_TYPE_ARMV7_INSTRUCTION);

    g_type_ensure(G_TYPE_ARMV7_ENDIAN_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_IFLAGS_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_ITCOND_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_LIMITATION_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_MACCESS_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_OFFSET_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_REGISTER_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_REGLIST_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_ROTATION_OPERAND);
    g_type_ensure(G_TYPE_ARMV7_SHIFT_OPERAND);

    g_type_ensure(G_TYPE_ARMV7_BANKED_REGISTER);
    g_type_ensure(G_TYPE_ARMV7_BASIC_REGISTER);
    g_type_ensure(G_TYPE_ARMV7_CP_REGISTER);
    g_type_ensure(G_TYPE_ARMV7_SIMD_REGISTER);
    g_type_ensure(G_TYPE_ARMV7_SPECIAL_REGISTER);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Met en place les mécanismes internes de l'architecture ARMv7.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_armv7_core(void)
{
    bool result;                            /* Bilan à renvoyer            */

    register_armv7_gtypes();

    result = register_processor_type(G_TYPE_ARMV7_PROCESSOR);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Supprime les mécanismes internes de l'architecture ARMv7.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_armv7_core(void)
{
    clean_armv7_banked_register_cache();
    clean_armv7_basic_register_cache();
    clean_armv7_cp_register_cache();
    clean_armv7_simd_register_cache();

}
