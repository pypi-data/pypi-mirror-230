
/* Chrysalide - Outil d'analyse de fichiers binaires
 * shorty.c - décodage de routines pour Dex
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


#include "shorty.h"


#include <analysis/types/basic.h>
#include <analysis/types/cse.h>



/* Extrait un type particulier dans un décodage Dex. */
static GDataType *dsd_shorty_return_type(input_buffer *);

/* Extrait un type particulier dans un décodage Dex. */
static GDataType *dsd_shorty_field_type(input_buffer *, char);



/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                                                                             *
*  Description : Extrait un routine particulière depuis un codage Dex.        *
*                                                                             *
*  Retour      : Nouveau type mis en place ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *dsd_shorty_descriptor(input_buffer *buffer)
{
    GBinRoutine *result;                    /* Type à retourner            */
    GDataType *type;                        /* Description de type obtenue */
    char ahead;                             /* Caractère déterminant lu    */
    GBinVariable *var;                      /* Argument de routine         */

    /**
     * La règle traitée est la suivante :
     *
     *    ShortyDescriptor →
     *        ShortyReturnType (ShortyFieldType)*
     *
     */

    result = g_binary_routine_new();

    /* Retour */

    type = dsd_shorty_return_type(buffer);

    if (type == NULL)
        goto dsd_error;

    else
        g_binary_routine_set_return_type(result, type);

    /* Arguments */

    for (ahead = get_input_buffer_next_char(buffer);
         ahead != '\0';
         ahead = get_input_buffer_next_char(buffer))
    {
        type = dsd_shorty_field_type(buffer, ahead);

        if (type == NULL)
            goto dsd_error;

        else
        {
            var = g_binary_variable_new(type);
            g_binary_routine_add_arg(result, var);
        }

    }

    return result;

 dsd_error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                                                                             *
*  Description : Extrait un type particulier dans un décodage Dex.            *
*                                                                             *
*  Retour      : Nouveau type mis en place ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *dsd_shorty_return_type(input_buffer *buffer)
{
    GDataType *result;                      /* Type à retourner            */
    char ahead;                             /* Caractère déterminant lu    */

    /**
     * La règle traitée est la suivante :
     *
     *    ShortyReturnType →
     *        'V'
     *    |   ShortyFieldType
     *
     */

    ahead = get_input_buffer_next_char(buffer);

    if (ahead == 'V')
        result = g_basic_type_new(BTP_VOID);

    else
        result = dsd_shorty_field_type(buffer, ahead);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                ahead  = caractère déjà dépilé de ces données.               *
*                                                                             *
*  Description : Extrait un type particulier dans un décodage Dex.            *
*                                                                             *
*  Retour      : Nouveau type mis en place ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *dsd_shorty_field_type(input_buffer *buffer, char ahead)
{
    GDataType *result;                      /* Type à retourner            */

    /**
     * La règle traitée est la suivante :
     *
     *    ShortyFieldType →
     *        'Z'
     *    |   'B'
     *    |   'S'
     *    |   'C'
     *    |   'I'
     *    |   'J'
     *    |   'F'
     *    |   'D'
     *    |   'L'
     *
     */

    switch (ahead)
    {
        case 'Z':
            result = g_basic_type_new(BTP_BOOL);
            break;

        case 'B':
            result = g_basic_type_new(BTP_UCHAR);
            break;

        case 'S':
            result = g_basic_type_new(BTP_SHORT);
            break;

        case 'C':
            result = g_basic_type_new(BTP_CHAR);
            break;

        case 'I':
            result = g_basic_type_new(BTP_INT);
            break;

        case 'J':
            result = g_basic_type_new(BTP_LONG);
            break;

        case 'F':
            result = g_basic_type_new(BTP_FLOAT);
            break;

        case 'D':
            result = g_basic_type_new(BTP_DOUBLE);
            break;

        case 'L':
            result = g_class_enum_type_new(CEK_CLASS, NULL);
            break;

        default:
            result = NULL;
            break;

    }

    return result;

}
