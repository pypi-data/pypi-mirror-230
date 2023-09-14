
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf_def.h - liste des structures et constantes utilisées par le format ELF
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


#ifndef _PLUGINS_ELF_ELF_DEF_H
#define _PLUGINS_ELF_ELF_DEF_H


#include <stdint.h>



/* ---------------------------- EN-TETE DES FICHIERS ELF ---------------------------- */


#define EI_NIDENT   16


/* En-tête de fichier ELF (32 et 64 bits) */

typedef struct _elf32_header
{
    uint8_t e_ident[EI_NIDENT];             /* Magic number + informations */
    uint16_t e_type;                        /* Type de fichier             */
    uint16_t e_machine;                     /* Architecture                */
    uint32_t e_version;                     /* Version du type de fichier  */
    uint32_t e_entry;                       /* Point d'entrée du programme */
    uint32_t e_phoff;                       /* Début de la table 'Program' */
    uint32_t e_shoff;                       /* Début de la table 'Section' */
    uint32_t e_flags;                       /* Prop. spécifiques au proc.  */
    uint16_t e_ehsize;                      /* Taille de l'en-tête en oct. */
    uint16_t e_phentsize;                   /* Taille d'une entrée Program */
    uint16_t e_phnum;                       /* Nombre d'éléments 'Program' */
    uint16_t e_shentsize;                   /* Taille d'une entrée Section */
    uint16_t e_shnum;                       /* Nombre d'éléments 'Section' */
    uint16_t e_shstrndx;                    /* Indice de la section chaînes*/

} elf32_header;

typedef struct _elf64_header
{
    uint8_t e_ident[EI_NIDENT];             /* Magic number + informations */
    uint16_t e_type;                        /* Type de fichier             */
    uint16_t e_machine;                     /* Architecture                */
    uint32_t e_version;                     /* Version du type de fichier  */
    uint64_t e_entry;                       /* Point d'entrée du programme */
    uint64_t e_phoff;                       /* Début de la table 'Program' */
    uint64_t e_shoff;                       /* Début de la table 'Section' */
    uint32_t e_flags;                       /* Prop. spécifiques au proc.  */
    uint16_t e_ehsize;                      /* Taille de l'en-tête en oct. */
    uint16_t e_phentsize;                   /* Taille d'une entrée Program */
    uint16_t e_phnum;                       /* Nombre d'éléments 'Program' */
    uint16_t e_shentsize;                   /* Taille d'une entrée Section */
    uint16_t e_shnum;                       /* Nombre d'éléments 'Section' */
    uint16_t e_shstrndx;                    /* Indice de la section chaînes*/

} elf64_header;

typedef union _elf_header
{
    elf32_header hdr32;                     /* Version 32 bits             */
    elf64_header hdr64;                     /* Version 64 bits             */

} elf_header;


#define ELF_HDR(fmt, hdr, fld) (fmt->is_32b ? (hdr).hdr32.fld : (hdr).hdr64.fld)

#define ELF_HDR_SET(fmt, hdr, fld, val)             \
    do                                              \
    {                                               \
        if (fmt->is_32b) (hdr).hdr32.fld = val;     \
        else (hdr).hdr64.fld = val;                 \
    }                                               \
    while (0)

#define ELF_HDR_OFFSET_OF(fmt, fld) (fmt->is_32b ? offsetof(elf32_header, fld) : offsetof(elf64_header, fld))

#define ELF_SIZEOF_HDR(fmt) (fmt->is_32b ? sizeof(elf32_header) : sizeof(elf64_header))


/* Composition du champ e_ident */

#define EI_MAG0         0                   /* Identification, octet #0    */
#define EI_MAG1         1                   /* Identification, octet #1    */
#define EI_MAG2         2                   /* Identification, octet #2    */
#define EI_MAG3         3                   /* Identification, octet #3    */
#define EI_CLASS        4                   /* Indice de classe du fichier */
#define EI_DATA         5                   /* Indice de l'encodage        */
#define EI_VERSION      6                   /* Version de fichier ELF      */
#define EI_OSABI        7                   /* Identification de l'ABI OS  */
#define EI_ABIVERSION   8                   /* Version de l'ABI            */
#define EI_PAD          9                   /* Premier octet de bourrage   */

