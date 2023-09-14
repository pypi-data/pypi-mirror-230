
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.c - décodage de types pour Dex
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


#include "type.h"


#include <string.h>


#include <analysis/types/basic.h>
#include <analysis/types/cse.h>
#include <analysis/types/encaps.h>


#include "simple.h"



/* Extrait un type particulier dans un décodage Dex. */
static GDataType *dtd_full_class_name(input_buffer *);

/* Extrait un type particulier dans un décodage Dex. */
static GDataType *dtd_field_type_descriptor(input_buffer *, char);

/* Extrait un type particulier dans un décodage Dex. */
static GDataType *dtd_non_array_field_type_descriptor(input_buffer *, char);



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

static GDataType *dtd_full_class_name(input_buffer *buffer)
{
    GDataType *result;                      /* Classe à retourner          */
    char *name;                             /* Désignation récupérée       */
    size_t saved;                           /* Point de sauvegarde         */
    char next;                              /* Prochain caractère obtenu   */
    GDataType *ns;                          /* Espace de nom à attribuer   */
    bool status;                            /* Bilan de rattachement       */

    /**
     * Les règles traitées sont les suivantes :
     *
     *    FullClassName →
     *        OptionalPackagePrefix SimpleName
     *    OptionalPackagePrefix →
     *        (SimpleName '/')*
     *
     */

    /* Premier étage... */

    name = dcd_simple_name(buffer);

    if (name == NULL)
    {
        result = NULL;
        goto dfcn_exit;
    }

    else
        result = g_class_enum_type_new(CEK_CLASS, name);

    /* Eventuels autres étages précédents */

    do
    {
        save_input_buffer_pos(buffer, &saved);

        next = get_input_buffer_next_char(buffer);

        if (next != '/')
        {
            restore_input_buffer_pos(buffer, saved);
            goto dfcn_exit;
        }

        name = dcd_simple_name(buffer);

        if (name == NULL)
        {
            restore_input_buffer_pos(buffer, saved);
            goto dfcn_exit;
        }

        ns = result;

        result = g_class_enum_type_new(CEK_CLASS, name);

        status = g_data_type_set_namespace(result, ns, ".");

        g_object_unref(G_OBJECT(ns));

        if (!status)
        {
            g_clear_object(&result);
            break;
        }

    }
    while (1);

 dfcn_exit:

 return result;

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

GDataType *dtd_type_descriptor(input_buffer *buffer)
{
    GDataType *result;                      /* Type à retourner            */
    char ahead;                             /* Caractère déterminant lu    */

    /**
     * La règle traitée est la suivante :
     *
     *    TypeDescriptor →
     *        'V'
     *    |   FieldTypeDescriptor
     *
     */

    ahead = get_input_buffer_next_char(buffer);

    if (ahead == 'V')
        result = g_basic_type_new(BTP_VOID);

    else
        result = dtd_field_type_descriptor(buffer, ahead);

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

static GDataType *dtd_field_type_descriptor(input_buffer *buffer, char ahead)
{
    GDataType *result;                      /* Type à retourner            */
    size_t dim;                             /* Dimension éventuelle        */
    GDataType *descriptor;                  /* (Sous-)type à charger       */

    /**
     * La règle traitée est la suivante :
     *
     *    FieldTypeDescriptor →
     *        NonArrayFieldTypeDescriptor
     *    |   ('[' * 1…255) NonArrayFieldTypeDescriptor
     *
     */

    dim = 0;

    while (ahead == '[')
    {
        dim++;
        ahead = get_input_buffer_next_char(buffer);
    }

    descriptor = dtd_non_array_field_type_descriptor(buffer, ahead);

    if (descriptor == NULL)
        result = NULL;

    else
    {
        if (dim == 0)
            result = descriptor;

        else
        {
            result = g_encapsulated_type_new(ECT_ARRAY, descriptor);

            g_encapsulated_type_set_dimension(G_ENCAPSULATED_TYPE(result), dim);

        }

    }

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

static GDataType *dtd_non_array_field_type_descriptor(input_buffer *buffer, char ahead)
{
    GDataType *result;                      /* Type à retourner            */
    char check;                             /* Vérification de conformité  */

    /**
     * La règle traitée est la suivante :
     *
     *    NonArrayFieldTypeDescriptor →
     *        'Z'
     *    |   'B'
     *    |   'S'
     *    |   'C'
     *    |   'I'
     *    |   'J'
     *    |   'F'
     *    |   'D'
     *    |   'L' FullClassName ';'
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

            result = dtd_full_class_name(buffer);

            if (result != NULL)
            {
                check = get_input_buffer_next_char(buffer);

                if (check != ';')
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

            break;

        default:
            result = NULL;
            break;

    }

    return result;

}
