
/* Chrysalide - Outil d'analyse de fichiers binaires
 * java-int.c - structures internes du format Java
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


#include "java-int.h"


#include "pool.h"
#include "../../common/endianness.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                header = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une en-tête de programme Java.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_java_header(const GJavaFormat *format, off_t *pos, java_header *header)
{
    bool result;                            /* Bilan à retourner           */
    const bin_t *content;                   /* Contenu binaire à lire      */
    off_t length;                           /* Taille totale du contenu    */
    uint32_t magic;                         /* Identifiant Java            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    content = NULL; //G_BIN_FORMAT(format)->content;
    length = 0; //G_BIN_FORMAT(format)->length;

    result &= read_u32(&magic, content, pos, length, SRE_BIG);
    printf("magic :: 0x%08x\n", magic);
    result &= read_u16(&header->minor_version, content, pos, length, SRE_BIG);
    result &= read_u16(&header->major_version, content, pos, length, SRE_BIG);

    printf("avant :: %d\n", result);

    result &= load_java_pool(format, pos);

    printf("après :: %d\n", result);

    result &= read_u16((uint16_t *)&header->access, content, pos, length, SRE_BIG);
    result &= read_u16(&header->this_class, content, pos, length, SRE_BIG);
    result &= read_u16(&header->super_class, content, pos, length, SRE_BIG);
    result &= read_u16(&header->interfaces_count, content, pos, length, SRE_BIG);

/*     for (i = 0; i < header->interfaces_count; i++) */
/*         result &= read_u16(&header->interfaces[i], content, pos, length, SRE_BIG)) */
/*             goto ldj_error; */

/*     result &= load_java_fields(result, pos); */

/*     result &= load_java_methods(result, pos); */

/*     result &= load_java_attributes(result, pos, &header->attributes, &header->attributes_count); */

    return result;

}