/* ... EI_MAG* */

#define ELFMAG          "\x7f\x45\x4c\x46"  /* .ELF                         */
#define SELFMAG         4

/* ... EI_CLASS */

#define ELFCLASSNONE    0                   /* Objet invalide              */
#define ELFCLASS32      1                   /* Objet 32 bits               */
#define ELFCLASS64      2                   /* Objet 64 bits               */

/* ... EI_DATA */

#define ELFDATANONE     0                   /* Encodage invalide           */
#define ELFDATA2LSB     1                   /* Complément à 2, petit bout. */
#define ELFDATA2MSB     2                   /* Complément à 2, grand bout. */

/* ... EI_VERSION */

#define EV_NONE         0                   /* Version ELF invalide        */
#define EV_CURRENT      1                   /* Version d'ELF courante      */

/* ... EI_OSABI */

#define ELFOSABI_NONE           0           /* UNIX System V ABI */
#define ELFOSABI_SYSV           0           /* Alias.  */
#define ELFOSABI_HPUX           1           /* HP-UX */
#define ELFOSABI_NETBSD         2           /* NetBSD.  */
#define ELFOSABI_GNU            3           /* Object uses GNU ELF extensions.  */
#define ELFOSABI_LINUX          ELFOSABI_GNU /* Compatibility alias.  */
#define ELFOSABI_SOLARIS        6           /* Sun Solaris.  */
#define ELFOSABI_AIX            7           /* IBM AIX.  */
#define ELFOSABI_IRIX           8           /* SGI Irix.  */
#define ELFOSABI_FREEBSD        9           /* FreeBSD.  */
#define ELFOSABI_TRU64          10          /* Compaq TRU64 UNIX.  */
#define ELFOSABI_MODESTO        11          /* Novell Modesto.  */
#define ELFOSABI_OPENBSD        12          /* OpenBSD.  */
#define ELFOSABI_ARM_AEABI      64          /* ARM EABI */
#define ELFOSABI_ARM            97          /* ARM */
#define ELFOSABI_STANDALONE     255         /* Standalone (embedded) application */

/* Valeurs possibles pour e_type */

#define ET_NONE         0                   /* Aucun type défini           */
#define ET_REL          1                   /* Fichier relogeable          */
#define ET_EXEC         2                   /* Fichier exécutable          */
#define ET_DYN          3                   /* Bibliothèque dynamique      */
#define ET_CORE         4                   /* Fichier Core                */
#define ET_LOOS         0xfe00              /* Spécifique OS : début       */
#define ET_HIOS         0xfeff              /* Spécifique OS : fin         */
#define ET_LOPROC       0xff00              /* Spécifique processeur : deb.*/
#define ET_HIPROC       0xffff              /* Spécifique processeur : fin */

/* Valeurs possibles pour e_machine */

