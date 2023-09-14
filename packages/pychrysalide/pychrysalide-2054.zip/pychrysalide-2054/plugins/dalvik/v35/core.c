
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - chargement et déchargement des mécanismes internes de l'architecture Dalvik v35
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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



/* Assure l'enregistrement de types pour les caches à charger. */
static void register_dalvik35_gtypes(void);



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

static void register_dalvik35_gtypes(void)
{
    g_type_ensure(G_TYPE_DALVIK35_INSTRUCTION);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Met en place les mécanismes internes de l'archi. Dalvik v35. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_dalvik35_core(void)
{
    bool result;                            /* Bilan à renvoyer            */

    register_dalvik35_gtypes();

    result = register_processor_type(G_TYPE_DALVIK35_PROCESSOR);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Supprime les mécanismes internes de l'archi. Dalvik v35.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_dalvik35_core(void)
{

}
