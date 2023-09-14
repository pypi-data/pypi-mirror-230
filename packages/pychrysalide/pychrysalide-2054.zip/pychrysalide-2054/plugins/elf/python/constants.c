
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - équivalent Python partiel du fichier "plugins/elf/elf_def.h"
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "constants.h"


#include <plugins/pychrysalide/helpers.h>


#include "../elf_def.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour le format Elf.                   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_python_elf_format_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    result = true;

    /**
     * En-tête de fichier ELF (32 et 64 bits)
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "EI_MAG0", EI_MAG0);
    if (result) result = add_const_to_group(values, "EI_MAG1", EI_MAG1);
    if (result) result = add_const_to_group(values, "EI_MAG2", EI_MAG2);
    if (result) result = add_const_to_group(values, "EI_MAG3", EI_MAG3);
    if (result) result = add_const_to_group(values, "EI_CLASS", EI_CLASS);
    if (result) result = add_const_to_group(values, "EI_DATA", EI_DATA);
    if (result) result = add_const_to_group(values, "EI_VERSION", EI_VERSION);
    if (result) result = add_const_to_group(values, "EI_OSABI", EI_OSABI);
    if (result) result = add_const_to_group(values, "EI_ABIVERSION", EI_ABIVERSION);
    if (result) result = add_const_to_group(values, "EI_PAD", EI_PAD);
    if (result) result = add_const_to_group(values, "EI_NIDENT", EI_NIDENT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfHeaderIdent", values,
                                            "Positions of information inside the *e_ident* field of ELF headers.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "ELFCLASSNONE", ELFCLASSNONE);
    if (result) result = add_const_to_group(values, "ELFCLASS32", ELFCLASS32);
    if (result) result = add_const_to_group(values, "ELFCLASS64", ELFCLASS64);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfClassIdent", values,
                                            "Class of ELF file formats at position *EI_CLASS*.");
    values = PyDict_New();

    if (result) result = add_const_to_group(values, "ELFDATANONE", ELFDATANONE);
    if (result) result = add_const_to_group(values, "ELFDATA2LSB", ELFDATA2LSB);
    if (result) result = add_const_to_group(values, "ELFDATA2MSB", ELFDATA2MSB);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfEndiannessIdent", values,
                                            "Endianness of ELF file formats at position *EI_DATA*.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "EV_NONE", EV_NONE);
    if (result) result = add_const_to_group(values, "EV_CURRENT", EV_CURRENT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfVersionIdent", values,
                                            "Version of ELF file formats at position *EI_VERSION*.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "ELFOSABI_NONE", ELFOSABI_NONE);
    if (result) result = add_const_to_group(values, "ELFOSABI_SYSV", ELFOSABI_SYSV);
    if (result) result = add_const_to_group(values, "ELFOSABI_HPUX", ELFOSABI_HPUX);
    if (result) result = add_const_to_group(values, "ELFOSABI_NETBSD", ELFOSABI_NETBSD);
    if (result) result = add_const_to_group(values, "ELFOSABI_GNU", ELFOSABI_GNU);
    if (result) result = add_const_to_group(values, "ELFOSABI_LINUX", ELFOSABI_LINUX);
    if (result) result = add_const_to_group(values, "ELFOSABI_SOLARIS", ELFOSABI_SOLARIS);
    if (result) result = add_const_to_group(values, "ELFOSABI_AIX", ELFOSABI_AIX);
    if (result) result = add_const_to_group(values, "ELFOSABI_IRIX", ELFOSABI_IRIX);
    if (result) result = add_const_to_group(values, "ELFOSABI_FREEBSD", ELFOSABI_FREEBSD);
    if (result) result = add_const_to_group(values, "ELFOSABI_TRU64", ELFOSABI_TRU64);
    if (result) result = add_const_to_group(values, "ELFOSABI_MODESTO", ELFOSABI_MODESTO);
    if (result) result = add_const_to_group(values, "ELFOSABI_OPENBSD", ELFOSABI_OPENBSD);
    if (result) result = add_const_to_group(values, "ELFOSABI_ARM_AEABI", ELFOSABI_ARM_AEABI);
    if (result) result = add_const_to_group(values, "ELFOSABI_ARM", ELFOSABI_ARM);
    if (result) result = add_const_to_group(values, "ELFOSABI_STANDALONE", ELFOSABI_STANDALONE);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfAbiIdent", values,
                                            "ABI of ELF file formats at position *EI_OSABI*.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "ET_NONE", ET_NONE);
    if (result) result = add_const_to_group(values, "ET_REL", ET_REL);
    if (result) result = add_const_to_group(values, "ET_EXEC", ET_EXEC);
    if (result) result = add_const_to_group(values, "ET_DYN", ET_DYN);
    if (result) result = add_const_to_group(values, "ET_CORE", ET_CORE);
    if (result) result = add_const_to_group(values, "ET_LOOS", ET_LOOS);
    if (result) result = add_const_to_group(values, "ET_HIOS", ET_HIOS);
    if (result) result = add_const_to_group(values, "ET_LOPROC", ET_LOPROC);
    if (result) result = add_const_to_group(values, "ET_HIPROC", ET_HIPROC);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfHeaderType", values,
                                            "Type available in the *e_type* field of ELF headers.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "EM_NONE", EM_NONE);
    if (result) result = add_const_to_group(values, "EM_M32", EM_M32);
    if (result) result = add_const_to_group(values, "EM_SPARC", EM_SPARC);
    if (result) result = add_const_to_group(values, "EM_386", EM_386);
    if (result) result = add_const_to_group(values, "EM_68K", EM_68K);
    if (result) result = add_const_to_group(values, "EM_88K", EM_88K);
    if (result) result = add_const_to_group(values, "EM_860", EM_860);
    if (result) result = add_const_to_group(values, "EM_MIPS", EM_MIPS);
    if (result) result = add_const_to_group(values, "EM_S370", EM_S370);
    if (result) result = add_const_to_group(values, "EM_MIPS_RS3_LE", EM_MIPS_RS3_LE);
    if (result) result = add_const_to_group(values, "EM_PARISC", EM_PARISC);
    if (result) result = add_const_to_group(values, "EM_VPP500", EM_VPP500);
    if (result) result = add_const_to_group(values, "EM_SPARC32PLUS", EM_SPARC32PLUS);
    if (result) result = add_const_to_group(values, "EM_960", EM_960);
    if (result) result = add_const_to_group(values, "EM_PPC", EM_PPC);
    if (result) result = add_const_to_group(values, "EM_PPC64", EM_PPC64);
    if (result) result = add_const_to_group(values, "EM_S390", EM_S390);
    if (result) result = add_const_to_group(values, "EM_V800", EM_V800);
    if (result) result = add_const_to_group(values, "EM_FR20", EM_FR20);
    if (result) result = add_const_to_group(values, "EM_RH32", EM_RH32);
    if (result) result = add_const_to_group(values, "EM_RCE", EM_RCE);
    if (result) result = add_const_to_group(values, "EM_ARM", EM_ARM);
    if (result) result = add_const_to_group(values, "EM_FAKE_ALPHA", EM_FAKE_ALPHA);
    if (result) result = add_const_to_group(values, "EM_SH", EM_SH);
    if (result) result = add_const_to_group(values, "EM_SPARCV9", EM_SPARCV9);
    if (result) result = add_const_to_group(values, "EM_TRICORE", EM_TRICORE);
    if (result) result = add_const_to_group(values, "EM_ARC", EM_ARC);
    if (result) result = add_const_to_group(values, "EM_H8_300", EM_H8_300);
    if (result) result = add_const_to_group(values, "EM_H8_300H", EM_H8_300H);
    if (result) result = add_const_to_group(values, "EM_H8S", EM_H8S);
    if (result) result = add_const_to_group(values, "EM_H8_500", EM_H8_500);
    if (result) result = add_const_to_group(values, "EM_IA_64", EM_IA_64);
    if (result) result = add_const_to_group(values, "EM_MIPS_X", EM_MIPS_X);
    if (result) result = add_const_to_group(values, "EM_COLDFIRE", EM_COLDFIRE);
    if (result) result = add_const_to_group(values, "EM_68HC12", EM_68HC12);
    if (result) result = add_const_to_group(values, "EM_MMA", EM_MMA);
    if (result) result = add_const_to_group(values, "EM_PCP", EM_PCP);
    if (result) result = add_const_to_group(values, "EM_NCPU", EM_NCPU);
    if (result) result = add_const_to_group(values, "EM_NDR1", EM_NDR1);
    if (result) result = add_const_to_group(values, "EM_STARCORE", EM_STARCORE);
    if (result) result = add_const_to_group(values, "EM_ME16", EM_ME16);
    if (result) result = add_const_to_group(values, "EM_ST100", EM_ST100);
    if (result) result = add_const_to_group(values, "EM_TINYJ", EM_TINYJ);
    if (result) result = add_const_to_group(values, "EM_X86_64", EM_X86_64);
    if (result) result = add_const_to_group(values, "EM_PDSP", EM_PDSP);
    if (result) result = add_const_to_group(values, "EM_FX66", EM_FX66);
    if (result) result = add_const_to_group(values, "EM_ST9PLUS", EM_ST9PLUS);
    if (result) result = add_const_to_group(values, "EM_ST7", EM_ST7);
    if (result) result = add_const_to_group(values, "EM_68HC16", EM_68HC16);
    if (result) result = add_const_to_group(values, "EM_68HC11", EM_68HC11);
    if (result) result = add_const_to_group(values, "EM_68HC08", EM_68HC08);
    if (result) result = add_const_to_group(values, "EM_68HC05", EM_68HC05);
    if (result) result = add_const_to_group(values, "EM_SVX", EM_SVX);
    if (result) result = add_const_to_group(values, "EM_ST19", EM_ST19);
    if (result) result = add_const_to_group(values, "EM_VAX", EM_VAX);
    if (result) result = add_const_to_group(values, "EM_CRIS", EM_CRIS);
    if (result) result = add_const_to_group(values, "EM_JAVELIN", EM_JAVELIN);
    if (result) result = add_const_to_group(values, "EM_FIREPATH", EM_FIREPATH);
    if (result) result = add_const_to_group(values, "EM_ZSP", EM_ZSP);
    if (result) result = add_const_to_group(values, "EM_MMIX", EM_MMIX);
    if (result) result = add_const_to_group(values, "EM_HUANY", EM_HUANY);
    if (result) result = add_const_to_group(values, "EM_PRISM", EM_PRISM);
    if (result) result = add_const_to_group(values, "EM_AVR", EM_AVR);
    if (result) result = add_const_to_group(values, "EM_FR30", EM_FR30);
    if (result) result = add_const_to_group(values, "EM_D10V", EM_D10V);
    if (result) result = add_const_to_group(values, "EM_D30V", EM_D30V);
    if (result) result = add_const_to_group(values, "EM_V850", EM_V850);
    if (result) result = add_const_to_group(values, "EM_M32R", EM_M32R);
    if (result) result = add_const_to_group(values, "EM_MN10300", EM_MN10300);
    if (result) result = add_const_to_group(values, "EM_MN10200", EM_MN10200);
    if (result) result = add_const_to_group(values, "EM_PJ", EM_PJ);
    if (result) result = add_const_to_group(values, "EM_OPENRISC", EM_OPENRISC);
    if (result) result = add_const_to_group(values, "EM_ARC_A5", EM_ARC_A5);
    if (result) result = add_const_to_group(values, "EM_XTENSA", EM_XTENSA);
    if (result) result = add_const_to_group(values, "EM_AARCH64", EM_AARCH64);
    if (result) result = add_const_to_group(values, "EM_TILEPRO", EM_TILEPRO);
    if (result) result = add_const_to_group(values, "EM_MICROBLAZE", EM_MICROBLAZE);
    if (result) result = add_const_to_group(values, "EM_TILEGX", EM_TILEGX);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfHeaderMachine", values,
                                            "Value inside the *e_machine* field of ELF headers.");

    /**
     * En-tête des programmes Elf
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "PT_NULL", PT_NULL);
    if (result) result = add_const_to_group(values, "PT_LOAD", PT_LOAD);
    if (result) result = add_const_to_group(values, "PT_DYNAMIC", PT_DYNAMIC);
    if (result) result = add_const_to_group(values, "PT_INTERP", PT_INTERP);
    if (result) result = add_const_to_group(values, "PT_NOTE", PT_NOTE);
    if (result) result = add_const_to_group(values, "PT_SHLIB", PT_SHLIB);
    if (result) result = add_const_to_group(values, "PT_PHDR", PT_PHDR);
    if (result) result = add_const_to_group(values, "PT_TLS", PT_TLS);
    if (result) result = add_const_to_group(values, "PT_NUM", PT_NUM);
    if (result) result = add_const_to_group(values, "PT_LOOS", PT_LOOS);
    if (result) result = add_const_to_group(values, "PT_GNU_EH_FRAME", PT_GNU_EH_FRAME);
    if (result) result = add_const_to_group(values, "PT_GNU_STACK", PT_GNU_STACK);
    if (result) result = add_const_to_group(values, "PT_GNU_RELRO", PT_GNU_RELRO);
    if (result) result = add_const_to_group(values, "PT_LOSUNW", PT_LOSUNW);
    if (result) result = add_const_to_group(values, "PT_SUNWBSS", PT_SUNWBSS);
    if (result) result = add_const_to_group(values, "PT_SUNWSTACK", PT_SUNWSTACK);
    if (result) result = add_const_to_group(values, "PT_HISUNW", PT_HISUNW);
    if (result) result = add_const_to_group(values, "PT_HIOS", PT_HIOS);
    if (result) result = add_const_to_group(values, "PT_LOPROC", PT_LOPROC);
    if (result) result = add_const_to_group(values, "PT_HIPROC", PT_HIPROC);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfProgramHeaderType", values,
                                            "Value inside the *p_type* field of ELF program headers.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "PF_X", PF_X);
    if (result) result = add_const_to_group(values, "PF_W", PF_W);
    if (result) result = add_const_to_group(values, "PF_R", PF_R);
    if (result) result = add_const_to_group(values, "PF_MASKOS", PF_MASKOS);
    if (result) result = add_const_to_group(values, "PF_MASKPROC", PF_MASKPROC);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfProgramHeaderFlags", values,
                                            "Value inside the *p_flags* field of ELF program headers.");

    /**
     * En-tête des sections Elf
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "SHT_NULL", SHT_NULL);
    if (result) result = add_const_to_group(values, "SHT_PROGBITS", SHT_PROGBITS);
    if (result) result = add_const_to_group(values, "SHT_SYMTAB", SHT_SYMTAB);
    if (result) result = add_const_to_group(values, "SHT_STRTAB", SHT_STRTAB);
    if (result) result = add_const_to_group(values, "SHT_RELA", SHT_RELA);
    if (result) result = add_const_to_group(values, "SHT_HASH", SHT_HASH);
    if (result) result = add_const_to_group(values, "SHT_DYNAMIC", SHT_DYNAMIC);
    if (result) result = add_const_to_group(values, "SHT_NOTE", SHT_NOTE);
    if (result) result = add_const_to_group(values, "SHT_NOBITS", SHT_NOBITS);
    if (result) result = add_const_to_group(values, "SHT_REL", SHT_REL);
    if (result) result = add_const_to_group(values, "SHT_SHLIB", SHT_SHLIB);
    if (result) result = add_const_to_group(values, "SHT_DYNSYM", SHT_DYNSYM);
    if (result) result = add_const_to_group(values, "SHT_INIT_ARRAY", SHT_INIT_ARRAY);
    if (result) result = add_const_to_group(values, "SHT_FINI_ARRAY", SHT_FINI_ARRAY);
    if (result) result = add_const_to_group(values, "SHT_PREINIT_ARRAY", SHT_PREINIT_ARRAY);
    if (result) result = add_const_to_group(values, "SHT_GROUP", SHT_GROUP);
    if (result) result = add_const_to_group(values, "SHT_SYMTAB_SHNDX", SHT_SYMTAB_SHNDX);
    if (result) result = add_const_to_group(values, "SHT_NUM", SHT_NUM);
    if (result) result = add_const_to_group(values, "SHT_LOOS", SHT_LOOS);
    if (result) result = add_const_to_group(values, "SHT_GNU_ATTRIBUTES", SHT_GNU_ATTRIBUTES);
    if (result) result = add_const_to_group(values, "SHT_GNU_HASH", SHT_GNU_HASH);
    if (result) result = add_const_to_group(values, "SHT_GNU_LIBLIST", SHT_GNU_LIBLIST);
    if (result) result = add_const_to_group(values, "SHT_CHECKSUM", SHT_CHECKSUM);
    if (result) result = add_const_to_group(values, "SHT_LOSUNW", SHT_LOSUNW);
    if (result) result = add_const_to_group(values, "SHT_SUNW_move", SHT_SUNW_move);
    if (result) result = add_const_to_group(values, "SHT_SUNW_COMDAT", SHT_SUNW_COMDAT);
    if (result) result = add_const_to_group(values, "SHT_SUNW_syminfo", SHT_SUNW_syminfo);
    if (result) result = add_const_to_group(values, "SHT_GNU_verdef", SHT_GNU_verdef);
    if (result) result = add_const_to_group(values, "SHT_GNU_verneed", SHT_GNU_verneed);
    if (result) result = add_const_to_group(values, "SHT_GNU_versym", SHT_GNU_versym);
    if (result) result = add_const_to_group(values, "SHT_HISUNW", SHT_HISUNW);
    if (result) result = add_const_to_group(values, "SHT_HIOS", SHT_HIOS);
    if (result) result = add_const_to_group(values, "SHT_LOPROC", SHT_LOPROC);
    if (result) result = add_const_to_group(values, "SHT_HIPROC", SHT_HIPROC);
    if (result) result = add_const_to_group(values, "SHT_LOUSER", SHT_LOUSER);
    if (result) result = add_const_to_group(values, "SHT_HIUSER", SHT_HIUSER);

    result = attach_constants_group_to_type(type, true, "ElfSectionHeaderType", values,
                                            "Value inside the *sh_type* field of ELF section headers.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "SHF_WRITE", SHF_WRITE);
    if (result) result = add_const_to_group(values, "SHF_ALLOC", SHF_ALLOC);
    if (result) result = add_const_to_group(values, "SHF_EXECINSTR", SHF_EXECINSTR);
    if (result) result = add_const_to_group(values, "SHF_MERGE", SHF_MERGE);
    if (result) result = add_const_to_group(values, "SHF_STRINGS", SHF_STRINGS);
    if (result) result = add_const_to_group(values, "SHF_INFO_LINK", SHF_INFO_LINK);
    if (result) result = add_const_to_group(values, "SHF_LINK_ORDER", SHF_LINK_ORDER);
    if (result) result = add_const_to_group(values, "SHF_OS_NONCONFORMING", SHF_OS_NONCONFORMING);
    if (result) result = add_const_to_group(values, "SHF_GROUP", SHF_GROUP);
    if (result) result = add_const_to_group(values, "SHF_TLS", SHF_TLS);
    if (result) result = add_const_to_group(values, "SHF_MASKOS", SHF_MASKOS);
    if (result) result = add_const_to_group(values, "SHF_MASKPROC", SHF_MASKPROC);
    if (result) result = add_const_to_group(values, "SHF_ORDERED", SHF_ORDERED);
    if (result) result = add_const_to_group(values, "SHF_EXCLUDE", SHF_EXCLUDE);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfSectionHeaderFlags", values,
                                            "Value inside the *sh_flags* field of ELF section headers.");

    /**
     * Données pour le linker
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "DT_NULL", DT_NULL);
    if (result) result = add_const_to_group(values, "DT_NEEDED", DT_NEEDED);
    if (result) result = add_const_to_group(values, "DT_PLTRELSZ", DT_PLTRELSZ);
    if (result) result = add_const_to_group(values, "DT_PLTGOT", DT_PLTGOT);
    if (result) result = add_const_to_group(values, "DT_HASH", DT_HASH);
    if (result) result = add_const_to_group(values, "DT_STRTAB", DT_STRTAB);
    if (result) result = add_const_to_group(values, "DT_SYMTAB", DT_SYMTAB);
    if (result) result = add_const_to_group(values, "DT_RELA", DT_RELA);
    if (result) result = add_const_to_group(values, "DT_RELASZ", DT_RELASZ);
    if (result) result = add_const_to_group(values, "DT_RELAENT", DT_RELAENT);
    if (result) result = add_const_to_group(values, "DT_STRSZ", DT_STRSZ);
    if (result) result = add_const_to_group(values, "DT_SYMENT", DT_SYMENT);
    if (result) result = add_const_to_group(values, "DT_INIT", DT_INIT);
    if (result) result = add_const_to_group(values, "DT_FINI", DT_FINI);
    if (result) result = add_const_to_group(values, "DT_SONAME", DT_SONAME);
    if (result) result = add_const_to_group(values, "DT_RPATH", DT_RPATH);
    if (result) result = add_const_to_group(values, "DT_SYMBOLIC", DT_SYMBOLIC);
    if (result) result = add_const_to_group(values, "DT_REL", DT_REL);
    if (result) result = add_const_to_group(values, "DT_RELSZ", DT_RELSZ);
    if (result) result = add_const_to_group(values, "DT_RELENT", DT_RELENT);
    if (result) result = add_const_to_group(values, "DT_PLTREL", DT_PLTREL);
    if (result) result = add_const_to_group(values, "DT_DEBUG", DT_DEBUG);
    if (result) result = add_const_to_group(values, "DT_TEXTREL", DT_TEXTREL);
    if (result) result = add_const_to_group(values, "DT_JMPREL", DT_JMPREL);
    if (result) result = add_const_to_group(values, "DT_BIND_NOW", DT_BIND_NOW);
    if (result) result = add_const_to_group(values, "DT_INIT_ARRAY", DT_INIT_ARRAY);
    if (result) result = add_const_to_group(values, "DT_FINI_ARRAY", DT_FINI_ARRAY);
    if (result) result = add_const_to_group(values, "DT_INIT_ARRAYSZ", DT_INIT_ARRAYSZ);
    if (result) result = add_const_to_group(values, "DT_FINI_ARRAYSZ", DT_FINI_ARRAYSZ);
    if (result) result = add_const_to_group(values, "DT_RUNPATH", DT_RUNPATH);
    if (result) result = add_const_to_group(values, "DT_FLAGS", DT_FLAGS);
    if (result) result = add_const_to_group(values, "DT_ENCODING", DT_ENCODING);
    if (result) result = add_const_to_group(values, "DT_PREINIT_ARRAY", DT_PREINIT_ARRAY);
    if (result) result = add_const_to_group(values, "DT_PREINIT_ARRAYSZ", DT_PREINIT_ARRAYSZ);
    if (result) result = add_const_to_group(values, "DT_NUM", DT_NUM);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfSectionHeaderFlags", values,
                                            "Value for the *d_tag* field of ELF file dynamic section entries.");

    /**
     * Symboles de binaires Elf
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "STT_NOTYPE", STT_NOTYPE);
    if (result) result = add_const_to_group(values, "STT_OBJECT", STT_OBJECT);
    if (result) result = add_const_to_group(values, "STT_FUNC", STT_FUNC);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfSymbolInfo", values,
                                            "Value inside the *st_info* field of ELF symbols.");

    /**
     * Informations de relocalisation
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "R_386_NONE", R_386_NONE);
    if (result) result = add_const_to_group(values, "R_386_JMP_SLOT", R_386_JMP_SLOT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfRelocation386", values,
                                            "Type of relocation for i386 ELF files.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "R_ARM_JUMP_SLOT", R_ARM_JUMP_SLOT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ElfRelocationArm", values,
                                            "Type of relocation for ARM ELF files.");

 exit:

    return result;

}
