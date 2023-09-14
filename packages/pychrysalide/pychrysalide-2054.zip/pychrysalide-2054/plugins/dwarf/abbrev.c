
/* Chrysalide - Outil d'analyse de fichiers binaires
 * abbrev.c - manipulation des abréviation DWARF
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


#include "abbrev.h"


#include <analysis/contents/restricted.h>


#include "checks.h"
#include "format-int.h"
#include "utils.h"



/* ----------------------- TRAITEMENT D'ABREVIATION A L'UNITE ----------------------- */


/* Description d'un attribut d'une abréviation */
typedef struct _dw_abbrev_attr
{
    DwarfAttrib name;                       /* Sujet de l'élément          */
    DwarfForm form;                         /* Représentation              */

} dw_abbrev_attr;

/* Description d'une abréviation */
struct _dw_abbrev
{
    uleb128_t code;                         /* Identifiant attribué        */
    DwarfTag tag;                           /* Sujet de l'élément          */

    bool has_children;                      /* Présence de sous-éléments ? */

    dw_abbrev_attr *attribs;                /* Liste des attributs         */
    size_t count;                           /* Nombre de ces attributs     */

};


/* Charge une abréviation valide pour un DWARF en mémoire. */
static bool load_dwarf_abbreviation(GDwarfFormat *, const dw_compil_unit_header *, GBinContent *, vmpa2t *, dw_abbrev **);

/* Supprime de la mémoire toute trace d'une abréviation DWARF. */
static void free_dwarf_abbrev(dw_abbrev *);

/* Procède à la conversion de base d'une abréviation DWARF. */
static bool conv_abbrev_decl(GDwarfFormat *, const dw_compil_unit_header *, const dw_abbrev_decl *, dw_abbrev *, const vmpa2t *);

/* Procède à la conversion d'un attribut d'abréviation DWARF. */
static bool conv_abbrev_attrib(GDwarfFormat *, const dw_compil_unit_header *, const dw_abbrev_raw_attr *, dw_abbrev_attr *, const vmpa2t *);



/* ----------------------- TRAITEMENT D'ABREVIATIONS PAR LOTS ----------------------- */


/* Brochette d'abréviations */
struct _dw_abbrev_brotherhood
{
    dw_abbrev **abbrevs;                    /* Liste des sous-éléments     */
    size_t count;                           /* Nombre de ces éléments      */

};