#define EM_NONE          0                  /* No machine */
#define EM_M32           1                  /* AT&T WE 32100 */
#define EM_SPARC         2                  /* SUN SPARC */
#define EM_386           3                  /* Intel 80386 */
#define EM_68K           4                  /* Motorola m68k family */
#define EM_88K           5                  /* Motorola m88k family */
#define EM_860           7                  /* Intel 80860 */
#define EM_MIPS          8                  /* MIPS R3000 big-endian */
#define EM_S370          9                  /* IBM System/370 */
#define EM_MIPS_RS3_LE  10                  /* MIPS R3000 little-endian */
#define EM_PARISC       15                  /* HPPA */
#define EM_VPP500       17                  /* Fujitsu VPP500 */
#define EM_SPARC32PLUS  18                  /* Sun's "v8plus" */
#define EM_960          19                  /* Intel 80960 */
#define EM_PPC          20                  /* PowerPC */
#define EM_PPC64        21                  /* PowerPC 64-bit */
#define EM_S390         22                  /* IBM S390 */
#define EM_V800         36                  /* NEC V800 series */
#define EM_FR20         37                  /* Fujitsu FR20 */
#define EM_RH32         38                  /* TRW RH-32 */
#define EM_RCE          39                  /* Motorola RCE */
#define EM_ARM          40                  /* ARM */
#define EM_FAKE_ALPHA   41                  /* Digital Alpha */
#define EM_SH           42                  /* Hitachi SH */
#define EM_SPARCV9      43                  /* SPARC v9 64-bit */
#define EM_TRICORE      44                  /* Siemens Tricore */
#define EM_ARC          45                  /* Argonaut RISC Core */
#define EM_H8_300       46                  /* Hitachi H8/300 */
#define EM_H8_300H      47                  /* Hitachi H8/300H */
#define EM_H8S          48                  /* Hitachi H8S */
#define EM_H8_500       49                  /* Hitachi H8/500 */
#define EM_IA_64        50                  /* Intel Merced */
#define EM_MIPS_X       51                  /* Stanford MIPS-X */
#define EM_COLDFIRE     52                  /* Motorola Coldfire */
#define EM_68HC12       53                  /* Motorola M68HC12 */
#define EM_MMA          54                  /* Fujitsu MMA Multimedia Accelerator*/
#define EM_PCP          55                  /* Siemens PCP */
#define EM_NCPU         56                  /* Sony nCPU embeeded RISC */
#define EM_NDR1         57                  /* Denso NDR1 microprocessor */
#define EM_STARCORE     58                  /* Motorola Start*Core processor */
#define EM_ME16         59                  /* Toyota ME16 processor */
#define EM_ST100        60                  /* STMicroelectronic ST100 processor */
#define EM_TINYJ        61                  /* Advanced Logic Corp. Tinyj emb.fam*/
#define EM_X86_64       62                  /* AMD x86-64 architecture */
#define EM_PDSP         63                  /* Sony DSP Processor */
#define EM_FX66         66                  /* Siemens FX66 microcontroller */
#define EM_ST9PLUS      67                  /* STMicroelectronics ST9+ 8/16 mc */
#define EM_ST7          68                  /* STmicroelectronics ST7 8 bit mc */
#define EM_68HC16       69                  /* Motorola MC68HC16 microcontroller */
#define EM_68HC11       70                  /* Motorola MC68HC11 microcontroller */
#define EM_68HC08       71                  /* Motorola MC68HC08 microcontroller */
#define EM_68HC05       72                  /* Motorola MC68HC05 microcontroller */
#define EM_SVX          73                  /* Silicon Graphics SVx */
#define EM_ST19         74                  /* STMicroelectronics ST19 8 bit mc */
#define EM_VAX          75                  /* Digital VAX */
#define EM_CRIS         76                  /* Axis Communications 32-bit embedded processor */
#define EM_JAVELIN      77                  /* Infineon Technologies 32-bit embedded processor */
#define EM_FIREPATH     78                  /* Element 14 64-bit DSP Processor */
#define EM_ZSP          79                  /* LSI Logic 16-bit DSP Processor */
#define EM_MMIX         80                  /* Donald Knuth's educational 64-bit processor */
#define EM_HUANY        81                  /* Harvard University machine-independent object files */
#define EM_PRISM        82                  /* SiTera Prism */
#define EM_AVR          83                  /* Atmel AVR 8-bit microcontroller */
#define EM_FR30         84                  /* Fujitsu FR30 */
#define EM_D10V         85                  /* Mitsubishi D10V */
#define EM_D30V         86                  /* Mitsubishi D30V */
#define EM_V850         87                  /* NEC v850 */
#define EM_M32R         88                  /* Mitsubishi M32R */
#define EM_MN10300      89                  /* Matsushita MN10300 */
#define EM_MN10200      90                  /* Matsushita MN10200 */
#define EM_PJ           91                  /* picoJava */
#define EM_OPENRISC     92                  /* OpenRISC 32-bit embedded processor */
#define EM_ARC_A5       93                  /* ARC Cores Tangent-A5 */
#define EM_XTENSA       94                  /* Tensilica Xtensa Architecture */
#define EM_AARCH64      183                 /* ARM AARCH64 */
#define EM_TILEPRO      188                 /* Tilera TILEPro */
#define EM_MICROBLAZE   189                 /* Xilinx MicroBlaze */
#define EM_TILEGX       191                 /* Tilera TILE-Gx */



