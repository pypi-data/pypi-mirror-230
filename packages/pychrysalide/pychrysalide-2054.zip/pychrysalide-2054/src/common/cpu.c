
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cpu.c - obtention d'indications de fonctionnalités liées au CPU
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


#include "cpu.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Indique les capacités de calculs parallèles anticipées.      *
*                                                                             *
*  Retour      : Fonctionnalités disponibles lors de la compilation.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

CPUSMIDFeature get_supported_cpu_smid_feature(void)
{
    CPUSMIDFeature result;                  /* Indications à retourner     */

    result = CSF_NONE;

    /**
     * $ gcc -mavx512f -dM -E - < /dev/null | grep AVX
     * #define __AVX512F__ 1
     * #define __AVX__ 1
     * #define __AVX2__ 1
     */

#ifdef __AVX2__
    result |= CSF_AVX2;
#endif

#ifdef __AVX512F__
    result |= CSF_AVX512;
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Indique les capacités de calculs parallèles sollicitables.   *
*                                                                             *
*  Retour      : Fonctionnalités disponibles dans l'environnement.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

CPUSMIDFeature get_avalaible_cpu_smid_feature(void)
{
    CPUSMIDFeature result;                  /* Indications à retourner     */

    result = CSF_NONE;

    /**
     * Cf. Documentations suivantes :
     *   - https://www.intel.com/content/dam/develop/external/us/en/documents/how-to-detect-new-instruction-support-in-the-4th-generation-intel-core-processor-family.pdf
     *   - https://gcc.gnu.org/onlinedocs/gcc/x86-Built-in-Functions.html
     */

  __builtin_cpu_init();

  if (__builtin_cpu_supports("ssse3"))
      result |= CSF_AVX2;

  if (__builtin_cpu_supports("avx512f"))
      result |= CSF_AVX512;

    return result;

}
