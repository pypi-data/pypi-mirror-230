
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dex_def.h - liste des structures et constantes utilisées par le format DEX
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_DEX_DEX_DEF_H
#define _PLUGINS_DEX_DEX_DEF_H


#include <common/leb128.h>



/* -------------------------- DESCRIPTION DU FORMAT DALVIK -------------------------- */


/* Identifiant magique "dex\n035\0" */
#define DEX_FILE_MAGIC          "\x64\x65\x78\x0a\x30\x33\x35\x00"
#define DEX_FILE_MAGIC_LEN      8

/* Types de boutisme */
#define ENDIAN_CONSTANT             0x12345678
#define REVERSE_ENDIAN_CONSTANT     0x78563412

/* Indice non valide */
#define NO_INDEX                0xffffffff


/* En-tête de tout programe Dex */
typedef struct _dex_header
{
    uint8_t magic[DEX_FILE_MAGIC_LEN];      /* Valeur magique du format    */

    uint32_t checksum;                      /* Somme de contrôle adler32   */
    uint8_t signature[20];                  /* Emprunte SHA-1 du reste     */
    uint32_t file_size;                     /* Taille du fichier           */
    uint32_t header_size;                   /* Taille de cette en-tête     */

    uint32_t endian_tag;                    /* Boutisme du fichier         */

    uint32_t link_size;                     /* Taille de section 'liaisons'*/
    uint32_t link_off;                      /* Position de ladite section  */
    uint32_t map_off;                       /* Position de la cartographie */
    uint32_t string_ids_size;               /* Nombre de chaînes de carac. */
    uint32_t string_ids_off;                /* Position de cette liste     */
    uint32_t type_ids_size;                 /* Nom d'identifiant de type   */
    uint32_t type_ids_off;                  /* Position de la liste        */
    uint32_t proto_ids_size;                /* Nombre de prototypes        */
    uint32_t proto_ids_off;                 /* Position de la liste        */
    uint32_t field_ids_size;                /* Nombre de champs            */
    uint32_t field_ids_off;                 /* Position de la liste        */
    uint32_t method_ids_size;               /* Nombre de méthodes          */
    uint32_t method_ids_off;                /* Position de la liste        */
    uint32_t class_defs_size;               /* Nombre de classes déclarées */
    uint32_t class_defs_off;                /* Position de la liste        */
    uint32_t data_size;                     /* Taille des données          */
    uint32_t data_off;                      /* Début des données           */

} dex_header;



/* -------------------------- CONSTANTES POUR DEX DIVERSES -------------------------- */


/* Définition des drapeaux d'accès */

#define ACC_PUBLIC  	            0x00001 /* Elément publique            */
#define ACC_PRIVATE 	            0x00002 /* Elément privé               */
#define ACC_PROTECTED 	            0x00004 /* Elément protégé             */
#define ACC_STATIC 	                0x00008 /* Elément statique            */
#define ACC_FINAL 	                0x00010 /* Non dérivable / modifiable  */
#define ACC_SYNCHRONIZED 	        0x00020 /* Pose de verrou automatique  */
#define ACC_VOLATILE 	            0x00040 /* Accès spécial threads       */
#define ACC_BRIDGE 	                0x00040 /* Méthode pont                */
#define ACC_TRANSIENT 	            0x00080 /* Pas de sérialisation        */
#define ACC_VARARGS 	            0x00080 /* Arguments variables         */
#define ACC_NATIVE 	                0x00100 /* Implémentation en code natif*/
#define ACC_INTERFACE 	            0x00200 /* Interface                   */
#define ACC_ABSTRACT 	            0x00400 /* Non instanciable directement*/
#define ACC_STRICT 	                0x00800 /* Règle pour les flottants    */
#define ACC_SYNTHETIC 	            0x01000 /* Non défini dans le code     */
#define ACC_ANNOTATION 	            0x02000 /* Annotation                  */
#define ACC_ENUM 	                0x04000 /* Enumération                 */
#define ACC_CONSTRUCTOR 	        0x10000 /* Constructeur                */
#define ACC_DECLARED_SYNCHRONIZED   0x20000 /* Pose de verrou automatique  */



/* ------------------------ ELEMENTS DE TABLE DES CONSTANTES ------------------------ */


/* Chaîne de caractères */

typedef struct _string_id_item
{
    uint32_t string_data_off;               /* Propriétés de la chaîne     */

} string_id_item;

typedef struct _string_data_item
{
    uleb128_t utf16_size;                   /* Taille du décodage          */
    const uint8_t *data;                    /* Caractères terminés par '\0'*/

} string_data_item;

/* Description d'un type */
typedef struct _type_id_item
{
    uint32_t descriptor_idx;                /* Description du type         */

} type_id_item;

/* Description d'un prototype */
typedef struct _proto_id_item
{
    uint32_t shorty_idx;                    /* Description version courte  */
    uint32_t return_type_idx;               /* Type de retour              */
    uint32_t parameters_off;                /* Position des arguments      */

} proto_id_item;

/* Description d'un champ */
typedef struct _field_id_item
{
    uint16_t class_idx;                     /* Classe d'appartenance       */
    uint16_t type_idx;                      /* Type du champ               */
    uint32_t name_idx;                      /* Nom du champ                */

} field_id_item;

/* Description d'une méthode */
typedef struct _method_id_item
{
    uint16_t class_idx;                     /* Classe d'appartenance       */
    uint16_t proto_idx;                     /* Prototype de la méthode     */
    uint32_t name_idx;                      /* Nom de la méthode           */

} method_id_item;

