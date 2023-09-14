
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pe_def.h - liste des structures et constantes utilisées par le format PE
 *
 * Copyright (C) 2010-2017 Cyrille Bagard
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


#ifndef _PLUGINS_PE_PE_DEF_H
#define _PLUGINS_PE_PE_DEF_H


#include <stdint.h>


/**
 * Références :
 *
 *  - https://fr.wikipedia.org/wiki/Portable_Executable#En-tête_MZ_sous_MS-DOS
 *  - https://www.nirsoft.net/kernel_struct/vista/IMAGE_DOS_HEADER.html
 *
 */



/* ---------------------------- DESCRIPTION DU FORMAT PE ---------------------------- */


/* En-tête DOS */
typedef struct _image_dos_header
{
    uint16_t e_magic;                       /* Numéro magique              */
    uint16_t e_cblp;                        /* Octets de la dernière page  */
    uint16_t e_cp;                          /* Pages dans le fichier       */
    uint16_t e_crlc;                        /* Relocalisations             */
    uint16_t e_cparhdr;                     /* Taille en paragraphes       */
    uint16_t e_minalloc;                    /* Nb min de paragraphes requis*/
    uint16_t e_maxalloc;                    /* Nb max de paragraphes requis*/
    uint16_t e_ss;                          /* Valeur (relative) SS init.  */
    uint16_t e_sp;                          /* Valeur SP initiale          */
    uint16_t e_csum;                        /* Empreinte                   */
    uint16_t e_ip;                          /* Valeur IP initiale          */
    uint16_t e_cs;                          /* Valeur (relative) CS init.  */
    uint16_t e_lfarlc;                      /* Position de table de reloc. */
    uint16_t e_ovno;                        /* Nombre d'overlay            */
    uint16_t e_res[4];                      /* Mots réservés               */
    uint16_t e_oemid;                       /* Identifiant OEM             */
    uint16_t e_oeminfo;                     /* Infos OEM pour e_oemid      */
    uint16_t e_res2[10];                    /* Mots réservés               */
    uint32_t e_lfanew;                      /* Décalage de bon en-tête     */

} image_dos_header;

/* Archtectures supportées */

/**
 * Cf. https://docs.microsoft.com/en-us/windows/win32/sysinfo/image-file-machine-constants
 */

#define IMAGE_FILE_MACHINE_UNKNOWN      0x0000  /* Unknown */
#define IMAGE_FILE_MACHINE_TARGET_HOST  0x0001  /* Interacts with the host and not a WOW64 guest */
#define IMAGE_FILE_MACHINE_I386         0x014c  /* Intel 386 */
#define IMAGE_FILE_MACHINE_R3000        0x0162  /* MIPS little-endian, 0x160 big-endian */
#define IMAGE_FILE_MACHINE_R4000        0x0166  /* MIPS little-endian */
#define IMAGE_FILE_MACHINE_R10000       0x0168  /* MIPS little-endian */
#define IMAGE_FILE_MACHINE_WCEMIPSV2    0x0169  /* MIPS little-endian WCE v2 */
#define IMAGE_FILE_MACHINE_ALPHA        0x0184  /* Alpha_AXP */
#define IMAGE_FILE_MACHINE_SH3          0x01a2  /* SH3 little-endian */
#define IMAGE_FILE_MACHINE_SH3DSP       0x01a3  /* SH3DSP */
#define IMAGE_FILE_MACHINE_SH3E         0x01a4  /* SH3E little-endian */
#define IMAGE_FILE_MACHINE_SH4          0x01a6  /* SH4 little-endian */
#define IMAGE_FILE_MACHINE_SH5          0x01a8  /* SH5 */
#define IMAGE_FILE_MACHINE_ARM          0x01c0  /* ARM Little-Endian */
#define IMAGE_FILE_MACHINE_THUMB        0x01c2  /* ARM Thumb/Thumb-2 Little-Endian */
#define IMAGE_FILE_MACHINE_ARMNT        0x01c4  /* ARM Thumb-2 Little-Endian */
#define IMAGE_FILE_MACHINE_AM33         0x01d3  /* TAM33BD */
#define IMAGE_FILE_MACHINE_POWERPC      0x01f0  /* IBM PowerPC Little-Endian */
#define IMAGE_FILE_MACHINE_POWERPCFP    0x01f1  /* POWERPCFP */
#define IMAGE_FILE_MACHINE_IA64         0x0200  /* Intel 64 */
#define IMAGE_FILE_MACHINE_MIPS16       0x0266  /* MIPS */
#define IMAGE_FILE_MACHINE_ALPHA64      0x0284  /* ALPHA64 */
/*#define IMAGE_FILE_MACHINE_AXP64        0x0284*/ /* AXP64 */
#define IMAGE_FILE_MACHINE_MIPSFPU      0x0366  /* MIPS */
#define IMAGE_FILE_MACHINE_MIPSFPU16    0x0466  /* MIPS */
#define IMAGE_FILE_MACHINE_TRICORE      0x0520  /*Infineon */
#define IMAGE_FILE_MACHINE_CEF          0x0cef  /* CEF */
#define IMAGE_FILE_MACHINE_EBC          0x0ebc  /* EFI Byte Code */
#define IMAGE_FILE_MACHINE_AMD64        0x8664  /* AMD64 (K8) */
#define IMAGE_FILE_MACHINE_M32R         0x9041  /* M32R little-endian */
#define IMAGE_FILE_MACHINE_ARM64        0xaa64  /* ARM64 Little-Endian */
#define IMAGE_FILE_MACHINE_CEE          0xc0ee  /* CEE */

