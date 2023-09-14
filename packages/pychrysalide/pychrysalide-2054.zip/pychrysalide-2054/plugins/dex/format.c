
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - support du format DEX
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
#include <string.h>


#include <i18n.h>
#include <core/demanglers.h>
#include <core/global.h>
#include <core/logs.h>
#include <plugins/pglist.h>


#include "dex-int.h"
#include "pool.h"



/* Initialise la classe des formats d'exécutables DEX. */
static void g_dex_format_class_init(GDexFormatClass *);

/* Initialise une instance de format d'exécutable DEX. */
static void g_dex_format_init(GDexFormat *);

/* Supprime toutes les références externes. */
static void g_dex_format_dispose(GDexFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_format_finalize(GDexFormat *);

/* Indique la désignation interne du format. */
static char *g_dex_format_get_key(const GDexFormat *);

/* Fournit une description humaine du format. */
static char *g_dex_format_get_description(const GDexFormat *);

/* Assure l'interprétation d'un format en différé. */
static bool g_dex_format_analyze(GDexFormat *, wgroup_id_t, GtkStatusStack *);

/* Informe quant au boutisme utilisé. */
static SourceEndian g_dex_format_get_endianness(const GDexFormat *);

/* Indique le type d'architecture visée par le format. */
static const char *g_dex_format_get_target_machine(const GDexFormat *);

/* Etend la définition des portions au sein d'un binaire. */
static void g_dex_format_refine_portions(GDexFormat *);

/* Fournit l'emplacement d'une section donnée. */
static bool g_dex_format_get_section_range_by_name(const GDexFormat *, const char *, mrange_t *);


















/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à traiter.                         *
*                                                                             *
*  Description : Valide un contenu comme étant un format Dex.                 *
*                                                                             *
*  Retour      : true si le format attendu a bien été reconnu, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_dex_format(const GBinContent *content)
{
    bool result;                            /* Bilan à faire remonter      */
    vmpa2t addr;                            /* Tête de lecture initiale    */
    char magic[DEX_FILE_MAGIC_LEN];         /* Idenfiant standard          */

    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &addr, DEX_FILE_MAGIC_LEN, (bin_t *)magic);

    if (result)
        result = (memcmp(magic, DEX_FILE_MAGIC, DEX_FILE_MAGIC_LEN) == 0);

    return result;

}


