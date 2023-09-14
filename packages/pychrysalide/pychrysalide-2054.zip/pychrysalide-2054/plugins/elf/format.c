
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - support du format ELF
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#include "format.h"


#include <assert.h>
#include <malloc.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>


#include <i18n.h>
#include <core/demanglers.h>
#include <core/logs.h>
#include <plugins/pglist.h>


#include "elf-int.h"
#include "helper_arm.h"
#include "program.h"
#include "section.h"
#include "strings.h"
#include "symbols.h"



/* Taille maximale d'une description */
#define MAX_PORTION_DESC 256


/* Initialise la classe des formats d'exécutables ELF. */
static void g_elf_format_class_init(GElfFormatClass *);

/* Initialise une instance de format d'exécutable ELF. */
static void g_elf_format_init(GElfFormat *);

/* Supprime toutes les références externes. */
static void g_elf_format_dispose(GElfFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_elf_format_finalize(GElfFormat *);

/* Indique la désignation interne du format. */
static char *g_elf_format_get_key(const GElfFormat *);

/* Fournit une description humaine du format. */
static char *g_elf_format_get_description(const GElfFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_elf_format_analyze(GElfFormat *, wgroup_id_t, GtkStatusStack *);

/* Informe quant au boutisme utilisé. */
static SourceEndian g_elf_format_get_endianness(const GElfFormat *);

/* Indique le type d'architecture visée par le format. */
static const char *g_elf_format_get_target_machine(const GElfFormat *);

/* Fournit l'adresse principale associée à un format Elf. */
static bool g_elf_format_get_main_address(GElfFormat *, vmpa2t *);

/* Etend la définition des portions au sein d'un binaire. */
static void g_elf_format_refine_portions(GElfFormat *);

/* Fournit l'emplacement d'une section donnée. */
static bool g_elf_format_get_section_range_by_name(const GElfFormat *, const char *, mrange_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à traiter.                         *
*                                                                             *
*  Description : Valide un contenu comme étant un format Elf.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_elf_format(const GBinContent *content)
{
    bool result;                            /* Bilan à faire remonter      */
    vmpa2t addr;                            /* Tête de lecture initiale    */
    char magic[4];                          /* Idenfiant standard          */

    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &addr, 4, (bin_t *)magic);

    if (result)
        result = (memcmp(magic, "\x7f\x45\x4c\x46" /* .ELF */, 4) == 0);

    return result;

}


/* Indique le type défini pour un format d'exécutable ELF. */
G_DEFINE_TYPE(GElfFormat, g_elf_format, G_TYPE_EXE_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables ELF.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_format_class_init(GElfFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de format connu     */
    GBinFormatClass *fmt;                   /* Version en format basique   */
    GExeFormatClass *exe;                   /* Version en exécutable       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_elf_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_elf_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_elf_format_get_key;
    known->get_desc = (known_get_desc_fc)g_elf_format_get_description;
    known->analyze = (known_analyze_fc)g_elf_format_analyze;

    fmt = G_BIN_FORMAT_CLASS(klass);

    fmt->get_endian = (format_get_endian_fc)g_elf_format_get_endianness;

    exe = G_EXE_FORMAT_CLASS(klass);

    exe->get_machine = (get_target_machine_fc)g_elf_format_get_target_machine;
    exe->get_main_addr = (get_main_addr_fc)g_elf_format_get_main_address;
    exe->refine_portions = (refine_portions_fc)g_elf_format_refine_portions;

    exe->translate_phys = (translate_phys_fc)g_exe_format_translate_offset_into_vmpa_using_portions;
    exe->translate_virt = (translate_virt_fc)g_exe_format_translate_address_into_vmpa_using_portions;

    exe->get_range_by_name = (get_range_by_name_fc)g_elf_format_get_section_range_by_name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable ELF.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_format_init(GElfFormat *format)
{
    GBinFormat *bin_format;                 /* Format parent à compléter   */

    bin_format = G_BIN_FORMAT(format);

    bin_format->demangler = get_compiler_demangler_for_key("itanium");
    assert(bin_format->demangler != NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_format_dispose(GElfFormat *format)
{
    G_OBJECT_CLASS(g_elf_format_parent_class)->dispose(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_format_finalize(GElfFormat *format)
{
    G_OBJECT_CLASS(g_elf_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Prend en charge un nouveau format ELF.                       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GExeFormat *g_elf_format_new(GBinContent *content)
{
    GElfFormat *result;                     /* Structure à retourner       */

    if (!check_elf_format(content))
        return NULL;

    result = g_object_new(G_TYPE_ELF_FORMAT, NULL);

    g_known_format_set_content(G_KNOWN_FORMAT(result), content);

    if (!read_elf_header(result, &result->header, &result->is_32b, &result->endian))
    {
        g_object_unref(G_OBJECT(result));
        return NULL;
    }

    return G_EXE_FORMAT(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Indique la désignation interne du format.                    *
*                                                                             *
*  Retour      : Désignation du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_elf_format_get_key(const GElfFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("elf");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Fournit une description humaine du format.                   *
*                                                                             *
*  Retour      : Description du format.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_elf_format_get_description(const GElfFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("Executable and Linkable Format");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure l'interprétation d'un format en différé.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_elf_format_analyze(GElfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *base;                       /* Version basique du format   */
    GExeFormat *exe;                        /* Autre version du format     */

    result = false;

    base = G_BIN_FORMAT(format);
    exe = G_EXE_FORMAT(format);

    /* Vérification des tailles d'entrée de table */

    if (ELF_HDR(format, format->header, e_phentsize) != ELF_SIZEOF_PHDR(format))
    {
        log_variadic_message(LMT_BAD_BINARY,
                             _("Corrupted program header size (%hu); fixed!" \
                               "  --  replacing 0x%04hx by 0x%04hx at offset 0x%x"),
                             ELF_HDR(format, format->header, e_phentsize),
                             ELF_HDR(format, format->header, e_phentsize),
                             ELF_SIZEOF_PHDR(format),
                             ELF_HDR_OFFSET_OF(format, e_phentsize));

        ELF_HDR_SET(format, format->header, e_phentsize, ELF_SIZEOF_PHDR(format));

    }

    if (ELF_HDR(format, format->header, e_shentsize) != ELF_SIZEOF_SHDR(format))
    {
        log_variadic_message(LMT_BAD_BINARY,
                             _("Corrupted section header size (%hu); fixed!" \
                               "  --  replacing 0x%04hx by 0x%04hx at offset 0x%x"),
                             ELF_HDR(format, format->header, e_shentsize),
                             ELF_HDR(format, format->header, e_shentsize),
                             ELF_SIZEOF_SHDR(format),
                             ELF_HDR_OFFSET_OF(format, e_shentsize));

        ELF_HDR_SET(format, format->header, e_shentsize, ELF_SIZEOF_SHDR(format));

    }

    /* Opérations spécifiques à l'architecture */

    switch (ELF_HDR(format, format->header, e_machine))
    {
        case EM_ARM:
            format->ops.get_type_desc = (get_elf_prgm_type_desc_cb)get_elf_program_arm_type_desc;
            format->ops.fix_virt = (fix_elf_virt_addr_cb)fix_elf_arm_virtual_address;
            format->ops.find_first_plt = (find_first_plt_entry_cb)find_first_plt_entry;
            format->ops.get_linkage_offset = (get_elf_linkage_offset_cb)retrieve_arm_linkage_offset;
            break;

        default:
            log_variadic_message(LMT_ERROR, "Architecture not supported for ELF binaries");
            goto error;
            break;

    }

    /* Chargements des informations utiles */

    g_executable_format_setup_portions(exe, status);

    /**
     * On inscrit les éléments préchargés avant tout !
     *
     * Cela permet de partir d'une base vide, et d'ajouter les instructions et
     * leurs commentaires par paires.
     *
     * Ensuite, on inscrit le reste (comme les chaînes de caractères).
     */

    preload_binary_format(PGA_FORMAT_PRELOAD, base, base->info, status);

    if (!load_elf_symbols(format, gid, status))
        goto error;

    if (!find_all_elf_strings(format, gid, status))
        goto error;

    if (!g_executable_format_complete_loading(exe, gid, status))
        goto error;

    result = true;

 error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Informe quant au boutisme utilisé.                           *
*                                                                             *
*  Retour      : Indicateur de boutisme.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static SourceEndian g_elf_format_get_endianness(const GElfFormat *format)
{
    return format->endian;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Indique le type d'architecture visée par le format.          *
*                                                                             *
*  Retour      : Identifiant de l'architecture ciblée par le format.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_elf_format_get_target_machine(const GElfFormat *format)
{
    const char *result;                     /* Identifiant à retourner     */

    switch (ELF_HDR(format, format->header, e_machine))
    {
        case EM_386:
            result = "i386";
            break;

        case EM_MIPS:
            result = "mips";
            break;

        case EM_ARM:
            result = "armv7";
            break;

        case EM_NONE:
        default:
            result = NULL;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse principale trouvée si possible. [OUT]       *
*                                                                             *
*  Description : Fournit l'adresse principale associée à un format Elf.       *
*                                                                             *
*  Retour      : Bilan des recherches.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_elf_format_get_main_address(GElfFormat *format, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GBinSymbol *symbol;                     /* Point d'entrée trouvé       */
    GBinFormat *base;                       /* Version d'instance parente  */
    const mrange_t *range;                  /* Emplacement de ce point     */

    result = false;
    symbol = NULL;

    base = G_BIN_FORMAT(format);

    if (g_binary_format_find_symbol_by_label(base, "main", &symbol))
        goto done;

    if (g_binary_format_find_symbol_by_label(base, "_start", &symbol))
        goto done;

    if (g_binary_format_find_symbol_by_label(base, "entry_point", &symbol))
        goto done;

 done:

    if (symbol != NULL)
    {
        result = true;

        range = g_binary_symbol_get_range(symbol);

        copy_vmpa(addr, get_mrange_addr(range));

        g_object_unref(G_OBJECT(symbol));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Etend la définition des portions au sein d'un binaire.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_format_refine_portions(GElfFormat *format)
{
    GExeFormat *exe_format;                 /* Autre version du format     */
    uint16_t max;                           /* Décompte d'éléments traités */
    uint16_t i;                             /* Boucle de parcours          */
    off_t offset;                           /* Début de part de programme  */
    vmpa2t origin;                          /* Origine d'une définition    */
    elf_phdr phdr;                          /* En-tête de programme ELF    */
    uint32_t p_flags;                       /* Droits associés à une partie*/
    const char *background;                 /* Fond signigicatif           */
    GBinPortion *new;                       /* Nouvelle portion définie    */
    char desc[MAX_PORTION_DESC];            /* Description d'une portion   */
    vmpa2t addr;                            /* Emplacement dans le binaire */
    PortionAccessRights rights;             /* Droits d'une portion        */
    elf_shdr strings;                       /* Section des descriptions    */
    bool has_strings;                       /* Section trouvée ?           */
    elf_shdr shdr;                          /* En-tête de section ELF      */
    uint64_t sh_flags;                      /* Droits associés à une partie*/
    mrange_t range;                         /* Emplacement d'une section   */
    const char *name;                       /* Nom trouvé ou NULL          */

    exe_format = G_EXE_FORMAT(format);

    /**
     * La copie des différents en-têtes cherche à reproduire l'inclusion native
     * du format :
     *
     *  EXIDX          0x001178 0x00009178 0x00009178 0x00008 0x00008 R   0x4
     *  PHDR           0x000034 0x00008034 0x00008034 0x00120 0x00120 R E 0x4
     *  INTERP         0x000154 0x00008154 0x00008154 0x00019 0x00019 R   0x1
     *  LOAD           0x000000 0x00008000 0x00008000 0x01184 0x01184 R E 0x8000
     *
     */

    /**
     * Côté segments basiques.
     */

    max = ELF_HDR(format, format->header, e_phnum);

    for (i = 0; i < max; i++)
    {
        offset = ELF_HDR(format, format->header, e_phoff)
            + ELF_HDR(format, format->header, e_phentsize) * i;

        init_vmpa(&origin, offset, VMPA_NO_VIRTUAL);

        if (!read_elf_program_header(format, offset, &phdr))
            continue;

        if (ELF_PHDR(format, phdr, p_type) == PT_NULL)
            continue;

        p_flags = ELF_PHDR(format, phdr, p_flags);

        if (p_flags & PF_X) background = BPC_CODE;
        else if (p_flags & PF_W) background = BPC_DATA;
        else background = BPC_DATA_RO;

        init_vmpa(&addr, ELF_PHDR(format, phdr, p_offset), ELF_PHDR(format, phdr, p_vaddr));

        new = g_binary_portion_new(background, &addr, ELF_PHDR(format, phdr, p_filesz));

        snprintf(desc, MAX_PORTION_DESC, "%s \"%s\"",
                 _("Segment"),
                 get_elf_program_type_desc(format, ELF_PHDR(format, phdr, p_type)));

        g_binary_portion_set_desc(new, desc);

        rights = PAC_NONE;
        if (p_flags & PF_R) rights |= PAC_READ;
        if (p_flags & PF_W) rights |= PAC_WRITE;
        if (p_flags & PF_X) rights |= PAC_EXEC;

        g_binary_portion_set_rights(new, rights);

        g_exe_format_include_portion(exe_format, new, &origin);

    }

    /**
     * Inclusion des sections, si possible...
     */

    has_strings = find_elf_section_by_index(format,
                                            ELF_HDR(format, format->header, e_shstrndx),
                                            &strings);

    max = ELF_HDR(format, format->header, e_shnum);

    for (i = 0; i < max; i++)
    {
        if (!find_elf_section_by_index(format, i, &shdr))
            continue;

        if (ELF_SHDR(format, shdr, sh_offset) == 0)
            continue;

        sh_flags = ELF_SHDR(format, shdr, sh_flags);

        if (sh_flags & SHF_EXECINSTR) background = BPC_CODE;
        else if (sh_flags & SHF_WRITE) background = BPC_DATA;
        else background = BPC_DATA_RO;

        get_elf_section_range(format, &shdr, &range);

        new = g_binary_portion_new(background, get_mrange_addr(&range), get_mrange_length(&range));

        if (has_strings)
            name = extract_name_from_elf_string_section(format, &strings,
                                                        ELF_SHDR(format, shdr, sh_name));
        else name = NULL;

        if (name != NULL)
            snprintf(desc, MAX_PORTION_DESC, "%s \"%s\"", _("Section"), name);
        else
            snprintf(desc, MAX_PORTION_DESC, "%s ???", _("Section"));

        g_binary_portion_set_desc(new, desc);

        rights = PAC_NONE;
        if (sh_flags & SHF_ALLOC) rights |= PAC_READ;
        if (sh_flags & SHF_WRITE) rights |= PAC_WRITE;
        if (sh_flags & SHF_EXECINSTR) rights |= PAC_EXEC;

        g_binary_portion_set_rights(new, rights);

        offset = ELF_HDR(format, format->header, e_shoff)
            + ELF_HDR(format, format->header, e_shentsize) * i;

        init_vmpa(&origin, offset, VMPA_NO_VIRTUAL);

        g_exe_format_include_portion(exe_format, new, &origin);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                name   = nom de la section recherchée.                       *
*                range  = emplacement en mémoire à renseigner. [OUT]          *
*                                                                             *
*  Description : Fournit l'emplacement d'une section donnée.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_elf_format_get_section_range_by_name(const GElfFormat *format, const char *name, mrange_t *range)
{
    bool result;                            /* Bilan à retourner           */
    phys_t offset;                          /* Position physique de section*/
    phys_t size;                            /* Taille de la section trouvée*/
    virt_t address;                         /* Adresse virtuelle de section*/
    vmpa2t tmp;                             /* Adresse à initialiser       */

    result = find_elf_section_content_by_name(format, name, &offset, &size, &address);

    if (result)
    {
        init_vmpa(&tmp, offset, address);
        init_mrange(range, &tmp, size);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Présente l'en-tête ELF du format chargé.                     *
*                                                                             *
*  Retour      : Pointeur vers la description principale.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const elf_header *g_elf_format_get_header(const GElfFormat *format)
{
    return &format->header;

}