/* Caractéristiques de l'image */
#define IMAGE_FILE_RELOCS_STRIPPED      0x0001  /* Pas de relocalisation   */
#define IMAGE_FILE_EXECUTABLE_IMAGE     0x0002  /* Fichier exécutable      */
#define IMAGE_FILE_LINE_NUMS_STRIPPED   0x0004  /* Pas de ligne COFF       */
#define IMAGE_FILE_LOCAL_SYMS_STRIPPED  0x0008  /* Pas de table de symboles COFF */
#define IMAGE_FILE_AGGRESIVE_WS_TRIM    0x0010  /* Aggressively trim the working set. This value is obsolete as of Windows 2000. */
#define IMAGE_FILE_LARGE_ADDRESS_AWARE  0x0020  /* Adressage > 2 Go        */
#define IMAGE_FILE_BYTES_REVERSED_LO    0x0080  /* Octets inv. ; obsolète  */
#define IMAGE_FILE_32BIT_MACHINE        0x0100  /* Machine 32 bits         */
#define IMAGE_FILE_DEBUG_STRIPPED       0x0200  /* Pas d'infos de débogage */	
#define IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP  0x0400  /* ...support amovible */
#define IMAGE_FILE_NET_RUN_FROM_SWAP    0x0800  /* Ficher issu du réseau   */
#define IMAGE_FILE_SYSTEM               0x1000  /* Fichier système         */
#define IMAGE_FILE_DLL                  0x2000  /* Fichier DLL             */
#define IMAGE_FILE_UP_SYSTEM_ONLY       0x4000  /* Mono-proc. seulement    */
#define IMAGE_FILE_BYTES_REVERSED_HI    0x8000  /* Octets inv. ; obsolète  */

/* Première en-tête du "vrai" format */
typedef struct _image_file_header
{
    uint16_t machine;                       /* Type de machine visée       */
    uint16_t number_of_sections;            /* Nombre de sections          */
    uint32_t time_date_stamp;               /* Date de la liaison          */
    uint32_t pointer_to_symbol_table;       /* Position de ladite table    */
    uint32_t number_of_symbols;             /* Nombre de symboles          */
    uint16_t size_of_optional_header;       /* Taille de l'en-tête n°2     */
    uint16_t characteristics;               /* Propriétés de l'image       */

} image_file_header;



/* -------------------------- EN-TETE EVOLUEE DU FORMAT PE -------------------------- */


/**
 * Références :
 *
 *  - http://msdn.microsoft.com/en-us/library/ms680305(VS.85).aspx
 *  - https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_optional_header32
 */

/* Zone de données Windows */
typedef struct _image_data_directory
{
    uint32_t virtual_address;               /* Adresse de la table         */
    uint32_t size;                          /* Taille de la table          */

} image_data_directory;

