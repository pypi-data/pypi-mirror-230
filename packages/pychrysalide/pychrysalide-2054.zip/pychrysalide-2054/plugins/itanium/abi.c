
/* Chrysalide - Outil d'analyse de fichiers binaires
 * abi.c - décodage des noms d'éléments selon l'ABI C++ Itanium
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


#include "abi.h"


#include <assert.h>
#include <ctype.h>
#include <stdlib.h>


#include <analysis/types/basic.h>
#include <analysis/types/cse.h>
#include <common/cpp.h>
#include <mangling/context-int.h>



/* Liste des opérateurs reconnus */

#define IDT_NL(s) s, sizeof(s) - 1

const itanium_operator_info itanium_demangle_operators[] = {

    { "aN", IDT_NL("&="),               2 },
    { "aS", IDT_NL("="),                2 },
    { "aa", IDT_NL("&&"),               2 },
    { "ad", IDT_NL("&"),                1 },
    { "an", IDT_NL("&"),                2 },
    { "at", IDT_NL("alignof "),         1 },
    { "az", IDT_NL("alignof "),         1 },
    { "cc", IDT_NL("const_cast"),       2 },
    { "cl", IDT_NL("()"),               2 },
    { "cm", IDT_NL(","),                2 },
    { "co", IDT_NL("~"),                1 },
    { "dV", IDT_NL("/="),               2 },
    { "da", IDT_NL("delete[] "),        1 },
    { "dc", IDT_NL("dynamic_cast"),     2 },
    { "de", IDT_NL("*"),                1 },
    { "dl", IDT_NL("delete "),          1 },
    { "ds", IDT_NL(".*"),               2 },
    { "dt", IDT_NL("."),                2 },
    { "dv", IDT_NL("/"),                2 },
    { "eO", IDT_NL("^="),               2 },
    { "eo", IDT_NL("^"),                2 },
    { "eq", IDT_NL("=="),               2 },
    { "ge", IDT_NL(">="),               2 },
    { "gs", IDT_NL("::"),               1 },
    { "gt", IDT_NL(">"),                2 },
    { "ix", IDT_NL("[]"),               2 },
    { "lS", IDT_NL("<<="),              2 },
    { "le", IDT_NL("<="),               2 },
    { "li", IDT_NL("operator\"\" "),    1 },
    { "ls", IDT_NL("<<"),               2 },
    { "lt", IDT_NL("<"),                2 },
    { "mI", IDT_NL("-="),               2 },
    { "mL", IDT_NL("*="),               2 },
    { "mi", IDT_NL("-"),                2 },
    { "ml", IDT_NL("*"),                2 },
    { "mm", IDT_NL("--"),               1 },
    { "na", IDT_NL("new[]"),            3 },
    { "ne", IDT_NL("!="),               2 },
    { "ng", IDT_NL("-"),                1 },
    { "nt", IDT_NL("!"),                1 },
    { "nw", IDT_NL("new"),              3 },
    { "oR", IDT_NL("|="),               2 },
    { "oo", IDT_NL("||"),               2 },
    { "or", IDT_NL("|"),                2 },
    { "pL", IDT_NL("+="),               2 },
    { "pl", IDT_NL("+"),                2 },
    { "pm", IDT_NL("->*"),              2 },
    { "pp", IDT_NL("++"),               1 },
    { "ps", IDT_NL("+"),                1 },
    { "pt", IDT_NL("->"),               2 },
    { "qu", IDT_NL("?"),                3 },
    { "rM", IDT_NL("%="),               2 },
    { "rS", IDT_NL(">>="),              2 },
    { "rc", IDT_NL("reinterpret_cast"), 2 },
    { "rm", IDT_NL("%"),                2 },
    { "rs", IDT_NL(">>"),               2 },
    { "sc", IDT_NL("static_cast"),      2 },
    { "st", IDT_NL("sizeof "),          1 },
    { "sz", IDT_NL("sizeof "),          1 }
};

/* Substitutions standards */

typedef struct _itanium_std_subst_info
{
    char code;                              /* Identifiant associé         */
    const char *class;                      /* Classe visée dans l'espace  */

} itanium_std_subst_info;

const itanium_std_subst_info itanium_standard_substitutions[] = {

    { 't', NULL },
    { 'a', "allocator" },
    { 'b', "basic_string" },
    { 's', "string" },
    { 'i', "istream" },
    { 'o', "ostream" },
    { 'd', "iostream" }

};


