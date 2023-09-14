
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pool.h - prototypes pour la lecture du réservoir de constantes
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


#ifndef _FORMAT_JAVA_POOL_H
#define _FORMAT_JAVA_POOL_H


#include "java.h"



/* Types de référence Java */
typedef enum _JavaRefType
{
    JRT_FIELD,                              /* Champ                       */
    JRT_METHOD,                             /* Méthode                     */
    JRT_INTERFACE_METHOD                    /* Méthode d'interface         */

} JavaRefType;


/* Charge le réservoir de constantes d'un binaire Java. xs*/
bool load_java_pool(GJavaFormat *, off_t *);

/* Décharge le réservoir de constantes d'un binaire Java. */
void unload_java_pool(GJavaFormat *);

/* Construit une version humaine de référence. */
char *build_reference_from_java_pool(const GJavaFormat *, uint16_t, JavaRefType);

/* Recherche une chaîne de caractères dans le réservoir. */
bool get_java_pool_ut8_string(const GJavaFormat *, uint16_t, const char **);



#endif  /* _FORMAT_JAVA_POOL_H */
