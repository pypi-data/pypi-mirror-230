
/* Chrysalide - Outil d'analyse de fichiers binaires
 * e_java.c - support du format Java
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


#include "e_java.h"


#include <malloc.h>
#include <string.h>


#include "attribute.h"
#include "field.h"
#include "java-int.h"
#include "method.h"
#include "pool.h"
#include "../../common/endianness.h"




/* Indique le type d'architecture visée par le format. */
FormatTargetMachine get_java_target_machine(const java_format *);



/* Fournit les références aux zones de code à analyser. */
bin_part **get_java_default_code_parts(const java_format *, size_t *);


/* Fournit le prototype de toutes les routines détectées. */
GBinRoutine **get_all_java_routines(const java_format *, size_t *);





/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                length  = taille du contenu en question.                     *
*                                                                             *
*  Description : Indique si le format peut être pris en charge ici.           *
*                                                                             *
*  Retour      : true si la réponse est positive, false sinon.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool java_is_matching(const uint8_t *content, off_t length)
{
    bool result;                            /* Bilan à faire connaître     */

    result = false;

    if (length >= 4)
        result = (strncmp((const char *)content, "\xca\xfe\xba\xbe", 4) == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                length  = taille du contenu en question.                     *
*                                                                             *
*  Description : Prend en charge une nouvelle classe Java.                    *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

exe_format *load_java(const uint8_t *content, off_t length)
{
    java_format *result;                    /* Adresse à retourner         */
    off_t pos;                              /* Point d'analyse             */
    uint32_t magic;                         /* Identifiant Java            */
    uint16_t i;                             /* Boucle de parcours          */

    result = (java_format *)calloc(1, sizeof(java_format));

    EXE_FORMAT(result)->content = content;
    EXE_FORMAT(result)->length = length;

    EXE_FORMAT(result)->get_target_machine = (get_target_machine_fc)get_java_target_machine;
    EXE_FORMAT(result)->get_def_parts = (get_def_parts_fc)get_java_default_code_parts;
    EXE_FORMAT(result)->get_all_routines = (get_all_routines_fc)get_all_java_routines;

    pos = 0;

    if (!read_u32(&magic, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->minor_version, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->major_version, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!load_java_pool(result, &pos))
        goto ldj_error;

    if (!read_u16((uint16_t *)&result->access, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->this_class, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->super_class, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->interfaces_count, content, &pos, length, SRE_BIG))
       goto ldj_error;

    for (i = 0; i < result->interfaces_count; i++)
        if (!read_u16(&result->interfaces[i], content, &pos, length, SRE_BIG))
            goto ldj_error;

    if (!load_java_fields(result, &pos))
        goto ldj_error;

    if (!load_java_methods(result, &pos))
        goto ldj_error;

    if (!load_java_attributes(result, &pos, &result->attributes, &result->attributes_count))
        goto ldj_error;

    return EXE_FORMAT(result);

 ldj_error:

    unload_java(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à supprimer.            *
*                                                                             *
*  Description : Efface la prise en charge une nouvelle classe Java.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java(java_format *format)
{
    if (format->pool_len > 0)
        unload_java_pool(format);

    if (format->interfaces_count > 0)
        free(format->interfaces);

    if (format->fields_count > 0)
        unload_java_fields(format);

    if (format->methods_count > 0)
        unload_java_methods(format);

    if (format->attributes_count > 0)
        unload_java_attributes(format, format->attributes, format->attributes_count);

    free(format);

}





/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Indique le type d'architecture visée par le format.          *
*                                                                             *
*  Retour      : Identifiant de l'architecture ciblée par le format.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

FormatTargetMachine get_java_target_machine(const java_format *format)
{
    return FTM_JVM;

}





/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                count  = quantité de zones listées. [OUT]                    *
*                                                                             *
*  Description : Fournit les références aux zones de code à analyser.         *
*                                                                             *
*  Retour      : Zones de code à analyser.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bin_part **get_java_default_code_parts(const java_format *format, size_t *count)
{
    bin_part **result;                      /* Tableau à retourner         */
    uint16_t i;                             /* Boucle de parcours          */
    off_t offset;                           /* Position physique           */
    off_t size;                             /* Taille de la partie         */
    bin_part *part;                         /* Partie à intégrer à la liste*/

    result = NULL;
    *count = 0;

    for (i = 0; i < format->methods_count; i++)
        if (find_java_method_code_part(&format->methods[i], &offset, &size))
        {
            part = create_bin_part();

            set_bin_part_values(part, offset, size, offset);

            result = (bin_part **)realloc(result, ++(*count) * sizeof(bin_part *));
            result[*count - 1] = part;

        }

    return result;

}




/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                count  = taille du tableau créé. [OUT]                       *
*                                                                             *
*  Description : Fournit le prototype de toutes les routines détectées.       *
*                                                                             *
*  Retour      : Tableau créé ou NULL si aucun symbole de routine trouvé.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine **get_all_java_routines(const java_format *format, size_t *count)
{
    *count = 0;

    return NULL;

}
