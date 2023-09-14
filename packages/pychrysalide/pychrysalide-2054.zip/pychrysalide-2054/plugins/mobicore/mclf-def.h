
/* Chrysalide - Outil d'analyse de fichiers binaires
 * mclf-def.h - liste des structures et constantes utilisées par le format MCLF
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _PLUGINS_MOBICORE_MCLF_DEF_H
#define _PLUGINS_MOBICORE_MCLF_DEF_H


#include <stdint.h>



/**
 * Ces définitions se basent sur :
 *
 *   https://github.com/Trustonic/trustonic-tee-user-space/blob/master/common/MobiCore/inc/mcLoadFormat.h
 */



/* ------------------------------ DECLARATIONS DE BASE ------------------------------ */


#define MC_SERVICE_HEADER_MAGIC_STR "MCLF"


/* En-tête de base */
typedef struct _mclf_intro_t
{
    uint32_t magic;                         /* Valeur magique "MCLF"       */
    uint32_t version;                       /* Version de l'en-tête        */

} mclf_intro_t;



/** Get major version number from complete version. */
#define MC_GET_MAJOR_VERSION(version) ((version) >> 16)

/** Get minor version number from complete version. */
#define MC_GET_MINOR_VERSION(version) ((version) & 0xffff)



/**
 * Drapeaux MCLF
 */

/* Le service ne peut pas être déchargé depuis MobiCore */
#define MC_SERVICE_HEADER_FLAGS_PERMANENT (1u << 0)

/* Le service n'a pas d'interface de contrôle WSM */
#define MC_SERVICE_HEADER_FLAGS_NO_CONTROL_INTERFACE (1u << 1)


/* Adresse, physique ou virtuelle */
typedef uint32_t mclf_addr_t;

/* Types de service définissant l'exécutable */
typedef enum service_type_t
{
    SERVICE_TYPE_ILLEGAL         = 0,       /* Type invalide               */
    SERVICE_TYPE_DRIVER          = 1,       /* Le service est un pilote    */
    SERVICE_TYPE_SP_TRUSTLET     = 2,       /* Le service est un Trustlet  */
    SERVICE_TYPE_SYSTEM_TRUSTLET = 3,       /* Idem, mais Trustlet système */
    SERVICE_TYPE_MIDDLEWARE      = 4,       /* Service middleware          */
    SERVICE_TYPE_LAST_ENTRY      = 5        /* Marqueur de fin             */

} service_type_t;

/* Types de mémoire */
typedef enum _mem_type_t
{
    MCLF_MEM_TYPE_INTERNAL_PREFERRED = 0,   /* Mémoire interne si possible */
    MCLF_MEM_TYPE_INTERNAL = 1,             /* Mémoire d'exécution interne */
    MCLF_MEM_TYPE_EXTERNAL = 2              /* Mémoire d'exécution externe */

} mem_type_t;

/* Description d'un segment mémoire */
typedef struct segment_descriptor_t
{
    mclf_addr_t start;                      /* Adresse virtuelle de départ */
    uint32_t len;                           /* Taille du segment           */

} segment_descriptor_t;



/* ------------------------------ IDENTIFIANTS UNIQUES ------------------------------ */


/* Identifiant sur 16 octets */
typedef struct _mc_uuid_t
{
    uint8_t value[16];                      /* Valeur de l'UUID            */

} mc_uuid_t;


#define MC_DRV_VENDOR_ID_SHIFT     (16)
#define MC_DRV_VENDOR_ID_MASK      (0xFFFF << MC_DRV_VENDOR_ID_SHIFT)
#define MC_DRV_NUMBER_MASK         (0x0000FFFF)

/* Identifiant de MobiCore */
typedef enum {

    MC_DRV_VENDOR_ID_GD   = 0 << MC_DRV_VENDOR_ID_SHIFT,

} mc_drv_vendor_id_t;

/* Identifiants de pilote GD pour MobiCore */
typedef enum {

    MC_DRV_NUMBER_INVALID            = 0,
    MC_DRV_NUMBER_CRYPTO             = 1,
    MC_DRV_NUMBER_LAST_PRE_INSTALLED = 100,
    TB_DRV_NUMBER_TUI                = 0x101,
    TB_DRV_NUMBER_TPLAY              = 0x600,

} mc_drv_number_t;