// Directory Entries
#define IMAGE_DIRECTORY_ENTRY_EXPORT          0   // Export Directory
#define IMAGE_DIRECTORY_ENTRY_IMPORT          1   // Import Directory
#define IMAGE_DIRECTORY_ENTRY_RESOURCE        2   // Resource Directory
#define IMAGE_DIRECTORY_ENTRY_EXCEPTION       3   // Exception Directory
#define IMAGE_DIRECTORY_ENTRY_SECURITY        4   // Security Directory
#define IMAGE_DIRECTORY_ENTRY_BASERELOC       5   // Base Relocation Table
#define IMAGE_DIRECTORY_ENTRY_DEBUG           6   // Debug Directory
//      IMAGE_DIRECTORY_ENTRY_COPYRIGHT       7   // (X86 usage)
#define IMAGE_DIRECTORY_ENTRY_ARCHITECTURE    7   // Architecture Specific Data
#define IMAGE_DIRECTORY_ENTRY_GLOBALPTR       8   // RVA of GP
#define IMAGE_DIRECTORY_ENTRY_TLS             9   // TLS Directory
#define IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG    10   // Load Configuration Directory
#define IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT   11   // Bound Import Directory in headers
#define IMAGE_DIRECTORY_ENTRY_IAT            12   // Import Address Table
#define IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT   13   // Delay Load Import Descriptors
#define IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR 14   // COM Runtime descriptor


/**
 * cf. http://msdn.microsoft.com/en-us/library/ms680339(VS.85).aspx
 */

#define IMAGE_NUMBEROF_DIRECTORY_ENTRIES 16

/* Seconde en-tête, optionnelle */

typedef struct _image_optional_header_32
{
    uint16_t magic;                         /* Type de binaire manipulé    */
    uint8_t major_linker_version;           /* Version majeure du linker   */
    uint8_t minor_linker_version;           /* Version mineure du linker   */
    uint32_t size_of_code;                  /* Taille de tout le code      */
    uint32_t size_of_initialized_data;      /* Taille des données init.    */
    uint32_t size_of_uninitialized_data;    /* Taille des données non init.*/
    uint32_t address_of_entry_point;        /* Point d'entrée pour un exe. */
    uint32_t base_of_code;                  /* Adresse relative du code    */
    uint32_t base_of_data;                  /* Adresse relative des données*/
    uint32_t image_base;                    /* Adresse souhaitée en mémoire*/
    uint32_t section_alignment;             /* Alignement des sections     */
    uint32_t file_alignment;                /* Alignement des données      */
    uint16_t major_operating_system_version;/* Numéro majeur d'OS requis   */
    uint16_t minor_operating_system_version;/* Numéro mineur d'OS requis   */
    uint16_t major_image_version;           /* Numéro majeur du binaire    */
    uint16_t minor_image_version;           /* Numéro mineur du binaire    */
    uint16_t major_subsystem_version;       /* Numéro majeur du sous-sys.  */
    uint16_t minor_subsystem_version;       /* Numéro mineur du sous-sys.  */
    uint32_t win32_version_value;           /* Réservé (-> 0)              */
    uint32_t size_of_image;                 /* Taille de l'image           */
    uint32_t size_of_headers;               /* Taille de l'en-tête         */
    uint32_t checksum;                      /* Somme de contrôle           */
    uint16_t subsystem;                     /* Sous-système visé           */
    uint16_t dll_characteristics;           /* Propriétés de la DLL        */
    uint32_t size_of_stack_reserve;         /* Taille de pile reservée     */
    uint32_t size_of_stack_commit;          /* Taille de pile au démarrage */
    uint32_t size_of_heap_reserve;          /* Taille de tas reservée      */
    uint32_t size_of_heap_commit;           /* Taille de tas au démarrage  */
    uint32_t loader_flags;                  /* Champ obslète               */
    uint32_t number_of_rva_and_sizes;       /* Nombre d'entrées suivantes  */
    image_data_directory data_directory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];

} image_optional_header_32;