/* --------------------------- EN-TETE DES PROGRAMMES ELF --------------------------- */


/* Version 32 et 64 bits */

typedef struct _elf32_phdr
{
    uint32_t p_type;                        /* Type de segment             */
    uint32_t p_offset;                      /* Position dans le fichier    */
    uint32_t p_vaddr;                       /* Adresse virtuelle du segment*/
    uint32_t p_paddr;                       /* Adresse physique du segment */
    uint32_t p_filesz;                      /* Taille dans le fichier      */
    uint32_t p_memsz;                       /* Taille en mémoire           */
    uint32_t p_flags;                       /* Drapeaux pour le segment    */
    uint32_t p_align;                       /* Alignement du segment       */

} elf32_phdr;

typedef struct _elf64_phdr
{
    uint32_t p_type;                        /* Type de segment             */
    uint32_t p_flags;                       /* Drapeaux pour le segment    */
    uint64_t p_offset;                      /* Position dans le fichier    */
    uint64_t p_vaddr;                       /* Adresse virtuelle du segment*/
    uint64_t p_paddr;                       /* Adresse physique du segment */
    uint64_t p_filesz;                      /* Taille dans le fichier      */
    uint64_t p_memsz;                       /* Taille en mémoire           */
    uint64_t p_align;                       /* Alignement du segment       */

} elf64_phdr;

typedef union _elf_phdr
{
    elf32_phdr phdr32;                      /* Version 32 bits             */
    elf64_phdr phdr64;                      /* Version 32 bits             */

} elf_phdr;


#define ELF_PHDR(fmt, hdr, fld) (fmt->is_32b ? (hdr).phdr32.fld : (hdr).phdr64.fld)

#define ELF_SIZEOF_PHDR(fmt) (fmt->is_32b ? sizeof(elf32_phdr) : sizeof(elf64_phdr))

/* Valeurs possibles pour p_type */

#define PT_NULL         0                   /* Program header table entry unused */
#define PT_LOAD         1                   /* Loadable program segment */
#define PT_DYNAMIC      2                   /* Dynamic linking information */
#define PT_INTERP       3                   /* Program interpreter */
#define PT_NOTE         4                   /* Auxiliary information */
#define PT_SHLIB        5                   /* Reserved */
#define PT_PHDR         6                   /* Entry for header table itself */
#define PT_TLS          7                   /* Thread-local storage segment */
#define PT_NUM          8                   /* Number of defined types */
#define PT_LOOS         0x60000000          /* Start of OS-specific */
#define PT_GNU_EH_FRAME 0x6474e550          /* GCC .eh_frame_hdr segment */
#define PT_GNU_STACK    0x6474e551          /* Indicates stack executability */
#define PT_GNU_RELRO    0x6474e552          /* Read-only after relocation */
#define PT_LOSUNW       0x6ffffffa
#define PT_SUNWBSS      0x6ffffffa          /* Sun Specific segment */
#define PT_SUNWSTACK    0x6ffffffb          /* Stack segment */
#define PT_HISUNW       0x6fffffff
#define PT_HIOS         0x6fffffff          /* End of OS-specific */
#define PT_LOPROC       0x70000000          /* Start of processor-specific */
#define PT_HIPROC       0x7fffffff          /* End of processor-specific */

/* Valeurs possibles pour p_flags */

