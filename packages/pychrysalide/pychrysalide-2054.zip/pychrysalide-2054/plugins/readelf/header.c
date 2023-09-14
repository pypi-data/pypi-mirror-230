
/* Chrysalide - Outil d'analyse de fichiers binaires
 * header.c - annotation des en-têtes de binaires ELF
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


#include "header.h"


#include <plugins/elf/format.h>
#include <plugins/fmtp/parser.h>



/* Définition des champs */

static field_desc_switch _elf_classes[] = {

    { .fixed = EV_NONE,    .desc = __("File class: invalid") },
    { .fixed = ELFCLASS32, .desc = __("File class: 32-bit objects") },
    { .fixed = ELFCLASS64, .desc = __("File class: 64-bit objects") }

};

static field_desc_switch _elf_data[] = {

    { .fixed = ELFDATANONE, .desc = __("Data encoding: invalid") },
    { .fixed = ELFDATA2LSB, .desc = __("Data encoding: 2's complement, little endian") },
    { .fixed = ELFDATA2MSB, .desc = __("Data encoding: 2's complement, big endian") }

};

static field_desc_switch _elf_versions[] = {

    { .fixed = EV_NONE,    .desc = __("File version: invalid") },
    { .fixed = EV_CURRENT, .desc = __("File version: current") }

};

static field_desc_switch _elf_os_abis[] = {

    { .fixed = ELFOSABI_SYSV,       .desc = __("OS ABI: UNIX System V ABI") },
    { .fixed = ELFOSABI_HPUX,       .desc = __("OS ABI: HP-UX") },
    { .fixed = ELFOSABI_NETBSD,     .desc = __("OS ABI: NetBSD") },
    { .fixed = ELFOSABI_GNU,        .desc = __("OS ABI: Object uses GNU ELF extensions") },
    { .fixed = ELFOSABI_SOLARIS,    .desc = __("OS ABI: Sun Solaris") },
    { .fixed = ELFOSABI_AIX,        .desc = __("OS ABI: IBM AIX") },
    { .fixed = ELFOSABI_IRIX,       .desc = __("OS ABI: SGI Irix") },
    { .fixed = ELFOSABI_FREEBSD,    .desc = __("OS ABI: FreeBSD") },
    { .fixed = ELFOSABI_TRU64,      .desc = __("OS ABI: Compaq TRU64 UNIX") },
    { .fixed = ELFOSABI_MODESTO,    .desc = __("OS ABI: Novell Modesto") },
    { .fixed = ELFOSABI_OPENBSD,    .desc = __("OS ABI: OpenBSD") },
    { .fixed = ELFOSABI_ARM_AEABI,  .desc = __("OS ABI: ARM EABI") },
    { .fixed = ELFOSABI_ARM,        .desc = __("OS ABI: ARM") },
    { .fixed = ELFOSABI_STANDALONE, .desc = __("OS ABI: Standalone (embedded) application") }

};

static field_desc_switch _elf_types[] = {

    { .fixed = ET_NONE, .desc = __("Object file type: no file type") },
    { .fixed = ET_REL,  .desc = __("Object file type: relocatable file") },
    { .fixed = ET_EXEC, .desc = __("Object file type: executable file") },
    { .fixed = ET_DYN,  .desc = __("Object file type: shared object file") },
    { .fixed = ET_CORE, .desc = __("Object file type: core file") },
    { .lower = ET_LOOS,   .upper = ET_HIOS,   .desc = __("Object file type: OS-specific") },
    { .lower = ET_LOPROC, .upper = ET_HIPROC, .desc = __("Object file type: processor-specific") }

};

