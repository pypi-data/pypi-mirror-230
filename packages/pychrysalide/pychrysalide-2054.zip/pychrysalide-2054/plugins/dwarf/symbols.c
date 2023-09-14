
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.c - gestion des symboles d'un DWARF
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "die.h"
#include "dwarf-int.h"
#include "form.h"
#include "../../core/params.h"
#include "../../mangling/demangler.h"



/* Charge les informations d'une routine en tant que symbole. */
static bool load_routine_as_symbol_from_dwarf(GDwarfFormat *, const dw_die *, const dw_abbrev *, bool);

/* Charge les informations d'un objet en tant que symbole. */
static bool load_object_as_symbol_from_dwarf(GDwarfFormat *, const dw_die *, const dw_abbrev *, bool);



/******************************************************************************
*                                                                             *
*  Paramètres  : format   = description de l'exécutable à compléter.          *
*                die      = entrée d'informations de débogage à utiliser.     *
*                abbrev   = abréviation déjà chargée sur laquelle s'appuyer.  *
*                use_virt = oriente le choix de la distinction ultime.        *
*                                                                             *
*  Description : Charge les informations d'une routine en tant que symbole.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_routine_as_symbol_from_dwarf(GDwarfFormat *format, const dw_die *die, const dw_abbrev *abbrev, bool use_virt)
{
    DwarfForm form;                         /* Type d'une valeur d'attribut*/
    const dw_form_value *value;             /* Valeur concrète d'attribut  */
    virt_t virt;                            /* Adresse virtuelle de départ */
    bool status;                            /* Bilan d'une récupération    */
    virt_t len;                             /* Taille de la zone couverte  */
    vmpa2t addr;                            /* Localisation complète       */
    mrange_t range;                         /* Espace de couverture total  */
    const char *name;                       /* Désignation humaine         */
    char alt_name[6 + VMPA_MAX_LEN];        /* Nom abstrait de substitution*/
    GBinRoutine *routine;                   /* Nouvelle routine trouvée    */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */

    /* Surface couverte */

    value = dw_die_peek_extended_value(die, DW_AT_low_pc, &form);
    if (value == NULL) goto lrasfd_bad_start;

    status = translate_form_into_address(value, form, &virt);
    if (!status) goto lrasfd_bad_start;

    value = dw_die_peek_extended_value(die, DW_AT_high_pc, &form);
    if (value == NULL) goto lrasfd_bad_start;

    status &= translate_form_into_address(value, form, &len);
    if (!status) goto lrasfd_bad_start;

    if (!g_exe_format_translate_address_into_vmpa(G_DBG_FORMAT(format)->executable, virt, &addr))
        init_vmpa(&addr, VMPA_NO_PHYSICAL, virt);

    init_mrange(&range, &addr, len);

    /* Désignation humaine */

    value = dw_die_peek_extended_value(die, DW_AT_name, &form);
    if (value == NULL) goto lrasfd_bad_name;

    name = translate_form_into_string(value, form);

    if (name == NULL)
    {
        strcpy(alt_name, "func_");

        if (use_virt)
            vmpa2_virt_to_string(&addr, MDS_UNDEFINED, alt_name + 5, NULL);
        else
            vmpa2_phys_to_string(&addr, MDS_UNDEFINED, alt_name + 5, NULL);

        name = alt_name;

    }

    /* Intégration en bonne et due forme */

    routine = g_binary_format_decode_routine(G_BIN_FORMAT(format), name);
    symbol = G_BIN_SYMBOL(routine);

    g_binary_symbol_set_range(symbol, &range);

    g_binary_format_add_symbol(G_BIN_FORMAT(format), symbol);




    printf(" --> [valid ?= %d] start @ 0x%08llx\n", status, virt);
    printf(" --> [valid ?= %d]   len = 0x%08llx\n", status, len);
    printf(" --> [valid ?= %d]  name = '%s'\n", status, name);


    return true;

 lrasfd_bad_start:
 lrasfd_bad_name:

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = description de l'exécutable à compléter.          *
*                die      = entrée d'informations de débogage à utiliser.     *
*                abbrev   = abréviation déjà chargée sur laquelle s'appuyer.  *
*                use_virt = oriente le choix de la distinction ultime.        *
*                                                                             *
*  Description : Charge les informations d'un objet en tant que symbole.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_object_as_symbol_from_dwarf(GDwarfFormat *format, const dw_die *die, const dw_abbrev *abbrev, bool use_virt)
{
    DwarfForm form;                         /* Type d'une valeur d'attribut*/
    const dw_form_value *value;             /* Valeur concrète d'attribut  */
    virt_t virt;                            /* Adresse virtuelle de départ */
    bool status;                            /* Bilan d'une récupération    */
    virt_t len;                             /* Taille de la zone couverte  */
    vmpa2t addr;                            /* Localisation complète       */
    mrange_t range;                         /* Espace de couverture total  */
    const char *name;                       /* Désignation humaine         */
    char alt_name[5 + VMPA_MAX_LEN];        /* Nom abstrait de substitution*/
    GBinRoutine *routine;                   /* Nouvelle routine trouvée    */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */

    /* Surface couverte */






    /*
    value = dw_die_peek_extended_value(die, DW_AT_low_pc, &form);
    if (value == NULL) goto lrasfd_bad_start;

    status = translate_form_into_address(value, form, &virt);
    if (!status) goto lrasfd_bad_start;

    value = dw_die_peek_extended_value(die, DW_AT_high_pc, &form);
    if (value == NULL) goto lrasfd_bad_start;

    status &= translate_form_into_address(value, form, &len);
    if (!status) goto lrasfd_bad_start;

    if (!g_exe_format_translate_address_into_vmpa(G_DBG_FORMAT(format)->executable, virt, &addr))
        init_vmpa(&addr, VMPA_NO_PHYSICAL, virt);

    init_mrange(&range, &addr, len);
    */





    /* Désignation humaine */

    value = dw_die_peek_extended_value(die, DW_AT_name, &form);
    if (value == NULL) goto lrasfd_bad_name;

    name = translate_form_into_string(value, form);

    if (name == NULL)
    {
        strcpy(alt_name, "obj_");

        if (use_virt)
            vmpa2_virt_to_string(&addr, MDS_UNDEFINED, alt_name + 5, NULL);
        else
            vmpa2_phys_to_string(&addr, MDS_UNDEFINED, alt_name + 5, NULL);

        name = alt_name;

    }

    /* Intégration en bonne et due forme */

    /*
    routine = try_to_demangle_routine(name);

    g_binary_symbol_set_range(G_BIN_SYMBOL(routine), &range);

    symbol = g_binary_symbol_new(NULL, STP_OBJECT);
    g_binary_symbol_attach_routine(symbol, routine);

    g_binary_format_add_symbol(G_BIN_FORMAT(format), symbol);
    */



    //printf(" --> [valid ?= %d] start @ 0x%08llx\n", status, virt);
    //printf(" --> [valid ?= %d]   len = 0x%08llx\n", status, len);
    //printf(" --> [valid ?= %d]  name = '%s'\n", status, name);


    return true;

 lrasfd_bad_start:
 lrasfd_bad_name:

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                                                                             *
*  Description : Charge en mémoire la liste humaine des symboles.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_dwarf_symbols(GDwarfFormat *format)
{
    bool result;                            /* Bilan à retourner           */
    bool no_name;                           /* Choix de construction de nom*/

    typedef struct _die_visit_info
    {
        GDwarfFormat *format;
        bool use_virt;

    } die_visit_info;

    die_visit_info vinfo;                   /* Information pour visiteur   */


    bool catch_dwarf_symbol(const dw_die *die, die_visit_info *info)
    {
        const dw_abbrev *abbrev;            /* Lien vers la représentation */
        DwarfTag tag;                       /* Etiquette à analyser        */
        bool status;                        /* Bilan d'un chargement       */

        abbrev = dw_die_get_abbrev(die);
        tag = dwarf_abbreviation_get_tag(abbrev);

        switch (tag)
        {
            case DW_TAG_subprogram:
                printf(" DIE ==> %p -> %p // tag = %x\n", die, abbrev, tag);
                status = load_routine_as_symbol_from_dwarf(info->format, die, abbrev, info->use_virt);
                break;

            case DW_TAG_variable:
                printf(" DIE ==> %p -> %p // tag = %x\n", die, abbrev, tag);
                status = load_object_as_symbol_from_dwarf(info->format, die, abbrev, info->use_virt);
                break;

            default:
                status = true;
                break;

        }

        return status;

    }


    if (!g_generic_config_get_value(get_main_configuration(), MPK_FORMAT_NO_NAME, &no_name))
        return false;

    vinfo.format = format;
    vinfo.use_virt = no_name;

    result = dw_die_visit(format->info_die, (visit_dies_fc)catch_dwarf_symbol, &vinfo);

    return result;

}