/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_encoding(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_name(GItaniumDemangling *);

/* Détermine si le composant suivant correspond à un type donné. */
static bool is_itd_unscoped_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_unscoped_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_unscoped_template_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_nested_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_prefix(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_template_prefix(GItaniumDemangling *);

/* Détermine si le composant suivant correspond à un type donné. */
static bool is_itd_unqualified_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_unqualified_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_source_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static bool itd_number(GItaniumDemangling *, ssize_t *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_identifier(GItaniumDemangling *, size_t);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_operator_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_special_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_call_offset(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_nv_offset(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_v_offset(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_ctor_dtor_name(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_type(GItaniumDemangling *);

/* Extrait une propriété de composant pour un contexte Itanium. */
static TypeQualifier itd_cv_qualifiers(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_builtin_type(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_function_type(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_bare_function_type(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_class_enum_type(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_array_type(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_pointer_to_member_type(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_template_param(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_template_template_param(GItaniumDemangling *);

/* Détermine si le composant suivant correspond à un type donné. */
static bool is_itd_template_args(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_template_args(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_template_arg(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_expression(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_value_to_string(GItaniumDemangling *, bool);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_expr_primary(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_data_member_prefix(GItaniumDemangling *);

/* Extrait un composant dans un contexte Itanium. */
static bool itd_seq_id(GItaniumDemangling *, char, size_t *);

/* Extrait un composant dans un contexte Itanium. */
static itanium_component *itd_substitution(GItaniumDemangling *);



#define itd_local_name(ctx) NULL



/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_mangled_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */

    /**
     * La règle traitée ici est la suivante :
     *
     * <mangled-name> ::= _Z <encoding>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, '_'))
        return NULL;

    if (!check_input_buffer_char(ibuf, 'Z'))
        return NULL;

    result = itd_encoding(context);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_encoding(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    itanium_component *types;               /* Composant 'bare-function...'*/

    /**
     * La règle traitée ici est la suivante :
     *
     * <encoding> ::= <function name> <bare-function-type>
     *            ::= <data name>
     *            ::= <special-name>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'T' || peek == 'G')
        result = itd_special_name(context);

    else
    {
        result = itd_name(context);

        if (result != NULL)
        {
            types = itd_bare_function_type(context);

            if (types != NULL)
                result = itd_make_binary(ICT_FUNCTION_ENCODING, result, types);

            /**
             * Si le chargement des types échoue, il peut y avoir deux explications :
             *    - on ne chargeait qu'un simple nom.
             *    - il y a eu une erreur de décodage pour les types.
             *
             * Le tampon aura été vidé dans le premier cas uniquement,
             * donc on laisse le contexte détecter une éventuelle erreur.
             */

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *tname;               /* Composant '...template-name'*/
    itanium_component *targs;               /* Composant 'template-args'   */

    /**
     * La règle traitée ici est la suivante :
     *
     * <name> ::= <nested-name>
     *        ::= <unscoped-name>
     *        ::= <unscoped-template-name> <template-args>
     *        ::= <local-name>
     *
     */

    g_itanium_demangling_push_state(context, &saved);

    result = itd_nested_name(context);

    if (result == NULL)
    {
        g_itanium_demangling_pop_state(context, &saved);

        tname = itd_unscoped_template_name(context);

        if (tname != NULL)
        {
            targs = itd_template_args(context);

            if (targs != NULL)
                result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, tname, targs);

            else
                itd_unref_comp(tname);

        }

    }

    /**
     * La règle <unscoped-name> doit être traitée après <unscoped-template-name>,
     * car ces deux dernières ont une base commune et la seconde peut avoir besoin
     * d'aller plus loin avec la règle <template-args>.
     *
     * On termine donc par moins gourmand si la règle la plus complexe n'a pas abouti.
     */

    if (result == NULL)
    {
        g_itanium_demangling_pop_state(context, &saved);
        result = itd_unscoped_name(context);
    }

    if (result == NULL)
    {
        g_itanium_demangling_pop_state(context, &saved);
        result = itd_local_name(context);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Détermine si le composant suivant correspond à un type donné.*
*                                                                             *
*  Retour      : true si le décodage va à priori réussir, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_itd_unscoped_name(GItaniumDemangling *context)
{
    bool result;                            /* Bilan à retourner           */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    char next_peek;                         /* Caractère après le prochain */

    /**
     * La règle anticipée ici est la suivante :
     *
     * <unscoped-name> ::= <unqualified-name>
     *                 ::= St <unqualified-name>   # ::std::
     *
     */

    result = is_itd_unqualified_name(context);

    if (!result)
    {
        ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

        peek = peek_input_buffer_char(ibuf);

        if (peek == 'S')
        {
            next_peek = peek_input_buffer_next_char(ibuf);

            result = (next_peek == 't');

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_unscoped_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    char next_peek;                         /* Caractère après le prochain */

    /**
     * La règle traitée ici est la suivante :
     *
     * <unscoped-name> ::= <unqualified-name>
     *                 ::= St <unqualified-name>   # ::std::
     *
     */


    if (is_itd_unqualified_name(context))
        result = itd_unqualified_name(context);

    else
    {
        ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

        peek = peek_input_buffer_char(ibuf);

        if (peek == 'S')
        {
            next_peek = peek_input_buffer_next_char(ibuf);

            if (next_peek == 't')
            {
                advance_input_buffer(ibuf, 2);

                result = itd_unqualified_name(context);

                if (result != NULL)
                    result = itd_make_unary(ICT_STD_UNSCOPED_NAME, result);

            }

            else
                result = NULL;

        }

        else
            result = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_unscoped_template_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */

    /**
     * La règle traitée ici est la suivante :
     *
     * <unscoped-template-name> ::= <unscoped-name>
     *                          ::= <substitution>
     *
     */

    if (is_itd_unscoped_name(context))
    {
        result = itd_unscoped_name(context);

        if (result != NULL)
            g_itanium_demangling_add_substitution(context, result);

    }

    else
    {
        ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

        peek = peek_input_buffer_char(ibuf);

        if (peek == 'S')
            result = itd_substitution(context);

        else
            result = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_nested_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    TypeQualifier qualifier;                /* Propriétés supplémentaires  */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *left;                /* Première partie             */
    itanium_component *right;               /* Seconde partie              */

    /**
     * La règle traitée ici est la suivante :
     *
     * <nested-name> ::= N [<CV-qualifiers>] <prefix> <unqualified-name> E
     *               ::= N [<CV-qualifiers>] <template-prefix> <template-args> E
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'N'))
        return NULL;

    qualifier = itd_cv_qualifiers(context);

    result = NULL;

    g_itanium_demangling_push_state(context, &saved);

    /**
     * Comme <prefix> <unqualified-name> peut aussi être <template-prefix>,
     * on commence par traiter la seconde règle.
     */

    left = itd_template_prefix(context);

    if (left != NULL)
    {
        /**
         * Quand son traitement est un succès, <template-prefix> doit toujours
         * se terminer par <template-args>.
         */

        assert(is_itd_template_args(context));

        right = itd_template_args(context);

        if (right != NULL)
        {
            if (check_input_buffer_char(ibuf, 'E'))
                result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, left, right);

            else
            {
                itd_unref_comp(left);
                itd_unref_comp(right);
            }

        }

        else
            itd_unref_comp(left);

    }

    if (result == NULL)
    {
        g_itanium_demangling_pop_state(context, &saved);

        left = itd_prefix(context);

        /**
         * Quand son traitement est un succès, <prefix> doit toujours
         * se terminer par <unqualified-name>.
         */

        assert(left == NULL || (left != NULL && is_itd_unqualified_name(context)));

        /**
         * La règle <prefix> peut être vide, donc on se doit de tenter un
         * <unqualified-name> dans tous les cas.
         */

        right = itd_unqualified_name(context);

        if (right != NULL)
        {
            if (check_input_buffer_char(ibuf, 'E'))
                result = itd_make_binary(ICT_NESTED_NAME, left, right);

            else
            {
                if (left != NULL)
                    itd_unref_comp(left);
                itd_unref_comp(right);
            }

        }

        else if (left != NULL)
            itd_unref_comp(left);

    }

    if (result != NULL)
        itd_make_qualified_type(result, qualifier);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_prefix(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    itanium_component *targs;               /* Composant 'template-args'   */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *further;             /* Tentative de progression    */
    itanium_component *backup;              /* Solution de repli existante */

    /**
     * La règle traitée ici est la suivante :
     *
     * <prefix> ::= <unqualified-name>
     *          ::= <prefix> <unqualified-name>
     *          ::= <template-prefix> <template-args>
     *          ::= <template-param>
     *          ::= <decltype>
     *          ::= <prefix> <data-member-prefix>
     *          ::= <substitution>
     *
     * Réorganisée, cette règle <prefix> a pour définition :
     *
     * <prefix> ::= <unqualified-name>
     *          ::= <template-param>
     *          ::= <decltype>
     *          ::= <substitution>
     *          ::= <template-prefix> <template-args>
     *
     *          ::= <prefix> <unqualified-name>
     *          ::= <prefix> <data-member-prefix>
     *
     * Il existe cependant une boucle infinie avec une règle de <prefix> :
     *
     * <template-prefix> ::= <prefix> <template unqualified-name>
     *
     * On déplie donc les règles afin de casser la boucle, quitte à gérer ici
     * une partie de la règle <template-prefix> :
     *
     * <prefix> ::= <unqualified-name>
     *          ::= <template-param>
     *          ::= <decltype>
     *          ::= <substitution>
     *
     *          ::= <unqualified-name> <template-args>
     *          ::= <template-param> <template-args>
     *          ::= <substitution> <template-args>
     *
     *          ::= <prefix> <unqualified-name>
     *          ::= <prefix> <unqualified-name> <template-args>
     *          ::= <prefix> <data-member-prefix>
     */

    result = NULL;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'S')
        result = itd_substitution(context);

    else if (peek == 'T')
        result = itd_template_param(context);

    else if (is_itd_unqualified_name(context))
        result = itd_unqualified_name(context);

    /**
     * Si le traitement débouche sur une règle <template-args>, c'est qu'il
     * était en fait potentiellement dans une voie <template-prefix>.
     *
     * Cette voie est vérifiée après coup en analysant la suite.
     */

    if (is_itd_template_args(context))
    {
        g_itanium_demangling_push_state(context, &saved);

        /* Ajout de la substitution tirée de <template-prefix> */
        g_itanium_demangling_add_substitution(context, result);

        targs = itd_template_args(context);

        if (targs != NULL)
        {
            if (!is_itd_unqualified_name(context))
            {
                g_itanium_demangling_pop_state(context, &saved);
                itd_unref_comp(targs);
            }

            else
                result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, result, targs);

        }

        else
        {
            itd_unref_comp(result);
            result = NULL;
            goto done;
        }

    }

    if (result == NULL)
        goto done;

    g_itanium_demangling_add_substitution(context, result);

    /* Tentative de rebouclage sur la règle <prefix> */

    while (count_input_buffer_remaining(ibuf) > 0)
    {
        g_itanium_demangling_push_state(context, &saved);

        /**
         * Comme <data-member-prefix> commence par une régle <source-name> et
         * complète ensuite sa définition et comme <unqualified-name> contient
         * également cette même règle <source-name> sans l'étendre, on commence
         * par traiter la règle <data-member-prefix>.
         */

        further = itd_data_member_prefix(context);

        if (further == NULL)
        {
            g_itanium_demangling_pop_state(context, &saved);
            further = itd_unqualified_name(context);
        }

        if (further == NULL)
            break;

        backup = result;
        itd_ref_comp(backup);

        result = itd_make_binary(ICT_PREFIX_BINARY, result, further);

        /* Ajout de la substitution tirée de <[template-]prefix> */
        g_itanium_demangling_add_substitution(context, result);

        if (is_itd_template_args(context))
        {
            targs = itd_template_args(context);

            if (targs == NULL)
            {
                itd_unref_comp(backup);
                itd_unref_comp(result);
                result = NULL;
                goto done;
            }

            result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, result, targs);

            g_itanium_demangling_add_substitution(context, result);

        }

        /* Si l'ensemble ne se termine pas par la règle finale attendue, on rétropédale */
        if (!is_itd_unqualified_name(context))
        {
            itd_unref_comp(result);

            result = backup;

            g_itanium_demangling_pop_state(context, &saved);

            break;

        }

        itd_unref_comp(backup);

    }

 done:

    /**
     * Quand son traitement est un succès, <prefix> doit toujours
     * se terminer par <unqualified-name>.
     */

    if (result != NULL)
    {
        if (!is_itd_unqualified_name(context))
        {
            itd_unref_comp(result);
            result = NULL;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_template_prefix(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    bool new_subst;                         /* Ajoute d'une substitution ? */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *name;                /* Second d'un couple de comp. */

    /**
     * La règle traitée ici est la suivante :
     *
     * <template-prefix> ::= <template unqualified-name>
     *                   ::= <prefix> <template unqualified-name>
     *                   ::= <template-param>
     *                   ::= <substitution>
     *
     * Il existe cependant une boucle infinie avec une règle de <prefix> :
     *
     * <prefix> ::= <template-prefix> <template-args>
     *
     * On traite donc cette règle de <prefix> en dernier, quand les autres
     * options ont été épuisées.
     */

    result = NULL;

    new_subst = true;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    g_itanium_demangling_push_state(context, &saved);

    if (peek == 'S')
    {
        result = itd_substitution(context);
        new_subst = false;
    }

    else if (peek == 'T')
        result = itd_template_param(context);

    else if (is_itd_unqualified_name(context))
        result = itd_unqualified_name(context);

    /* Vérification : a-t-on empiété sur une règle <prefix> ? */

    if (result != NULL)
    {
        if (is_itd_template_args(context))
            goto done;

        else
        {
            new_subst = true;

            itd_unref_comp(result);
            result = NULL;

            g_itanium_demangling_pop_state(context, &saved);

        }

    }

    /* Tentative avec <prefix> <template unqualified-name> en dernier recours */

    result = itd_prefix(context);

    if (result != NULL)
    {
        /**
         * Quand son traitement est un succès, <prefix> doit toujours
         * se terminer par <unqualified-name>.
         *
         * De même, toutes les règles <template-prefix> se poursuivent avec une
         * règle <template-args> ; la procédure n'est donc un succès que dans ce cas.
         */

        assert(is_itd_unqualified_name(context));

        name = itd_unqualified_name(context);

        if (name != NULL)
            result = itd_make_binary(ICT_TPREFIX_BINARY, result, name);

        else
        {
            itd_unref_comp(result);
            result = NULL;
        }

    }

 done:

    if (result != NULL)
    {
        if (!is_itd_template_args(context))
        {
            itd_unref_comp(result);
            result = NULL;
        }

        else if (new_subst)
            g_itanium_demangling_add_substitution(context, result);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Détermine si le composant suivant correspond à un type donné.*
*                                                                             *
*  Retour      : true si le décodage va à priori réussir, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_itd_unqualified_name(GItaniumDemangling *context)
{
    bool result;                            /* Bilan à retourner           */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */

    /**
     * La règle anticipée ici est la suivante :
     *
     * <unqualified-name> ::= <operator-name>
     *                    ::= <ctor-dtor-name>
     *                    ::= <source-name>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    result = islower(peek)                  /* <operator-name> */
           || (peek == 'C' || peek == 'D')  /* <ctor-dtor-name> */
           || isdigit(peek);                /* <source-name> */

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_unqualified_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */

    /**
     * La règle traitée ici est la suivante :
     *
     * <unqualified-name> ::= <operator-name>
     *                    ::= <ctor-dtor-name>
     *                    ::= <source-name>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (islower(peek))
        result = itd_operator_name(context);

    else if (peek == 'C' || peek == 'D')
        result = itd_ctor_dtor_name(context);

    else if (isdigit(peek))
        result = itd_source_name(context);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_source_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    ssize_t number;                         /* Taille positive             */

    /**
     * La règle traitée ici est la suivante :
     *
     * <source-name> ::= <positive length number> <identifier>
     *
     */

    if (!itd_number(context, &number))
        return NULL;

    if (number <= 0)
        return NULL;

    result = itd_identifier(context, number);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                size    = taille positive ou non lue. [OUT]                  *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Bilan de l'opération (un chifre lu au moins).                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool itd_number(GItaniumDemangling *context, ssize_t *size)
{
    bool result;                            /* Validité à renvoyer         */
    bool negative;                          /* Taille négative ?           */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */

    /**
     * La règle traitée ici est la suivante :
     *
     * <number> ::= [n] <non-negative decimal integer>
     *
     */

    result = false;

    negative = false;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'n')
    {
        negative = true;
        advance_input_buffer(ibuf, 1);
        peek = peek_input_buffer_char(ibuf);
    }

    *size = 0;

    while (isdigit(peek))
    {
        result = true;
        *size = *size * 10 + peek - '0';
        advance_input_buffer(ibuf, 1);
        peek = peek_input_buffer_char(ibuf);
    }

    if (negative)
        *size *= -1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                length  = taille de l'identifiant à retrouver.               *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_identifier(GItaniumDemangling *context, size_t length)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    const char *data;                       /* Données restantes           */
    size_t remaining;                       /* Quantité d'octets           */

    /**
     * La règle traitée ici est la suivante :
     *
     * <identifier> ::= <unqualified source code identifier>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    data = get_input_buffer_string(ibuf, &remaining);

    if (length > remaining)
        return NULL;

    result = itd_make_name(data, length);

    if (result != NULL)
        advance_input_buffer(ibuf, length);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_operator_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char code[2];                           /* Code à venir lire           */
    itanium_component *type;                /* Type transtypé              */
    itanium_operator_info info;             /* Clef des informations       */
    itanium_operator_info *found;           /* Informations complètes      */

    /**
     * La règle traitée ici est la suivante :
     *
     * <operator-name> ::= nw    # new
     *                 ::= na    # new[]
     *                 ::= dl    # delete
     *                 ::= da    # delete[]
     *                 ::= ps    # + (unary)
     *                 ::= ng    # - (unary)
     *                 ::= ad    # & (unary)
     *                 ::= de    # * (unary)
     *                 ::= co    # ~
     *                 ::= pl    # +
     *                 ::= mi    # -
     *                 ::= ml    # *
     *                 ::= dv    # /
     *                 ::= rm    # %
     *                 ::= an    # &
     *                 ::= or    # |
     *                 ::= eo    # ^
     *                 ::= aS    # =
     *                 ::= pL    # +=
     *                 ::= mI    # -=
     *                 ::= mL    # *=
     *                 ::= dV    # /=
     *                 ::= rM    # %=
     *                 ::= aN    # &=
     *                 ::= oR    # |=
     *                 ::= eO    # ^=
     *                 ::= ls    # <<
     *                 ::= rs    # >>
     *                 ::= lS    # <<=
     *                 ::= rS    # >>=
     *                 ::= eq    # ==
     *                 ::= ne    # !=
     *                 ::= lt    # <
     *                 ::= gt    # >
     *                 ::= le    # <=
     *                 ::= ge    # >=
     *                 ::= nt    # !
     *                 ::= aa    # &&
     *                 ::= oo    # ||
     *                 ::= pp    # ++
     *                 ::= mm    # --
     *                 ::= cm    # ,
     *                 ::= pm    # ->*
     *                 ::= pt    # ->
     *                 ::= cl    # ()
     *                 ::= ix    # []
     *                 ::= qu    # ?
     *                 ::= st    # sizeof (a type)
     *                 ::= sz    # sizeof (an expression)
     *                 ::= cv <type> # (cast)
     *                 ::= v <digit> <source-name>   # vendor extended operator
     *
     */

    result = NULL;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!get_input_buffer_next_char_carefully(ibuf, &code[0]))
        goto itd_operator_name_exit;

    if (code[0] == 'v')
    {
        type = itd_type(context);

        if (type != NULL)
            result = itd_make_cast_operator(type);
        else
            result = NULL;

        goto itd_operator_name_exit;

    }

    if (!get_input_buffer_next_char_carefully(ibuf, &code[1]))
        goto itd_operator_name_exit;

    if (code[0] == 'c' && code[1] == 'v')
    {
        result = NULL;
        goto itd_operator_name_exit;
    }

    /* Recherche dans la liste des opérateurs reconnus */

    info.code = code;

    int comp_itanium_operators(const itanium_operator_info *a, const itanium_operator_info *b)
    {
        int result;                         /* Bilan à renvoyer            */

        if (a->code[0] < b->code[0])
            result = -1;
        else if (a->code[0] > b->code[0])
            result = 1;
        else
        {
            if (a->code[1] < b->code[1])
                result = -1;
            else if (a->code[1] > b->code[1])
                result = 1;
            else
                result = 0;
        }

        return result;

    }

    found = bsearch(&info, itanium_demangle_operators,
                    ARRAY_SIZE(itanium_demangle_operators),
                    sizeof(itanium_operator_info), (__compar_fn_t)comp_itanium_operators);

    if (found != NULL)
        result = itd_make_operator(found);

 itd_operator_name_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_special_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char next;                              /* Caractère suivant           */
    char peek;                              /* Prochain caractère lu       */
    itanium_component *offset1;             /* Décalage extrait #1         */
    itanium_component *offset2;             /* Décalage extrait #2         */
    itanium_component *encoding;            /* Encodage suivant            */

    /**
     * La règle traitée ici est la suivante :
     *
     * <special-name> ::= TV <type>  # virtual table
     *                ::= TT <type>  # VTT structure (construction vtable index)
     *                ::= TI <type>  # typeinfo structure
     *                ::= TS <type>  # typeinfo name (null-terminated byte string)
     *                ::= Tc <call-offset> <call-offset> <base encoding>
     *                     # base is the nominal target function of thunk
     *                     # first call-offset is 'this' adjustment
     *                     # second call-offset is result adjustment
     *                ::= T <call-offset> <base encoding>
     *                     # base is the nominal target function of thunk
     */

    result = NULL;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!get_input_buffer_next_char_carefully(ibuf, &next))
        goto exit_eof;

    if (next == 'T')
    {
        peek = peek_input_buffer_char(ibuf);

        switch (peek)
        {
            case 'V':

                advance_input_buffer(ibuf, 1);

                result = itd_type(context);

                if (result != NULL)
                    result = itd_make_unary(ICT_SPECIAL_NAME_VTABLE, result);

                break;

            case 'T':

                advance_input_buffer(ibuf, 1);

                result = itd_type(context);

                if (result != NULL)
                    result = itd_make_unary(ICT_SPECIAL_NAME_VSTRUCT, result);

                break;

            case 'I':
                advance_input_buffer(ibuf, 1);
                result = itd_type(context);
                break;

            case 'S':
                advance_input_buffer(ibuf, 1);
                result = itd_type(context);
                break;

            case 'c':

                advance_input_buffer(ibuf, 1);

                offset1 = itd_call_offset(context);
                if (offset1 == NULL) break;

                offset2 = itd_call_offset(context);
                if (offset2 == NULL)
                {
                    itd_unref_comp(offset1);
                    break;
                }

                encoding = itd_encoding(context);

                if (encoding == NULL)
                {
                    itd_unref_comp(offset1);
                    itd_unref_comp(offset2);
                }

                else
                    result = itd_make_ternary(ICT_FUNCTION_COVARIANT_THUNK, encoding, offset1, offset2);

                break;

            case '\0':

                /**
                 * Si on se trouve à la fin du tampon, on n'avance pas aveuglément !
                 */

                result = NULL;
                break;

            default:

                advance_input_buffer(ibuf, 1);

                offset1 = itd_call_offset(context);
                if (offset1 == NULL) break;

                encoding = itd_encoding(context);

                if (encoding == NULL)
                    itd_unref_comp(offset1);
                else
                    result = itd_make_binary(ICT_FUNCTION_THUNK, encoding, offset1);

                break;

        }

    }

 exit_eof:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_call_offset(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char next;                              /* Caractère suivant           */

    /**
     * La règle traitée ici est la suivante :
     *
     * <call-offset> ::= h <nv-offset> _
     *               ::= v <v-offset> _
     */

    result = NULL;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (get_input_buffer_next_char_carefully(ibuf, &next))
        goto exit_eof;

    switch (next)
    {
        case 'h':
            result = itd_nv_offset(context);
            break;

        case 'v':
            result = itd_v_offset(context);
            break;

    }

    if (result != NULL && !check_input_buffer_char(ibuf, '_'))
    {
        itd_unref_comp(result);
        result = NULL;
    }

 exit_eof:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_nv_offset(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    ssize_t offset;                         /* Décalage obtenu             */

    /**
     * La règle traitée ici est la suivante :
     *
     * <nv-offset> ::= <offset number>
     *                     # non-virtual base override
     */

    if (!itd_number(context, &offset))
        return NULL;

    result = itd_make_offset(ICT_NON_VIRTUAL_OFFSET, offset);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_v_offset(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    ssize_t offset;                         /* Décalage obtenu #1          */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    ssize_t voffset;                        /* Décalage obtenu #2          */

    /**
     * La règle traitée ici est la suivante :
     *
     * <v-offset>  ::= <offset number> _ <virtual offset number>
     *                     # virtual base override, with vcall offset
     */

    if (!itd_number(context, &offset))
        return NULL;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, '_'))
        return NULL;

    if (!itd_number(context, &voffset))
        return NULL;

    result = itd_make_binary(ICT_DOUBLE_OFFSET,
                             itd_make_offset(ICT_NON_VIRTUAL_OFFSET, offset),
                             itd_make_offset(ICT_VIRTUAL_OFFSET, voffset));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_ctor_dtor_name(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char next;                              /* Caractère suivant           */
    ItaniumComponentType type;              /* Type de composant           */

    /**
     * La règle traitée ici est la suivante :
     *
     * <ctor-dtor-name> ::= C1   # complete object constructor
     *                  ::= C2   # base object constructor
     *                  ::= C3   # complete object allocating constructor
     *                  ::= D0   # deleting destructor
     *                  ::= D1   # complete object destructor
     *                  ::= D2   # base object destructor
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    next = peek_input_buffer_char(ibuf);

    if (next == 'C')
        type = ICT_CONSTRUCTOR;
    else if (next == 'D')
        type = ICT_DESTRUCTOR;
    else
        return NULL;

    advance_input_buffer(ibuf, 1);

    next = peek_input_buffer_char(ibuf);

    if (next != '0' && next != '1' && next != '2')
        return NULL;

    advance_input_buffer(ibuf, 1);

    result = itd_make_with_type(type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    TypeQualifier qualifier;                /* Propriétés supplémentaires  */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    bool handled;                           /* Prise en compte effectuée ? */
    itanium_component *sub;                 /* Sous-type lié à associer    */
    itanium_component *vendor;              /* Extension propriétaire      */
    GDataType *builtin;                     /* Type construit              */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *targs;               /* Composant 'template-args'   */
    ItaniumComponentType comp_type;         /* Type de composant final     */

    /**
     * La règle traitée ici est la suivante :
     *
     * <type> ::= <builtin-type>
     *        ::= <function-type>
     *        ::= <class-enum-type>
     *        ::= <array-type>
     *        ::= <pointer-to-member-type>
     *        ::= <template-param>
     *        ::= <template-template-param> <template-args>
     *        ::= <substitution> # See Compression below
     *        ::= <CV-qualifiers> <type>
     *        ::= P <type>   # pointer-to
     *        ::= R <type>   # reference-to
     *        ::= O <type>   # rvalue reference-to (C++0x)
     *        ::= C <type>   # complex pair (C 2000)
     *        ::= G <type>   # imaginary (C 2000)
     *        ::= U <source-name> <type> # vendor extended type qualifier
     *        ::= Dp <type>  # pack expansion (C++0x)
     *
     */

    result = NULL;

    qualifier = itd_cv_qualifiers(context);

    if (qualifier != TQF_NONE)
    {
        result = itd_type(context);

        if (result != NULL)
            result = itd_make_qualified_type(result, qualifier);

        goto itd_type_end;

    }

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    handled = false;

    switch (peek_input_buffer_char(ibuf))
    {
        case 'F':
            result = itd_function_type(context);
            handled = true;
            break;

        case 'A':
            result = itd_array_type(context);
            handled = true;
            break;

        case 'M':
            result = itd_pointer_to_member_type(context);
            handled = true;
            break;

        case 'P':

            advance_input_buffer(ibuf, 1);

            sub = itd_type(context);
            if (sub == NULL) return NULL;

            result = itd_make_unary(ICT_POINTER_TO, sub);
            handled = true;
            break;

        case 'R':

            advance_input_buffer(ibuf, 1);

            sub = itd_type(context);
            if (sub == NULL) return NULL;

            result = itd_make_unary(ICT_REFERENCE_TO, sub);
            handled = true;
            break;

        case 'O':

            advance_input_buffer(ibuf, 1);

            sub = itd_type(context);
            if (sub == NULL) return NULL;

            result = itd_make_unary(ICT_RVALUE_REFERENCE_TO, sub);
            handled = true;
            break;

        case 'C':

            advance_input_buffer(ibuf, 1);

            sub = itd_type(context);
            if (sub == NULL) return NULL;

            result = itd_make_unary(ICT_COMPLEX_PAIR, sub);
            handled = true;
            break;

        case 'G':

            advance_input_buffer(ibuf, 1);

            sub = itd_type(context);
            if (sub == NULL) return NULL;

            result = itd_make_unary(ICT_IMAGINARY, sub);
            handled = true;
            break;

        case 'U':

            advance_input_buffer(ibuf, 1);

            result = NULL;

            vendor = itd_source_name(context);

            if (vendor == NULL)
                result = NULL;

            else
            {
                builtin = g_class_enum_type_new(CEK_UNKNOWN, itd_translate_component(vendor, NULL));
                result = itd_make_type(builtin);
                itd_set_type(result, ICT_VENDOR_TYPE);
                itd_unref_comp(vendor);

                sub = itd_type(context);

                if (sub != NULL)
                    itd_unref_comp(sub);

                else
                {
                    itd_unref_comp(result);
                    result = NULL;
                }

            }

            handled = true;
            break;

        case 'D':
            if (peek_input_buffer_next_char(ibuf) == 'p')
            {
                advance_input_buffer(ibuf, 2);

                result = itd_type(context);
                handled = true;

            }
            break;

        case 'T':

            /**
             * Comme on a la définition suivante :
             *
             * <template-template-param> ::= <template-param>
             *                           ::= <substitution>
             *
             * On ne sait pas laquelle de ces deux directions prendre :
             *
             * <type> ::= <template-param>
             *        ::= <template-template-param> <template-args>
             *
             * Comme <template-args> commence toujour par un I, on teste
             * le caractère courant après <template-param> et on revient
             * un poil en arrière au besoin.
             *
             * Le cas <substitution> est traité de façon similaire après.
             */

            g_itanium_demangling_push_state(context, &saved);

            result = itd_template_param(context);

            if (result != NULL)
            {
                if (peek_input_buffer_char(ibuf) == 'I')
                {
                    itd_unref_comp(result);

                    g_itanium_demangling_pop_state(context, &saved);

                    result = itd_template_template_param(context);

                    if (result != NULL)
                    {
                        targs = itd_template_args(context);

                        if (targs != NULL)
                            result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, result, targs);

                        else
                        {
                            itd_unref_comp(result);
                            result = NULL;
                        }

                    }

                }

            }

            handled = true;
            break;

    }

    if (handled) goto itd_type_end;

    g_itanium_demangling_push_state(context, &saved);

    result = itd_builtin_type(context);
    if (result != NULL) goto itd_type_end;

    g_itanium_demangling_pop_state(context, &saved);

    result = itd_class_enum_type(context);
    if (result != NULL) goto itd_type_end;

    g_itanium_demangling_pop_state(context, &saved);

    /**
     * De façon similaire au cas <template-param> traité au dessus,
     * on guette un usage de <substitution> via :
     *
     * <template-template-param> ::= <template-param>
     *                           ::= <substitution>
     *
     * La distinction se réalise via une liste d'argument, et on tranche
     * cette fois entre les deux directions suivantes :
     *
     * <type> ::= <template-template-param> <template-args>
     *        ::= <substitution> # See Compression below
     */

    g_itanium_demangling_push_state(context, &saved);

    result = itd_substitution(context);

    if (result != NULL && peek_input_buffer_char(ibuf) == 'I')
    {
        itd_unref_comp(result);

        g_itanium_demangling_pop_state(context, &saved);

        result = itd_template_template_param(context);

        if (result != NULL)
        {
            targs = itd_template_args(context);

            if (targs != NULL)
                result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, result, targs);

            else
            {
                itd_unref_comp(result);
                result = NULL;
            }

        }

    }

 itd_type_end:

    if (result != NULL)
    {
        /**
         * Les spécifications (§ 5.1.9) précisent:
         *
         *    There are two exceptions that appear to be substitution candidates
         *    from the grammar, but are explicitly excluded:
         *
         *       <builtin-type> other than vendor extended types, and
         *       function and operator names other than extern "C" functions.
         *
         * On saute donc éventuelleement certains résultats.
         *
         * Par ailleurs, il existe quelques restrictions à propos des qualificatifs :
         *
         *    For purposes of substitution, given a CV-qualified type, the base
         *    type is substitutible, and the type with all the C, V, and r qualifiers
         *    plus any vendor extended types in the same order-insensitive set is
         *    substitutible; any type with a subset of those qualifiers is not.
         *
         * Le code courant englobe tous les qualificatifs, donc il n'y a pas de
         * mesure particulière à prendre ici.
         */

        comp_type = itd_get_component_type(result);

        if (comp_type != ICT_TYPE
            && (comp_type != ICT_FUNCTION_TYPE || itd_is_external_function(result)))
        {
            g_itanium_demangling_add_substitution(context, result);
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait une propriété de composant pour un contexte Itanium. *
*                                                                             *
*  Retour      : Indication extraite.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static TypeQualifier itd_cv_qualifiers(GItaniumDemangling *context)
{
    TypeQualifier result;                   /* Valeur à remonter           */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */

    /**
     * La règle traitée ici est la suivante :
     *
     * <CV-qualifiers> ::= [r] [V] [K]  # restrict (C99), volatile, const
     *
     */

    result = TQF_NONE;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    while (1)
        switch (peek_input_buffer_char(ibuf))
        {
            case 'r':
                result = TQF_RESTRICT;
                advance_input_buffer(ibuf, 1);
                break;

            case 'V':
                result = TQF_VOLATILE;
                advance_input_buffer(ibuf, 1);
                break;

            case 'K':
                result = TQF_CONST;
                advance_input_buffer(ibuf, 1);
                break;

            default:
                goto itd_cv_qualifiers_exit;
                break;

        }

 itd_cv_qualifiers_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_builtin_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    size_t consumed;                        /* Nombre de consommations     */
    BaseType type;                          /* Type reconnu ou BTP_INVALID */
    GDataType *std;                         /* Espace de noms              */
    itanium_component *vendor;              /* Extension propriétaire      */
    GDataType *builtin;                     /* Type construit              */
    bool status;                            /* Bilan de rattachement       */

    /**
     * La règle traitée ici est la suivante :
     *
     * <builtin-type> ::= v  # void
     *                ::= w  # wchar_t
     *                ::= b  # bool
     *                ::= c  # char
     *                ::= a  # signed char
     *                ::= h  # unsigned char
     *                ::= s  # short
     *                ::= t  # unsigned short
     *                ::= i  # int
     *                ::= j  # unsigned int
     *                ::= l  # long
     *                ::= m  # unsigned long
     *                ::= x  # long long, __int64
     *                ::= y  # unsigned long long, __int64
     *                ::= n  # __int128
     *                ::= o  # unsigned __int128
     *                ::= f  # float
     *                ::= d  # double
     *                ::= e  # long double, __float80
     *                ::= g  # __float128
     *                ::= z  # ellipsis
     *                ::= Dd # IEEE 754r decimal floating point (64 bits)
     *                ::= De # IEEE 754r decimal floating point (128 bits)
     *                ::= Df # IEEE 754r decimal floating point (32 bits)
     *                ::= Dh # IEEE 754r half-precision floating point (16 bits)
     *                ::= DF <number> _ # ISO/IEC TS 18661 binary floating point type _FloatN (N bits)
     *                ::= Di # char32_t
     *                ::= Ds # char16_t
     *                ::= Da # auto
     *                ::= Dc # decltype(auto)
     *                ::= Dn # std::nullptr_t (i.e., decltype(nullptr))
     *                ::= u <source-name> # vendor extended type
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    consumed = 1;

    switch (peek_input_buffer_char(ibuf))
    {
        case 'v':
            type = BTP_VOID;
            break;
        case 'w':
            type = BTP_WCHAR_T;
            break;
        case 'b':
            type = BTP_BOOL;
            break;
        case 'c':
            type = BTP_CHAR;
            break;
        case 'a':
            type = BTP_SCHAR;
            break;
        case 'h':
            type = BTP_UCHAR;
            break;
        case 's':
            type = BTP_SHORT;
            break;
        case 't':
            type = BTP_USHORT;
            break;
        case 'i':
            type = BTP_INT;
            break;
        case 'j':
            type = BTP_UINT;
            break;
        case 'l':
            type = BTP_LONG;
            break;
        case 'm':
            type = BTP_ULONG;
            break;
        case 'x':
            type = BTP_LONG_LONG;
            break;
        case 'y':
            type = BTP_ULONG_LONG;
            break;
        case 'n':
            type = BTP_INT128;
            break;
        case 'o':
            type = BTP_UINT128;
            break;
        case 'f':
            type = BTP_FLOAT;
            break;
        case 'd':
            type = BTP_DOUBLE;
            break;
        case 'e':
            type = BTP_LONG_DOUBLE;
            break;
        case 'g':
            type = BTP_FLOAT128;
            break;
        case 'z':
            type = BTP_ELLIPSIS;
            break;

        case 'D':

            consumed = 2;

            switch (peek_input_buffer_next_char(ibuf))
            {
                case 'd':
                    type = BTP_754R_64;
                    break;
                case 'e':
                    type = BTP_754R_128;
                    break;
                case 'f':
                    type = BTP_754R_32;
                    break;
                case 'h':
                    type = BTP_754R_16;
                    break;

                case 'F':
                    advance_input_buffer(ibuf, 2);

                    if (itd_number(context, (ssize_t []) { 0 }) && check_input_buffer_char(ibuf, '_'))
                        type = BTP_754R_N;
                    else
                        type = BTP_INVALID;

                    consumed = 0;
                    break;

                case 'i':
                    type = BTP_CHAR32_T;
                    break;
                case 's':
                    type = BTP_CHAR16_T;
                    break;
                case 'a':
                    type = BTP_AUTO;
                    break;
                case 'c':
                    type = BTP_DECL_AUTO;
                    break;

                case 'n':

                    std = g_class_enum_type_new(CEK_NAMESPACE, strdup("std"));

                    builtin = g_class_enum_type_new(CEK_CLASS, strdup("nullptr_t"));
                    status = g_data_type_set_namespace(builtin, std, "::");

                    g_object_unref(G_OBJECT(std));

                    if (!status)
                    {
                        g_object_unref(G_OBJECT(builtin));
                        result = NULL;
                        goto done;
                    }

                    result = itd_make_type(builtin);
                    itd_set_type(result, ICT_STD_SUBST);

                    goto done;
                    break;

                default:
                    type = BTP_INVALID;
                    break;

            }

            break;

        case 'u':

            advance_input_buffer(ibuf, 1);

            vendor = itd_source_name(context);

            if (vendor == NULL)
                result = NULL;
            else
            {
                builtin = g_class_enum_type_new(CEK_UNKNOWN, itd_translate_component(vendor, NULL));
                result = itd_make_type(builtin);
                itd_unref_comp(vendor);
            }

            goto done;
            break;

        default:
            type = BTP_INVALID;
            break;

    }

    if (type != BTP_INVALID)
    {
        builtin = g_basic_type_new(type);
        result = itd_make_type(builtin);
        advance_input_buffer(ibuf, consumed);
    }
    else
        result = NULL;

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_function_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère dispo.   */
    itanium_component *args;                /* Liste des arguments         */

    /**
     * La règle traitée ici est la suivante :
     *
     * <function-type> ::= F [Y] <bare-function-type> E
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'F'))
        return NULL;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'Y')
        advance_input_buffer(ibuf, 1);

    args = itd_bare_function_type(context);

    if (args == NULL)
        result = NULL;

    else
    {
        result = itd_make_function_type(peek == 'Y', args);

        if (!check_input_buffer_char(ibuf, 'E'))
        {
            itd_unref_comp(result);
            result = NULL;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_bare_function_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    itanium_component *type;                /* Nouvel élément à intégrer   */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    itd_state saved;                        /* Position d'analyse courante */

    /**
     * La règle traitée ici est la suivante :
     *
     * <bare-function-type> ::= <signature type>+
     *       # types are possible return type, then parameter types
     *
     */

    type = itd_type(context);
    if (type == NULL) return NULL;

    result = itd_append_right_to_binary(ICT_TYPES_LIST, NULL, type);

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    while (count_input_buffer_remaining(ibuf) > 0)
    {
        g_itanium_demangling_push_state(context, &saved);

        type = itd_type(context);

        if (type == NULL)
        {
            g_itanium_demangling_pop_state(context, &saved);
            break;
        }

        result = itd_append_right_to_binary(ICT_TYPES_LIST, result, type);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_class_enum_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */

    /**
     * La règle traitée ici est la suivante :
     *
     * <class-enum-type> ::= <name>
     *
     */

    result = itd_name(context);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_array_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    ssize_t dim_number;                     /* Dimension par un nombre     */
    itanium_component *type;                /* Type du tableau             */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *dim_expr;            /* Dimension via expression    */

    /**
     * La règle traitée ici est la suivante :
     *
     * <array-type> ::= A <positive dimension number> _ <element type>
     *              ::= A [<dimension expression>] _ <element type>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'A'))
        return NULL;

    if (itd_number(context, &dim_number))
    {
        if (!check_input_buffer_char(ibuf, '_'))
            return NULL;

        type = itd_type(context);

        if (type == NULL)
            return NULL;

        result = itd_make_array_with_dim_number(dim_number, type);

    }

    else
    {
        g_itanium_demangling_push_state(context, &saved);

        dim_expr = itd_expression(context);

        if (dim_expr == NULL)
            g_itanium_demangling_pop_state(context, &saved);

        if (!check_input_buffer_char(ibuf, '_'))
        {
            if (dim_expr != NULL)
                itd_unref_comp(dim_expr);
            return NULL;
        }

        type = itd_type(context);

        if (type == NULL)
        {
            if (dim_expr != NULL)
                itd_unref_comp(dim_expr);
            return NULL;
        }

        result = itd_make_array_with_dim_expr(dim_expr, type);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_pointer_to_member_type(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    itanium_component *class;               /* Classe d'appatenance        */
    itanium_component *member;              /* Membre représenté           */

    /**
     * La règle traitée ici est la suivante :
     *
     * <pointer-to-member-type> ::= M <class type> <member type>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'M'))
        return NULL;

    class = itd_type(context);

    if (class != NULL)
    {
        member = itd_type(context);

        if (member != NULL)
            result = itd_make_pointer_to_memeber_type(class, member);

        else
        {
            itd_unref_comp(class);
            result = NULL;
        }

    }

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_template_param(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char cur;                               /* Caractère analysé           */
    size_t id;                              /* Identifiant de substitution */

    /**
     * La règle traitée ici est la suivante :
     *
     * <template-param> ::= T_  # first template parameter
     *                  ::= T <parameter-2 non-negative number> _
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'T'))
        return NULL;

    result = NULL;

    if (get_input_buffer_next_char_carefully(ibuf, &cur))
    {
        if (cur == '_' || isdigit(cur) || isupper(cur))
        {
            if (!itd_seq_id(context, cur, &id))
                return NULL;

            result = g_itanium_demangling_get_template_arg(context, id);

            if (result != NULL)
                result = itd_make_unary(ICT_TEMPLATE_PARAM, result);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_template_template_param(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère dispo.   */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'T')
        result = itd_template_param(context);

    else
        result = itd_substitution(context);

    return result;

}
/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Détermine si le composant suivant correspond à un type donné.*
*                                                                             *
*  Retour      : true si le décodage va à priori réussir, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_itd_template_args(GItaniumDemangling *context)
{
    bool result;                            /* Bilan à retourner           */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */

    /**
     * La règle anticipée ici est la suivante :
     *
     * <template-args> ::= I <template-arg>+ E
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    result = (peek == 'I');

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_template_args(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    itanium_component *arg;                 /* Nouvel argument extrait     */
    itd_state saved;                        /* Position d'analyse courante */

    /**
     * La règle traitée ici est la suivante :
     *
     * <template-args> ::= I <template-arg>+ E
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'I'))
        return NULL;

    arg = itd_template_arg(context);
    if (arg == NULL) return NULL;

    result = itd_merge_list_right_to_binary(ICT_TYPES_LIST, NULL, arg);

    while (1)
    {
        g_itanium_demangling_push_state(context, &saved);

        arg = itd_template_arg(context);
        if (arg == NULL)
        {
            g_itanium_demangling_pop_state(context, &saved);
            break;
        }

        result = itd_merge_list_right_to_binary(ICT_TYPES_LIST, result, arg);

    }

    if (!check_input_buffer_char(ibuf, 'E'))
    {
        itd_unref_comp(result);
        return NULL;
    }

    result = itd_make_unary(ICT_TEMPLATE_ARGS, result);

    g_itanium_demangling_add_template_args(context, result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_template_arg(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    itanium_component *packed;              /* Argument compressé          */

    /**
     * La règle traitée ici est la suivante :
     *
     * <template-arg> ::= <type>                     # type or template
     *                ::= X <expression> E           # expression
     *                ::= <expr-primary>             # simple expressions
     *                ::= J <template-arg>* E        # argument pack
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'X')
    {
        advance_input_buffer(ibuf, 1);

        result = itd_expression(context);

        if (result != NULL && !check_input_buffer_char(ibuf, 'E'))
        {
            itd_unref_comp(result);
            result = NULL;
        }

    }

    else if (peek == 'L')
        result = itd_expr_primary(context);

    else if (peek == 'J')
    {
        advance_input_buffer(ibuf, 1);

        result = NULL;

        while (peek_input_buffer_char(ibuf) != 'E')
        {
            packed = itd_template_arg(context);

            if (packed == NULL)
            {
                if (result != NULL)
                {
                    itd_unref_comp(result);
                    result = NULL;
                }

                goto packed_failed;

            }

            result = itd_merge_list_right_to_binary(ICT_TYPES_LIST, result, packed);

        }

        if (result == NULL)
            result = itd_make_with_type(ICT_PACKED_EMPTY);

        if (!check_input_buffer_char(ibuf, 'E'))
        {
            itd_unref_comp(result);
            result = NULL;
        }

    }

    else
        result = itd_type(context);

 packed_failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_expression(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char peek;                              /* Prochain caractère lu       */
    char next_peek;                         /* Caractère après le prochain */
    itanium_component *targs;               /* Composant 'template-args'   */
    ItaniumOperatorType otype;              /* Type d'opérateur            */
    const void *odata;                      /* Données associées           */
    const itanium_operator_info *simple;    /* Données d'opérateur simple  */
    int i;                                  /* Boucle de parcours          */
    itanium_component *list;                /* Liste de sous-expressions   */
    itanium_component *sub;                 /* Sous-expression chargée     */

    /**
     * La règle traitée ici est la suivante :
     *
     * <expression> ::= <unary operator-name> <expression>
     *              ::= <binary operator-name> <expression> <expression>
     *              ::= <trinary operator-name> <expression> <expression> <expression>
     *              ::= st <type>
     *              ::= <template-param>
     *              ::= sr <type> <unqualified-name>                   # dependent name
     *              ::= sr <type> <unqualified-name> <template-args>   # dependent template-id
     *              ::= <expr-primary>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    peek = peek_input_buffer_char(ibuf);

    if (peek == 'T')
        result = itd_template_param(context);

    else if (peek == 'L')
        result = itd_expr_primary(context);

    else if (islower(peek))
    {
        next_peek = peek_input_buffer_next_char(ibuf);

        if (peek == 's' && next_peek == 't')
        {
            advance_input_buffer(ibuf, 2);

            result = itd_type(context);

        }

        else if (peek == 's' && next_peek == 'r')
        {
            advance_input_buffer(ibuf, 2);

            result = itd_type(context);

            if (result != NULL)
            {
                itd_unref_comp(result);

                result = itd_unqualified_name(context);

                if (result)
                {
                    peek = peek_input_buffer_char(ibuf);

                    if (peek == 'I')
                    {
                        targs = itd_template_args(context);

                        if (targs != NULL)
                            result = itd_make_binary(ICT_TEMPLATE_NAME_ARGS, result, targs);

                        else
                        {
                            itd_unref_comp(result);
                            result = NULL;
                        }

                    }

                }

            }

        }

        else
        {
            result = itd_operator_name(context);

            if (result != NULL)
            {
                odata = itd_get_operator_info(result, &otype);

                switch (otype)
                {
                    case IOT_SIMPLE:

                        simple = (const itanium_operator_info *)odata;

                        list = NULL;

                        for (i = 0; i < simple->args; i++)
                        {
                            sub = itd_expression(context);

                            if (sub == NULL)
                            {
                                if (list != NULL)
                                {
                                    itd_unref_comp(list);
                                    list = NULL;
                                }

                                break;

                            }

                            list = itd_append_right_to_binary(ICT_EXPR_LIST, list, sub);

                        }

                        if (list == NULL)
                        {
                            itd_unref_comp(result);
                            result = NULL;
                        }

                        else
                            result = itd_make_binary(ICT_OPERATED_EXPRESSION, result, list);

                        break;

                    case IOT_CAST:

                        sub = itd_expression(context);

                        if (sub == NULL)
                        {
                            itd_unref_comp(result);
                            result = NULL;
                        }

                        else
                        {
                            list = itd_append_right_to_binary(ICT_EXPR_LIST, NULL, sub);
                            result = itd_make_binary(ICT_OPERATED_EXPRESSION, result, list);
                        }

                        break;

                    default:
                        assert(false);
                        itd_unref_comp(result);
                        result = NULL;
                        break;

                }

            }

        }

    }

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                hex     = prise en compte des caractères hexadécimaux ?      *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_value_to_string(GItaniumDemangling *context, bool hex)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    const char *data;                       /* Données restantes           */
    itd_state saved;                        /* Position d'analyse initiale */
    itd_state cur;                          /* Position d'analyse courante */
    char peek;                              /* Prochain caractère lu       */

    /**
     * Les règles traitées ici sont les suivantes :
     *
     * <value number>  # integer literal
     * <value float>   # floating literal
     *
     */

    result = NULL;

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    data = get_input_buffer_text_access(ibuf);

    g_itanium_demangling_push_state(context, &saved);

    while (1)
    {
        peek = peek_input_buffer_char(ibuf);

        switch (peek)
        {
            case '0' ... '9':
                advance_input_buffer(ibuf, 1);
                break;

            case 'a' ... 'f':
                if (hex)
                    advance_input_buffer(ibuf, 1);
                else
                    goto exit_iits;
                break;

            case 'E':
                goto exit_loop;
                break;

            default:
                goto exit_iits;

        }

    }

 exit_loop:

    g_itanium_demangling_push_state(context, &cur);

    if ((cur.pos - saved.pos) > 0)
        result = itd_make_name(data, cur.pos - saved.pos);

 exit_iits:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_expr_primary(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    itd_state saved;                        /* Position d'analyse courante */
    itanium_component *type;                /* Type de valeur extrait      */
    itd_state saved_value;                  /* Position d'analyse courante */

    /**
     * La règle traitée ici est la suivante :
     *
     * <expr-primary> ::= L <type> <value number> E  # integer literal
     *                ::= L <type> <value float> E   # floating literal
     *                ::= L <mangled-name> E         # external name
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'L'))
        return NULL;

    g_itanium_demangling_push_state(context, &saved);

    type = itd_type(context);

    if (type != NULL)
    {
        g_itanium_demangling_push_state(context, &saved_value);

        /* Règle <type> <value number> */

        result = itd_value_to_string(context, false);

        if (result != NULL && !check_input_buffer_char(ibuf, 'E'))
        {
            itd_unref_comp(result);
            result = NULL;
        }

        /* Règle <type> <value float> */

        if (result == NULL)
        {
            g_itanium_demangling_pop_state(context, &saved_value);

            result = itd_value_to_string(context, true);

            if (result != NULL && !check_input_buffer_char(ibuf, 'E'))
            {
                itd_unref_comp(result);
                result = NULL;
            }

        }

        itd_unref_comp(type);

    }
    else
        result = NULL;

    /* Règle <mangled-name> */

    if (result == NULL)
    {
        g_itanium_demangling_pop_state(context, &saved);
        result = itd_mangled_name(context);

        if (result != NULL && !check_input_buffer_char(ibuf, 'E'))
        {
            itd_unref_comp(result);
            result = NULL;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_data_member_prefix(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */

    result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                cur     = caractère courant.                                 *
*                id      = identifiant lu en cas de succès. [OUT]             *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool itd_seq_id(GItaniumDemangling *context, char cur, size_t *id)
{
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */

    /**
     * La règle traitée ici est la suivante :
     *
     * <seq-id>
     *
     */

    *id = 0;

    /**
     * La fonction n'est appelée que si un début de séquence est détecté.
     * (ie, cur == '_' || isdigit(cur) || isupper(cur)).
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (cur != '_')
    {
        do
        {
            if (isdigit(cur))
                *id = *id * 36 + cur - '0';
            else if (isupper(cur))
                *id = *id * 36 + cur - 'A' + 10;
            else
                return false;

            if (!get_input_buffer_next_char_carefully(ibuf, &cur))
                return false;

        }
        while (cur != '_');

        (*id)++;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à utiliser.                   *
*                                                                             *
*  Description : Extrait un composant dans un contexte Itanium.               *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_substitution(GItaniumDemangling *context)
{
    itanium_component *result;              /* Construction à retourner    */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    char cur;                               /* Caractère analysé           */
    size_t id;                              /* Identifiant de substitution */
    size_t i;                               /* Boucle de parcours          */
    const itanium_std_subst_info *stdinfo;  /* Raccourci de confort        */
    GDataType *std;                         /* Espace de noms              */
    GDataType *type;                        /* Type complet final          */
    bool status;                            /* Bilan de rattachement       */

    /**
     * La règle traitée ici est la suivante :
     *
     * <substitution> ::= S <seq-id> _
     *                ::= S_
     *                ::= St # ::std::
     *                ::= Sa # ::std::allocator
     *                ::= Sb # ::std::basic_string
     *                ::= Ss # ::std::basic_string<char, ::std::char_traits<char>, ::std::allocator<char>>
     *                ::= Si # ::std::basic_istream<char, std::char_traits<char>>
     *                ::= So # ::std::basic_ostream<char, std::char_traits<char>>
     *                ::= Sd # ::std::basic_iostream<char, std::char_traits<char>>
     *
     */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    if (!check_input_buffer_char(ibuf, 'S'))
        return NULL;

    result = NULL;

    if (!get_input_buffer_next_char_carefully(ibuf, &cur))
        goto exit_eof;

    if (cur == '_' || isdigit(cur) || isupper(cur))
    {
        if (!itd_seq_id(context, cur, &id))
            return NULL;

        result = g_itanium_demangling_get_substitution(context, id);

    }
    else
    {
        for (i = 0; i < ARRAY_SIZE(itanium_standard_substitutions); i++)
        {
            stdinfo = &itanium_standard_substitutions[i];

            if (stdinfo->code == cur)
            {
                std = g_class_enum_type_new(CEK_NAMESPACE, strdup("std"));

                if (stdinfo->class == NULL)
                    type = std;

                else
                {
                    type = g_class_enum_type_new(CEK_CLASS, strdup(stdinfo->class));
                    status = g_data_type_set_namespace(type, std, "::");
                    g_object_unref(G_OBJECT(std));

                    if (!status)
                        break;

                }

                result = itd_make_type(type);
                itd_set_type(result, ICT_STD_SUBST);

                break;

            }

        }

    }

 exit_eof:

    return result;

}
