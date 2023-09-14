
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.c - gestion des symboles d'un PE
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


#include "symbols.h"


#include <malloc.h>


#include <i18n.h>


#include "pe-int.h"
#include "routine.h"



/* Charge en mémoire la liste humaine des symboles exportés. */
static bool load_pe_exported_symbols(GPeFormat *, wgroup_id_t, GtkStatusStack *);

/* Charge en mémoire la liste humaine des symboles importés. */
static bool load_pe_imported_symbols(GPeFormat *, wgroup_id_t, GtkStatusStack *);

/* Assure l'inscription du point d'entrée d'un binaire PE. */
static bool load_pe_entry_point(GPeFormat *, GtkStatusStack *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire la liste humaine des symboles exportés.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_pe_exported_symbols(GPeFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    image_export_directory *export;         /* Répertoire de type 0        */
    const image_data_directory *dir;        /* Localisation du répertoire  */
    GBinFormat *base;                       /* Version basique du format   */
    GExeFormat *exe;                        /* Autre vision du format      */
    bool ret;                               /* Bilan d'un traitement       */
    vmpa2t functions;                       /* Localisation des adresses   */
    vmpa2t names;                           /* Localisation de RVA de noms */
    vmpa2t ordinals;                        /* Localisation des ordinaux   */
    const GBinContent *content;             /* Contenu binaire à lire      */
    uint32_t i;                             /* Boucle de parcours          */
    uint32_t rva;                           /* Adresse relative à traiter  */
    vmpa2t pos;                             /* Position correspondante     */
    const bin_t *name;                      /* Pointeur vers des données   */
    uint16_t ordinal;                       /* Indice de l'exportation     */
    bool forwarded;                         /* Le symbole est renvoyé ?    */
    GPeExportedRoutine *routine;            /* Nouvelle routine trouvée    */
    GBinSymbol *symbol;                     /* Equivalence en symbole      */
    mrange_t range;                         /* Couverture mémoire associée */

    result = false;

    export = g_pe_format_get_directory(format, IMAGE_DIRECTORY_ENTRY_EXPORT);
    if (export == NULL) goto exit;

    dir = g_pe_format_get_directories(format, NULL);
    dir += IMAGE_DIRECTORY_ENTRY_EXPORT;

    base = G_BIN_FORMAT(format);
    exe = G_EXE_FORMAT(format);

    ret = g_exe_format_translate_address_into_vmpa(exe, export->address_of_functions, &functions);
    if (!ret) goto exit_loading;

    ret = g_exe_format_translate_address_into_vmpa(exe, export->address_of_names, &names);
    if (!ret) goto exit_loading;

    ret = g_exe_format_translate_address_into_vmpa(exe, export->address_of_name_ordinals, &ordinals);
    if (!ret) goto exit_loading;

    content = G_KNOWN_FORMAT(format)->content;

    for (i = 0; i < export->number_of_names; i++)
    {
        /* Dénomination */

        ret = g_binary_content_read_u32(content, &names, SRE_LITTLE, &rva);
        if (!ret) goto exit_loading;

        ret = g_exe_format_translate_address_into_vmpa(exe, rva, &pos);
        if (!ret) goto exit_loading;

        name = g_binary_content_get_raw_access(content, &pos, 1);
        if (name == NULL) goto exit_loading;

        /* Ordinal */

        ret = g_binary_content_read_u16(content, &ordinals, SRE_LITTLE, &ordinal);
        if (!ret) goto exit_loading;

        ordinal += export->base;

        /* Adresse */

        copy_vmpa(&pos, &functions);
        advance_vmpa(&pos, ordinal * sizeof(uint32_t));

        ret = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &rva);
        if (!ret) goto exit_loading;

        /**
         * Entrée de type "Forwarder RVA" ?
         */
        forwarded = (dir->virtual_address <= rva && rva < (dir->virtual_address + dir->size));

        ret = g_exe_format_translate_address_into_vmpa(exe, rva, &pos);
        if (!ret) continue;

        /* Mise en place du symbole */

        routine = g_pe_exported_routine_new((char *)name);

        g_pe_exported_routine_set_ordinal(routine, ordinal);

        symbol = G_BIN_SYMBOL(routine);

        if (forwarded)
            g_binary_symbol_set_flag(symbol, PSF_FORWARDED);

        g_binary_symbol_set_status(symbol, SSS_EXPORTED);

        init_mrange(&range, &pos, 0);

        g_binary_symbol_set_range(symbol, &range);

        g_binary_format_add_symbol(base, symbol);

    }

    result = true;

 exit_loading:

    free(export);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire la liste humaine des symboles importés.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_pe_imported_symbols(GPeFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    bool is_32b;                            /* Exécutable 32 bits ?        */
    image_import_descriptor *imports;       /* Répertoire de type 1        */
    GBinFormat *base;                       /* Version basique du format   */
    GExeFormat *exe;                        /* Autre vision du format      */
    const GBinContent *content;             /* Contenu binaire à lire      */
    size_t counter;                         /* Compteur d'importations     */
    image_import_descriptor *iter;          /* Boucle de parcours          */
    vmpa2t dll;                             /* Nom de la DLL concernée     */
    bool ret;                               /* Bilan d'un traitement       */
    const bin_t *library;                   /* Pointeur vers des données   */
    vmpa2t lookup;                          /* Informations d'importation  */
    vmpa2t overwritten;                     /* Emplacement d'adresse finale*/
    uint32_t val32;                         /* Indications sur 32 bits     */
    uint64_t val64;                         /* Indications sur 64 bits     */
    uint32_t rva;                           /* Adresse relative à traiter  */
    vmpa2t name;                            /* Désignation humaine         */
    const bin_t *hint;                      /* Pointeur vers des données   */
    GPeImportedRoutine *routine;            /* Nouvelle routine trouvée    */
    GBinSymbol *symbol;                     /* Equivalence en symbole      */
    mrange_t range;                         /* Couverture mémoire associée */

    result = false;

    is_32b = g_pe_format_get_is_32b(format);

    imports = g_pe_format_get_directory(format, IMAGE_DIRECTORY_ENTRY_IMPORT);
    if (imports == NULL) goto exit;

    base = G_BIN_FORMAT(format);
    exe = G_EXE_FORMAT(format);

    content = G_KNOWN_FORMAT(format)->content;

    counter = 0;

    for (iter = imports; iter->original_first_thunk != 0; iter++)
    {
        /* Bibliothèque impactée */

        ret = g_exe_format_translate_address_into_vmpa(exe, iter->module_name, &dll);
        if (!ret) goto exit_loading;

        library = g_binary_content_get_raw_access(content, &dll, 1);
        if (library == NULL) goto exit_loading;

        /* Liste des fonctions importées */

        ret = g_exe_format_translate_address_into_vmpa(exe, iter->original_first_thunk, &lookup);
        if (!ret) goto exit_loading;

        ret = g_exe_format_translate_address_into_vmpa(exe, iter->first_thunk, &overwritten);
        if (!ret) goto exit_loading;

        do
        {
            if (is_32b)
            {
                ret = g_binary_content_read_u32(content, &lookup, SRE_LITTLE, &val32);
                if (!ret) goto exit_loading;

                val64 = ((uint64_t)(val32 & 0x80000000)) << 32 | val32;

            }
            else
            {
                ret = g_binary_content_read_u64(content, &lookup, SRE_LITTLE, &val64);
                if (!ret) goto exit_loading;
            }

            if (val64 == 0)
                break;

            if (val64 & 0x8000000000000000)
            {
                routine = g_pe_imported_routine_new(NULL, counter++);

                g_pe_exported_routine_set_ordinal(G_PE_EXPORTED_ROUTINE(routine), val64 & 0xffff);

            }
            else
            {
                rva = (val64 & 0x7fffffff);

                ret = g_exe_format_translate_address_into_vmpa(exe, rva, &name);
                if (!ret) goto exit_loading;

                hint = g_binary_content_get_raw_access(content, &name, 3);
                if (hint == NULL) goto exit_loading;

                hint += 2;

                //routine = g_binary_format_decode_routine(base, hint);
                routine = g_pe_imported_routine_new((char *)hint, counter++);

            }

            g_pe_imported_routine_set_library(routine, (char *)library);

            symbol = G_BIN_SYMBOL(routine);

            g_binary_symbol_set_status(symbol, SSS_IMPORTED);

            init_mrange(&range, &overwritten, sizeof(uint32_t));
            advance_vmpa(&overwritten, sizeof(uint32_t));

            g_binary_symbol_set_range(symbol, &range);

            g_binary_format_add_symbol(base, symbol);

        }
        while (true);

    }

    result = true;

 exit_loading:

    free(imports);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure l'inscription du point d'entrée d'un binaire PE.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_pe_entry_point(GPeFormat *format, GtkStatusStack *status)
{
    bool result;                            /* Bilan à renvoyer            */
    activity_id_t msg;                      /* Message de progression      */
    const image_nt_headers *headers;        /* Informations d'entête       */
    virt_t ep;                              /* Point d'entrée détecté      */
    vmpa2t addr;                            /* Localisation d'une routine  */
    GBinFormat *base;                       /* Autre version du format     */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */
    GBinRoutine *routine;                   /* Routine à associer au point */
    mrange_t range;                         /* Couverture mémoire associée */

    msg = gtk_status_stack_add_activity(status, _("Registering entry point..."), 0);

    headers = g_pe_format_get_nt_headers(format);
    ep = headers->optional_header.header_32.address_of_entry_point;

    result = g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), ep, &addr);
    if (!result) goto exit;

    base = G_BIN_FORMAT(format);

    if (!g_binary_format_find_symbol_at(base, &addr, &symbol))
    {
        routine = g_binary_format_decode_routine(base, "entry_point");

        symbol = G_BIN_SYMBOL(routine);
        g_object_ref(G_OBJECT(symbol));

        init_mrange(&range, &addr, 0);
        g_binary_symbol_set_range(symbol, &range);

        g_binary_format_add_symbol(base, symbol);

    }

    g_binary_symbol_set_stype(symbol, STP_ENTRY_POINT);

    g_object_unref(G_OBJECT(symbol));

    /* Comptabilisation pour le désassemblage brut */
    g_binary_format_register_code_point(base, get_virt_addr(&addr), DPL_ENTRY_POINT);

 exit:

    gtk_status_stack_remove_activity(status, msg);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est lancée.            *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire la liste humaine des symboles.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_pe_symbols(GPeFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */

    result = load_pe_exported_symbols(format, gid, status);

    if (result)
        result = load_pe_imported_symbols(format, gid, status);

    /* Symbole d'entrée, si encore besoin */

    if (result)
        result = load_pe_entry_point(format, status);

    return result;

}
