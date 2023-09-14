
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pe.c - support du format Portable Executable
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


#include "format.h"


#include <assert.h>


#include "pe-int.h"
#include "rich.h"
#include "section.h"
#include "symbols.h"



/* Initialise la classe des formats d'exécutables ELF. */
static void g_pe_format_class_init(GPeFormatClass *);

/* Initialise une instance de format d'exécutable ELF. */
static void g_pe_format_init(GPeFormat *);

/* Supprime toutes les références externes. */
static void g_pe_format_dispose(GPeFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_pe_format_finalize(GPeFormat *);

/* Indique la désignation interne du format. */
static char *g_pe_format_get_key(const GPeFormat *);

/* Fournit une description humaine du format. */
static char *g_pe_format_get_description(const GPeFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_pe_format_analyze(GPeFormat *, wgroup_id_t, GtkStatusStack *);

/* Informe quant au boutisme utilisé. */
static SourceEndian g_pe_format_get_endianness(const GPeFormat *);

/* Indique le type d'architecture visée par le format. */
static const char *g_pe_format_get_target_machine(const GPeFormat *);

/* Fournit l'adresse principale associée à un format Elf. */
static bool g_pe_format_get_main_address(GPeFormat *, vmpa2t *);


#if 0

/* Etend la définition des portions au sein d'un binaire. */
static void g_pe_format_refine_portions(GPeFormat *);

#endif



/* Fournit l'emplacement correspondant à une adresse virtuelle. */
bool g_pe_format_translate_address_into_vmpa_using_portions(GPeFormat *, virt_t, vmpa2t *);


#if 0

/* Fournit l'emplacement d'une section donnée. */
static bool g_pe_format_get_section_range_by_name(const GPeFormat *, const char *, mrange_t *);
#endif





/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à traiter.                         *
*                                                                             *
*  Description : Valide un contenu comme étant un format PE.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_pe_format(const GBinContent *content)
{
    bool result;                            /* Bilan à faire remonter      */
    vmpa2t addr;                            /* Tête de lecture initiale    */
    char magic[4];                          /* Idenfiant standard          */
    GPeFormat format;                       /* Format factice              */

    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &addr, 2, (bin_t *)magic);

    if (result)
        result = (memcmp(magic, "\x4d\x5a" /* MZ */, 2) == 0);

    if (result)
    {
        G_KNOWN_FORMAT(&format)->content = (GBinContent *)content;
        result = read_dos_image_header(&format, &format.dos_header);
    }

    if (result)
    {
        init_vmpa(&addr, format.dos_header.e_lfanew, VMPA_NO_VIRTUAL);

        result = g_binary_content_read_raw(content, &addr, 4, (bin_t *)magic);

        if (result)
            result = (memcmp(magic, "\x50\x45\x00\x00" /* PE00 */, 4) == 0);

    }

    return result;

}


/* Indique le type défini pour un format d'exécutable ELF. */
G_DEFINE_TYPE(GPeFormat, g_pe_format, G_TYPE_EXE_FORMAT);


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

static void g_pe_format_class_init(GPeFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de format connu     */
    GBinFormatClass *fmt;                   /* Version en format basique   */
    GExeFormatClass *exe;                   /* Version en exécutable       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_pe_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_pe_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_pe_format_get_key;
    known->get_desc = (known_get_desc_fc)g_pe_format_get_description;
    known->analyze = (known_analyze_fc)g_pe_format_analyze;

    fmt = G_BIN_FORMAT_CLASS(klass);

    fmt->get_endian = (format_get_endian_fc)g_pe_format_get_endianness;

    exe = G_EXE_FORMAT_CLASS(klass);

    exe->get_machine = (get_target_machine_fc)g_pe_format_get_target_machine;
    exe->get_main_addr = (get_main_addr_fc)g_pe_format_get_main_address;
    //exe->refine_portions = (refine_portions_fc)g_pe_format_refine_portions;

    //exe->translate_phys = (translate_phys_fc)g_exe_format_translate_offset_into_vmpa_using_portions;
    exe->translate_virt = (translate_virt_fc)g_pe_format_translate_address_into_vmpa_using_portions;

    //exe->get_range_by_name = (get_range_by_name_fc)g_pe_format_get_section_range_by_name;

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

static void g_pe_format_init(GPeFormat *format)
{
    format->sections = NULL;

    format->loaded = false;

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

static void g_pe_format_dispose(GPeFormat *format)
{
    G_OBJECT_CLASS(g_pe_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_pe_format_finalize(GPeFormat *format)
{
    if (format->sections != NULL)
        free(format->sections);

    G_OBJECT_CLASS(g_pe_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Prend en charge un nouveau format PE.                        *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GExeFormat *g_pe_format_new(GBinContent *content)
{
    GPeFormat *result;                      /* Structure à retourner       */

    if (!check_pe_format(content))
        return NULL;

    result = g_object_new(G_TYPE_PE_FORMAT, NULL);

    g_known_format_set_content(G_KNOWN_FORMAT(result), content);

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

static char *g_pe_format_get_key(const GPeFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("pe");

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

static char *g_pe_format_get_description(const GPeFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("Portable Executable");

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

static bool g_pe_format_analyze(GPeFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GExeFormat *exe;                        /* Autre version du format     */
    vmpa2t section_start;                   /* Zone de départ des sections */

    exe = G_EXE_FORMAT(format);

    result = read_dos_image_header(format, &format->dos_header);
    if (!result) goto error;

    result = read_pe_nt_header(format, &format->nt_headers, &section_start);
    if (!result) goto error;

    format->sections = read_all_pe_sections(format, &section_start);
    if (format->sections == NULL) goto error;

    extract_pe_rich_header(format);

    result = load_pe_symbols(format, gid, status);
    if (!result) goto error;

    result = g_executable_format_complete_loading(exe, gid, status);
    if (!result) goto error;

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

static SourceEndian g_pe_format_get_endianness(const GPeFormat *format)
{
    SourceEndian result;                    /* Boutisme à retourner        */

    /**
     * Sauf exception, le boutisme est généralement petit.
     *
     * Cf. https://reverseengineering.stackexchange.com/a/17923
     *     https://docs.microsoft.com/en-us/cpp/build/overview-of-arm-abi-conventions?view=msvc-160#endianness
     */

    result = SRE_LITTLE;

    return result;

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

static const char *g_pe_format_get_target_machine(const GPeFormat *format)
{
    const char *result;                     /* Identifiant à retourner     */

    switch (format->nt_headers.file_header.machine)
    {
        case IMAGE_FILE_MACHINE_I386:
            result = "i386";
            break;

        case IMAGE_FILE_MACHINE_R3000:
        case IMAGE_FILE_MACHINE_R4000:
        case IMAGE_FILE_MACHINE_R10000:
        case IMAGE_FILE_MACHINE_WCEMIPSV2:
        case IMAGE_FILE_MACHINE_MIPS16:
        case IMAGE_FILE_MACHINE_MIPSFPU:
        case IMAGE_FILE_MACHINE_MIPSFPU16:
            result = "mips";
            break;

        case IMAGE_FILE_MACHINE_ARM:
        case IMAGE_FILE_MACHINE_THUMB:
        case IMAGE_FILE_MACHINE_ARMNT:
            result = "armv7";
            break;

        case IMAGE_FILE_MACHINE_UNKNOWN:
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

static bool g_pe_format_get_main_address(GPeFormat *format, vmpa2t *addr)
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


#if 0

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

static void g_pe_format_refine_portions(GPeFormat *format)
{

}

#endif



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                addr   = adresse virtuelle à retrouver.                      *
*                pos    = position correspondante. [OUT]                      *
*                                                                             *
*  Description : Fournit l'emplacement correspondant à une adresse virtuelle. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_pe_format_translate_address_into_vmpa_using_portions(GPeFormat *format, virt_t addr, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t i;                             /* Boucle de parcours          */
    const image_section_header *section;    /* Section à consulter         */
    phys_t diff;                            /* Décallage à appliquer       */

    result = false;

    for (i = 0; i < format->nt_headers.file_header.number_of_sections && !result; i++)
    {
        section = &format->sections[i];

        if (addr < section->virtual_address)
            continue;

        if (addr >= (section->virtual_address + section->size_of_raw_data))
            continue;

        diff = addr - section->virtual_address;

        init_vmpa(pos, section->pointer_to_raw_data + diff, addr);

        result = true;

    }

    //printf(" // trans // %x -> %x  (valid? %d)\n", (unsigned int)addr, (unsigned int)pos->physical, result);

    return result;

}




#if 0


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

static bool g_pe_format_get_section_range_by_name(const GPeFormat *format, const char *name, mrange_t *range)
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
#endif








/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                                                                             *
*  Description : Présente l'en-tête MS-DOS du format chargé.                  *
*                                                                             *
*  Retour      : Pointeur vers la description principale.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const image_dos_header *g_pe_format_get_dos_header(const GPeFormat *format)
{
    const image_dos_header *result;         /* Informations à retourner    */

    result = &format->dos_header;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                                                                             *
*  Description : Présente l'en-tête NT du format chargé.                      *
*                                                                             *
*  Retour      : Pointeur vers la description principale.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const image_nt_headers *g_pe_format_get_nt_headers(const GPeFormat *format)
{
    const image_nt_headers *result;         /* Informations à retourner    */

    result = &format->nt_headers;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                                                                             *
*  Description : Indique si le format PE est en 32 bits ou en 64 bits.        *
*                                                                             *
*  Retour      : true si le format est en 32 bits, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_pe_format_get_is_32b(const GPeFormat *format)
{
    bool result;                            /* Nature à retourner          */

    assert(format->loaded);

    switch (format->nt_headers.optional_header.header_32.magic)
    {
        case IMAGE_NT_OPTIONAL_HDR32_MAGIC:
            result = true;
            break;
        case IMAGE_NT_OPTIONAL_HDR64_MAGIC:
            result = false;
            break;
        default:
            result = true;
            assert(false);
            break;
    }

    return result;


}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                count  = taille (fixe) du tableau renvoyé. [OUT]             *
*                                                                             *
*  Description : Offre un raccourci vers les répertoires du format PE.        *
*                                                                             *
*  Retour      : Pointeur vers le tableau des répertoires.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const image_data_directory *g_pe_format_get_directories(const GPeFormat *format, size_t *count)
{
    const image_data_directory *result;     /* Liste à retourner           */

    if (g_pe_format_get_is_32b(format))
    {
        result = format->nt_headers.optional_header.header_32.data_directory;

        if (count != NULL)
            *count = format->nt_headers.optional_header.header_32.number_of_rva_and_sizes;

    }
    else
    {
        result = format->nt_headers.optional_header.header_64.data_directory;

        if (count != NULL)
            *count = format->nt_headers.optional_header.header_64.number_of_rva_and_sizes;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                index  = indice du répertoire visé.                          *
*                                                                             *
*  Description : Extrait le contenu d'un répertoire du format PE.             *
*                                                                             *
*  Retour      : Pointeur vers un contenu chargé ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *g_pe_format_get_directory(const GPeFormat *format, size_t index)
{
    void *result;                           /* Données à retourner         */
    size_t max;                             /* Quantité de répertoires     */
    const image_data_directory *dir;        /* Localisation du répertoire  */
    vmpa2t pos;                             /* Tête de lecture             */
    bool status;                            /* Bilan d'un traitement       */
    image_export_directory *export;         /* Répertoire de type 0        */
    image_import_descriptor *imports;       /* Répertoire de type 1        */
    size_t imported_count;                  /* Quantité de DLL requises    */

    result = NULL;

    dir = g_pe_format_get_directories(format, &max);

    if (index >= max)
        goto exit;

    dir += index;

    status = g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), dir->virtual_address, &pos);
    if (!status) goto exit;

    switch (index)
    {
        case IMAGE_DIRECTORY_ENTRY_EXPORT:

            export = malloc(sizeof(image_export_directory));

            status = read_pe_image_export_directory(format, &pos, export);

            if (!status)
            {
                free(export);
                goto exit;
            }

            result = export;
            break;

        case IMAGE_DIRECTORY_ENTRY_IMPORT:

            imports = NULL;
            imported_count = 0;

            do
            {
                imports = realloc(imports, ++imported_count * sizeof(image_import_descriptor));

                status = read_pe_image_import_descriptor(format, &pos, imports + (imported_count - 1));

                if (!status)
                {
                    free(imports);
                    goto exit;
                }

            }
            while (imports[imported_count - 1].original_first_thunk != 0);

            result = imports;
            break;

    }

 exit:

    return result;

}
