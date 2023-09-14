
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - prise en compte d'une syntaxe du langage d'assemblage
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


#include "manager.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../helpers.h"



/* Propriétés particulières pour les opérandes */
typedef enum _SyntaxItemFlags
{
    SIF_NONE     = (0 << 0),                /* Aucune propriété            */
    SIF_DECIMAL  = (1 << 0),                /* Affichage en décimal        */
    SIF_OPTIONAL = (1 << 1)                 /* Absence tolérée             */

} SyntaxItemFlags;

/* Elément défini dans une syntaxe */
typedef struct _syntax_item
{
    char *name;                             /* Désignation humaine         */
    SyntaxItemFlags flags;                  /* Propriétés supplémentaires  */

} syntax_item;

/* Syntaxe d'une ligne d'assembleur */
struct _asm_pattern
{
    syntax_item *items;                     /* Eléments de la syntaxe      */
    size_t items_count;                     /* Nombre de ces éléments      */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouvel indicateur pour l'écriture d'une instruction. *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

asm_pattern *create_asm_pattern(void)
{
    asm_pattern *result;                    /* Définition vierge à renvoyer*/

    result = (asm_pattern *)calloc(1, sizeof(asm_pattern));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = gestionnaire d'un ensemble d'éléments de syntaxe.  *
*                                                                             *
*  Description : Supprime de la mémoire un indicateur d'écriture ASM.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_asm_pattern(asm_pattern *pattern)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < pattern->items_count; i++)
        free(pattern->items[i].name);

    if (pattern->items != NULL)
        free(pattern->items);

    free(pattern);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = gestionnaire d'un ensemble d'éléments de syntaxe.  *
*                name    = désignation de l'opérande dans la spécification.   *
*                                                                             *
*  Description : Enregistre la présence d'un nouvel opérande dans la syntaxe. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_asm_pattern_item(asm_pattern *pattern, char *name)
{
    syntax_item *item;                      /* Nouvelle prise en compte    */
    size_t len;                             /* Taille du nom fourni        */

    pattern->items = (syntax_item *)realloc(pattern->items, ++pattern->items_count * sizeof(syntax_item));

    item = &pattern->items[pattern->items_count - 1];

    /* Récupération des drapeaux */

    item->flags = SIF_NONE;

    for (len = strlen(name); len > 0; len--)
        switch (name[0])
        {
            case '#':
                item->flags |= SIF_DECIMAL;
                memmove(name, name + 1, len);
                break;

            case '?':
                item->flags |= SIF_OPTIONAL;
                memmove(name, name + 1, len);
                break;

            default:
                len = 1;
                break;

        }

    item->name = make_string_lower(name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = gestionnaire d'un ensemble d'éléments de syntaxe.  *
*                bits    = gestionnaire des bits d'encodage.                  *
*                list    = liste de l'ensemble des fonctions de conversion.   *
*                                                                             *
*  Description : Marque les champs de bits effectivement utilisés.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mark_asm_pattern_items(const asm_pattern *pattern, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    syntax_item *item;                      /* Lien vers un opérande       */
    conv_func *func;                        /* Fonction de conversion      */

    result = true;

    for (i = 1; i < pattern->items_count && result; i++)
    {
        item = &pattern->items[i];

        func = find_named_conv_in_list(list, item->name);
        if (func == NULL)
        {
            fprintf(stderr, "Error: expected conversion for '%s'.\n", item->name);
            result = false;
        }

        result = mark_conv_func(func, false, bits, list);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern  = gestionnaire d'un ensemble d'éléments de syntaxe. *
*                fd       = descripteur d'un flux ouvert en écriture.         *
*                bits     = gestionnaire des bits d'encodage.                 *
*                list     = liste de l'ensemble des fonctions de conversion.  *
*                tab      = décalage éventuel selon l'inclusion.              *
*                imm_decl = une déclaration d'immédiat est déjà faite ? [OUT] *
*                                                                             *
*  Description : Déclare les variables C associées aux opérandes de syntaxe.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool declare_asm_pattern(const asm_pattern *pattern, int fd, const coding_bits *bits, const conv_list *list, const char *tab, bool *imm_decl)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    syntax_item *item;                      /* Lien vers un opérande       */
    conv_func *func;                        /* Fonction de conversion      */

    result = true;

    for (i = 1; i < pattern->items_count && result; i++)
    {
        item = &pattern->items[i];

        func = find_named_conv_in_list(list, item->name);
        assert(func != NULL);

        result = declare_conv_func(func, fd, bits, list, tab);

        if (result && item->flags & SIF_DECIMAL && !*imm_decl)
        {
            dprintf(fd, "\t%sGImmOperand *imm;\n", tab);
            *imm_decl = true;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = gestionnaire d'un ensemble d'éléments de syntaxe.  *
*                                                                             *
*  Description : Fournit si elle existe un nom nouveau pour une instruction.  *
*                                                                             *
*  Retour      : Eventuelle chaîne de caractères trouvée ou NULL.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_keyword_from_asm_pattern(const asm_pattern *pattern)
{
    const char *result;                     /* Nom éventuel à renvoyer     */

    assert(pattern->items_count > 0);

    result = pattern->items[0].name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = gestionnaire d'un ensemble d'éléments de syntaxe.  *
*                fd      = descripteur d'un flux ouvert en écriture.          *
*                arch    = architecture visée par l'opération globale.        *
*                bits    = gestionnaire des bits d'encodage.                  *
*                list    = liste de l'ensemble des fonctions de conversion.   *
*                tab     = décalage éventuel selon l'inclusion.               *
*                exit    = exprime le besoin d'une voie de sortie. [OUT]      *
*                                                                             *
*  Description : Définit les variables C associées aux opérandes de syntaxe.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_asm_pattern(const asm_pattern *pattern, int fd, const char *arch, const coding_bits *bits, const conv_list *list, const char *tab, bool *exit)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    syntax_item *item;                      /* Lien vers un opérande       */
    conv_func *func;                        /* Fonction de conversion      */
    bool optional;                          /* Opérande optionnelle ?      */

    result = true;

    for (i = 1; i < pattern->items_count; i++)
    {
        item = &pattern->items[i];

        func = find_named_conv_in_list(list, item->name);
        assert(func != NULL);

        optional = item->flags & SIF_OPTIONAL;

        result = define_conv_func(func, fd, bits, list, tab, optional, exit);
        if (!result) break;

        if (optional)
        {
            dprintf(fd, "\t%sif (", tab);

            write_conv_func(func, fd, false);

            dprintf(fd, " != NULL)");

            dprintf(fd, "\n");

            if (item->flags & SIF_DECIMAL)
            {
                dprintf(fd, "\t%s{\n", tab);

                dprintf(fd, "\t%s\timm = G_IMM_OPERAND(", tab);

                write_conv_func(func, fd, false);

                dprintf(fd, ");\n");

                dprintf(fd, "\t%s\tg_imm_operand_set_default_display(imm, IOD_DEC);\n", tab);

                dprintf(fd, "\n");

                dprintf(fd, "\t%s\tg_arch_instruction_attach_extra_operand(result, ", tab);

                write_conv_func(func, fd, false);

                dprintf(fd, ");\n");

                dprintf(fd, "\n");

                dprintf(fd, "\t%s}\n", tab);

                dprintf(fd, "\n");

            }

            else
            {
                dprintf(fd, "\t%s\tg_arch_instruction_attach_extra_operand(result, ", tab);

                write_conv_func(func, fd, false);

                dprintf(fd, ");\n");

                dprintf(fd, "\n");

            }

        }

        else
        {
            if (item->flags & SIF_DECIMAL)
            {
                dprintf(fd, "\t%simm = G_IMM_OPERAND(", tab);

                write_conv_func(func, fd, false);

                dprintf(fd, ");\n");

                dprintf(fd, "\t%sg_imm_operand_set_default_display(imm, IOD_DEC);\n", tab);

                dprintf(fd, "\n");

            }

            dprintf(fd, "\t%sg_arch_instruction_attach_extra_operand(result, ", tab);

            write_conv_func(func, fd, false);

            dprintf(fd, ");\n");

            dprintf(fd, "\n");

        }

    }

    return result;

}
