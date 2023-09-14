
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cpu.h - prototypes pour l'obtention d'indications de fonctionnalités liées au CPU
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _COMMON_CPU_H
#define _COMMON_CPU_H



/* Indication de capacité de calculs parallèles */
typedef enum _CPUSMIDFeature
{
    CSF_NONE   = (0 << 0),                  /* Absence d'indication        */

    CSF_AVX2   = (1 << 0),                  /* Advanced Vector Extensions  */
    CSF_AVX512 = (1 << 1),                  /* Advanced Vector Extensions  */

    CSF_ALL    = ((1 << 2) - 1),

} CPUSMIDFeature;


/* Indique les capacités de calculs parallèles anticipées. */
CPUSMIDFeature get_supported_cpu_smid_feature(void);

/* Indique les capacités de calculs parallèles sollicitables. */
CPUSMIDFeature get_avalaible_cpu_smid_feature(void);



#endif  /* _COMMON_CPU_H */