#define PF_X        (1 << 0)                /* Le segment est exécutable   */
#define PF_W        (1 << 1)                /* Le segment est écrasable    */
#define PF_R        (1 << 2)                /* Le segment est lisible      */
#define PF_MASKOS   0x0ff00000              /* Spécifique à l'OS           */
#define PF_MASKPROC 0xf0000000              /* Spécifique au processeur    */



/* ---------------------------- EN-TETE DES SECTIONS ELF ---------------------------- */


/* Version 32 et 64 bits */

typedef struct _elf32_shdr
{
    uint32_t sh_name;                       /* Indice du nom de la section */
    uint32_t sh_type;                       /* Type de section             */
    uint32_t sh_flags;                      /* Drapeaux pour la section    */
    uint32_t sh_addr;                       /* Adresse virtuelle à l'exec. */
    uint32_t sh_offset;                     /* Position dans le fichier    */
    uint32_t sh_size;                       /* Taille en octets            */
    uint32_t sh_link;                       /* Lien vers une autre section */
    uint32_t sh_info;                       /* Infos. complémentaires      */
    uint32_t sh_addralign;                  /* Alignement de la section    */
    uint32_t sh_entsize;                    /* Eventuelle taille d'élément */

} elf32_shdr;

typedef struct _elf64_shdr
{
    uint32_t sh_name;                       /* Indice du nom de la section */
    uint32_t sh_type;                       /* Type de section             */
    uint64_t sh_flags;                      /* Drapeaux pour la section    */
    uint64_t sh_addr;                       /* Adresse virtuelle à l'exec. */
    uint64_t sh_offset;                     /* Position dans le fichier    */
    uint64_t sh_size;                       /* Taille en octets            */
    uint32_t sh_link;                       /* Lien vers une autre section */
    uint32_t sh_info;                       /* Infos. complémentaires      */
    uint64_t sh_addralign;                  /* Alignement de la section    */
    uint64_t sh_entsize;                    /* Eventuelle taille d'élément */

} elf64_shdr;

typedef union _elf_shdr
{
    elf32_shdr shdr32;                      /* Version 32 bits             */
    elf64_shdr shdr64;                      /* Version 64 bits             */

} elf_shdr;


#define ELF_SHDR(fmt, shdr, fld) (fmt->is_32b ? (shdr).shdr32.fld : (shdr).shdr64.fld)

#define ELF_SIZEOF_SHDR(fmt) (fmt->is_32b ? sizeof(elf32_shdr) : sizeof(elf64_shdr))


/* Valeurs possibles pour sh_type */

#define SHT_NULL        0                   /* Entrée non utilisée         */
#define SHT_PROGBITS    1                   /* Données de programme        */
#define SHT_SYMTAB      2                   /* Table des symboles          */
#define SHT_STRTAB      3                   /* Table de chaînes de carac.  */

#define SHT_RELA          4             /* Relocation entries with addends */
#define SHT_HASH          5             /* Symbol hash table */

#define SHT_DYNAMIC     6                   /* Info. de liaison dynamique  */

