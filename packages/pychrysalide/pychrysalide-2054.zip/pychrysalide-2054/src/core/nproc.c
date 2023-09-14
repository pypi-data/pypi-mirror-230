
/* Chrysalide - Outil d'analyse de fichiers binaires
 * nproc.c - détermination du volume de traitements parallèles idéal
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


#include "nproc.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Indique le nombre idéal de tâches pour bien occuper le CPU.  *
*                                                                             *
*  Retour      : Quantité de threads pour les groupes de travail sans retenue.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

guint get_max_online_threads(void)
{
    guint result;                           /* Estimation à retourner      */

    result = g_get_num_processors();

    /**
     * Un peu arbitraire, mais bon...
     */
    result *= 2;

    return result;

}
