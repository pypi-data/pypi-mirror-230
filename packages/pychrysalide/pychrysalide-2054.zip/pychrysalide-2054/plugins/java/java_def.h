
/* Chrysalide - Outil d'analyse de fichiers binaires
 * java_def.h - liste des structures et constantes utilisées par le format Java
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


#ifndef _FORMAT_JAVA_JAVA_DEF_H
#define _FORMAT_JAVA_JAVA_DEF_H


#include <stdint.h>



/* Description des attributs Java */
typedef struct _java_attribute java_attribute;



/* ----------------------- ELEMENTS DU RESERVOIR A CONSTANTES ----------------------- */


/* Types de données dans le réservoir (§4.4) */
typedef enum _ConstantPoolTag
{
    CONSTANT_EMPTY                  =  0,   /* Non initialisé ou sur 2     */

    CONSTANT_CLASS                  =  7,   /* Classe ou interface         */
    CONSTANT_FIELD_REF              =  9,   /* Champ ou méthode            */
    CONSTANT_METHOD_REF             = 10,   /* Champ ou méthode            */
    CONSTANT_INTERFACE_METHOD_REF   = 11,   /* Champ ou méthode            */
    CONSTANT_STRING                 =  8,   /* Chaîne constante            */
    CONSTANT_INTEGER                =  3,   /* Valeur entière              */
    CONSTANT_FLOAT                  =  4,   /* Valeur flottante            */
    CONSTANT_LONG                   =  5,   /* Valeur longue               */
    CONSTANT_DOUBLE                 =  6,   /* Valeur double               */
    CONSTANT_NAME_AND_TYPE          = 12,   /* Prototype complet           */
    CONSTANT_UTF8                   =  1    /* Chaîne codée en UTF8        */

} ConstantPoolTag;


/* Représentation d'une classe ou d'une interface */
typedef struct _class_info
{
    uint16_t name_index;                    /* Indice pour le nom          */

} class_info;

/* Représentation d'un champ ou d'une méthode */
typedef struct _ref_info
{
    uint16_t class_index;                   /* Indice de la classe         */
    uint16_t name_and_type_index;           /* Prototype associé           */

} ref_info;

/* Représentation d'une chaîne constante */
typedef struct _string_info
{
    uint16_t string_index;                  /* Indice de la valeur UTF8    */

} string_info;

/* Représentation d'une valeur 'int' */
typedef struct _integer_info
{
    uint32_t val;                           /* Valeur au format 'int'      */

} integer_info;

/* Représentation d'une valeur 'float' */
typedef struct _float_info
{
    float val;                              /* Valeur au format 'float'    */

} float_info;

/* Représentation d'une valeur 'long' */
typedef struct _long_info
{
    long val;                               /* Valeur au format 'long'     */

} long_info;

/* Représentation d'une valeur 'double' */
typedef struct _double_info
{
    double val;                             /* Valeur au format 'double'   */

} double_info;

/* Représentation brève d'un champ ou d'une méthode */
typedef struct _name_and_type_info
{
    uint16_t name_index;                   /* Indice du nom correspondant */
    uint16_t descriptor_index;             /* Prototype associé           */

} name_and_type_info;

/* Représentation d'une chaîne codée en UTF8 */
typedef struct _utf8_info
{
    char *bytes;                            /* Valeur de la chaîne         */

} utf8_info;


/* Entrée du réservoir */
typedef struct _constant_pool_entry
{
    ConstantPoolTag tag;                    /* Type d'entrée présente      */

    union
    {
        class_info class;
        ref_info ref;
        string_info string;
        integer_info int_val;
        float_info float_val;
        long_info long_val;
        double_info double_val;
        name_and_type_info name_type;
        utf8_info utf8;

    } info;                                 /* Infos portées par l'entrée  */

} constant_pool_entry;



/* ------------------------ ATTRIBUTS POUR DES ELEMENTS JAVA ------------------------ */


/* Types des attributs reconnus */
typedef enum _JavaAttributeType
{
    JAT_NONE                = 0,            /* Attribu non chargé          */

    JAT_CONSTANT_VALUE,                     /* Valeur constante            */
    JAT_CODE,                               /* Code exécutable             */
    JAT_EXCEPTIONS,                         /* Exceptions remontables      */
    JAT_INNER_CLASSES,                      /* Classes internes            */
    JAT_SYNTHETIC,                          /* Membre non présent          */
    JAT_SOURCE_FILE,                        /* Fichier source du code      */
    JAT_LINE_NUMBER,                        /* Correspondances de débogage */
    JAT_LOCAL_VARIABLES,                    /* Variable(s) locale(s)       */
    JAT_DEPRECATED                          /* Elément vieillot à oublier  */

} JavaAttributeType;

