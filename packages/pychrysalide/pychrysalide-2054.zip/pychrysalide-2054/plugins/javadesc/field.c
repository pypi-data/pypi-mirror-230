
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.c - décodage de types pour Java
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
#include <string.h>


#include <analysis/types/basic.h>
#include <analysis/types/cse.h>
#include <analysis/types/encaps.h>



/* Extrait un type particulier dans un décodage Java. */
static GDataType *jtd_object_type_descriptor(input_buffer *);

/* Extrait un type particulier dans un décodage Java. */
static GDataType *jtd_array_type_descriptor(input_buffer *);

/* Extrait un type particulier dans un décodage Java. */
static GDataType *jtd_base_type_descriptor(input_buffer *, char);



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

static GDataType *jtd_object_type_descriptor(input_buffer *buffer)
{
    GDataType *result;                      /* Classe à retourner          */
    char *name;                             /* Désignation récupérée       */
    size_t len;                             /* Taille de cette désignation */
    char next;                              /* Prochain caractère obtenu   */
    GDataType *root;                        /* Espace de noms racine       */
    GDataType *ns;                          /* Espace de noms à attribuer  */
    GDataType *parent;                      /* Espace de noms parent       */
    bool status;                            /* Bilan de rattachement       */

    result = NULL;

    name = NULL;
    len = 0;

    do
    {
        next = get_input_buffer_next_char(buffer);

        if (next == ';')
            break;

        else if (next == '/' || next == '$')
        {
            /**
             * Il faut obligatoirement avoir déjà traité un nom de paquet !
             */
            if (len == 0)
                break;

            name = realloc(name, ++len * sizeof(char));

            name[len - 1] = '\0';

            root = g_class_enum_type_new(CEK_CLASS, name);

            /**
             * Pour éviter les fuites si aucun paquet n'est présent...
             */
            name = NULL;

            result = jtd_object_type_descriptor(buffer);

            if (result == NULL)
                g_object_unref(G_OBJECT(root));

            else
            {
                ns = g_data_type_get_namespace(result);

                if (ns == NULL)
                    status = g_data_type_set_namespace(result, root, ".");

                else
                {
                    while ((parent = g_data_type_get_namespace(ns)) != NULL)
                    {
                        g_object_unref(G_OBJECT(ns));
                        ns = parent;
                    }

                    status = g_data_type_set_namespace(ns, root, ".");

                    g_object_unref(G_OBJECT(ns));

                }

                g_object_unref(G_OBJECT(root));

                if (!status)
                {
                    g_clear_object(&result);
                    goto error;
                }

            }

            break;

        }

        else if (next != '\0')
        {
            name = realloc(name, ++len * sizeof(char));

            name[len - 1] = next;

        }

        else
        {
            if (name != NULL)
            {
                free(name);
                name = NULL;
            }

            break;

        }

    }
    while (1);

    if (name != NULL)
        result = g_class_enum_type_new(CEK_CLASS, name);

 error:

    return result;

}


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

static GDataType *jtd_array_type_descriptor(input_buffer *buffer)
{
    GDataType *result;                      /* Type à retourner            */
    size_t dim;                             /* Dimension éventuelle        */
    char ahead;                             /* Caractère déterminant lu    */
    GDataType *descriptor;                  /* (Sous-)type à charger       */

    /**
     * La règle traitée est la suivante :
     *
     *    ArrayType:
     *      [ ComponentType
     *
     */


    dim = 0;

    do
    {
        dim++;

        ahead = peek_input_buffer_char(buffer);

        if (ahead == '[')
            advance_input_buffer(buffer, 1);
        else
            break;

    }
    while (1);

    descriptor = jtd_field_descriptor(buffer);

    if (descriptor == NULL)
        result = NULL;

    else
    {
        result = g_encapsulated_type_new(ECT_ARRAY, descriptor);

        g_encapsulated_type_set_dimension(G_ENCAPSULATED_TYPE(result), dim);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                ahead  = caractère déjà dépilé de ces données.               *
*                                                                             *
*  Description : Extrait un type particulier dans un décodage Java.           *
*                                                                             *
*  Retour      : Nouveau type mis en place ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *jtd_base_type_descriptor(input_buffer *buffer, char ahead)
{
    GDataType *result;                      /* Type à retourner            */

    /**
     * La règle traitée est la suivante :
     *
     *    BaseType:
     *      B
     *      C
     *      D
     *      F
     *      I
     *      J
     *      S
     *      Z
     *
     */

    switch (ahead)
    {
        case 'B':
            result = g_basic_type_new(BTP_SCHAR);
            break;

        case 'C':
            result = g_basic_type_new(BTP_UCHAR);
            break;

        case 'D':
            result = g_basic_type_new(BTP_DOUBLE);
            break;

        case 'F':
            result = g_basic_type_new(BTP_FLOAT);
            break;

        case 'I':
            result = g_basic_type_new(BTP_INT);
            break;

        case 'J':
            result = g_basic_type_new(BTP_LONG);
            break;

        case 'S':
            result = g_basic_type_new(BTP_SHORT);
            break;

        case 'Z':
            result = g_basic_type_new(BTP_BOOL);
            break;

        default:
            result = NULL;
            break;

    }

    return result;

}


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

GDataType *jtd_field_descriptor(input_buffer *buffer)
{
    GDataType *result;                      /* Type à retourner            */
    char ahead;                             /* Caractère déterminant lu    */

    /**
     * La règle traitée est la suivante :
     *
     *    FieldType:
     *      BaseType
     *      ObjectType
     *      ArrayType
     *
     * Cf. § 4.3.2. Field Descriptors
     */

    ahead = get_input_buffer_next_char(buffer);

    if (ahead == 'L')
        result = jtd_object_type_descriptor(buffer);

    else if (ahead == '[')
        result = jtd_array_type_descriptor(buffer);

    else
        result = jtd_base_type_descriptor(buffer, ahead);

    return result;

}
