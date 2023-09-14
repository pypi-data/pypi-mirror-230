
/* Chrysalide - Outil d'analyse de fichiers binaires
 * method.c - gestion des méthodes Java
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


#include "method.h"


#include <malloc.h>


#include "attribute.h"
#include "../../common/endianness.h"



/* Charge les propriétés d'une méthode de classe. */
bool load_java_method(java_format *, java_method *, off_t *);

/* Décharge les propriétés d'une méthode de classe. */
void unload_java_method(java_format *, java_method *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les méthodes d'un binaire Java.                       *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_methods(java_format *format, off_t *pos)
{
    bool result;                            /* Bilan à remonter            */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&format->methods_count, EXE_FORMAT(format)->content, pos,
                      EXE_FORMAT(format)->length, SRE_BIG);

    if (!result) return false;

    if (format->methods_count > 0)
    {
        format->methods = (java_method *)calloc(format->methods_count, sizeof(java_method));

        for (i = 0; i < format->methods_count && result; i++)
            result = load_java_method(format, &format->methods[i], pos);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à vider.                *
*                                                                             *
*  Description : Décharge les méthodes d'un binaire Java.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_methods(java_format *format)
{
    uint16_t i;                             /* Boucle de parcours          */

    for (i = 0; i < format->methods_count; i++)
        unload_java_method(format, &format->methods[i]);

    free(format->methods);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                method = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'une méthode de classe.               *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_method(java_format *format, java_method *method, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = read_u16((uint16_t *)&method->access, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= read_u16(&method->name_index, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);
    result &= read_u16(&method->descriptor_index, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= load_java_attributes(format, pos,
                                   &method->attributes, &method->attributes_count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                method = élément à libérer.                                  *
*                                                                             *
*  Description : Décharge les propriétés d'une méthode de classe.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_method(java_format *format, java_method *method)
{
    if (method->attributes_count > 0)
        unload_java_attributes(format, method->attributes, method->attributes_count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = élément à traiter.                                  *
*                offset = position physique du code de la méthode. [OUT]      *
*                size   = taille du code de la méthode. [OUT]                 *
*                                                                             *
*  Description : Retrouve le code binaire correspondant à une méthode.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_java_method_code_part(const java_method *method, off_t *offset, off_t *size)
{
    uint16_t i;                             /* Boucle de parcours          */

    for (i = 0; i < method->attributes_count; i++)
        if (method->attributes[i].type == JAT_CODE)
        {
            *offset = method->attributes[i].info.code.content;
            *size = method->attributes[i].info.code.code_length;
            break;
        }

    return (i < method->attributes_count);

}