typedef struct _image_optional_header_64
{

    uint16_t magic;                         /* Type de binaire manipulé    */
    uint8_t major_linker_version;           /* Version majeure du linker   */
    uint8_t minor_linker_version;           /* Version mineure du linker   */
    uint32_t size_of_code;                  /* Taille de tout le code      */
    uint32_t size_of_initialized_data;      /* Taille des données init.    */
    uint32_t size_of_uninitialized_data;    /* Taille des données non init.*/
    uint32_t address_of_entry_point;        /* Point d'entrée pour un exe. */
    uint32_t base_of_code;                  /* Adresse relative du code    */
    uint64_t image_base;                    /* Adresse souhaitée en mémoire*/
    uint32_t section_alignment;             /* Alignement des sections     */
    uint32_t file_alignment;                /* Alignement des données      */
    uint16_t major_operating_system_version;/* Numéro majeur d'OS requis   */
    uint16_t minor_operating_system_version;/* Numéro mineur d'OS requis   */
    uint16_t major_image_version;           /* Numéro majeur du binaire    */
    uint16_t minor_image_version;           /* Numéro mineur du binaire    */
    uint16_t major_subsystem_version;       /* Numéro majeur du sous-sys.  */
    uint16_t minor_subsystem_version;       /* Numéro mineur du sous-sys.  */
    uint32_t win32_version_value;           /* Réservé (-> 0)              */
    uint32_t size_of_image;                 /* Taille de l'image           */
    uint32_t size_of_headers;               /* Taille de l'en-tête         */
    uint32_t checksum;                      /* Somme de contrôle           */
    uint16_t subsystem;                     /* Sous-système visé           */
    uint16_t dll_characteristics;           /* Propriétés de la DLL        */
    uint64_t size_of_stack_reserve;         /* Taille de pile reservée     */
    uint64_t size_of_stack_commit;          /* Taille de pile au démarrage */
    uint64_t size_of_heap_reserve;          /* Taille de tas reservée      */
    uint64_t size_of_heap_commit;           /* Taille de tas au démarrage  */
    uint32_t loader_flags;                  /* Champ obslète               */
    uint32_t number_of_rva_and_sizes;       /* Nombre d'entrées suivantes  */
    image_data_directory data_directory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];

} image_optional_header_64;

typedef union _image_optional_header
{
    image_optional_header_32 header_32;     /* Version 32 bits             */
    image_optional_header_64 header_64;     /* Version 64 bits             */

} image_optional_header;




/* Valeurs pour le champ 'magic' */
#define IMAGE_NT_OPTIONAL_HDR32_MAGIC   0x10b   /* Exécutable 32 bits      */
#define IMAGE_NT_OPTIONAL_HDR64_MAGIC   0x20b   /* Exécutable 64 bits      */
#define IMAGE_ROM_OPTIONAL_HDR_MAGIC    0x107   /* Image ROM               */

/* Sous-système attendu (champ 'subsystem') */
#define IMAGE_SUBSYSTEM_UNKNOWN                  0  /* Inconnu             */
#define IMAGE_SUBSYSTEM_NATIVE                   1  /* Rien de requis      */
#define IMAGE_SUBSYSTEM_WINDOWS_GUI              2  /* Windows GUI         */
#define IMAGE_SUBSYSTEM_WINDOWS_CUI              3  /* Windows CUI         */
#define IMAGE_SUBSYSTEM_OS2_CUI                  5  /* OS/2 CUI            */
#define IMAGE_SUBSYSTEM_POSIX_CUI                7  /* Posix CUI           */
#define IMAGE_SUBSYSTEM_WINDOWS_CE_GUI           9  /* Windows CE          */
#define IMAGE_SUBSYSTEM_EFI_APPLICATION         10  /* Application EFI     */
#define IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER 11  /* Pilote EFI + boot   */
#define IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER      12  /* Pilote EFI + serv.  */
#define IMAGE_SUBSYSTEM_EFI_ROM                 13  /* Image ROM EFI       */
#define IMAGE_SUBSYSTEM_XBOX                    14  /* Xbox                */
#define IMAGE_SUBSYSTEM_WINDOWS_BOOT_APPLICATION 16 /* Application de boot */

/* Détails pour le champ 'dll_characteristics' */
#define IMAGE_DLLCHARACTERISTICS_UNKNOW_0 0x0001    /* Réservé             */
#define IMAGE_DLLCHARACTERISTICS_UNKNOW_1 0x0002    /* Réservé             */
#define IMAGE_DLLCHARACTERISTICS_UNKNOW_2 0x0004    /* Réservé             */
#define IMAGE_DLLCHARACTERISTICS_UNKNOW_3 0x0008    /* Réservé             */
#define IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE 0x0040/* Reloc. possible     */
#define IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY 0x0080 /* Vérif. forcées  */
#define IMAGE_DLLCHARACTERISTICS_NX_COMPAT 0x0100   /* Compatible DEP      */
#define IMAGE_DLLCHARACTERISTICS_NO_ISOLATION 0x0200/* Pas d'isolation     */
#define IMAGE_DLLCHARACTERISTICS_NO_SEH 0x0400      /* Pas de SEH          */
#define IMAGE_DLLCHARACTERISTICS_NO_BIND 0x0800     /* Ne pas lier         */
#define IMAGE_DLLCHARACTERISTICS_UNKNOW_4 0x1000    /* Réservé             */
#define IMAGE_DLLCHARACTERISTICS_WDM_DRIVER 0x2000  /* Pilote WDM          */
#define IMAGE_DLLCHARACTERISTICS_UNKNOW_5 0x4000    /* Réservé             */
#define IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE 0x8000   /* Support */