/* Indique le type défini pour un format d'exécutable DEX. */
G_DEFINE_TYPE(GDexFormat, g_dex_format, G_TYPE_EXE_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables DEX.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_format_class_init(GDexFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKnownFormatClass *known;               /* Version de format connu     */
    GBinFormatClass *fmt;                   /* Version en format basique   */
    GExeFormatClass *exe;                   /* Version en exécutable       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_format_finalize;

    known = G_KNOWN_FORMAT_CLASS(klass);

    known->get_key = (known_get_key_fc)g_dex_format_get_key;
    known->get_desc = (known_get_desc_fc)g_dex_format_get_description;
    known->analyze = (known_analyze_fc)g_dex_format_analyze;

    fmt = G_BIN_FORMAT_CLASS(klass);

    fmt->get_endian = (format_get_endian_fc)g_dex_format_get_endianness;

    exe = G_EXE_FORMAT_CLASS(klass);

    exe->get_machine = (get_target_machine_fc)g_dex_format_get_target_machine;
    exe->refine_portions = (refine_portions_fc)g_dex_format_refine_portions;

    exe->translate_phys = (translate_phys_fc)g_exe_format_without_virt_translate_offset_into_vmpa;
    exe->translate_virt = (translate_virt_fc)g_exe_format_without_virt_translate_address_into_vmpa;

    exe->get_range_by_name = (get_range_by_name_fc)g_dex_format_get_section_range_by_name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable DEX.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_format_init(GDexFormat *format)
{
    GBinFormat *bin_format;                 /* Format parent à compléter   */

    bin_format = G_BIN_FORMAT(format);

    bin_format->demangler = get_compiler_demangler_for_key("dex");
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

static void g_dex_format_dispose(GDexFormat *format)
{
    g_clear_object(&format->pool);

    G_OBJECT_CLASS(g_dex_format_parent_class)->dispose(G_OBJECT(format));

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

static void g_dex_format_finalize(GDexFormat *format)
{
    G_OBJECT_CLASS(g_dex_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Prend en charge un nouveau format Dex.                       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GExeFormat *g_dex_format_new(GBinContent *content)
{
    GDexFormat *result;                     /* Structure à retourner       */
    vmpa2t pos;                             /* Position de tête de lecture */

    if (!check_dex_format(content))
        return NULL;

    result = g_object_new(G_TYPE_DEX_FORMAT, NULL);

    g_known_format_set_content(G_KNOWN_FORMAT(result), content);

    result->pool = g_dex_pool_new(result);

    init_vmpa(&pos, 0, VMPA_NO_VIRTUAL);

    if (!read_dex_header(result, &pos, &result->header))
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

static char *g_dex_format_get_key(const GDexFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("dex");

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

static char *g_dex_format_get_description(const GDexFormat *format)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("Dalvik Executable format (version '035')");

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

static bool g_dex_format_analyze(GDexFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *base;                       /* Version basique du format   */
    GExeFormat *exe;                        /* Autre version du format     */
    vmpa2t pos;                             /* Position de tête de lecture */
    phys_t size;                            /* Taille du binaire           */
    VMPA_BUFFER(size_str);                  /* Conversion en chaîne        */
    uint32_t max;                           /* Nombre maximal d'éléments   */
    GDexPool *pool;                         /* Table de ressources         */

    result = false;

    base = G_BIN_FORMAT(format);
    exe = G_EXE_FORMAT(format);

    /* Vérification des tailles fournies */

    size = g_binary_content_compute_size(G_KNOWN_FORMAT(base)->content);

    if (size >= 0xffffffffllu)
    {
        init_vmpa(&pos, size, VMPA_NO_VIRTUAL);
        vmpa2_phys_to_string(&pos, MDS_UNDEFINED, size_str, NULL);

        log_variadic_message(LMT_BAD_BINARY, _("The binary content is too big (size=%s)"), size_str);
        goto gdfa_error;

    }


#define CHECK_DEX_HEADER(type, cstruct, hardlim, msg)                                               \
    do                                                                                              \
    {                                                                                               \
        if (format->header. type ## _off > size)                                                    \
        {                                                                                           \
            log_variadic_message(LMT_BAD_BINARY,                                                    \
                                 _("Corrupted " msg " offset; fixed!  --  replacing 0x%x by 0x%x"), \
                                 format->header. type ## _off, size);                               \
            format->header. type ## _off = size;                                                    \
        }                                                                                           \
                                                                                                    \
        max = (size - format->header. type ## _off) / sizeof(cstruct);                              \
                                                                                                    \
        if (hardlim && max > 65535)                                                                 \
            max = 65535;                                                                            \
                                                                                                    \
        if (format->header. type ## _size > max)                                                    \
        {                                                                                           \
            log_variadic_message(LMT_BAD_BINARY,                                                    \
                                 _("Corrupted " msg " size; fixed!  --  replacing 0x%x by 0x%x"),   \
                                 format->header. type ## _size, max);                               \
            format->header. type ## _size = max;                                                    \
        }                                                                                           \
    }                                                                                               \
    while (0);

    CHECK_DEX_HEADER(type_ids, type_id_item, true, "type identifiers");
    CHECK_DEX_HEADER(proto_ids, proto_id_item, true, "prototype identifiers");
    CHECK_DEX_HEADER(field_ids, field_id_item, true, "field identifiers");
    CHECK_DEX_HEADER(method_ids, method_id_item, true, "method identifiers");
    CHECK_DEX_HEADER(class_defs, class_def_item, false, "class definitions");


    /* TODO : vérifier que les *_id ne se chevauchent pas */


    pool = g_dex_format_get_pool(format);

    if (!g_dex_pool_load_all_string_symbols(pool, gid, status))
        goto pool_error;

    if (!g_dex_pool_load_all_types(pool, gid, status))
        goto pool_error;

    if (!g_dex_pool_load_all_fields(pool, gid, status))
        goto pool_error;

    if (!g_dex_pool_load_all_methods(pool, gid, status))
        goto pool_error;

    if (!g_dex_pool_load_all_classes(pool, gid, status))
        goto pool_error;

    preload_binary_format(PGA_FORMAT_PRELOAD, base, base->info, status);

    g_executable_format_setup_portions(exe, status);

    if (!g_executable_format_complete_loading(exe, gid, status))
        goto pool_error;

    result = true;

 pool_error:

    g_object_unref(G_OBJECT(pool));

 gdfa_error:

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

static SourceEndian g_dex_format_get_endianness(const GDexFormat *format)
{
    return SRE_LITTLE;

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

static const char *g_dex_format_get_target_machine(const GDexFormat *format)
{
    return "dalvik35";

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                main   = couche de portions principale à raffiner.           *
*                                                                             *
*  Description : Etend la définition des portions au sein d'un binaire.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_format_refine_portions(GDexFormat *format)
{
    GExeFormat *exe_format;                 /* Autre version du format     */
    size_t max;                             /* Nombre d'itérations prévues */
    size_t i;                               /* Boucle de parcours          */
    GDexClass *class;                       /* Classe du format Dex        */

    exe_format = G_EXE_FORMAT(format);

    max = g_dex_pool_count_classes(format->pool);

    for (i = 0; i < max; i++)
    {
        class = g_dex_pool_get_class(format->pool, i);

        if (class != NULL)
        {
            g_dex_class_include_as_portion(class, exe_format);
            g_object_unref(G_OBJECT(class));
        }

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

static bool g_dex_format_get_section_range_by_name(const GDexFormat *format, const char *name, mrange_t *range)
{
    bool result;                            /* Bilan à retourner           */

    result = false;

    return result;

}










/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                addr   = adresse de la routine à retrouver.                  *
*                                                                             *
*  Description : Retrouve si possible la méthode associée à une adresse.      *
*                                                                             *
*  Retour      : Méthde retrouvée ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_format_find_method_by_address(const GDexFormat *format, vmpa_t addr)
{

    return NULL;


#if 0
    GDexMethod *result;                     /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < format->classes_count && result == NULL; i++)
        result = g_dex_class_find_method_by_address(format->classes[i], addr);

    return result;
#endif

}




/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Présente l'en-tête DEX du format chargé.                     *
*                                                                             *
*  Retour      : Pointeur vers la description principale.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const dex_header *g_dex_format_get_header(const GDexFormat *format)
{
    return &format->header;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Fournit la table des ressources associée au format Dex.      *
*                                                                             *
*  Retour      : Table de ressources mise en place ou NULL si aucune.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexPool *g_dex_format_get_pool(const GDexFormat *format)
{
    GDexPool *result;                       /* Instance à retourner        */

    result = format->pool;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}
