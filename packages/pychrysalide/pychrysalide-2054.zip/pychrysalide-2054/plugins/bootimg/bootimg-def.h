
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf_def.h - liste des structures et constantes utilisées par le format BOOT.img
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _PLUGINS_BOOTIMG_BOOTIMG_DEF_H
#define _PLUGINS_BOOTIMG_BOOTIMG_DEF_H


#include <stdint.h>



/**
 * Références :
 *
 *   - https://source.android.com/devices/bootloader/boot-image-header
 *   - https://android.googlesource.com/platform/system/core/+/android-4.4_r1/mkbootimg/bootimg.h
 */


#define BOOT_MAGIC "ANDROID!"
#define BOOT_MAGIC_SIZE (sizeof(BOOT_MAGIC) - 1)

#define BOOT_NAME_SIZE       16
#define BOOT_ARGS_SIZE       512
#define BOOT_EXTRA_ARGS_SIZE 1024


/* Entêtes, ancienne et nouvelle, pour une image de démarrage Android */
typedef struct _boot_img_hdr
{
    uint8_t magic[BOOT_MAGIC_SIZE];         /* Identifiant magique         */
    uint32_t kernel_size;                   /* Taille en octets            */
    uint32_t kernel_addr;                   /* Adresse de chargement phys. */

    uint32_t ramdisk_size;                  /* Taille en octets            */
    uint32_t ramdisk_addr;                  /* Adresse de chargement phys. */

    uint32_t second_size;                   /* Taille en octets            */
    uint32_t second_addr;                   /* Adresse de chargement phys. */

    uint32_t tags_addr;                     /* Adresse de chargement phys. */
    uint32_t page_size;                     /* Taille des pages de Flash   */
    uint32_t header_version;                /* Version de cet entête       */
    uint32_t os_version;                    /* Version de l'OS             */
    uint8_t name[BOOT_NAME_SIZE];           /* Désignation ASCII du produit*/
    uint8_t cmdline[BOOT_ARGS_SIZE];        /* Arguments de démarrage      */
    uint32_t id[8];                         /* Horodatage, empreinte, etc. */
    uint8_t extra_cmdline[BOOT_EXTRA_ARGS_SIZE]; /* Arg. supplémentaires   */

    uint32_t recovery_dtbo_size;            /* Taille de l'image DTBO      */
    uint64_t recovery_dtbo_offset;          /* Emplacement dans le contenu */
    uint32_t header_size;                   /* Taille de l'entête en octets*/

} boot_img_hdr;



#endif  /* _PLUGINS_BOOTIMG_BOOTIMG_DEF_H */
