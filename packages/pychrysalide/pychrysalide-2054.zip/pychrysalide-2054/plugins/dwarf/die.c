
/* Chrysalide - Outil d'analyse de fichiers binaires
 * die.c - gestion des entrées renvoyant à des informations de débogage
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


#include "die.h"



/**
 * § 2.1 The Debugging Information Entry (DIE).
 */

typedef struct _dw_die
{
    dw_value *values;                       /* Liste des valeurs associées */
    size_t values_count;                    /* Taille de cette liste       */

    struct _dw_die **children;              /* Liste d'éventuels enfants   */
    size_t children_count;                  /* Taille de cette liste       */

} dw_die;



/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                content = contenu encadré à parcourir.                       *
*                pos     = position de début de lecture. [OUT]                *
*                cu      = en-tête de description de l'unité à traiter.       *
*                die     = emplacement de stockage de l'entrée ou NULL. [OUT] *
*                                                                             *
*  Description : Procède à la lecture d'un élément d'information de débogage. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : Le format autorise à ne rien produire ici légitimement.      *
*                                                                             *
******************************************************************************/

bool build_dwarf_die(GDwarfFormat *format, GBinContent *content, vmpa2t *pos, const dw_compil_unit_header *cu, const dw_abbrev_brotherhood *abbrevs, dw_die **die)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t code;                         /* Code de la description liée */
    bool status;                            /* Bilan de la lecture         */
    const dw_abbrev *abbrev;                /* Lien vers la représentation */
    dw_value *values;                       /* Liste des valeurs associées */
    dw_die *child;                          /* Sous-élément à intégrer     */

    result = false;

    /**
     * § 7.5.2 Debugging Information Entry.
     */

    status = g_binary_content_read_uleb128(content, pos, &code);
    if (!status) goto exit;

    if (code == 0)
    {
        *die = NULL;
        goto end_of_sibling;
    }

    abbrev = find_dwarf_abbreviation(abbrevs, code);
    if (abbrev == NULL) goto exit;

    values = translate_abbrev_attribs(abbrev, format, content, pos, cu);
    if (values == NULL) goto exit;

    *die = calloc(1, sizeof(dw_die));

    (*die)->values = values;
    (*die)->values_count = dwarf_abbreviation_count_attribs(abbrev);

    if (has_abbrev_children(abbrev))
        while (true)
        {
            status = build_dwarf_die(format, content, pos, cu, abbrevs, &child);

            if (!status)
            {
                delete_dwarf_die(*die);
                goto exit;
            }

            if (child == NULL)
                break;

            (*die)->children = realloc((*die)->children, ++(*die)->children_count * sizeof(dw_die *));
            (*die)->children[(*die)->children_count - 1] = child;

        }

 end_of_sibling:

    result = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : die = entrée à libérer de la mémoire.                        *
*                                                                             *
*  Description : Supprime les éléments mis en place pour une entrée d'info.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_dwarf_die(dw_die *die)
{
    size_t i;                               /* Boucle de parcours          */

    if (die->values != NULL)
        free_abbrev_attribs(die->values, die->values_count);

    for (i = 0; i < die->children_count; i++)
        delete_dwarf_die(die->children[i]);

    if (die->children != NULL)
        free(die->children);

    free(die);

}