/* ---------------------------------------------------------------------------------- */
/*                         TRAITEMENT D'ABREVIATION A L'UNITE                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations de débogage à consulter.              *
*                cu      = unité de compilation parente.                      *
*                content = contenu binaire borné à parcourir.                 *
*                pos     = tête de lecture à faire évoluer. [OUT]             *
*                abbrev  = abréviation lue et complète, NULL si aucune. [OUT] *
*                                                                             *
*  Description : Charge une abréviation valide pour un DWARF en mémoire.      *
*                                                                             *
*  Retour      : Bilan de l'opération, potentiellement un succès sans sortie. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_dwarf_abbreviation(GDwarfFormat *format, const dw_compil_unit_header *cu, GBinContent *content, vmpa2t *pos, dw_abbrev **abbrev)
{
    vmpa2t old;                             /* Mémorisation d'une position */
    dw_abbrev *new;                         /* Nouvelle abréviation        */
    dw_abbrev_decl decl;                    /* En-tête d'abréviation       */
    dw_abbrev_raw_attr attr;                /* Attribut de l'abréviation   */
    bool status;                            /* Bilan d'une lecture         */

    new = NULL;

    /**
     * Cette routine est la transcription du paragraphe 7.5.3 ("Abbreviations Tables"),
     * de la quatrième version de la définition du format DWARF.
     *
     * La spécification précise :
     *
     *    As mentioned in Section 2.3, each chain of sibling entries is terminated by a null entry.
     *
     * Par ailleurs, readelf comporte le commentaire suivant dans le fichier 'dwarf_reader.cc' :
     *
     *    Read the abbrev code. A zero here indicates the end of the abbrev table.
     *
     */

    copy_vmpa(&old, pos);

    if (!read_dwarf_abbrev_decl(content, pos, &decl))
        goto lda_bad_exit;

    if (decl.code == 0)
        goto lda_exit;

    new = (dw_abbrev *)calloc(1, sizeof(dw_abbrev));

    if (!conv_abbrev_decl(format, cu, &decl, new, &old))
        goto lda_bad_exit;

    /* Chargement des attributs */

    for (;;)
    {
        copy_vmpa(&old, pos);

        status = read_dwarf_abbrev_attr(content, pos, &attr);
        if (!status) goto lda_bad_exit;

        if (attr.name == 0 && attr.form == 0)
            break;

        new->count++;
        new->attribs = (dw_abbrev_attr *)realloc(new->attribs,
                                                 new->count * sizeof(dw_abbrev_attr));

        status = conv_abbrev_attrib(format, cu, &attr, &new->attribs[new->count - 1], &old);
        if (!status) goto lda_bad_exit;

    }

 lda_exit:

    *abbrev = new;

    return true;

 lda_bad_exit:

    if (new != NULL)
        free_dwarf_abbrev(new);

    *abbrev = NULL;

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : abbrev = abréviation chargée en mémoire à traiter.           *
*                                                                             *
*  Description : Supprime de la mémoire toute trace d'une abréviation DWARF.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void free_dwarf_abbrev(dw_abbrev *abbrev)
{
    if (abbrev->attribs != NULL)
        free(abbrev->attribs);

    free(abbrev);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations de débogage à consulter.               *
*                cu     = unité de compilation parente.                       *
*                decl   = structure brute dont le contenu est à valider.      *
*                abbrev = abréviation à constituer à partir du brut. [OUT]    *
*                pos    = emplacement de l'élément à vérifier dans le binaire.*
*                                                                             *
*  Description : Procède à la conversion de base d'une abréviation DWARF.     *
*                                                                             *
*  Retour      : Validité confirmée ou non.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool conv_abbrev_decl(GDwarfFormat *format, const dw_compil_unit_header *cu, const dw_abbrev_decl *decl, dw_abbrev *abbrev, const vmpa2t *pos)
{
    bool result;                            /* Validité à retourner        */

    result = check_dwarf_abbrev_decl(format, decl, cu->version, pos);

    if (result)
    {
        abbrev->code = decl->code;
        abbrev->tag = decl->tag;

        abbrev->has_children = (decl->has_children == DW_CHILDREN_yes);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations de débogage à consulter.               *
*                cu     = unité de compilation parente.                       *
*                decl   = structure brute dont le contenu est à valider.      *
*                abbrev = abréviation à constituer à partir du brut. [OUT]    *
*                pos    = emplacement de l'élément à vérifier dans le binaire.*
*                                                                             *
*  Description : Procède à la conversion d'un attribut d'abréviation DWARF.   *
*                                                                             *
*  Retour      : Validité confirmée ou non.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool conv_abbrev_attrib(GDwarfFormat *format, const dw_compil_unit_header *cu, const dw_abbrev_raw_attr *attr, dw_abbrev_attr *attrib, const vmpa2t *pos)
{
    bool result;                            /* Validité à retourner        */

    result = check_dwarf_abbrev_attrib(format, attr, cu->version, pos);

    if (result)
    {
        attrib->name = attr->name;
        attrib->form = attr->form;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : abbrev = abréviation chargée en mémoire à consulter.         *
*                                                                             *
*  Description : Compte le nombre d'attributs présents dans une abréviation.  *
*                                                                             *
*  Retour      : Quantité d'attributs pris en compte dans l'abréviation.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t dwarf_abbreviation_count_attribs(const dw_abbrev *abbrev)
{
    return abbrev->count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : abbrev  = abréviation à consulter.                           *
*                format  = contenu binaire de débogage à parcourir.           *
*                content = contenu encadré à parcourir.                       *
*                pos     = tête de lecture au sein des données. [OUT]         *
*                cu      = unité de compilation parente.                      *
*                                                                             *
*  Description : Lit la valeur correspondant à un type donné.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dw_value *translate_abbrev_attribs(const dw_abbrev *abbrev, const GDwarfFormat *format, GBinContent *content, vmpa2t *pos, const dw_compil_unit_header *cu)
{
    dw_value *result;                       /* Valeurs lues retournées     */
    size_t i;                               /* Boucle de parcours          */
    bool status;                            /* Bilan d'une lecture         */

    result = (dw_value *)calloc(abbrev->count, sizeof(dw_value));

    for (i = 0; i < abbrev->count; i++)
    {
        result[i].attrib = abbrev->attribs[i].name;

        status = read_dwarf_form_value(format, content, pos, cu,
                                       abbrev->attribs[i].form, &result[i].value);

        if (!status) break;

    }

    if (i != abbrev->count)
    {
        free_abbrev_attribs(result, abbrev->count);
        result = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : values = liste de valeurs typées à traiter.                  *
*                count  = nombre d'éléments de la liste.                      *
*                                                                             *
*  Description : Supprime de la mémoire une liste de valeurs typées.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void free_abbrev_attribs(dw_value *values, size_t count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < count; i++)
        if (values[i].value != NULL)
            free_dwarf_form_value(values[i].value);

    free(values);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : abbrev = abréviation à consulter.                            *
*                                                                             *
*  Description : Détermine si l'abréviation possède des enfants.              *
*                                                                             *
*  Retour      : true si des sous-éléments sont présents.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_abbrev_children(const dw_abbrev *abbrev)
{
    bool result;                            /* Bilan à retourner           */

    result = abbrev->has_children;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         TRAITEMENT D'ABREVIATIONS PAR LOTS                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations de débogage à constituer.              *
*                cu     = en-tête de description de l'unité à traiter.        *
*                                                                             *
*  Description : Charge une série d'abréviations présentes dans un DWARF.     *
*                                                                             *
*  Retour      : Structure mise en place, ou NULL en cas d'erreur.            *
*                                                                             *
*  Remarques   : Le décalage est positionné à VMPA_NO_PHYSICAL en cas de fin. *
*                                                                             *
******************************************************************************/

dw_abbrev_brotherhood *load_all_dwarf_abbreviations(GDwarfFormat *format, const dw_compil_unit_header *cu)
{
    dw_abbrev_brotherhood *result;          /* Abréviations à retourner    */
    GExeFormat *exe;                        /* Exécutable associé          */
    mrange_t range;                         /* Couverture d'une section    */
    bool status;                            /* Bilan d'un appel            */
    GBinContent *content;                   /* Contenu binaire à lire      */
    GBinContent *restricted;                /* Limitation des traitements  */
    vmpa2t pos;                             /* Position de tête de lecture */
    dw_abbrev *abbrev;                      /* Nouvelle abréviation        */

    result = NULL;

    exe = G_DBG_FORMAT(format)->executable;

    status = g_exe_format_get_section_range_by_name(exe, ".debug_abbrev", &range);

    if (status)
    {
        /* Définition d'un zone de travail */

        content = G_KNOWN_FORMAT(format)->content;
        restricted = g_restricted_content_new(content, &range);

        copy_vmpa(&pos, get_mrange_addr(&range));
        advance_vmpa(&pos, cu->debug_abbrev_offset);

        /* Lecture de toutes les abréviations */

        result = calloc(1, sizeof(dw_abbrev_brotherhood));

        while (true)
        {
            status = load_dwarf_abbreviation(format, cu, restricted, &pos, &abbrev);
            if (!status) break;

            if (abbrev == NULL)
                break;

            result->abbrevs = realloc(result->abbrevs, ++result->count * sizeof(dw_abbrev *));

            result->abbrevs[result->count - 1] = abbrev;

        }

        /* Nettoyage */

        if (!status)
        {
            free_all_dwarf_abbreviations(result);
            result = NULL;
        }

        g_object_unref(G_OBJECT(restricted));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = série d'abréviations chargées en mémoire à traiter.   *
*                                                                             *
*  Description : Supprime de la mémoire toute trace d'abréviations DWARF.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void free_all_dwarf_abbreviations(dw_abbrev_brotherhood *list)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < list->count; i++)
        free_dwarf_abbrev(list->abbrevs[i]);

    if (list->abbrevs != NULL)
        free(list->abbrevs);

    free(list);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = série d'abréviations à consulter.                     *
*                code = identifiant de l'abbréviation recherchée.             *
*                                                                             *
*  Description : Recherche une abréviation DWARF donnée.                      *
*                                                                             *
*  Retour      : Adresse d'une abréviation ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const dw_abbrev *find_dwarf_abbreviation(const dw_abbrev_brotherhood *list, uleb128_t code)
{
    const dw_abbrev *result;                /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < list->count; i++)
        if (list->abbrevs[i]->code == code)
        {
            result = list->abbrevs[i];
            break;
        }

    return result;

}
