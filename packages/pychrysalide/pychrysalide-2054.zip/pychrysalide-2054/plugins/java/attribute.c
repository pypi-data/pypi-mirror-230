
/* Chrysalide - Outil d'analyse de fichiers binaires
 * attribute.c - manipulation des attributs Java
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


#include "attribute.h"


#include <malloc.h>
#include <string.h>


#include "java-int.h"
#include "pool.h"
#include "../../common/endianness.h"
#include "../../panel/log.h"



#define _(str) str



/* Charge les propriétés d'un attribut quelconque. */
bool load_java_attribute(java_format *, java_attribute *, off_t *);

/* Décharge les propriétés d'un attribut quelconque. */
void unload_java_attribute(java_format *, java_attribute *);

/* Charge les propriétés d'un attribut de valeur constante. */
bool load_java_const_value_attribute(java_format *, const_value_attrib *, off_t *);

/* Charge les propriétés d'un attribut de code. */
bool load_java_code_attribute(java_format *, code_attrib *, off_t *);

/* Décharge les propriétés d'un attribut de code. */
void unload_java_code_attribute(java_format *, code_attrib *);

/*Charge les propriétés d'un attribut d'exceptions lançables. */
bool load_java_exceptions_attribute(java_format *, exceptions_attrib *, off_t *);

/* Décharge les propriétés d'un attribut d'exceptions lançables. */
void unload_java_exceptions_attribute(java_format *, exceptions_attrib *);

/* Charge les propriétés d'un attribut de classes internes. */
bool load_java_inner_classes_attribute(java_format *, inner_classes_attrib *, off_t *);

/* Décharge les propriétés d'un attribut de classes internes. */
void unload_java_inner_classes_attribute(java_format *, inner_classes_attrib *);

/* Charge les propriétés d'un attribut de fichier source. */
bool load_java_source_file_attribute(java_format *, source_file_attrib *, off_t *);

/* Charge les propriétés d'un attribut de correspondance. */
bool load_java_line_number_attribute(java_format *, line_number_attrib *, off_t *);

/* Décharge les propriétés d'un attribut de correspondance. */
void unload_java_line_number_attribute(java_format *, line_number_attrib *);

/* Charge les propriétés d'un attribut de variables locales. */
bool load_java_local_variables_attribute(java_format *, local_variables_attrib *, off_t *);

