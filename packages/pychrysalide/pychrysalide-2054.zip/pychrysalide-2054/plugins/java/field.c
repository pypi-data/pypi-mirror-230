
/* Chrysalide - Outil d'analyse de fichiers binaires
 * field.c - gestion des champs Java
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


#include "field.h"


#include <malloc.h>


#include "attribute.h"
#include "java-int.h"
#include "../../common/endianness.h"



/* Charge les propriétés d'un champ de classe. */
bool load_java_field(java_format *, java_field *, off_t *);

/* Décharge les propriétés d'un champ de classe. */
void unload_java_field(java_format *, java_field *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les champs d'un binaire Java.                         *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_fields(java_format *format, off_t *pos)
{
    bool result;                            /* Bilan à remonter            */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&format->fields_count, EXE_FORMAT(format)->content, pos,
                      EXE_FORMAT(format)->length, SRE_BIG);

    if (!result) return false;

    if (format->fields_count > 0)
    {
        format->fields = (java_field *)calloc(format->fields_count, sizeof(java_field));

        for (i = 0; i < format->fields_count && result; i++)
            result = load_java_field(format, &format->fields[i], pos);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à vider.                *
*                                                                             *
*  Description : Décharge les champs d'un binaire Java.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_fields(java_format *format)
{
    uint16_t i;                             /* Boucle de parcours          */

    for (i = 0; i < format->fields_count; i++)
        unload_java_field(format, &format->fields[i]);

    free(format->fields);


}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                field  = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un champ de classe.                  *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_field(java_format *format, java_field *field, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = read_u16((uint16_t *)&field->access, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= read_u16(&field->name_index, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);
    result &= read_u16(&field->descriptor_index, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= load_java_attributes(format, pos,
                                   &field->attributes, &field->attributes_count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                field  = élément à libérer.                                  *
*                                                                             *
*  Description : Décharge les propriétés d'un champ de classe.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_field(java_format *format, java_field *field)
{
    if (field->attributes_count > 0)
        unload_java_attributes(format, field->attributes, field->attributes_count);

}