/* Représentation d'un attribut à valeur constante (§4.7.2) */
typedef struct _const_value_attrib
{
    uint16_t const_value_index;             /* Indice dans le réservoir    */

} const_value_attrib;

/* Représentation d'un attribut de code (§4.7.3) */

typedef struct _code_exception
{
    uint16_t start_pc;                      /* Début de la zone couverte   */
    uint16_t end_pc;                        /* Fin de la zone couverte     */
    uint16_t handler_pc;                    /* Début du gestionnaire       */
    uint16_t catch_type;                    /* Indice du type d'exception  */

} code_exception;

typedef struct _code_attrib
{
    uint16_t max_stack;                     /* Taille maximale de la pile  */
    uint16_t max_locals;                    /* Nombre de variables (!)     */
    uint32_t code_length;                   /* Taille du code référencé    */

    off_t content;                          /* Début du code exécutable    */

    code_exception *exceptions;             /* Exceptions gérées           */
    uint16_t exceptions_count;              /* Nombre de ces exceptions    */

    java_attribute *attributes;             /* Attributs liés au code      */
    uint16_t attributes_count;              /* Nombre de ces attributs     */

} code_attrib;

/* Représentation d'un attribut fixant les exceptions remontables (§4.7.4) */

typedef struct _exceptions_attrib
{
    uint16_t *throw;                        /* Exceptions remontées        */
    uint16_t throw_count;                   /* Nombre de ces exceptions    */

} exceptions_attrib;

/* Représentation d'un attribut présentant les classes internes (§4.7.5) */

typedef enum _InnerClassAccessFlags
{
    ICA_PUBLIC      = 0x0001,               /* Elément public              */
    ICA_PRIVATE     = 0x0002,               /* Elément privé               */
    ICA_PROTECTED   = 0x0004,               /* Elément sous protection     */
    ICA_STATIC      = 0x0008,               /* Elément statique            */
    ICA_FINAL       = 0x0010,               /* Elément défini un seule fois*/
    ICA_INTERFACE   = 0x0200,               /* Déclaration d'interface     */
    ICA_ABSTRACT    = 0x0400                /* Déclaré comme abstrait      */

} InnerClassAccessFlags;

typedef struct _inner_class
{
    uint16_t inner_class_info_index;        /* Propriétés de la classe     */
    uint16_t outer_class_info_index;        /* Propriétés de la parente    */
    uint16_t inner_name_index;              /* Nom de la classe            */
    InnerClassAccessFlags access;           /* Droits d'accès              */

} inner_class;

typedef struct _inner_classes_attrib
{
    inner_class *classes;                   /* Classes internes            */
    uint16_t classes_count;                 /* Nombre de ces classe        */

} inner_classes_attrib;

/* Représentation d'un fichier source (§4.7.7) */
typedef struct _source_file_attrib
{
    uint16_t source_file_index;             /* Indice dans le réservoir    */

} source_file_attrib;

/* Représentation des correspondances entre lignes et code (§4.7.8) */

typedef struct _pc_and_line
{
    uint16_t start_pc;                      /* Début de la zone visée      */
    uint16_t number;                        /* Numéro de ligne du code     */

} pc_and_line;

typedef struct _line_number_attrib
{
    pc_and_line *lines;                     /* Correspondances code/source */
    uint16_t lines_count;                   /* Nombre de correspondances   */

} line_number_attrib;

/* Représentation des variables locales (§4.7.9) */

typedef struct _local_variable
{
    uint16_t start_pc;                      /* Position dans le code       */
    uint16_t length;                        /* Taille de la variable       */
    uint16_t name_index;                    /* Indice nominal de réservoir */ 
    uint16_t descriptor_index;              /* Type de la variable         */
    uint16_t index;                         /* Place dans la liste complète*/

} local_variable;

typedef struct _local_variables_attrib
{
    local_variable *vars;                   /* Variables locales           */
    uint16_t vars_count;                    /* Nombre de ces variables     */

} local_variables_attrib;

/* Description des attributs Java */
struct _java_attribute
{
    JavaAttributeType type;                 /* Type d'attribut représenté  */

    union
    {
        const_value_attrib const_value;
        code_attrib code;
        exceptions_attrib exceptions;
        inner_classes_attrib inner_classes;
        source_file_attrib source_file;
        line_number_attrib line_number;
        local_variables_attrib local_vars;

    } info;                                 /* Infos portées par l'attribut*/

};