static field_desc_switch _elf_machines[] = {

    { .fixed = EM_NONE,        .desc = __("Architecture: No machine") },
    { .fixed = EM_M32,         .desc = __("Architecture: AT&T WE 32100") },
    { .fixed = EM_SPARC,       .desc = __("Architecture: SUN SPARC") },
    { .fixed = EM_386,         .desc = __("Architecture: Intel 80386") },
    { .fixed = EM_68K,         .desc = __("Architecture: Motorola m68k family") },
    { .fixed = EM_88K,         .desc = __("Architecture: Motorola m88k family") },
    { .fixed = EM_860,         .desc = __("Architecture: Intel 80860") },
    { .fixed = EM_MIPS,        .desc = __("Architecture: MIPS R3000 big-endian") },
    { .fixed = EM_S370,        .desc = __("Architecture: IBM System/370") },
    { .fixed = EM_MIPS_RS3_LE, .desc = __("Architecture: MIPS R3000 little-endian") },
    { .fixed = EM_PARISC,      .desc = __("Architecture: HPPA") },
    { .fixed = EM_VPP500,      .desc = __("Architecture: Fujitsu VPP500") },
    { .fixed = EM_SPARC32PLUS, .desc = __("Architecture: Sun's \"v8plus\"") },
    { .fixed = EM_960,         .desc = __("Architecture: Intel 80960") },
    { .fixed = EM_PPC,         .desc = __("Architecture: PowerPC") },
    { .fixed = EM_PPC64,       .desc = __("Architecture: PowerPC 64-bit") },
    { .fixed = EM_S390,        .desc = __("Architecture: IBM S390") },
    { .fixed = EM_V800,        .desc = __("Architecture: NEC V800 series") },
    { .fixed = EM_FR20,        .desc = __("Architecture: Fujitsu FR20") },
    { .fixed = EM_RH32,        .desc = __("Architecture: TRW RH-32") },
    { .fixed = EM_RCE,         .desc = __("Architecture: Motorola RCE") },
    { .fixed = EM_ARM,         .desc = __("Architecture: ARM") },
    { .fixed = EM_FAKE_ALPHA,  .desc = __("Architecture: Digital Alpha") },
    { .fixed = EM_SH,          .desc = __("Architecture: Hitachi SH") },
    { .fixed = EM_SPARCV9,     .desc = __("Architecture: SPARC v9 64-bit") },
    { .fixed = EM_TRICORE,     .desc = __("Architecture: Siemens Tricore") },
    { .fixed = EM_ARC,         .desc = __("Architecture: Argonaut RISC Core") },
    { .fixed = EM_H8_300,      .desc = __("Architecture: Hitachi H8/300") },
    { .fixed = EM_H8_300H,     .desc = __("Architecture: Hitachi H8/300H") },
    { .fixed = EM_H8S,         .desc = __("Architecture: Hitachi H8S") },
    { .fixed = EM_H8_500,      .desc = __("Architecture: Hitachi H8/500") },
    { .fixed = EM_IA_64,       .desc = __("Architecture: Intel Merced") },
    { .fixed = EM_MIPS_X,      .desc = __("Architecture: Stanford MIPS-X") },
    { .fixed = EM_COLDFIRE,    .desc = __("Architecture: Motorola Coldfire") },
    { .fixed = EM_68HC12,      .desc = __("Architecture: Motorola M68HC12") },
    { .fixed = EM_MMA,         .desc = __("Architecture: Fujitsu MMA Multimedia Accelerator") },
    { .fixed = EM_PCP,         .desc = __("Architecture: Siemens PCP") },
    { .fixed = EM_NCPU,        .desc = __("Architecture: Sony nCPU embeeded RISC") },
    { .fixed = EM_NDR1,        .desc = __("Architecture: Denso NDR1 microprocessor") },
    { .fixed = EM_STARCORE,    .desc = __("Architecture: Motorola Start*Core processor") },
    { .fixed = EM_ME16,        .desc = __("Architecture: Toyota ME16 processor") },
    { .fixed = EM_ST100,       .desc = __("Architecture: STMicroelectronic ST100 processor") },
    { .fixed = EM_TINYJ,       .desc = __("Architecture: Advanced Logic Corp. Tinyj emb.fam") },
    { .fixed = EM_X86_64,      .desc = __("Architecture: AMD x86-64 architecture") },
    { .fixed = EM_PDSP,        .desc = __("Architecture: Sony DSP Processor") },
    { .fixed = EM_FX66,        .desc = __("Architecture: Siemens FX66 microcontroller") },
    { .fixed = EM_ST9PLUS,     .desc = __("Architecture: STMicroelectronics ST9+ 8/16 mc") },
    { .fixed = EM_ST7,         .desc = __("Architecture: STmicroelectronics ST7 8 bit mc") },
    { .fixed = EM_68HC16,      .desc = __("Architecture: Motorola MC68HC16 microcontroller") },
    { .fixed = EM_68HC11,      .desc = __("Architecture: Motorola MC68HC11 microcontroller") },
    { .fixed = EM_68HC08,      .desc = __("Architecture: Motorola MC68HC08 microcontroller") },
    { .fixed = EM_68HC05,      .desc = __("Architecture: Motorola MC68HC05 microcontroller") },
    { .fixed = EM_SVX,         .desc = __("Architecture: Silicon Graphics SVx") },
    { .fixed = EM_ST19,        .desc = __("Architecture: STMicroelectronics ST19 8 bit mc") },
    { .fixed = EM_VAX,         .desc = __("Architecture: Digital VAX") },
    { .fixed = EM_CRIS,        .desc = __("Architecture: Axis Communications 32-bit embedded processor") },
    { .fixed = EM_JAVELIN,     .desc = __("Architecture: Infineon Technologies 32-bit embedded processor") },
    { .fixed = EM_FIREPATH,    .desc = __("Architecture: Element 14 64-bit DSP Processor") },
    { .fixed = EM_ZSP,         .desc = __("Architecture: LSI Logic 16-bit DSP Processor") },
    { .fixed = EM_MMIX,        .desc = __("Architecture: Donald Knuth's educational 64-bit processor") },
    { .fixed = EM_HUANY,       .desc = __("Architecture: Harvard University machine-independent object files") },
    { .fixed = EM_PRISM,       .desc = __("Architecture: SiTera Prism") },
    { .fixed = EM_AVR,         .desc = __("Architecture: Atmel AVR 8-bit microcontroller") },
    { .fixed = EM_FR30,        .desc = __("Architecture: Fujitsu FR30") },
    { .fixed = EM_D10V,        .desc = __("Architecture: Mitsubishi D10V") },
    { .fixed = EM_D30V,        .desc = __("Architecture: Mitsubishi D30V") },
    { .fixed = EM_V850,        .desc = __("Architecture: NEC v850") },
    { .fixed = EM_M32R,        .desc = __("Architecture: Mitsubishi M32R") },
    { .fixed = EM_MN10300,     .desc = __("Architecture: Matsushita MN10300") },
    { .fixed = EM_MN10200,     .desc = __("Architecture: Matsushita MN10200") },
    { .fixed = EM_PJ,          .desc = __("Architecture: picoJava") },
    { .fixed = EM_OPENRISC,    .desc = __("Architecture: OpenRISC 32-bit embedded processor") },
    { .fixed = EM_ARC_A5,      .desc = __("Architecture: ARC Cores Tangent-A5") },
    { .fixed = EM_XTENSA,      .desc = __("Architecture: Tensilica Xtensa Architecture") },
    { .fixed = EM_AARCH64,     .desc = __("Architecture: ARM AARCH64") },
    { .fixed = EM_TILEPRO,     .desc = __("Architecture: Tilera TILEPro") },
    { .fixed = EM_MICROBLAZE,  .desc = __("Architecture: Xilinx MicroBlaze") },
    { .fixed = EM_TILEGX,      .desc = __("Architecture: Tilera TILE-Gx") }

};