#define SHT_NOTE          7             /* Notes */
#define SHT_NOBITS        8             /* Program space with no data (bss) */
#define SHT_REL           9             /* Relocation entries, no addends */
#define SHT_SHLIB         10            /* Reserved */
#define SHT_DYNSYM        11            /* Dynamic linker symbol table */
#define SHT_INIT_ARRAY    14            /* Array of constructors */
#define SHT_FINI_ARRAY    15            /* Array of destructors */
#define SHT_PREINIT_ARRAY 16            /* Array of pre-constructors */
#define SHT_GROUP         17            /* Section group */
#define SHT_SYMTAB_SHNDX  18            /* Extended section indeces */
#define SHT_NUM           19            /* Number of defined types.  */
#define SHT_LOOS          0x60000000    /* Start OS-specific.  */
#define SHT_GNU_ATTRIBUTES 0x6ffffff5   /* Object attributes.  */
#define SHT_GNU_HASH      0x6ffffff6    /* GNU-style hash table.  */
#define SHT_GNU_LIBLIST   0x6ffffff7    /* Prelink library list */
#define SHT_CHECKSUM      0x6ffffff8    /* Checksum for DSO content.  */
#define SHT_LOSUNW        0x6ffffffa    /* Sun-specific low bound.  */
#define SHT_SUNW_move     0x6ffffffa
#define SHT_SUNW_COMDAT   0x6ffffffb
#define SHT_SUNW_syminfo  0x6ffffffc
#define SHT_GNU_verdef    0x6ffffffd    /* Version definition section.  */
#define SHT_GNU_verneed   0x6ffffffe    /* Version needs section.  */
#define SHT_GNU_versym    0x6fffffff    /* Version symbol table.  */
#define SHT_HISUNW        0x6fffffff    /* Sun-specific high bound.  */
#define SHT_HIOS          0x6fffffff    /* End OS-specific type */
#define SHT_LOPROC        0x70000000    /* Start of processor-specific */
#define SHT_HIPROC        0x7fffffff    /* End of processor-specific */
#define SHT_LOUSER        0x80000000    /* Start of application-specific */
#define SHT_HIUSER        0x8fffffff    /* End of application-specific */


/* Valeurs possibles pour sh_flags */

#define SHF_WRITE               (1 << 0)    /* Accessible en écriture      */
#define SHF_ALLOC               (1 << 1)    /* Copie en mémoire pdt l'exec.*/
#define SHF_EXECINSTR           (1 << 2)    /* Section exécutable          */
#define SHF_MERGE               (1 << 4)    /* Peut être fusionné          */
#define SHF_STRINGS             (1 << 5)    /* Contient des chaînes ('\0') */
#define SHF_INFO_LINK           (1 << 6)    /* 'sh_info' contient un index */
#define SHF_LINK_ORDER          (1 << 7)    /* Préservation de l'ordre     */
#define SHF_OS_NONCONFORMING    (1 << 8)    /* Gestion non standard requise*/
#define SHF_GROUP               (1 << 9)    /* Section membre d'un groupe  */
#define SHF_TLS                 (1 << 10)   /* Données pour un thread local*/

#define SHF_MASKOS           0x0ff00000 /* OS-specific.  */
#define SHF_MASKPROC         0xf0000000 /* Processor-specific */
#define SHF_ORDERED          (1 << 30)  /* Special ordering requirement
                                           (Solaris).  */
#define SHF_EXCLUDE          (1 << 31)  /* Section is excluded unless
                                           referenced or allocated (Solaris).*/


/* ----------------------------- DONNEES POUR LE LINKER ----------------------------- */


/* Entrées de la section dynamique (version 32 et 64 bits) */

typedef struct _elf32_dyn
{
    int32_t d_tag;                          /* Type de l'entrée            */

    union
    {
        uint32_t d_val;                     /* Valeur entière              */
        uint32_t d_ptr;                     /* Valeur d'adresse            */

    } d_un;

} elf32_dyn;

typedef struct _elf64_dyn
{
    int64_t d_tag;                          /* Type de l'entrée            */

    union
    {
        uint64_t d_val;                     /* Valeur entière              */
        uint64_t d_ptr;                     /* Valeur d'adresse            */

    } d_un;

} elf64_dyn;

typedef union _elf_dyn
{
    elf32_dyn dyn32;                        /* Version 32 bits             */
    elf64_dyn dyn64;                        /* Version 32 bits             */

} elf_dyn;


#define ELF_DYN(fmt, dyn, fld) (fmt->is_32b ? (dyn).dyn32.fld : (dyn).dyn64.fld)

#define ELF_SIZEOF_DYN(fmt) (fmt->is_32b ? sizeof(elf32_dyn) : sizeof(elf64_dyn))



/* Valeurs possibles pour d_tag */