/* Décharge les propriétés d'un attribut de variables locales. */
void unload_java_local_variables_attribute(java_format *, local_variables_attrib *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format     = description de l'exécutable à compléter.        *
*                pos        = point de lecture à faire évoluer. [OUT]         *
*                attributes = tableau des attributs chargés. [OUT]            *
*                count      = nombre d'éléments à charger. [OUT]              *
*                                                                             *
*  Description : Charge les attribus d'un élément d'un binaire Java.          *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_attributes(java_format *format, off_t *pos, java_attribute **attributes, uint16_t *count)
{
    bool result;                            /* Bilan à remonter            */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(count, EXE_FORMAT(format)->content, pos,
                      EXE_FORMAT(format)->length, SRE_BIG);

    if (!result) return false;

    if (*count > 0)
    {
        *attributes = (java_attribute *)calloc(*count, sizeof(java_attribute));

        for (i = 0; i < *count && result; i++)
            result = load_java_attribute(format, &(*attributes)[i], pos);

        if (!result)
            unload_java_attributes(format, *attributes, *count);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format     = description de l'exécutable à libérer.          *
*                attributes = tableau des attributs à décharger.              *
*                count      = nombre d'éléments à décharger.                  *
*                                                                             *
*  Description : Décharge les attribus d'un élément d'un binaire Java.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_attributes(java_format *format, java_attribute *attributes, uint16_t count)
{
    uint16_t i;                             /* Boucle de parcours          */

    for (i = 0; i < count; i++)
        unload_java_attribute(format, &attributes[i]);

    free(attributes);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut quelconque.              *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_attribute(java_format *format, java_attribute *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t index;                         /* Indice du nom assimilé      */
    const char *name;                       /* Version humainement lisible */
    uint32_t attrib_length;                 /* Taille de la charge utile   */
    off_t saved_pos;                        /* Conservation de la position */

    result = read_u16(&index, EXE_FORMAT(format)->content, pos,
                      EXE_FORMAT(format)->length, SRE_BIG);

    result &= get_java_pool_ut8_string(format, index, &name);

    if (result)
    {
        result = read_u32(&attrib_length, EXE_FORMAT(format)->content,
                          pos, EXE_FORMAT(format)->length, SRE_BIG);

        saved_pos = *pos;

        if (result && strcmp("ConstantValue", name) == 0)
        {
            attrib->type = JAT_CONSTANT_VALUE;
            result = load_java_const_value_attribute(format, &attrib->info.const_value, pos);
        }

        else if (result && strcmp("Code", name) == 0)
        {
            attrib->type = JAT_CODE;
            result = load_java_code_attribute(format, &attrib->info.code, pos);
        }

        else if (result && strcmp("Exceptions", name) == 0)
        {
            attrib->type = JAT_EXCEPTIONS;
            result = load_java_exceptions_attribute(format, &attrib->info.exceptions, pos);
        }

        else if (result && strcmp("InnerClasses", name) == 0)
        {
            attrib->type = JAT_INNER_CLASSES;
            result = load_java_inner_classes_attribute(format, &attrib->info.inner_classes, pos);
        }

        else if (result && strcmp("Synthetic", name) == 0)
            attrib->type = JAT_SYNTHETIC;

        else if (result && strcmp("SourceFile", name) == 0)
        {
            attrib->type = JAT_LINE_NUMBER;
            result = load_java_source_file_attribute(format, &attrib->info.source_file, pos);
        }

        else if (result && strcmp("LineNumberTable", name) == 0)
        {
            attrib->type = JAT_SOURCE_FILE;
            result = load_java_line_number_attribute(format, &attrib->info.line_number, pos);
        }

        else if (result && strcmp("LocalVariableTable", name) == 0)
        {
            attrib->type = JAT_LOCAL_VARIABLES;
            result = load_java_local_variables_attribute(format, &attrib->info.local_vars, pos);
        }

        else if (result && strcmp("Deprecated", name) == 0)
            attrib->type = JAT_DEPRECATED;

        else if (result)
        {
            result = false;
            log_variadic_message(LMT_BAD_BINARY, _("Attribute name not supported: '%s'"), name);
        }

        if (result && attrib_length != (*pos - saved_pos))
            log_variadic_message(LMT_BAD_BINARY, _("Size indication of the attribute '%s' not verified: %d vs %d"),
                                 name, attrib_length, *pos - saved_pos);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à libérer.                                  *
*                                                                             *
*  Description : Décharge les propriétés d'un attribut quelconque.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_attribute(java_format *format, java_attribute *attrib)
{
    switch (attrib->type)
    {
        case JAT_NONE:
            break;

        case JAT_CONSTANT_VALUE:
            break;

        case JAT_CODE:
            unload_java_code_attribute(format, &attrib->info.code);
            break;

        case JAT_EXCEPTIONS:
            unload_java_exceptions_attribute(format, &attrib->info.exceptions);
            break;

        case JAT_INNER_CLASSES:
            unload_java_inner_classes_attribute(format, &attrib->info.inner_classes);
            break;

        case JAT_SYNTHETIC:
            break;

        case JAT_SOURCE_FILE:
            break;

        case JAT_LINE_NUMBER:
            unload_java_line_number_attribute(format, &attrib->info.line_number);
            break;

        case JAT_LOCAL_VARIABLES:
            unload_java_local_variables_attribute(format, &attrib->info.local_vars);
            break;

        case JAT_DEPRECATED:
            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut de valeur constante.     *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_const_value_attribute(java_format *format, const_value_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = read_u16(&attrib->const_value_index, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut de code.                 *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_code_attribute(java_format *format, code_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&attrib->max_stack, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= read_u16(&attrib->max_locals, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= read_u32(&attrib->code_length, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);

    result &= ((*pos + attrib->code_length) <= EXE_FORMAT(format)->length);

    if (result)
    {
        attrib->content = *pos;
        *pos += attrib->code_length;
    }

    result &= read_u16(&attrib->exceptions_count, EXE_FORMAT(format)->content,
                       pos, EXE_FORMAT(format)->length, SRE_BIG);

    if (result && attrib->exceptions_count > 0)
    {
        attrib->exceptions = (code_exception *)calloc(attrib->exceptions_count, sizeof(code_exception));

        for (i = 0; i < attrib->exceptions_count && result; i++)
        {
            result &= read_u16(&attrib->exceptions[i].start_pc, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->exceptions[i].end_pc, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->exceptions[i].handler_pc, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->exceptions[i].catch_type, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

        }

    }

    result &= load_java_attributes(format, pos, &attrib->attributes, &attrib->attributes_count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à libérer de la mémoire.                    *
*                                                                             *
*  Description : Décharge les propriétés d'un attribut de code.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_code_attribute(java_format *format, code_attrib *attrib)
{
    if (attrib->exceptions != NULL)
        free(attrib->exceptions);

    if (attrib->attributes != NULL)
        unload_java_attributes(format, attrib->attributes, attrib->attributes_count);

}



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut d'exceptions lançables.  *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_exceptions_attribute(java_format *format, exceptions_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&attrib->throw_count, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    if (result && attrib->throw_count > 0)
    {
        attrib->throw = (uint16_t *)calloc(attrib->throw_count, sizeof(uint16_t));

        for (i = 0; i < attrib->throw_count && result; i++)
            result &= read_u16(&attrib->throw[i], EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à libérer de la mémoire.                    *
*                                                                             *
*  Description : Décharge les propriétés d'un attribut d'exceptions lançables.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_exceptions_attribute(java_format *format, exceptions_attrib *attrib)
{
    if (attrib->throw != NULL)
        free(attrib->throw);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut de classes internes.     *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_inner_classes_attribute(java_format *format, inner_classes_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&attrib->classes_count, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    if (result && attrib->classes_count > 0)
    {
        attrib->classes = (inner_class *)calloc(attrib->classes_count, sizeof(inner_class));

        for (i = 0; i < attrib->classes_count && result; i++)
        {
            result &= read_u16(&attrib->classes[i].inner_class_info_index, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->classes[i].outer_class_info_index, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->classes[i].inner_name_index, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16((uint16_t *)&attrib->classes[i].access, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à libérer de la mémoire.                    *
*                                                                             *
*  Description : Décharge les propriétés d'un attribut de classes internes.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_inner_classes_attribute(java_format *format, inner_classes_attrib *attrib)
{
    if (attrib->classes != NULL)
        free(attrib->classes);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut de fichier source.       *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_source_file_attribute(java_format *format, source_file_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = read_u16(&attrib->source_file_index, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut de correspondance.       *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_line_number_attribute(java_format *format, line_number_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&attrib->lines_count, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    if (result && attrib->lines_count > 0)
    {
        attrib->lines = (pc_and_line *)calloc(attrib->lines_count, sizeof(pc_and_line));

        for (i = 0; i < attrib->lines_count && result; i++)
        {
            result &= read_u16(&attrib->lines[i].start_pc, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->lines[i].number, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à libérer de la mémoire.                    *
*                                                                             *
*  Description : Décharge les propriétés d'un attribut de correspondance.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_line_number_attribute(java_format *format, line_number_attrib *attrib)
{
    if (attrib->lines != NULL)
        free(attrib->lines);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à spécifier. [OUT]                          *
*                pos    = point de lecture à faire évoluer. [OUT]             *
*                                                                             *
*  Description : Charge les propriétés d'un attribut de variables locales.    *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_java_local_variables_attribute(java_format *format, local_variables_attrib *attrib, off_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */

    result = read_u16(&attrib->vars_count, EXE_FORMAT(format)->content,
                      pos, EXE_FORMAT(format)->length, SRE_BIG);

    if (result && attrib->vars_count > 0)
    {
        attrib->vars = (local_variable *)calloc(attrib->vars_count, sizeof(local_variable));

        for (i = 0; i < attrib->vars_count && result; i++)
        {
            result &= read_u16(&attrib->vars[i].start_pc, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->vars[i].length, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->vars[i].name_index, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->vars[i].descriptor_index, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

            result &= read_u16(&attrib->vars[i].index, EXE_FORMAT(format)->content,
                               pos, EXE_FORMAT(format)->length, SRE_BIG);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                attrib = élément à libérer de la mémoire.                    *
*                                                                             *
*  Description : Décharge les propriétés d'un attribut de variables locales.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java_local_variables_attribute(java_format *format, local_variables_attrib *attrib)
{
    if (attrib->vars != NULL)
        free(attrib->vars);

}
