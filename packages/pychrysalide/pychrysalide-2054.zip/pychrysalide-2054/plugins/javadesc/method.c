
/* Chrysalide - Outil d'analyse de fichiers binaires
 * shorty.c - décodage de routines pour Java
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


#include "field.h"



/* Extrait un type particulier dans un décodage Java. */
static GDataType *jmd_method_return_type(input_buffer *);



/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                                                                             *
*  Description : Extrait un type particulier dans un décodage Java.           *
*                                                                             *
*  Retour      : Nouveau type mis en place ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *jmd_method_return_type(input_buffer *buffer)
{
    GDataType *result;                      /* Type à retourner            */
    char ahead;                             /* Caractère déterminant lu    */

    /**
     * La règle traitée est la suivante :
     *
     *    ReturnDescriptor:
     *      FieldType
     *      V
     *
     */

    ahead = peek_input_buffer_char(buffer);

    if (ahead == 'V')
    {
        advance_input_buffer(buffer, 1);
        result = g_basic_type_new(BTP_VOID);
    }

    else
        result = jtd_field_descriptor(buffer);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                                                                             *
*  Description : Extrait un routine particulière depuis un codage Java.       *
*                                                                             *
*  Retour      : Nouveau type mis en place ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *jmd_method_descriptor(input_buffer *buffer)
{
    GBinRoutine *result;                    /* Type à retourner            */
    char ahead;                             /* Caractère déterminant lu    */
    GDataType *type;                        /* Description de type obtenue */
    GBinVariable *var;                      /* Argument de routine         */

    /**
     * La règle traitée est la suivante :
     *
     *    MethodDescriptor:
     *    ( {ParameterDescriptor} ) ReturnDescriptor
     *
     */

    if (!check_input_buffer_char(buffer, '('))
        goto exit;

    result = g_binary_routine_new();

    /* Arguments */

    for (ahead = peek_input_buffer_char(buffer);
         ahead != ')';
         ahead = peek_input_buffer_char(buffer))
    {
        type = jtd_field_descriptor(buffer);

        if (type == NULL)
            goto error;

        else
        {
            var = g_binary_variable_new(type);
            g_binary_routine_add_arg(result, var);
        }

    }

    if (!check_input_buffer_char(buffer, ')'))
        goto error;

    /* Retour */

    type = jmd_method_return_type(buffer);

    if (type == NULL)
        goto error;

    else
        g_binary_routine_set_return_type(result, type);

    return result;

 error:

    g_object_unref(G_OBJECT(result));

 exit:

    return NULL;

}