#define DT_NULL         0               /* Marque de fin de section        */
#define DT_NEEDED       1               /* Nom d'une dépendance            */
#define DT_PLTRELSZ     2               /* Taille des relocation PLT       */
#define DT_PLTGOT       3               /* Valeur spécifique au processeur */
#define DT_HASH         4               /* Adresse de la table d'empreintes*/
#define DT_STRTAB       5               /* Adresse de la table des chaînes */
#define DT_SYMTAB       6               /* Adresse de la table des symboles*/
#define DT_RELA         7               /* Adresse des relocations Rela    */
#define DT_RELASZ       8               /* Taille totale de ces relocations*/
#define DT_RELAENT      9               /* Taille d'une relocation Rela    */
#define DT_STRSZ        10              /* Taille de la table de chaînes   */
#define DT_SYMENT       11              /* Taille d'un élément des symboles*/
#define DT_INIT         12              /* Adresse de fonction init        */
#define DT_FINI         13              /* Adresse de fonction fini        */
#define DT_SONAME       14              /* Nom d'un objet partagé          */
#define DT_RPATH        15              /* Chemin de recherche (déprécié)  */
#define DT_SYMBOLIC     16              /* Départ de recherche de symbole  */
#define DT_REL          17              /* Adresse des relocations Rel     */
#define DT_RELSZ        18              /* Taille totale de ces relocations*/
#define DT_RELENT       19              /* Taille d'une relocation Rel     */
#define DT_PLTREL       20              /* Type de relocation dans PLT     */
#define DT_DEBUG        21              /* Pour le débogage ; ???          */
#define DT_TEXTREL      22              /* Les relocs. peuvent maj le code */
#define DT_JMPREL       23              /* Adresse des relocations PLT     */
#define DT_BIND_NOW     24              /* Force la relocation des objets  */
#define DT_INIT_ARRAY   25              /* Tableau de fonctions init       */
#define DT_FINI_ARRAY   26              /* Tableau de fonctions fini       */
#define DT_INIT_ARRAYSZ 27              /* Taille de DT_INIT_ARRAY         */
#define DT_FINI_ARRAYSZ 28              /* Taille de DT_FINI_ARRAY         */
#define DT_RUNPATH      29              /* Chemin de recherche             */
#define DT_FLAGS        30              /* Fanions pour le chargement      */
#define DT_ENCODING     32              /* Départ d'encodage               */
#define DT_PREINIT_ARRAY 32             /* Tableau de fonctions preinit    */
#define DT_PREINIT_ARRAYSZ 33           /* Taille de DT_PREINIT_ARRAY      */
#define DT_NUM          34              /* Nombre utilisé                  */

#define DT_GNU_HASH     0x6ffffef5      /* Table d'empreintes version GNU  */



/* ---------------------------- SYMBOLES DE BINAIRES ELF ---------------------------- */


/* Elément de la table des symboles */

typedef struct _elf32_sym
{
    uint32_t st_name;                       /* Indice pour le nom          */
    uint32_t st_value;                      /* Valeur du symbole           */
    uint32_t st_size;                       /* Taille du symbole           */
    unsigned char st_info;                  /* Type et infos. du symbole   */
    unsigned char st_other;                 /* Visibilité du symbole       */
    uint16_t st_shndx;                      /* Indice de la section        */

} elf32_sym;

typedef struct _elf64_sym
{
    uint32_t st_name;                       /* Indice pour le nom          */
    unsigned char st_info;                  /* Type et infos. du symbole   */
    unsigned char st_other;                 /* Visibilité du symbole       */
    uint16_t st_shndx;                      /* Indice de la section        */
    uint64_t st_value;                      /* Valeur du symbole           */
    uint64_t st_size;                       /* Taille du symbole           */

} elf64_sym;

typedef union _elf_sym
{
    elf32_sym sym32;                        /* Version 32 bits             */
    elf64_sym sym64;                        /* Version 64 bits             */

} elf_sym;


