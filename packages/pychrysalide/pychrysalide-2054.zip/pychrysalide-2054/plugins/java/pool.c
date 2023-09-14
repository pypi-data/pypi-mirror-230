
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pool.c - lecture du réservoir de constantes
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


#include "pool.h"


#include <malloc.h>
#include <math.h>
#include <string.h>

#include "java-int.h"
#include "../../common/endianness.h"
#include "../../common/extstr.h"



/* Charge les propriétés d'une constante du réservoir. */
bool load_java_pool_entry(GJavaFormat *, constant_pool_entry *, off_t *);

/* Fournit une entrée donnée du réservoir de constantes. */
const constant_pool_entry *get_java_pool_entry(const GJavaFormat *, uint16_t, ConstantPoolTag);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge le réservoir de constantes d'un binaire Java.         *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_pool(GJavaFormat *format, off_t *pos)
{
    bool result;                            /* Bilan à remonter            */
    uint16_t count;                         /* Nombre d'éléments présents  */
    uint16_t i;                             /* Boucle de parcours          */

    result = false/*read_u16(&count, G_BIN_FORMAT(format)->content, pos,
                    G_BIN_FORMAT(format)->length, SRE_BIG)*/;
#if 0
    printf("Alloc %hu entries (result=%d)\n", count, result);

    format->header.pool_len = count - 1;
    format->header.pool = (constant_pool_entry *)calloc(count - 1, sizeof(constant_pool_entry));

    for (i = 1; i < count && result; i++)
    {
        result = load_java_pool_entry(format, &format->header.pool[i - 1], pos);

        if (format->header.pool[i - 1].tag == CONSTANT_LONG
            || format->header.pool[i - 1].tag == CONSTANT_DOUBLE)
        {
            i++;

            /* On n'est jamais trop prudent */
            if (i < count)
                format->header.pool[i - 1].tag = CONSTANT_EMPTY;

        }

    }
#endif
    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à vider.                *
*                                                                             *
*  Description : Décharge le réservoir de constantes d'un binaire Java.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_pool(GJavaFormat *format)
{
    uint16_t i;                             /* Boucle de parcours          */

    for (i = 0; i < format->header.pool_len; i++)
        switch (format->header.pool[i].tag)
        {
            case CONSTANT_EMPTY:
            case CONSTANT_CLASS:
            case CONSTANT_FIELD_REF:
            case CONSTANT_METHOD_REF:
            case CONSTANT_INTERFACE_METHOD_REF:
            case CONSTANT_STRING:
            case CONSTANT_INTEGER:
            case CONSTANT_FLOAT:
            case CONSTANT_LONG:
            case CONSTANT_DOUBLE:
            case CONSTANT_NAME_AND_TYPE:
                break;

            case CONSTANT_UTF8:
                free(format->header.pool[i].info.utf8.bytes);
                break;

        }

    free(format->header.pool);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                entry  = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'une constante du réservoir.          *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_pool_entry(GJavaFormat *format, constant_pool_entry *entry, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint8_t tag;                            /* Type de l'élément           */
    uint32_t low_bytes;                     /* Octets de poids faible      */
    uint32_t high_bytes;                    /* Octets de poids fort        */
    uint64_t bits;                          /* Nombre lu sur 64 bits       */
    int sign;                               /* Signe du nombre lu          */
	int exponent;                           /* Exposant du nombre lu       */
	uint64_t mantissa32;                    /* Mantisse du nombre lu 32b   */
	uint64_t mantissa64;                    /* Mantisse du nombre lu 64b   */
    uint16_t length;                        /* Taille d'une chaîne         */

    result = false/*read_u8(&tag, G_BIN_FORMAT(format)->content, pos,
                    G_BIN_FORMAT(format)->length, SRE_BIG)*/;
#if 0
    entry->tag = tag;

    switch (entry->tag)
    {
        case CONSTANT_CLASS:
            result = read_u16(&entry->info.class.name_index, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            break;

        case CONSTANT_FIELD_REF:
        case CONSTANT_METHOD_REF:
        case CONSTANT_INTERFACE_METHOD_REF:

            result = read_u16(&entry->info.ref.class_index, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            result &= read_u16(&entry->info.ref.name_and_type_index, G_BIN_FORMAT(format)->content,
                               pos, G_BIN_FORMAT(format)->length, SRE_BIG);

            break;

        case CONSTANT_STRING:
            result = read_u16(&entry->info.string.string_index, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            break;

        case CONSTANT_INTEGER:
            result = read_u32(&entry->info.int_val.val, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            break;

        case CONSTANT_FLOAT:

            result = read_u32(&low_bytes, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);

            if (result)
            {
                if (low_bytes == 0x7f800000)
                    entry->info.float_val.val = INFINITY;

                else if (low_bytes == 0xff800000)
                    entry->info.float_val.val = /* -1* */INFINITY;

                else if ((low_bytes >= 0x7f800001 && low_bytes <= 0x7fffffff)
                         || (low_bytes >= 0xff800001 && low_bytes <= 0xffffffff))
                    entry->info.float_val.val = NAN;

                else if (low_bytes == 0x00000000 || low_bytes == 0x80000000)
                    entry->info.float_val.val = 0;

                else
                {
                    sign = (low_bytes & 0x80000000) ? -1 : 1;
                    exponent = (low_bytes >> 23) & 0xff;
                    mantissa32 = (exponent == 0 ?
                                  (low_bytes & 0x7fffff) << 1 :
                                  (low_bytes & 0x7fffff) | 0x800000);

                    entry->info.float_val.val = pow(2, (exponent - 150));
                    entry->info.float_val.val *= mantissa32;
                    entry->info.float_val.val *= sign;

                }

            }

            break;

        case CONSTANT_LONG:

            result = read_u32(&high_bytes, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            result &= read_u32(&low_bytes, G_BIN_FORMAT(format)->content,
                               pos, G_BIN_FORMAT(format)->length, SRE_BIG);

            if (result)
            {
                entry->info.double_val.val = (uint64_t)high_bytes << 32;
                entry->info.double_val.val += low_bytes;
            }

            break;

        case CONSTANT_DOUBLE:

            result = read_u32(&high_bytes, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            result &= read_u32(&low_bytes, G_BIN_FORMAT(format)->content,
                               pos, G_BIN_FORMAT(format)->length, SRE_BIG);

            if (result)
            {
                bits = (uint64_t)high_bytes << 32 | (uint64_t)low_bytes;

                if (bits == 0x7ff0000000000000ll)
                    entry->info.double_val.val = INFINITY;

                else if (bits == 0xfff0000000000000ll)
                    entry->info.double_val.val = /* -1* */INFINITY;

                else if ((bits >= 0x7ff0000000000001ll && bits <= 0x7fffffffffffffffll)
                         || (bits >= 0xfff0000000000001ll && bits <= 0xffffffffffffffffll))
                    entry->info.double_val.val = NAN;

                else if (bits == 0x0000000000000000ll || bits == 0x8000000000000000ll)
                    entry->info.double_val.val = 0;

                else
                {
                    sign = ((bits >> 63) == 0) ? 1 : -1;
                    exponent = (bits >> 52) & 0x7ffl;
                    mantissa64 = (exponent == 0 ?
                                  (bits & 0xfffffffffffffll) << 1 :
                                  (bits & 0xfffffffffffffll) | 0x10000000000000ll);

                    entry->info.double_val.val = pow(2, (exponent - 1075));
                    entry->info.double_val.val *= mantissa64;
                    entry->info.double_val.val *= sign;

                }

            }

            break;

        case CONSTANT_NAME_AND_TYPE:

            result = read_u16(&entry->info.name_type.name_index, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);
            result &= read_u16(&entry->info.name_type.descriptor_index, G_BIN_FORMAT(format)->content,
                               pos, G_BIN_FORMAT(format)->length, SRE_BIG);

            break;

        case CONSTANT_UTF8:

            result = read_u16(&length, G_BIN_FORMAT(format)->content,
                              pos, G_BIN_FORMAT(format)->length, SRE_BIG);

            if (result)
            {
                entry->info.utf8.bytes = (char *)calloc(length + 1, sizeof(char));
                memcpy(entry->info.utf8.bytes, &G_BIN_FORMAT(format)->content[*pos], length);
                *pos += length;
            }

            break;

        default:
            result = false;
            break;

    }
#endif
    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                index  = indice de l'élément dont la valeur est à recupérer. *
*                expected = type de l'élément à trouver à l'indice donné.     *
*                                                                             *
*  Description : Fournit une entrée donnée du réservoir de constantes.        *
*                                                                             *
*  Retour      : Entrée du réservoir de constantes ou NULL en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const constant_pool_entry *get_java_pool_entry(const GJavaFormat *format, uint16_t index, ConstantPoolTag expected)
{
    const constant_pool_entry *result;      /* Entrée à retourner          */
    constant_pool_entry *entry;             /* Entrée du réservoir visée   */

    result = NULL;

    if (/*index < 0 && FIXME */index <= format->header.pool_len);
    {
        entry = &format->header.pool[index - 1];

        if (entry->tag == expected)
            result = entry;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = description de l'exécutable à consulter.          *
*                index    = indice de l'élément de la table à recupérer.      *
*                expected = type de l'élément à trouver à l'indice donné.     *
*                                                                             *
*  Description : Construit une version humaine de référence.                  *
*                                                                             *
*  Retour      : Référence construite ou NULL en cas de problème.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_reference_from_java_pool(const GJavaFormat *format, uint16_t index, JavaRefType expected)
{
    char *result;                           /* Chaîne humaine à retourner  */
    const constant_pool_entry *entry;       /* Entrée du réservoir visée 1 */
    const constant_pool_entry *subentry;    /* Entrée du réservoir visée 2 */
    const char *tmp;                        /* Copie de chaîne intouchable */

    result = NULL;

    switch (expected)
    {
        case JRT_FIELD:
            entry = get_java_pool_entry(format, index, CONSTANT_FIELD_REF);
            break;
        case JRT_METHOD:
            entry = get_java_pool_entry(format, index, CONSTANT_METHOD_REF);
            break;
        case JRT_INTERFACE_METHOD:
            entry = get_java_pool_entry(format, index, CONSTANT_INTERFACE_METHOD_REF);
            break;
        default:
            entry = NULL;
            break;
    }

    if (entry == NULL)
        goto brfjp_error;

    /* Lieu parent où trouver la référence */

    subentry = get_java_pool_entry(format, entry->info.ref.class_index, CONSTANT_CLASS);

    if (subentry == NULL)
        goto brfjp_error;

    if (!get_java_pool_ut8_string(format, subentry->info.class.name_index, &tmp))
        goto brfjp_error;

    result = strdup(tmp);

    /* Champ proprement dit */

    subentry = get_java_pool_entry(format, entry->info.ref.name_and_type_index, CONSTANT_NAME_AND_TYPE);

    if (subentry == NULL)
        goto brfjp_error;

    if (!get_java_pool_ut8_string(format, subentry->info.name_type.name_index, &tmp))
        goto brfjp_error;

    result = stradd(result, ".");
    result = stradd(result, tmp);

    /* Petites retouches finales */

    result = strrpl(result, "/", ".");
    result = strrpl(result, "<", "&lt;");
    result = strrpl(result, ">", "&gt;");

    return result;

 brfjp_error:

    if (result != NULL)
        free(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                index  = indice de l'élément dont la valeur est à recupérer. *
*                str    = adresse où placer la chaîne de caractères trouvée.  *
*                                                                             *
*  Description : Recherche une chaîne de caractères dans le réservoir.        *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_java_pool_ut8_string(const GJavaFormat *format, uint16_t index, const char **str)
{
    bool result;                            /* Bilan à renvoyer            */
    const constant_pool_entry *entry;       /* Entrée du réservoir visée   */

    entry = get_java_pool_entry(format, index, CONSTANT_UTF8);

    result = (entry != NULL);

    if (result)
        (*str) = entry->info.utf8.bytes;

    return result;

}
