
/* Chrysalide - Outil d'analyse de fichiers binaires
 * syntax.c - représentation complète d'une syntaxe
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#include "syntax.h"


#include <assert.h>
#include <malloc.h>



/* Mémorisation d'une définition de syntaxe */
struct _encoding_syntax
{
    instr_id *subid;                        /* Gestionnaire d'identifiant  */
    disass_assert *assertions;              /* Conditions de désassemblage */
    conv_list *conversions;                 /* Conversions des données     */
    asm_pattern *pattern;                   /* Calligraphe d'assemblage    */
    decoding_rules *rules;                  /* Règles supplémentaires      */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau suivi d'une définition de syntaxe.           *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

encoding_syntax *create_encoding_syntax(void)
{
    encoding_syntax *result;                  /* Définition vierge à renvoyer*/

    result = (encoding_syntax *)calloc(1, sizeof(encoding_syntax));

    result->subid = create_instruction_id();
    result->assertions = create_disass_assert();
    result->conversions = create_conv_list();
    result->pattern = create_asm_pattern();
    result->rules = create_decoding_rules();

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = définition de syntaxe à libérer de la mémoire.      *
*                                                                             *
*  Description : Supprime de la mémoire le suivi d'une définition de syntaxe. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_encoding_syntax(encoding_syntax *syntax)
{
    delete_instruction_id(syntax->subid);
    delete_disass_assert(syntax->assertions);
    delete_conv_list(syntax->conversions);
    delete_asm_pattern(syntax->pattern);
    delete_decoding_rules(syntax->rules);

    free(syntax);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = définition de syntaxe à consulter.                  *
*                                                                             *
*  Description : Fournit le gestionnaire des définitions d'identifiant.       *
*                                                                             *
*  Retour      : Structure assurant la définition d'identifiant.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_id *get_encoding_syntax_subid(const encoding_syntax *syntax)
{
    return syntax->subid;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = définition de syntaxe à consulter.                  *
*                                                                             *
*  Description : Fournit la liste de conditions préalables.                   *
*                                                                             *
*  Retour      : Structure assurant la gestion de conditions de désassemblage.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

disass_assert *get_assertions_for_encoding_syntax(const encoding_syntax *syntax)
{
    return syntax->assertions;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = définition de syntaxe à consulter.                  *
*                                                                             *
*  Description : Fournit la liste des fonctions de conversion.                *
*                                                                             *
*  Retour      : Structure assurant la gestion des fonctions de conversion.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

conv_list *get_conversions_in_encoding_syntax(const encoding_syntax *syntax)
{
    return syntax->conversions;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = définition de syntaxe à consulter.                  *
*                                                                             *
*  Description : Fournit l'indicateur des écritures correctes d'assembleur.   *
*                                                                             *
*  Retour      : Structure assurant la gestion des éléments de syntaxe.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

asm_pattern *get_asm_pattern_in_encoding_syntax(const encoding_syntax *syntax)
{
    return syntax->pattern;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = définition de syntaxe à consulter.                  *
*                                                                             *
*  Description : Fournit un ensemble de règles supplémentaires éventuel.      *
*                                                                             *
*  Retour      : Structure assurant la gestion de ces règles.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

decoding_rules *get_rules_in_encoding_syntax(const encoding_syntax *syntax)
{
    return syntax->rules;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = gestionnaire d'un ensemble d'éléments de syntaxe.   *
*                bits   = gestionnaire des bits d'encodage.                   *
*                                                                             *
*  Description : Marque les éléments de syntaxe effectivement utilisés.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mark_syntax_items(const encoding_syntax *syntax, const coding_bits *bits)
{
    bool result;                            /* Bilan à retourner           */

    result = mark_disass_assert(syntax->assertions, bits);

    if (result)
        result = mark_asm_pattern_items(syntax->pattern, bits, syntax->conversions);

    if (result)
        result = mark_decoding_rules(syntax->rules, bits, syntax->conversions);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax = gestionnaire d'un ensemble d'éléments de syntaxe.   *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                bits   = gestionnaire des bits d'encodage.                   *
*                                                                             *
*  Description : Déclare les éléments d'une syntaxe isolée.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool declare_encoding_syntax(const encoding_syntax *syntax, int fd, const coding_bits *bits)
{
    bool result;                            /* Bilan à retourner           */
    bool imm_decl;                          /* Suivi des déclaration       */

    imm_decl = false;

    result = declare_asm_pattern(syntax->pattern, fd, bits, syntax->conversions, "", &imm_decl);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : syntax  = gestionnaire d'un ensemble d'éléments de syntaxe.  *
*                fd      = descripteur d'un flux ouvert en écriture.          *
*                arch    = architecture visée par l'opération globale.        *
*                bits    = gestionnaire des bits d'encodage.                  *
*                openbar = peut-on se placer en zone principale ?             *
*                pp      = pré-processeur pour les échanges de chaînes.       *
*                id      = identifiant unique attribué à l'instruction.       *
*                sid     = base d'identifiant unique attribué à l'encodage.   *
*                index   = indice de la syntaxe ou NULL si syntaxe unique.    *
*                exit    = exprime le besoin d'une voie de sortie. [OUT]      *
*                                                                             *
*  Description : Amorce la construction des éléments d'une syntaxe.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_encoding_syntax(const encoding_syntax *syntax, int fd, const char *arch, const coding_bits *bits, bool openbar, const char *id, const char *sid, const size_t *index, bool *exit)
{
    bool result;                            /* Bilan à retourner           */
    bool conditional;                       /* Définition sous condition ? */
    const char *tab;                        /* Décalage supplémentaire ?   */
    bool imm_decl;                          /* Suivi des déclaration       */

    conditional = !is_disass_assert_empty(syntax->assertions);

    assert((conditional && !openbar) || (!conditional && openbar));

    if (conditional)
    {
        dprintf(fd, "\tif (");

        result = define_disass_assert(syntax->assertions, fd, bits);
        if (!result) goto wes_exit;

        dprintf(fd, ")\n");
        dprintf(fd, "\t{\n");

        tab = "\t";

    }

    else
        tab = (openbar ? "" : "\t");

    if (!openbar)
    {
        imm_decl = false;

        result = declare_asm_pattern(syntax->pattern, fd, bits, syntax->conversions, "\t", &imm_decl);
        if (!result) goto wes_exit;

        dprintf(fd, "\n");

    }

    if (!openbar)
    {
        dprintf(fd, "\t%sassert(result == NULL);\n", tab);
        dprintf(fd, "\n");
    }

    if (index == NULL)
        dprintf(fd, "\t%sresult = g_%s_instruction_new(%s, %s);\n", tab, arch, id, sid);
    else
        dprintf(fd, "\t%sresult = g_%s_instruction_new(%s, %s_%zu);\n", tab, arch, id, sid, *index);

    dprintf(fd, "\n");

    result = define_asm_pattern(syntax->pattern, fd, arch, bits, syntax->conversions, tab, exit);
    if (!result) goto wes_exit;

    result = write_decoding_rules(syntax->rules, CAT_CHECKED_CALL, fd, arch, bits, syntax->conversions, tab, exit);
    if (!result) goto wes_exit;

    result = write_decoding_rules(syntax->rules, CAT_CALL, fd, arch, bits, syntax->conversions, tab, exit);
    if (!result) goto wes_exit;

    if (conditional)
    {
        dprintf(fd, "\t}\n");

        dprintf(fd, "\n");

    }

 wes_exit:

    return result;

}