static fmt_field_def _elf_header_base[] = {

    {
        .name = "e_ident[EI_MAG]",

        .size = MDS_8_BITS,
        .repeat = 4,

        DISPLAY_RULES(IOD_HEX, IOD_CHAR, IOD_CHAR, IOD_CHAR),

        PLAIN_COMMENT(__("ELF magic number"))

    },

    {
        .name = "e_ident[EI_CLASS]",

        .size = MDS_8_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_elf_classes, __("File class: unknown"))

    },

    {
        .name = "e_ident[EI_DATA]",

        .size = MDS_8_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_elf_data, __("Data encoding: unknown"))

    },

    {
        .name = "e_ident[EI_VERSION]",

        .size = MDS_8_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_elf_versions, __("File version: unknown"))

    },

    {
        .name = "e_ident[EI_OSABI]",

        .size = MDS_8_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_elf_os_abis, __("OS ABI: unknown"))

    },

    {
        .name = "e_ident[EI_ABIVERSION]",

        .size = MDS_8_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("ABI version"))

    },

    {
        .name = "...",

        .size = MDS_8_BITS,
        .repeat = 7,

        .is_padding = true,

        PLAIN_COMMENT(__("Padding"))

    },

    {
        .name = "e_type",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_elf_types, __("Object file type: unkown"))

    },

    {
        .name = "e_machine",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_elf_machines, __("Architecture: unknown"))

    },

    {
        .name = "e_version",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Object file version"))

    }

};

static fmt_field_def _elf_header_offset_32[] = {

    {
        .name = "e_entry",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Entry point virtual address"))

    },

    {
        .name = "e_phoff",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Program header table file offset"))

    },

    {
        .name = "e_shoff",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section header table file offset"))

    }

};

static fmt_field_def _elf_header_offset_64[] = {

    {
        .name = "e_entry",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Entry point virtual address"))

    },

    {
        .name = "e_phoff",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Program header table file offset"))

    },

    {
        .name = "e_shoff",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section header table file offset"))

    }

};

static fmt_field_def _elf_header_ending[] = {

    {
        .name = "e_flags",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Processor-specific flags"))

    },

    {
        .name = "e_ehsize",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("ELF header size in bytes"))

    },

    {
        .name = "e_phentsize",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Program header table entry size"))

    },

    {
        .name = "e_phnum",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Program header table entry count"))

    },

    {
        .name = "e_shentsize",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Section header table entry size"))

    },

    {
        .name = "e_shnum",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Section header table entry count"))

    },

    {
        .name = "e_shstrndx",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Section header string table index"))

    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                                                                             *
*  Description : Charge tous les symboles de l'en-tête ELF.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_elf_header(GBinFormat *format, GPreloadInfo *info)
{
    bool result;                            /* Bilan à retourner           */
    const elf_header *header;               /* En-tête principale          */
    vmpa2t pos;                             /* Tête de lecture des symboles*/

    header = g_elf_format_get_header(G_ELF_FORMAT(format));

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), 0, &pos);

    if (result)
        result = parse_field_definitions(PARSING_DEFS(_elf_header_base), format, info, &pos, NULL);

    if (result)
    {
        if (header->hdr32.e_ident[EI_CLASS] == ELFCLASS32)
            result = parse_field_definitions(PARSING_DEFS(_elf_header_offset_32), format, info, &pos, NULL);

        else if (header->hdr32.e_ident[EI_CLASS] == ELFCLASS64)
            result = parse_field_definitions(PARSING_DEFS(_elf_header_offset_64), format, info, &pos, NULL);

        else
            result = false;

    }

    if (result)
        result = parse_field_definitions(PARSING_DEFS(_elf_header_ending), format, info, &pos, NULL);

    return result;

}