/* Description d'une classe */
typedef struct _class_def_item
{
    uint32_t class_idx;                     /* Type de la classe           */
    uint32_t access_flags;                  /* Drapeaux d'accès déclarés   */
    uint32_t superclass_idx;                /* Type de la classe parente   */
    uint32_t interfaces_off;                /* Liste des interfaces        */
    uint32_t source_file_idx;               /* Fichier source d'origine    */
    uint32_t annotations_off;               /* Eventuelles annotations     */
    uint32_t class_data_off;                /* Données de la classe        */
    uint32_t static_values_off;             /* Initialisations statiques   */

} class_def_item;



/* --------------------------- DESCRIPTION DE CLASSES DEX --------------------------- */


/* Propriétés d'une champ */
typedef struct _encoded_field
{
    uleb128_t field_idx_diff;               /* Description du champ        */
    uleb128_t access_flags;                 /* Conditions d'accès          */

} encoded_field;

/* Propriétés d'une méthode */
typedef struct _encoded_method
{
    uleb128_t method_idx_diff;              /* Description de la méthode   */
    uleb128_t access_flags;                 /* Conditions d'accès          */
    uleb128_t code_off;                     /* Position du code associé    */

    vmpa2t origin;                          /* Rajout pour suivi interne   */

} encoded_method;

/* Type quelconque */
typedef struct _type_item
{
    uint16_t type_idx;                      /* Indice dans la table adaptée*/

} type_item;

/* Liste de types */
typedef struct _type_list
{
    uint32_t size;                          /* Nombre d'éléments présents  */
    const type_item *list;                  /* Liste des éléments inscrits */

} type_list;

/* Données de fonctionnement pour classe */
typedef struct _class_data_item
{
    uleb128_t static_fields_size;           /* Quantité de champs statiques*/
    uleb128_t instance_fields_size;         /* Qté de champs instanciables */
    uleb128_t direct_methods_size;          /* Qté de méthodes propres     */
    uleb128_t virtual_methods_size;         /* Qté de méthodes virtuelles  */

    encoded_field *static_fields;           /* Champs statiques            */
    encoded_field *instance_fields;         /* Champs instanciables        */
    encoded_method *direct_methods;         /* Méthodes propres            */
    encoded_method *virtual_methods;        /* Méthodes virtuelles         */

} class_data_item;



/* --------------------------- PORTION DE CODE EXECUTABLE --------------------------- */


/* Exception gérée */
typedef struct _encoded_type_addr_pair
{
    uleb128_t type_idx;                     /* Type d'exception couverte   */
    uleb128_t addr;                         /* Adresse du début du code    */

} encoded_type_addr_pair;

/* Ensemble d'exceptions prises en compte */
typedef struct _encoded_catch_handler
{
    leb128_t size;                          /* Quantité d'exceptions       */
    encoded_type_addr_pair *handlers;       /* Gestionnaires explicites    */
    uleb128_t catch_all_addr;               /* Adresse par défaut          */

    /**
     * Note : les spécifications indiquent que le champ handler_off de
     * try_item renvoie vers le gestionnaire à partir de la base de la structure
     * encoded_catch_handler_list. Comme la représentation interne de cette
     * structure efface la représentation physique, on conserve en mémoire
     * le décalage rencontré à la lecture dans un champ artificiel.
     */
    phys_t offset;                          /* Position dans le binaire    */

} encoded_catch_handler;

/* Liste des différents gestionnaires d'exceptions */
typedef struct _encoded_catch_handler_list
{
    uleb128_t size;                         /* Taille de la liste          */
    encoded_catch_handler *list;            /* Gestionnaires en place      */

} encoded_catch_handler_list;

/* Zone couverte en cas de pépin */
typedef struct _try_item
{
    uint32_t start_addr;                    /* Adresse du début couvert    */
    uint16_t insn_count;                    /* Nbre de doubles-octets gérés*/
    uint16_t handler_off;                   /* Indice du gestionnaire      */

} try_item;

/* Description de la zone */
typedef struct _code_item
{
    uint16_t registers_size;                /* Qté de registres utilisés   */
    uint16_t ins_size;                      /* Nbre d'arguments en entrée  */
    uint16_t outs_size;                     /* Nbre d'arguments en sortie  */
    uint16_t tries_size;                    /* Qté de try/catch            */
    uint32_t debug_info_off;                /* Information de débogage     */
    uint32_t insns_size;                    /* Nbre de blocs de 2 octets   */

    uint16_t *insns;                        /* Code exécutable             */
    try_item *tries;                        /* Zone d'exceptions           */
    encoded_catch_handler_list *handlers;   /* Gestionnaires associés      */

} code_item;



/* ------------------------------- AIGUILLAGES DIVERS ------------------------------- */


/* Aiguillage compressé */
typedef struct _packed_switch
{
    uint16_t ident;                         /* Pseudo-code d'identification*/
    uint16_t size;                          /* Nombre d'entrées            */
    uint32_t first_key;                     /* Première et plus petite clef*/
    uint32_t *targets;                      /* Cibles relatives            */

} packed_switch;

/* Aiguillage dispersé */
typedef struct _sparse_switch
{
    uint16_t ident;                         /* Pseudo-code d'identification*/
    uint16_t size;                          /* Nombre d'entrées            */
    uint32_t *keys;                         /* Clefs valeureuses           */
    uint32_t *targets;                      /* Cibles relatives            */

} sparse_switch;

/* Manipulation interne */
typedef union _dex_switch
{
    packed_switch packed;                   /* Modèle compact              */
    sparse_switch sparse;                   /* Modèle dispersé             */

} dex_switch;



#endif  /* _PLUGINS_DEX_DEX_DEF_H */