/* Résumé global */
typedef struct _image_nt_headers
{
    uint32_t signature;                     /* Numéro magique              */
    image_file_header file_header;          /* En-tête n°1                 */
    image_optional_header optional_header;  /* En-tête n°2                 */

} image_nt_headers;



/* --------------------------- SECTIONS POUR LE FORMAT PE --------------------------- */

/**
 * cf. http://msdn.microsoft.com/en-us/library/ms680341(VS.85).aspx
 */

/* Taille maximale d'un nom, avec ou sans '\0' final */
#define IMAGE_SIZEOF_SHORT_NAME 8

/* Description d'une section */
typedef struct _image_section_header
{
    char name[IMAGE_SIZEOF_SHORT_NAME];     /* Nom de la section           */

    union
    {
        uint32_t physical_address;          /* Adresse physique            */
        uint32_t virtual_size;              /* Taille en mémoire           */

    } misc;

    uint32_t virtual_address;               /* Adresse en mémoire          */
    uint32_t size_of_raw_data;              /* Taille de données définies  */
    uint32_t pointer_to_raw_data;           /* Position de ces données     */
    uint32_t pointer_to_relocations;        /* Position des relocalisations*/
    uint32_t pointer_to_line_numbers;       /* Position de numéros de ligne*/
    uint16_t number_of_relocations;         /* Quantité de relocalisations */
    uint16_t number_of_line_numbers;        /* Quantité de numéros de ligne*/
    uint32_t characteristics;               /* Caractéristiques            */

} image_section_header;

