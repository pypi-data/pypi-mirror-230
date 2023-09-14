
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.c - conversion de structures Dex en objets Python
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "translate.h"


#include <assert.h>


#include <plugins/pychrysalide/struct.h>


#include "../dex_def.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des informations de type Dex en Python.              *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_type_id_to_python(const type_id_item *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ENCODED_TYPE_PROP(_f)                     \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_ENCODED_TYPE_PROP(descriptor_idx);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des informations de type Dex en Python.              *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_type_item_to_python(const type_item *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ENCODED_TYPE_PROP(_f)                     \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_ENCODED_TYPE_PROP(type_idx);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des informations de champ Dex en Python.             *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_field_id_to_python(const field_id_item *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ENCODED_FIELD_PROP(_f)                    \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_ENCODED_FIELD_PROP(class_idx);
    TRANSLATE_ENCODED_FIELD_PROP(type_idx);
    TRANSLATE_ENCODED_FIELD_PROP(name_idx);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des informations de champ de classe Dex en Python.   *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_field_info_to_python(const encoded_field *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ENCODED_FIELD_PROP(_f)                    \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_ENCODED_FIELD_PROP(field_idx_diff);
    TRANSLATE_ENCODED_FIELD_PROP(access_flags);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des identifiants de prototype Dex en Python.         *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_proto_id_to_python(const proto_id_item *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ID_PROTO_PROP(_f)                         \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto failed;                          \
    }                                                       \
    while (0);

    TRANSLATE_ID_PROTO_PROP(shorty_idx);
    TRANSLATE_ID_PROTO_PROP(return_type_idx);
    TRANSLATE_ID_PROTO_PROP(parameters_off);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des identifiants de méthode Dex en Python.           *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_method_id_to_python(const method_id_item *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ID_METHOD_PROP(_f)                        \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_ID_METHOD_PROP(class_idx);
    TRANSLATE_ID_METHOD_PROP(proto_idx);
    TRANSLATE_ID_METHOD_PROP(name_idx);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des informations de méthode Dex en Python.           *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_method_info_to_python(const encoded_method *info)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_ENCODED_METHOD_PROP(_f)                   \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(info->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_ENCODED_METHOD_PROP(method_idx_diff);
    TRANSLATE_ENCODED_METHOD_PROP(access_flags);
    TRANSLATE_ENCODED_METHOD_PROP(code_off);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des informations de corps de méthode Dex en Python.  *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_method_body_to_python(const code_item *body)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_CODE_ITEM_PROP(_f)                        \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(body->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_CODE_ITEM_PROP(registers_size);
    TRANSLATE_CODE_ITEM_PROP(ins_size);
    TRANSLATE_CODE_ITEM_PROP(outs_size);
    TRANSLATE_CODE_ITEM_PROP(tries_size);
    TRANSLATE_CODE_ITEM_PROP(debug_info_off);
    TRANSLATE_CODE_ITEM_PROP(insns_size);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit une définition de classe Dex en Python.              *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_class_definition_to_python(const class_def_item *item)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_CLASS_DEF_PROP(_f)                        \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(item->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_CLASS_DEF_PROP(class_idx);
    TRANSLATE_CLASS_DEF_PROP(access_flags);
    TRANSLATE_CLASS_DEF_PROP(superclass_idx);
    TRANSLATE_CLASS_DEF_PROP(interfaces_off);
    TRANSLATE_CLASS_DEF_PROP(source_file_idx);
    TRANSLATE_CLASS_DEF_PROP(annotations_off);
    TRANSLATE_CLASS_DEF_PROP(class_data_off);
    TRANSLATE_CLASS_DEF_PROP(static_values_off);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = ensemble d'informations Dex à décrire en Python.      *
*                                                                             *
*  Description : Traduit des données de classe Dex en Python.                 *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_dex_class_data_to_python(const class_data_item *item)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_CLASS_DATA_PROP(_f)                       \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(item->_f);     \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto tdcdtp_failed;                   \
    }                                                       \
    while (0);

    TRANSLATE_CLASS_DATA_PROP(static_fields_size);
    TRANSLATE_CLASS_DATA_PROP(instance_fields_size);
    TRANSLATE_CLASS_DATA_PROP(direct_methods_size);
    TRANSLATE_CLASS_DATA_PROP(virtual_methods_size);

    return result;

 tdcdtp_failed:

    Py_DECREF(result);

    return NULL;

}