/* Identifiants de pilote Mobicore pour les Trustlets */
typedef enum {

    MC_DRV_ID_INVALID            = MC_DRV_VENDOR_ID_GD | MC_DRV_NUMBER_INVALID,
    MC_DRV_ID_CRYPTO             = MC_DRV_VENDOR_ID_GD | MC_DRV_NUMBER_CRYPTO,
    MC_DRV_ID_LAST_PRE_INSTALLED = MC_DRV_VENDOR_ID_GD | MC_DRV_NUMBER_LAST_PRE_INSTALLED,
    TB_DRV_ID_TUI                = MC_DRV_VENDOR_ID_GD | TB_DRV_NUMBER_TUI,
    TB_DRV_ID_TPLAY              = MC_DRV_VENDOR_ID_GD | TB_DRV_NUMBER_TPLAY,

} mc_driver_id_t;



/* ----------------------------- DEFINITION VERSION N°1 ----------------------------- */


/* En-tête associée */
typedef struct _mclf_header_v1_t
{
    mclf_intro_t intro;                     /* Introduction obligatoire    */
    uint32_t flags;                         /* Indicateurs de service      */
    mem_type_t mem_type;                    /* Type de mémoire d'exécution */
    service_type_t service_type;            /* Type de service             */

    uint32_t num_instances;                 /* Nbre d'instances simultanées*/
    mc_uuid_t uuid;                         /* Identifiant unique (UUID)   */
    mc_driver_id_t driver_id;               /* Identifiant éventuel        */
    uint32_t num_threads;                   /* Nbre de threads du service  */

    segment_descriptor_t text;              /* Segment virtuel de code     */
    segment_descriptor_t data;              /* Segment virtuel de données  */

    uint32_t bss_len;                       /* Taille du segment BSS       */
    mclf_addr_t entry;                      /* Point d'entrée du service   */

} mclf_header_v1_t;



/* ----------------------------- DEFINITION VERSION N°2 ----------------------------- */


/* En-tête associée */
typedef struct _mclf_header_v2_t
{
    mclf_intro_t intro;                     /* Introduction obligatoire    */
    uint32_t flags;                         /* Indicateurs de service      */
    mem_type_t mem_type;                    /* Type de mémoire d'exécution */
    service_type_t service_type;            /* Type de service             */

    uint32_t num_instances;                 /* Nbre d'instances simultanées*/
    mc_uuid_t uuid;                         /* Identifiant unique (UUID)   */
    mc_driver_id_t driver_id;               /* Identifiant éventuel        */
    uint32_t num_threads;                   /* Nbre de threads du service  */

    segment_descriptor_t text;              /* Segment virtuel de code     */
    segment_descriptor_t data;              /* Segment virtuel de données  */

    uint32_t bss_len;                       /* Taille du segment BSS       */
    mclf_addr_t entry;                      /* Point d'entrée du service   */
    uint32_t service_version;               /* Version de l'interface      */

} mclf_header_v2_t;





/* ------------------------------- DEFINITION GLOBALE ------------------------------- */
/* ------------------------------- DEFINITION GLOBALE ------------------------------- */




/**
 * Version 2 MCLF text segment header.
 * Required to be present in MobiCore 1.2 components at address (0x1080).
 * This extension is initialized already at trustlet compile time,
 * but may be modified later by configuration tools and by MobiCore at load time.
 */
typedef struct _mclf_text_header_t
{
    uint32_t version;                       /* Version de la structure     */
    uint32_t text_header_len;               /* Taille de la structure      */
    uint32_t required_feat;                 /* Fonctionnalités requises    */

    uint32_t mc_lib_entry;                  /* Adresse d'entrée McLib      */
    segment_descriptor_t mc_lib_data;       /* Segment pour McLib          */
    uint32_t mc_lib_base;                   /* Adresse de base pour McLib  */

    uint32_t tl_api_vers;                   /* Version TlApi utilisée      */
    uint32_t dr_api_vers;                   /* Version DrApi utilisée      */
    uint32_t ta_properties;                 /* Position de _TA_Properties  */

} mclf_text_header_t;





/* ------------------------------- DEFINITION GLOBALE ------------------------------- */


/* En-tête générique */
typedef union _mclf_header_t
{
    mclf_intro_t intro;                     /* Base pour identification    */
    mclf_header_v1_t v1;                    /* En-tête version 1           */
    mclf_header_v2_t v2;                    /* En-tête version 2           */

} mclf_header_t;



#endif  /* _PLUGINS_MOBICORE_MCLF_DEF_H */