/* Détails des caractéristiques d'une image (champ 'characteristics') */
#define IMAGE_SCN_UNKNOWN_0         0x00000000  /* Réservé                 */
#define IMAGE_SCN_UNKNOWN_1         0x00000001  /* Réservé                 */
#define IMAGE_SCN_UNKNOWN_2         0x00000002  /* Réservé                 */
#define IMAGE_SCN_UNKNOWN_3         0x00000004  /* Réservé                 */
#define IMAGE_SCN_TYPE_NO_PAD       0x00000008  /* Pas de complément (obs) */
#define IMAGE_SCN_UNKNOWN_4         0x00000010  /* Réservé                 */
#define IMAGE_SCN_CNT_CODE          0x00000020  /* Code exécutable         */
#define IMAGE_SCN_CNT_INITIALIZED_DATA 0x00000040   /* Données intialisées */
#define IMAGE_SCN_CNT_UNINITIALIZED_DATA 0x00000080 /* Données non init.   */
#define IMAGE_SCN_LNK_OTHER         0x00000100  /* Réservé                 */
#define IMAGE_SCN_LNK_INFO          0x00000200  /* Commentaires ou autres  */
#define IMAGE_SCN_UNKNOWN_5         0x00000400  /* Réservé                 */
#define IMAGE_SCN_LNK_REMOVE        0x00000800  /* A ne pas intégrer       */
#define IMAGE_SCN_LNK_COMDAT        0x00001000  /* Données COMDAT          */
#define IMAGE_SCN_UNKNOWN_6         0x00002000  /* Réservé                 */
#define IMAGE_SCN_NO_DEFER_SPEC_EXC 0x00004000  /* Reset des exceptions    */
#define IMAGE_SCN_GPREL             0x00008000  /* Références globales     */
#define IMAGE_SCN_UNKNOWN_7         0x00010000  /* Réservé                 */
#define IMAGE_SCN_MEM_PURGEABLE     0x00020000  /* Réservé                 */
#define IMAGE_SCN_MEM_LOCKED        0x00040000  /* Réservé                 */
#define IMAGE_SCN_MEM_PRELOAD       0x00080000  /* Réservé                 */
#define IMAGE_SCN_ALIGN_1BYTES      0x00100000  /* Alignement sur 1 octet  */
#define IMAGE_SCN_ALIGN_2BYTES      0x00200000  /* Alignement sur 2 octets */
#define IMAGE_SCN_ALIGN_4BYTES      0x00300000  /* Alignement sur 4 octets */
#define IMAGE_SCN_ALIGN_8BYTES      0x00400000  /* Alignement sur 8 octets */
#define IMAGE_SCN_ALIGN_16BYTES     0x00500000  /* Alignement de 16 octets */
#define IMAGE_SCN_ALIGN_32BYTES     0x00600000  /* Alignement de 32 octets */
#define IMAGE_SCN_ALIGN_64BYTES     0x00700000  /* Alignement de 64 octets */
#define IMAGE_SCN_ALIGN_128BYTES    0x00800000  /* Alignement de 128 octets*/
#define IMAGE_SCN_ALIGN_256BYTES    0x00900000  /* Alignement de 256 octets*/
#define IMAGE_SCN_ALIGN_512BYTES    0x00a00000  /* Alignement de 512 octets*/
#define IMAGE_SCN_ALIGN_1024BYTES   0x00b00000  /* Alignement sur 1 ko     */
#define IMAGE_SCN_ALIGN_2048BYTES   0x00c00000  /* Alignement sur 2 ko     */
#define IMAGE_SCN_ALIGN_4096BYTES   0x00d00000  /* Alignement sur 4 ko     */
#define IMAGE_SCN_ALIGN_8192BYTES   0x00e00000  /* Alignement sur 8 ko     */
#define IMAGE_SCN_LNK_NRELOC_OVFL   0x01000000  /* Trop de Relocalisations */
#define IMAGE_SCN_MEM_DISCARDABLE   0x02000000  /* Section abandonnable    */
#define IMAGE_SCN_MEM_NOT_CACHED    0x04000000  /* Section non cachable    */
#define IMAGE_SCN_MEM_NOT_PAGED     0x08000000  /* Section non paginable   */
#define IMAGE_SCN_MEM_SHARED        0x10000000  /* Section partageable     */
#define IMAGE_SCN_MEM_EXECUTE       0x20000000  /* Section exécutable      */
#define IMAGE_SCN_MEM_READ          0x40000000  /* Section lisible         */
#define IMAGE_SCN_MEM_WRITE         0x80000000  /* Section modifiable      */



/* --------------------------- IDENTIFICATION DE SYMBOLES --------------------------- */


/**
 * https://docs.microsoft.com/en-us/previous-versions/ms809762(v=msdn.10)?redirectedfrom=MSDN#pe-file-exports
 * https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#the-edata-section-image-only
 */

/* Répertoire des importations */
typedef struct _image_export_directory
{
    uint32_t characteristics;               /* Zéro !?                     */
    uint32_t time_date_stamp;               /* Date de création du fichier */
    uint16_t major_version;                 /* Numéro majeur de version    */
    uint16_t minor_version;                 /* Numéro lineur de version    */
    uint32_t name;                          /* RVA du nom de la DLL visée  */
    uint32_t base;                          /* Départ des ordinaux listés  */
    uint32_t number_of_functions;           /* Taille de liste de fonctions*/
    uint32_t number_of_names;               /* Taille de liste de noms     */
    uint32_t address_of_functions;          /* Liste de RVA de fonctions   */
    uint32_t address_of_names;              /* Liste de RVA de noms        */
    uint32_t address_of_name_ordinals;      /* Liste de RVA d'ordinaux     */

} image_export_directory;


/**
 * http://msdn.microsoft.com/en-us/library/ms809762.aspx
 * http://sandsprite.com/CodeStuff/Understanding_imports.html
 * http://olance.developpez.com/articles/windows/pe-iczelion/import-table/
 *
 * https://docs.microsoft.com/en-us/previous-versions/ms809762(v=msdn.10)?redirectedfrom=MSDN#pe-file-imports
 * https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#the-idata-section
 */

/* Point de départ de la chaîne des importations */
typedef struct _image_import_descriptor
{
    uint32_t original_first_thunk;
    uint32_t time_date_stamp;
    uint32_t forwarder_chain;
    uint32_t module_name;
    uint32_t first_thunk;

} image_import_descriptor;



#endif  /* _PLUGINS_PE_PE_DEF_H */