/* ---------------------------- CHAMPS POUR CLASSES JAVA ---------------------------- */


/* Types d'accès aux champs (§4.5) */
typedef enum _FieldAccessFlags
{
    FAC_PUBLIC      = 0x0001,               /* Elément public              */
    FAC_PRIVATE     = 0x0002,               /* Elément privé               */
    FAC_PROTECTED   = 0x0004,               /* Elément sous protection     */
    FAC_STATIC      = 0x0008,               /* Elément statique            */
    FAC_FINAL       = 0x0010,               /* Elément défini un seule fois*/
    FAC_VOLATILE    = 0x0040,               /* Elément sans cache          */
    FAC_TRANSIENT   = 0x0080                /* Elément ni lu ni écrit...   */

} FieldAccessFlags;

/* Description d'un champ Java */
typedef struct _java_field
{
    FieldAccessFlags access;                /* Droits d'accès              */

    uint16_t name_index;                    /* Nom dans le réservoir       */
    uint16_t descriptor_index;              /* Prototype au même endroit   */

    java_attribute *attributes;             /* Attributs liés au champ     */
    uint16_t attributes_count;              /* Nombre de ces attributs     */

} java_field;



/* --------------------------- METHODES POUR CLASSES JAVA --------------------------- */


/* Types d'accès aux champs (§4.6) */
typedef enum _MethodAccessFlags
{
    MAC_PUBLIC          = 0x0001,           /* Elément public              */
    MAC_PRIVATE         = 0x0002,           /* Elément privé               */
    MAC_PROTECTED       = 0x0004,           /* Elément sous protection     */
    MAC_STATIC          = 0x0008,           /* Elément statique            */
    MAC_FINAL           = 0x0010,           /* Elément défini un seule fois*/
    MAC_SYNCHRONIZED    = 0x0020,           /* Elément avec mutex natif    */
    MAC_NATIVE          = 0x0100,           /* Elément conçu sans Java     */
    MAC_ABSTRACT        = 0x0400,           /* Elément sans implantation   */
    MAC_STRICT          = 0x0800            /* Elément déclaré stricte FP  */ 

} MethodAccessFlags;

/* Description d'une méthode Java */
typedef struct _java_method
{
    MethodAccessFlags access;               /* Droits d'accès              */

    uint16_t name_index;                    /* Nom dans le réservoir       */
    uint16_t descriptor_index;              /* Prototype au même endroit   */

    java_attribute *attributes;             /* Attributs liés à la méthode */
    uint16_t attributes_count;              /* Nombre de ces attributs     */

} java_method;



/* ---------------------------- LISTE DES DROITS D'ACCES ---------------------------- */


/* Types d'accès (§4.1) */
typedef enum _ClassAccessFlags
{
    CAC_PUBLIC      = 0x0001,               /* Elément public              */
    CAC_FINAL       = 0x0010,               /* Déclaré comme final         */
    CAC_SUPER       = 0x0020,               /* Traitement spécial          */
    CAC_INTERFACE   = 0x0200,               /* Déclaration d'interface     */
    CAC_ABSTRACT    = 0x0400                /* Déclaré comme abstrait      */

} ClassAccessFlags;



/* --------------------------- DESCRIPTION DU FORMAT JAVA --------------------------- */


/* En-tête de tout programe Java */
typedef struct _java_header
{
    uint16_t minor_version;                 /* Numéro de révision mineur   */
    uint16_t major_version;                 /* Numéro de révision majeur   */

    constant_pool_entry *pool;              /* Réservoir de constantes     */
    uint16_t pool_len;                      /* Quantité de ces éléments    */

    ClassAccessFlags access;                /* Type de classe/interface    */

    uint16_t this_class;                    /* Infos sur la classe         */
    uint16_t super_class;                   /* Infos sur la classe parente */

    uint16_t *interfaces;                   /* Interfaces intégrées        */
    uint16_t interfaces_count;              /* Nombre de ces interfaces    */

    java_field *fields;                     /* Champs de la classe         */
    uint16_t fields_count;                  /* Nombre de champs présents   */

    java_method *methods;                   /* Méthodes de la classe       */
    uint16_t methods_count;                 /* Nombre de méthodes listées  */

    java_attribute *attributes;             /* Attributs liés à la classe  */
    uint16_t attributes_count;              /* Nombre de ces attributs     */

} java_header;



#endif  /* _FORMAT_JAVA_JAVA_DEF_H */