#define ELF_SYM(fmt, sb, fld) (fmt->is_32b ? (sb).sym32.fld : (sb).sym64.fld)

#define ELF_ST_BIND(fmt, sym) (fmt->is_32b ? ELF32_ST_BIND(sym.sym32.st_info) : ELF64_ST_BIND(sym.sym64.st_info))
#define ELF_ST_TYPE(fmt, sym) (fmt->is_32b ? ELF32_ST_TYPE(sym.sym32.st_info) : ELF64_ST_TYPE(sym.sym64.st_info))

#define ELF_SIZEOF_SYM(fmt) (fmt->is_32b ? sizeof(elf32_sym) : sizeof(elf64_sym))


/* Extraction des informations de st_info */

#define ELF32_ST_BIND(val)      (((unsigned char)(val)) >> 4)
#define ELF32_ST_TYPE(val)      ((val) & 0xf)

#define ELF64_ST_BIND(val)      ELF32_ST_BIND(val)
#define ELF64_ST_TYPE(val)      ELF32_ST_TYPE(val)

/* Valeurs pour le sous-champ ST_TYPE de st_info  */

#define STT_NOTYPE  0                       /* Type de symbole non spécifié*/
#define STT_OBJECT  1                       /* Symbole, objet de données   */
#define STT_FUNC    2                       /* Symbole, objet de code      */



/* ------------------------- INFORMATIONS DE RELOCALISATION ------------------------- */


/* Entrée de la table de relocalisation */

typedef struct _elf32_rel
{
    uint32_t r_offset;                      /* Adresse                     */
    uint32_t r_info;			            /* Indice de type et symbole   */

} elf32_rel;

typedef struct _elf64_rel
{
    uint64_t r_offset;                      /* Adresse                     */
    uint64_t r_info;			            /* Indice de type et symbole   */

} elf64_rel;

typedef union _elf_rel
{
    elf32_rel rel32;                        /* Version 32 bits             */
    elf64_rel rel64;                        /* Version 64 bits             */

} elf_rel;


#define ELF_REL(fmt, rl, fld) (fmt->is_32b ? (rl).rel32.fld : (rl).rel64.fld)

#define ELF_REL_SYM(fmt, rl) (fmt->is_32b ? ELF32_R_SYM((rl).rel32.r_info) : ELF64_R_SYM((rl).rel64.r_info))
#define ELF_REL_TYPE(fmt, rl) (fmt->is_32b ? ELF32_R_TYPE((rl).rel32.r_info) : ELF64_R_TYPE((rl).rel64.r_info))

#define ELF_SIZEOF_REL(fmt) (fmt->is_32b ? sizeof(elf32_rel) : sizeof(elf64_rel))


/* Extraction des informations de r_info */

#define ELF32_R_SYM(val)        ((val) >> 8)
#define ELF32_R_TYPE(val)       ((val) & 0xff)

#define ELF64_R_SYM(val)        ((val) >> 32)
#define ELF64_R_TYPE(val)       ((val) & 0xffffffff)

/* Type de relocalisation (x86) */

#define R_386_NONE          0               /* Pas de relocalisation       */
#define R_386_JMP_SLOT      7               /* Entrée PLT                  */

/* Type de relocalisation (ARM) */

#define R_ARM_JUMP_SLOT         22          /* Create PLT entry */



/* --------------------------- NOTES ARBITRAIRES LAISSEES --------------------------- */


/**
 * Notes contenues dans un fichier ELF.
 * Se rapporter au chapitre 5, partie "Note Section", des spécifications ABI
 * du Système V pour d'avantage d'informations.
 */

typedef struct _elf_note
{
    uint32_t namesz;                        /* Taille du nom éventuel      */
    uint32_t descsz;                        /* Qté de données éventuelles  */
    uint32_t type;                          /* Indication supplémentaire   */

    const char *name;                       /* Auteur de la note           */
    const void *desc;                       /* Données complémentaires     */

} elf_note;



#endif  /* _PLUGINS_ELF_ELF_DEF_H */
