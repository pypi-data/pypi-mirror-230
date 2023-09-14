
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encoding.c - représentation complète d'un encodage
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


#include "encoding.h"


#include <assert.h>
#include <malloc.h>
#include <regex.h>
#include <stdio.h>
#include <string.h>


#include "helpers.h"
#include "qckcall.h"



/* Mémorisation d'un encodage complet */
struct _encoding_spec
{
    char *prefix;                           /* Distinction principale      */
    char *lprefix;                          /* Distinction en minuscules   */
    unsigned int index;                     /* Distinction secondaire      */

    operands_format *format;                /* Définition des opérandes    */

    coding_bits *bits;                      /* Encodage des bits associés  */
    instr_hooks *hooks;                     /* Fonctions complémentaires   */

    encoding_syntax **syntaxes;             /* Définitions déjà en place   */
    size_t syntax_count;                    /* Nombre de ces définitions   */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau suivi de l'encodage d'une instruction.       *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

encoding_spec *create_encoding_spec(void)
{
    encoding_spec *result;                  /* Définition vierge à renvoyer*/

    result = (encoding_spec *)calloc(1, sizeof(encoding_spec));

    result->format = create_operands_format();

    result->bits = create_coding_bits();
    result->hooks = create_instr_hooks();

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à libérer de la mémoire.     *
*                                                                             *
*  Description : Supprime de la mémoire un suivi d'encodage d'une instruction.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_encoding_spec(encoding_spec *spec)
{
    size_t i;                               /* Boucle de parcours          */

    delete_operands_format(spec->format);

    delete_coding_bits(spec->bits);
    delete_instr_hooks(spec->hooks);

    if (spec->syntaxes != NULL)
    {
        for (i = 0; i < spec->syntax_count; i++)
            delete_encoding_syntax(spec->syntaxes[i]);

        free(spec->syntaxes);

    }

    free(spec);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification d'encodage à compléter.               *
*                prefix = distinction principale entre les définitions.       *
*                index  = distinction secondaire entre les définitions.       *
*                                                                             *
*  Description : Définit le nom de code d'une spécification d'encodage.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void define_encoding_spec_code_name(encoding_spec *spec, char *prefix, unsigned int index)
{
    spec->prefix = prefix;
    spec->lprefix = make_string_lower(strdup(prefix));
    spec->index = index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification d'encodage à consulter.               *
*                prefix = distinction principale entre les définitions.       *
*                                                                             *
*  Description : Indique si une spécification se range dans une catégorie.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_encoding_spec_prefix(const encoding_spec *spec, const char *prefix)
{
    bool result;                            /* Bilan à renvoyer            */

    if (spec->prefix == NULL && prefix == NULL)
        result = true;

    else if (spec->prefix != NULL && prefix != NULL)
        result = strcmp(spec->prefix, prefix) == 0;

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à consulter.                 *
*                                                                             *
*  Description : Construit la distinction propre à un encodage.               *
*                                                                             *
*  Retour      : Distinction à libérer de la mémoire après usage.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_encoding_spec_prefix(const encoding_spec *spec)
{
    char *result;                           /* Chaîne à retourner          */
    int ret;                                /* Recette de construction     */

    assert(spec->lprefix);

    ret = asprintf(&result, "%s%u", spec->lprefix, spec->index);

    if (ret == -1)
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à consulter.                 *
*                                                                             *
*  Description : Fournit le gestionnaire des définitions d'opérandes.         *
*                                                                             *
*  Retour      : Structure assurant la définition des opérandes.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

operands_format *get_format_in_encoding_spec(const encoding_spec *spec)
{
    return spec->format;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à consulter.                 *
*                                                                             *
*  Description : Fournit le gestionnaire des bits d'un encodage d'instruction.*
*                                                                             *
*  Retour      : Structure assurant le suivi des bits.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

coding_bits *get_bits_in_encoding_spec(const encoding_spec *spec)
{
    return spec->bits;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à consulter.                 *
*                                                                             *
*  Description : Fournit la liste des fonctions à lier à une instruction.     *
*                                                                             *
*  Retour      : Structure assurant la gestion des fonctions de conversion.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_hooks *get_hooks_in_encoding_spec(const encoding_spec *spec)
{
    return spec->hooks;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à étendre.                   *
*                                                                             *
*  Description : Enregistre une définition de syntaxe supplémentaire.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void push_new_encoding_syntax(encoding_spec *spec)
{
    encoding_syntax *syntax;                /* Définition à compléter      */

    syntax = create_encoding_syntax();

    spec->syntaxes = realloc(spec->syntaxes, ++spec->syntax_count * sizeof(encoding_syntax *));
    spec->syntaxes[spec->syntax_count - 1] = syntax;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification d'encodage à consulter.                 *
*                                                                             *
*  Description : Fournit un lien vers la définition de syntaxe courante.      *
*                                                                             *
*  Retour      : Définition en cours d'édition.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

encoding_syntax *get_current_encoding_syntax(const encoding_spec *spec)
{
    encoding_syntax *result;                /* Définition à retourner      */

    if (spec->syntax_count == 0)
        result = NULL;

    else
        result = spec->syntaxes[spec->syntax_count - 1];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification servant de base à l'opération.          *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                arch = architecture visée par l'opération.                   *
*                id   = désignation de l'identifiant d'instruction.           *
*                pp   = pré-processeur pour les échanges de chaînes.          *
*                                                                             *
*  Description : Traduit en code une sous-fonction de désassemblage.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_encoding_spec_raw_disass(const encoding_spec *spec, int fd, const char *arch, const char *id, const pre_processor *pp)
{
    bool result;                            /* Bilan à retourner           */
    bool openbar;                           /* Syntaxe unique par défaut ? */
    disass_assert *dassert;                 /* Eventuelles conditions      */
    char *suffix;                           /* Complément d'identifiant    */
    char *sid;                              /* Base de sous-identifiant    */
    int ret;                                /* Bilan d'une construction    */
    size_t i;                               /* Boucle de parcours          */
    bool op_decl;                           /* Suivi des déclaration #1    */
    bool imm_decl;                          /* Suivi des déclaration #2    */
    bool bad_exit;                          /* Ajout d'une sortie d'échec ?*/
    bool quick_exit;                        /* Inclusion de sortie rapide ?*/
    char *encoding_fc;                      /* Spécification d'encodage    */
    char *cast;                             /* Conversion vers le format   */

    result = true;

    /* Détermination de la forme du code */

    openbar = (spec->syntax_count == 1);

    if (openbar)
    {
        dassert = get_assertions_for_encoding_syntax(spec->syntaxes[0]);
        openbar = is_disass_assert_empty(dassert);
    }

    else
    {
        for (i = 0; i < spec->syntax_count && result; i++)
        {
            dassert = get_assertions_for_encoding_syntax(spec->syntaxes[0]);

            if (is_disass_assert_empty(dassert))
            {
                fprintf(stderr, "The syntax definition #%zu has no entry conditions!\n", i);
                result = false;
            }

        }

    }

    if (!result)
        goto exit;

    /* Déclarations préalables */

    dprintf(fd, "\tGArchInstruction *result;               /* Instruction créée à renvoyer*/\n");

    for (i = 0; i < spec->syntax_count && result; i++)
        result = mark_syntax_items(spec->syntaxes[i], spec->bits);

    if (!result)
        goto exit;

    result = declare_used_bits_fields(spec->bits, fd);
    if (!result) goto exit;

    if (openbar)
    {
        result = declare_encoding_syntax(spec->syntaxes[0], fd, spec->bits);
        if (!result) goto exit;
    }

    dprintf(fd, "\n");

    /* Vérification que le décodage est possible */

    result = check_bits_correctness(spec->bits, fd);
    if (!result) goto exit;

    dprintf(fd, "\n");

    /* Initialisation du resultat d'un point de vue global */

    if (!openbar)
    {
        dprintf(fd, "\tresult = NULL;\n");
        dprintf(fd, "\n");
    }

    /* Définition des champs bruts */

    result = define_used_bits_fields(spec->bits, fd);
    if (!result) goto exit;

    suffix = build_encoding_spec_prefix(spec);
    if (suffix == NULL) goto exit;

    make_string_upper(suffix);

    ret = asprintf(&sid, "%s_%s", id, suffix);

    free(suffix);

    if (ret == -1)
        goto exit;

    for (i = 0; i < spec->syntax_count && result; i++)
    {
        if (spec->syntax_count > 1)
            result = write_encoding_syntax(spec->syntaxes[i], fd, arch, spec->bits, openbar, id, sid, &i, &bad_exit);
        else
            result = write_encoding_syntax(spec->syntaxes[i], fd, arch, spec->bits, openbar, id, sid, NULL, &bad_exit);
    }

    free(sid);

    if (!result)
        goto exit;

    /* Encodage en dernier lieu */

    ret = asprintf(&encoding_fc, "g_%s_instruction_set_encoding", arch);

    if (ret == -1)
        goto exit;

    cast = build_cast_if_needed(encoding_fc);

    if (!openbar)
        dprintf(fd, "\tif (result != NULL)\n");

    dprintf(fd, "\t%s%s(%s(result), \"%s\");\n", openbar ? "" : "\t", encoding_fc, cast, spec->prefix);

    free(cast);

    free(encoding_fc);

    dprintf(fd, "\n");

    /* Conclusion globale */

    dprintf(fd, "\treturn result;\n");

    dprintf(fd, "\n");

    if (bad_exit)
    {
        dprintf(fd, " bad_exit:\n");
        dprintf(fd, "\n");

        dprintf(fd, "\tg_object_unref(G_OBJECT(result));\n");
        dprintf(fd, "\treturn NULL;\n");

        dprintf(fd, "\n");

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification servant de base à l'opération.        *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                arch   = architecture visée par l'opération.                 *
*                id     = identifiant unique attribué à l'instruction.        *
*                prefix = préfixe pour le type de définitions d'opérandes.    *
*                                                                             *
*  Description : Traduit en code une sous-fonction de désassemblage.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_encoding_spec_format_disass(const encoding_spec *spec, int fd, const char *arch, const char *id, const char *prefix)
{
    bool result;                            /* Bilan à retourner           */
    bool bad_exit;                          /* Ajout d'une sortie d'échec ?*/
    conv_list *conversions;                 /* Conversions de la syntaxe   */
    decoding_rules *rules;                  /* Règles de la syntaxe        */

    /* Déclarations préalables */

    dprintf(fd, "\tGArchInstruction *result;               /* Instruction créée à renvoyer*/\n");
    dprintf(fd, "\tSourceEndian endian;                    /* Boutisme lié au binaire     */\n");

    dprintf(fd, "\n");

    /* Création de l'instruction en elle-même */

    dprintf(fd, "\tresult = g_%s_instruction_new(%s);\n", arch, id);

    dprintf(fd, "\n");

    bad_exit = false;

    assert(spec->syntax_count <= 1);

    if (spec->syntax_count > 0)
    {
        conversions = get_conversions_in_encoding_syntax(spec->syntaxes[0]);
        rules = get_rules_in_encoding_syntax(spec->syntaxes[0]);

        result = write_decoding_rules(rules, CAT_CHECKED_CALL, fd, arch, spec->bits, conversions, "", &bad_exit);
        if (!result) goto wesfd_exit;

        result = write_decoding_rules(rules, CAT_CALL, fd, arch, spec->bits, conversions, "", &bad_exit);
        if (!result) goto wesfd_exit;

    }

    /* Création des opérandes */

    dprintf(fd, "\tendian = g_arch_processor_get_endianness(proc);\n");

    dprintf(fd, "\n");

    result = define_operands_loading(spec->format, fd, arch, prefix, &bad_exit);
    if (!result) goto wesfd_exit;

    /* Conclusion de la procédure */

    dprintf(fd, "\treturn result;\n");

    dprintf(fd, "\n");

    if (bad_exit)
    {
        if (bad_exit)
            dprintf(fd, " bad_exit:\n");

        dprintf(fd, "\n");

        dprintf(fd, "\tg_object_unref(G_OBJECT(result));\n");
        dprintf(fd, "\treturn NULL;\n");

        dprintf(fd, "\n");

    }

 wesfd_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification servant de base à l'opération.        *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                name   = désignation de l'identifiant d'instruction.         *
*                                                                             *
*  Description : Imprime les mots clefs de chaque syntaxe.                    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_encoding_spec_keywords(const encoding_spec *spec, int fd, const char *name)
{
    bool result;                            /* Bilan à retourner           */
    char *suffix;                           /* Complément d'identifiant    */
    size_t i;                               /* Boucle de parcours          */
    asm_pattern *pattern;                   /* Définition d'assemblage     */
    const char *keyword;                    /* Mot clef principal          */

    suffix = build_encoding_spec_prefix(spec);

    result = (suffix != NULL);
    if (!result) goto exit;

    make_string_upper(suffix);

    for (i = 0; i < spec->syntax_count; i++)
    {
        /* Impression de la colonne */

        if (spec->syntax_count == 1)
            dprintf(fd, "\t[%s_%s]", name, suffix);
        else
            dprintf(fd, "\t[%s_%s_%zu]", name, suffix, i);

        /* Impression des décrochages */

        pattern = get_asm_pattern_in_encoding_syntax(spec->syntaxes[i]);

        keyword = get_keyword_from_asm_pattern(pattern);

        dprintf(fd, " = \"%s\",\n", keyword);

    }

    free(suffix);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification servant de base à l'opération.        *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                name   = désignation de l'identifiant d'instruction.         *
*                                                                             *
*  Description : Imprime la définition d'un sous-identifiant pour un encodage.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_encoding_spec_subid(const encoding_spec *spec, int fd, const char *name)
{
    bool result;                            /* Bilan à retourner           */
    char *suffix;                           /* Complément d'identifiant    */
    size_t i;                               /* Boucle de parcours          */
    instr_id *subid;                        /* Sous-identifiant de syntaxe */
    unsigned int idval;                     /* Identifiant unique attribué */

    suffix = build_encoding_spec_prefix(spec);

    result = (suffix != NULL);
    if (!result) goto exit;

    make_string_upper(suffix);

    for (i = 0; i < spec->syntax_count; i++)
    {
        subid = get_encoding_syntax_subid(spec->syntaxes[i]);
        idval = get_instruction_id_value(subid);

        if (spec->syntax_count == 1)
            dprintf(fd, "\t%s_%s = %u,\n", name, suffix, idval);
        else
            dprintf(fd, "\t%s_%s_%zu = %u,\n", name, suffix, i, idval);

    }

    free(suffix);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification servant de base à l'opération.        *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                name   = désignation de l'identifiant d'instruction.         *
*                refine = utilisation d'un identifiant plus précis ?          *
*                                                                             *
*  Description : Imprime d'éventuels décrochages spécifiés pour un encodage.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_encoding_spec_hooks(const encoding_spec *spec, int fd, const char *name, bool refine)
{
    bool result;                            /* Bilan à retourner           */
    char *suffix;                           /* Complément d'identifiant    */
    size_t i;                               /* Boucle de parcours          */

    if (!has_hook_functions(spec->hooks))
        result = true;

    else
    {
        if (refine)
        {
            suffix = build_encoding_spec_prefix(spec);

            result = (suffix != NULL);
            if (!result) goto exit;

            make_string_upper(suffix);

            for (i = 0; i < spec->syntax_count; i++)
            {
                /* Impression de la colonne */

                if (spec->syntax_count == 1)
                    dprintf(fd, "\t[%s_%s]", name, suffix);
                else
                    dprintf(fd, "\t[%s_%s_%zu]", name, suffix, i);

                /* Impression des décrochages */

                dprintf(fd, " = {\n", name);

                result = write_hook_functions(spec->hooks, fd);

                dprintf(fd, "\t},\n", name);

            }

            free(suffix);

        }

        else
        {
            /* Impression de la colonne */

            dprintf(fd, "\t[%s]", name);

            /* Impression des décrochages */

            dprintf(fd, " = {\n", name);

            result = write_hook_functions(spec->hooks, fd);

            dprintf(fd, "\t},\n", name);

        }

    }

 exit:

    return result;

}
