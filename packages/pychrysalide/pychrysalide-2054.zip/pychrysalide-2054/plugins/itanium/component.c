
/* Chrysalide - Outil d'analyse de fichiers binaires
 * component.c - représentation des composants extraits de l'ABI C++ Itanium
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "component.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <analysis/types/array.h>
#include <analysis/types/cse.h>
#include <analysis/types/expr.h>
#include <analysis/types/override.h>
#include <analysis/types/proto.h>
#include <analysis/types/template.h>
#include <common/extstr.h>
#include <common/fnv1a.h>


#include "component-int.h"



/* Procédure à appliquer sur un composant visité */
typedef void (* visit_comp_fc) (itanium_component *);


/* Crée un composant de contexte Itanium complètement vierge. */
static itanium_component *itd_alloc(void);

/* Efface de la mémoire un composant de context Itanium. */
static void itd_free(itanium_component *);

/* Visite les composants en présence. */
static void visit_comp(itanium_component *, visit_comp_fc);

/* Traduit les composants de contexte Itanium en décalage. */
static bool itd_translate_component_to_offset(const itanium_component *, call_offset_t *);

/* Ajoute un espace de noms à un type déjà préparé. */
static void itd_prepend_namespace_to_type(GDataType *, GDataType *);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un composant de contexte Itanium complètement vierge.   *
*                                                                             *
*  Retour      : Composant créé ou NULL en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static itanium_component *itd_alloc(void)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = calloc(1, sizeof(itanium_component));

    result->refcount = 1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant à supprimer.                                *
*                                                                             *
*  Description : Efface de la mémoire un composant de context Itanium.        *
*                                                                             *
*  Retour      : Composant créé ou NULL en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void itd_free(itanium_component *comp)
{
    free(comp);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp    = composant à traiter.                               *
*                visitor = fonction à appliquer sur les composants présents.  *
*                                                                             *
*  Description : Visite les composants en présence.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void visit_comp(itanium_component *comp, visit_comp_fc visitor)
{
    switch (comp->type)
    {
        case ICT_NAME:
            break;

        case ICT_STD_UNSCOPED_NAME:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_NESTED_NAME:
            if (comp->binary.left != NULL)
                visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_TEMPLATE_NAME_ARGS:
            visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_PREFIX_BINARY:
            visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_TPREFIX_BINARY:
            if (comp->binary.left != NULL)
                visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_OPERATOR_NAME:
            if (comp->operator.otype == IOT_CAST)
                visit_comp(comp->operator.trans, visitor);
            break;

        case ICT_SPECIAL_NAME_VTABLE:
        case ICT_SPECIAL_NAME_VSTRUCT:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_NON_VIRTUAL_OFFSET:
        case ICT_VIRTUAL_OFFSET:
            break;

        case ICT_DOUBLE_OFFSET:
            visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;


        case ICT_FUNCTION_THUNK:
            visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_FUNCTION_COVARIANT_THUNK:
            visit_comp(comp->ternary.first, visitor);
            visit_comp(comp->ternary.second, visitor);
            visit_comp(comp->ternary.third, visitor);
            break;

        case ICT_CONSTRUCTOR:
        case ICT_DESTRUCTOR:
            break;

        case ICT_TYPE:
        case ICT_VENDOR_TYPE:
            break;

        case ICT_QUALIFIED_TYPE:
            visit_comp(comp->qualified.sub, visitor);
            break;

        case ICT_POINTER_TO:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_REFERENCE_TO:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_RVALUE_REFERENCE_TO:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_COMPLEX_PAIR:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_IMAGINARY:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_FUNCTION_TYPE:
            visit_comp(comp->function.args, visitor);
            break;

        case ICT_FUNCTION_ENCODING:
            visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_ARRAY:
            if (!comp->array.numbered_dim && comp->array.dim_expr != NULL)
                visit_comp(comp->array.dim_expr, visitor);
            visit_comp(comp->array.atype, visitor);
            break;

        case ICT_POINTER_TO_MEMBER:
            visit_comp(comp->pmember.class, visitor);
            visit_comp(comp->pmember.member, visitor);
            break;

        case ICT_TEMPLATE_PARAM:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_TEMPLATE_ARGS:
            visit_comp(comp->unary, visitor);
            break;

        case ICT_TYPES_LIST:

            visit_comp(comp->binary.left, visitor);

            if (comp->binary.right != NULL)
                visit_comp(comp->binary.right, visitor);

            break;

        case ICT_PACKED_EMPTY:
            break;

        case ICT_EXPR_LIST:

            visit_comp(comp->binary.left, visitor);

            if (comp->binary.right != NULL)
                visit_comp(comp->binary.right, visitor);

            break;

        case ICT_OPERATED_EXPRESSION:
            visit_comp(comp->binary.left, visitor);
            visit_comp(comp->binary.right, visitor);
            break;

        case ICT_STD_SUBST:
            break;

        case ICT_COUNT:
            break;

    }

    visitor(comp);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant à mettre à jour.                            *
*                                                                             *
*  Description : Incrémente le nombre d'utilisation du composant.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void itd_ref_comp(itanium_component *comp)
{
    void visit_for_ref(itanium_component *comp)
    {
        comp->refcount++;

    }

    visit_comp(comp, visit_for_ref);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant à mettre à jour.                            *
*                                                                             *
*  Description : Décrémente le nombre d'utilisation du composant.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void itd_unref_comp(itanium_component *comp)
{
    void visit_for_unref(itanium_component *comp)
    {
        if (--comp->refcount == 0)
        {
            if (comp->type == ICT_TYPE || comp->type == ICT_VENDOR_TYPE || comp->type == ICT_STD_SUBST)
                g_object_unref(G_OBJECT(comp->dtype));

            itd_free(comp);

        }

    }

    visit_comp(comp, visit_for_unref);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à définir pour le composant.                     *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_with_type(ItaniumComponentType type)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str = chaîne de caractères à conserver.                      *
*                len = taille de l'identifiant à retrouver.                   *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_name(const char *str, size_t len)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_NAME;
    result->s_name.str = str;
    result->s_name.len = len;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = information de base sur l'opérateur manipulé.         *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_operator(const itanium_operator_info *info)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_OPERATOR_NAME;
    result->operator.otype = IOT_SIMPLE;
    result->operator.info = *info;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = information de base sur l'opérateur manipulé.         *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_cast_operator(itanium_component *type)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_OPERATOR_NAME;
    result->operator.otype = IOT_CAST;
    result->operator.trans = type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant Itanium décodé à consulter.                 *
*                type = type d'opérateur représenté.                          *
*                                                                             *
*  Description : Donne des indications quant à un opérateur Itanium.          *
*                                                                             *
*  Retour      : Informations à interpréter selon le type transmis.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const void *itd_get_operator_info(const itanium_component *comp, ItaniumOperatorType *type)
{
    const void *result;                     /* Données à retourner         */

    assert(comp->type == ICT_OPERATOR_NAME);

    *type = comp->operator.otype;

    switch (*type)
    {
        case IOT_SIMPLE:
            result = &comp->operator.info;
            break;

        case IOT_CAST:
            result = comp->operator.trans;
            break;

        default:
            assert(false);
            result = NULL;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type   = type exacte de décalage.                            *
*                offset = décalage extrait de l'encodage.                     *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_offset(ItaniumComponentType type, ssize_t offset)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = type;
    result->offset = offset;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dtype = instance de type en place à conserver.               *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_type(GDataType *dtype)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_TYPE;
    result->dtype = dtype;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sub       = composant de type en place à référencer.         *
*                qualifier = propriétés supplémentaires pour le type.         *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_qualified_type(itanium_component *sub, TypeQualifier qualifier)
{
    itanium_component *result;              /* Composant à renvoyer        */

    if (qualifier == TQF_NONE)
        result = sub;

    else
    {
        result = itd_alloc();

        result->type = ICT_QUALIFIED_TYPE;
        result->qualified.sub = sub;
        result->qualified.qualifier = qualifier;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : extern_c = nature de la fonction à représenter.              *
*                args     = arguments de cette même fonction.                 *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_function_type(bool extern_c, itanium_component *args)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_FUNCTION_TYPE;
    result->function.extern_c = extern_c;
    result->function.args = args;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant Itanium à consulter.                        *
*                                                                             *
*  Description : Indique si une fonction est externalisée en C.               *
*                                                                             *
*  Retour      : Nature de la fonction représentée.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool itd_is_external_function(const itanium_component *comp)
{
    bool result;                            /* Bilan à retourner           */

    assert(comp->type == ICT_FUNCTION_TYPE);

    result = comp->function.extern_c;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : number = dimension du tableau.                               *
*                type   = type des membres du même tableau.                   *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_array_with_dim_number(ssize_t number, itanium_component *type)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_ARRAY;
    result->array.numbered_dim = true;
    result->array.dim_number = number;
    result->array.atype = type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = dimension du tableau.                                 *
*                type = type des membres du même tableau.                     *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_array_with_dim_expr(itanium_component *expr, itanium_component *type)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_ARRAY;
    result->array.numbered_dim = false;
    result->array.dim_expr = expr;
    result->array.atype = type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe d'appatenance.                               *
*                member = membre représenté.                                  *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_pointer_to_memeber_type(itanium_component *class, itanium_component *member)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = ICT_POINTER_TO_MEMBER;
    result->pmember.class = class;
    result->pmember.member = member;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type du composant à mettre en place.                 *
*                unary = sous-composant à associer.                           *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_unary(ItaniumComponentType type, itanium_component *unary)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = type;
    result->unary = unary;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type du composant à mettre en place.                 *
*                left  = premier composant à associer.                        *
*                right = second composant à associer.                         *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_binary(ItaniumComponentType type, itanium_component *left, itanium_component *right)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = type;
    result->binary.left = left;
    result->binary.right = right;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du composant à mettre en place.                  *
*                left = second composant à associer.                          *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_append_right_to_binary(ItaniumComponentType type, itanium_component *parent, itanium_component *left)
{
    itanium_component *result;              /* Composant à renvoyer        */
    itanium_component *iter;                /* Boucle de parcours          */

    result = itd_alloc();

    result->type = type;
    result->binary.left = left;
    result->binary.right = NULL;

    if (parent != NULL)
    {
        for (iter = parent; iter->binary.right != NULL; iter = iter->binary.right)
            ;
        iter->binary.right = result;
    }

    return (parent != NULL ? parent : result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du composant à mettre en place.                  *
*                left = second composant à associer.                          *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_merge_list_right_to_binary(ItaniumComponentType type, itanium_component *parent, itanium_component *left)
{
    itanium_component *result;              /* Composant à renvoyer        */
    itanium_component *iter;                /* Boucle de parcours          */

    if (left->type != ICT_TYPES_LIST)
        result = itd_append_right_to_binary(type, parent, left);

    else
    {
        if (parent == NULL)
            result = left;

        else
        {
            for (iter = parent; iter->binary.right != NULL; iter = iter->binary.right)
                ;
            iter->binary.right = left;
        }

    }

    return (parent != NULL ? parent : result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du composant à mettre en place.                  *
*                c0   = premier composant à associer.                         *
*                c1   = second composant à associer.                          *
*                c2   = troisième composant à associer.                       *
*                                                                             *
*  Description : Construit un composant dans un contexte Itanium.             *
*                                                                             *
*  Retour      : Composant extrait ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *itd_make_ternary(ItaniumComponentType type, itanium_component *c0, itanium_component *c1, itanium_component *c2)
{
    itanium_component *result;              /* Composant à renvoyer        */

    result = itd_alloc();

    result->type = type;
    result->ternary.first = c0;
    result->ternary.second = c1;
    result->ternary.third = c2;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant à mettre à jour.                            *
*                type = type à redéfinir pour le composant.                   *
*                                                                             *
*  Description : Modifie légèrement le type d'un composant donné.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void itd_set_type(itanium_component *comp, ItaniumComponentType type)
{
    comp->type = type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant à consulter.                                *
*                                                                             *
*  Description : Fournit le type d'un composant issu d'un contexte Itanium.   *
*                                                                             *
*  Retour      : Type enregistré.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ItaniumComponentType itd_get_component_type(const itanium_component *comp)
{
    return comp->type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = second composant à associer.                          *
*                base = éventuelle base à compléter ou NULL si aucune.        *
*                                                                             *
*  Description : Traduit les composants de contexte Itanium.                  *
*                                                                             *
*  Retour      : Traduction en format humainement lisible effectuée.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *itd_translate_component(const itanium_component *comp, char *base)
{
    char *result;                           /* Chaîne à retourner          */
    char *name;                             /* Désignation à copier        */
    const itanium_component *sub;           /* Sous-partie de composant    */
    ItaniumOperatorType otype;              /* Type d'opérateur            */
    const void *odata;                      /* Données associées           */
    const itanium_operator_info *simple;    /* Données d'opérateur simple  */
    char *tmp;                              /* Transcription temporaire    */

    switch (comp->type)
    {
        case ICT_NAME:
            result = strnadd(base, comp->s_name.str, comp->s_name.len);
            break;

        case ICT_STD_UNSCOPED_NAME:
            result = stradd(base, "std::");
            result = itd_translate_component(comp->unary, result);
            break;

        case ICT_NESTED_NAME:

            if (comp->binary.right->type == ICT_TEMPLATE_ARGS)
            {
                result = itd_translate_component(comp->binary.left, base);
                result = itd_translate_component(comp->binary.right, result);
            }

            else
            {
                if (comp->binary.left != NULL)
                {
                    result = itd_translate_component(comp->binary.left, base);
                    result = stradd(result, "::");
                }
                else
                    result = base;

                result = itd_translate_component(comp->binary.right, result);

            }

            break;

        case ICT_TEMPLATE_NAME_ARGS:
            result = itd_translate_component(comp->binary.left, base);
            result = itd_translate_component(comp->binary.right, result);
            break;

        case ICT_PREFIX_BINARY:
            result = itd_translate_component(comp->binary.left, base);
            if (comp->binary.right->type != ICT_TEMPLATE_ARGS)
                result = stradd(result, "::");
            result = itd_translate_component(comp->binary.right, result);
            break;

        case ICT_TPREFIX_BINARY:
            if (comp->binary.left != NULL)
            {
                result = itd_translate_component(comp->binary.left, base);
                if (comp->binary.right->type != ICT_TEMPLATE_ARGS)
                    result = stradd(result, "::");
            }
            else
                result = base;
            result = itd_translate_component(comp->binary.right, result);
            break;

        case ICT_OPERATOR_NAME:
            switch (comp->operator.otype)
            {
                case IOT_SIMPLE:
                    result = stradd(base, "operator");
                    result = stradd(result, comp->operator.info.name);
                    break;
                case IOT_CAST:
                    result = stradd(base, "(");
                    result = itd_translate_component(comp->operator.trans, result);
                    result = stradd(result, ")");
                    break;
                default:
                    result = NULL;
                    break;
            }
            break;

        case ICT_SPECIAL_NAME_VTABLE:
            result = itd_translate_component(comp->unary, base);
            result = stradd(result, "::vtable");
            break;

        case ICT_SPECIAL_NAME_VSTRUCT:
            result = itd_translate_component(comp->unary, base);
            result = stradd(result, "::vstruct");
            break;

        case ICT_NON_VIRTUAL_OFFSET:
        case ICT_VIRTUAL_OFFSET:
            asprintf(&tmp, "%zd", comp->offset);
            result = stradd(base, tmp);
            free(tmp);
            break;

        case ICT_DOUBLE_OFFSET:
            result = itd_translate_component(comp->binary.left, base);
            result = stradd(result, "_");
            result = itd_translate_component(comp->binary.right, result);
            break;

        case ICT_FUNCTION_THUNK:
            result = itd_translate_component(comp->binary.left, base);
            result = stradd(result, "_");
            result = itd_translate_component(comp->binary.right, result);
            break;

        case ICT_FUNCTION_COVARIANT_THUNK:
            result = itd_translate_component(comp->ternary.first, base);
            result = stradd(result, "_");
            result = itd_translate_component(comp->ternary.second, result);
            result = stradd(result, "_");
            result = itd_translate_component(comp->ternary.third, result);
            break;

        case ICT_CONSTRUCTOR:
            result = stradd(base, "<ctor>");
            break;

        case ICT_DESTRUCTOR:
            result = stradd(base, "<dtor>");
            break;

        case ICT_TYPE:
        case ICT_VENDOR_TYPE:
            name = g_data_type_to_string(comp->dtype, true);
            result = stradd(base, name);
            free(name);
            break;

        case ICT_QUALIFIED_TYPE:

            switch (comp->qualified.qualifier)
            {
                case TQF_RESTRICT:
                    result = stradd(base, "restrict ");
                    break;
                case TQF_VOLATILE:
                    result = stradd(base, "volatile ");
                    break;
                case TQF_CONST:
                    result = stradd(base, "const ");
                    break;
                default:
                    assert(false);
                    result = NULL;
                    break;
            }

            result = itd_translate_component(comp->qualified.sub, result);

            break;

        case ICT_POINTER_TO:
            result = itd_translate_component(comp->unary, base);
            result = stradd(result, " *");
            break;

        case ICT_REFERENCE_TO:
            result = itd_translate_component(comp->unary, base);
            result = stradd(result, " &");
            break;

        case ICT_RVALUE_REFERENCE_TO:
            result = itd_translate_component(comp->unary, base);
            result = stradd(result, " &");
            break;

        case ICT_COMPLEX_PAIR:
            result = stradd(base, "<?>");
            result = itd_translate_component(comp->unary, result);
            break;

        case ICT_IMAGINARY:
            result = stradd(base, "<?>");
            result = itd_translate_component(comp->unary, result);
            break;

        case ICT_FUNCTION_TYPE:
            result = stradd(base, "(*) (");
            result = itd_translate_component(comp->function.args, result);
            result = stradd(result, ")");
            break;

        case ICT_FUNCTION_ENCODING:

            result = stradd(base, "???");

            result = stradd(result, " ");

            result = itd_translate_component(comp->binary.left, result);

            result = stradd(result, "(");

            result = itd_translate_component(comp->binary.right, result);

            result = stradd(result, ")");

            break;

        case ICT_ARRAY:

            result = itd_translate_component(comp->array.atype, base);

            result = stradd(result, "[");

            if (comp->array.numbered_dim)
            {
                asprintf(&tmp, "%zd", comp->array.dim_number);
                result = stradd(result, tmp);
                free(tmp);
            }

            else if (comp->array.dim_expr != NULL)
                result = itd_translate_component(comp->array.dim_expr, result);

            result = stradd(result, "]");

            break;

        case ICT_POINTER_TO_MEMBER:
            result = itd_translate_component(comp->pmember.class, base);
            result = stradd(result, "::");
            result = itd_translate_component(comp->pmember.member, result);
            break;

        case ICT_TEMPLATE_PARAM:
            result = itd_translate_component(comp->unary, base);
            break;

        case ICT_TEMPLATE_ARGS:
            result = stradd(base, "<");
            result = itd_translate_component(comp->unary, result);
            result = stradd(result, ">");
            break;

        case ICT_TYPES_LIST:

            result = itd_translate_component(comp->binary.left, base);

            if (comp->binary.right != NULL)
            {
                result = stradd(result, ", ");
                result = itd_translate_component(comp->binary.right, result);
            }

            break;

        case ICT_PACKED_EMPTY:
            break;

        case ICT_EXPR_LIST:

            /**
             * A priori traité en amont.
             */

            result = itd_translate_component(comp->binary.left, base);

            if (comp->binary.right != NULL)
            {
                result = stradd(result, ", ");
                result = itd_translate_component(comp->binary.right, result);
            }

            break;

        case ICT_OPERATED_EXPRESSION:

            odata = itd_get_operator_info(comp->binary.left, &otype);

            sub = comp->binary.right;
            assert(sub->type == ICT_EXPR_LIST);

            switch (otype)
            {
                case IOT_SIMPLE:

                    simple = (const itanium_operator_info *)odata;

                    switch (simple->args)
                    {
                        case 1:
                            result = stradd(base, simple->name);
                            result = itd_translate_component(sub->binary.left, result);
                            assert(sub->binary.right == NULL);
                            break;

                        case 2:

                            result = itd_translate_component(sub->binary.left, base);

                            result = stradd(result, simple->name);

                            sub = sub->binary.right;
                            assert(sub->type == ICT_EXPR_LIST);
                            result = itd_translate_component(sub->binary.left, result);
                            assert(sub->binary.right == NULL);
                            break;

                        case 3:

                            result = itd_translate_component(sub->binary.left, base);

                            result = stradd(result, simple->name);

                            sub = sub->binary.right;
                            assert(sub->type == ICT_EXPR_LIST);
                            result = itd_translate_component(sub->binary.left, result);

                            result = stradd(result, ":");

                            sub = sub->binary.right;
                            assert(sub->type == ICT_EXPR_LIST);
                            result = itd_translate_component(sub->binary.left, result);
                            assert(sub->binary.right == NULL);

                            break;

                    }

                    break;

                case IOT_CAST:
                    result = stradd(base, "(");
                    sub = (const itanium_component *)odata;
                    result = itd_translate_component(sub, result);
                    result = stradd(result, ")");
                    break;

                default:
                    result = NULL;
                    break;

            }

            break;

        case ICT_STD_SUBST:
            name = g_data_type_to_string(comp->dtype, true);
            result = stradd(base, name);
            free(name);
            break;

        case ICT_COUNT:
            result = base;
            break;

    }



    return result;


}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant Itanium à traduire en décalage.             *
*                off  = réceptacle pour les informations traduites.           *
*                                                                             *
*  Description : Traduit les composants de contexte Itanium en décalage.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool itd_translate_component_to_offset(const itanium_component *comp, call_offset_t *off)
{
    bool result;                            /* Bilan à retourner           */

    if (comp->type == ICT_DOUBLE_OFFSET)
    {
        result = comp->binary.left->type == ICT_NON_VIRTUAL_OFFSET
            && comp->binary.right->type == ICT_VIRTUAL_OFFSET;

        assert(result);

        if (result)
        {
            off->values[0] = comp->binary.left->offset;
            off->values[1] = comp->binary.right->offset;
            off->virtual = true;
        }

    }

    else if (comp->type == ICT_NON_VIRTUAL_OFFSET)
    {
        result = true;

        off->values[0] = comp->offset;
        off->virtual = false;

    }

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à traiter.                                       *
*                ns   = espace à intégrer.                                    *
*                                                                             *
*  Description : Ajoute un espace de noms à un type déjà préparé.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void itd_prepend_namespace_to_type(GDataType *type, GDataType *ns)
{
    GDataType *existing;                    /* Espace en place ?           */

    existing = g_data_type_get_namespace(type);

    if (existing == NULL)
    {
        g_data_type_set_namespace(type, ns, "::");
        g_object_unref(G_OBJECT(ns));
    }

    else
    {
        itd_prepend_namespace_to_type(existing, ns);

        g_object_unref(G_OBJECT(existing));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp  = composant Itanium à traduire en type.                *
*                rtype = type de l'éventuelle routine en construction.        *
*                                                                             *
*  Description : Traduit les composants de contexte Itanium en type.          *
*                                                                             *
*  Retour      : Traduction en type décodé.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *itd_translate_component_to_type(const itanium_component *comp, RoutineType *rtype)
{
    GDataType *result;                      /* Type à retourner            */
    char *name;                             /* Attribution finale          */
    GDataType *ns;                          /* Espace de noms d'un type    */
    GDataType *sub;                         /* Sous-titre à traiter        */
    call_offset_t off0;                     /* Décalage #0                 */
    call_offset_t off1;                     /* Décalage #1                 */
    itanium_component *iter;                /* Boucle de parcours          */
    GDataType *arg;                         /* Argument de prototype       */
    GDataType *members;                     /* Type de membres de tableau  */
    GDataType *param;                       /* Paramètre de gabarit        */
    char *value;                            /* Valeur quelconque exprimée  */

    /* Pour GCC !? */
    result = NULL;

    switch (comp->type)
    {
        case ICT_NAME:
            name = itd_translate_component(comp, NULL);
            result = g_class_enum_type_new(CEK_STRUCT, name);
            break;

        case ICT_STD_UNSCOPED_NAME:
            result = itd_translate_component_to_type(comp->unary, rtype);
            if (result != NULL)
            {
                ns = g_class_enum_type_new(CEK_NAMESPACE, strdup("std"));
                itd_prepend_namespace_to_type(result, ns);
            }
            break;

        case ICT_NESTED_NAME:

            if (comp->binary.right->type == ICT_TEMPLATE_ARGS)
            {
                name = itd_translate_component(comp->binary.left, NULL);
                name = itd_translate_component(comp->binary.right, name);

                result = g_class_enum_type_new(CEK_CLASS, name);

            }

            else
            {
                if (comp->binary.left != NULL)
                {
                    ns = itd_translate_component_to_type(comp->binary.left, rtype);
                    if (ns == NULL)
                    {
                        result = NULL;
                        break;
                    }
                }
                else
                    ns = NULL;

                result = itd_translate_component_to_type(comp->binary.right, rtype);

                if (result != NULL)
                {
                    if (ns != NULL)
                        itd_prepend_namespace_to_type(result, ns);
                }

                else
                {
                    if (*rtype != RTT_CLASSIC)
                        result = ns;

                    else if (ns != NULL)
                        g_object_unref(G_OBJECT(ns));

                }

            }

            break;

        case ICT_TEMPLATE_NAME_ARGS:

            result = itd_translate_component_to_type(comp->binary.right, rtype);

            if (result != NULL)
            {
                sub = itd_translate_component_to_type(comp->binary.left, rtype);

                if (sub == NULL)
                {
                    name = itd_translate_component(comp->binary.left, NULL);
                    ns = NULL;
                }

                else
                {
                    ns = g_data_type_get_namespace(sub);
                    g_data_type_set_namespace(sub, NULL, NULL);

                    name = g_data_type_to_string(sub, true);

                    g_object_unref(G_OBJECT(sub));

                }

                g_template_type_set_name(G_TEMPLATE_TYPE(result), name);
                free(name);

                if (ns != NULL)
                    itd_prepend_namespace_to_type(result, ns);

            }

            break;

        case ICT_PREFIX_BINARY:

            if (comp->binary.right->type == ICT_TEMPLATE_ARGS)
            {
                name = itd_translate_component(comp->binary.left, NULL);
                name = itd_translate_component(comp->binary.right, name);

                result = g_class_enum_type_new(CEK_CLASS, name);

            }

            else
            {
                ns = itd_translate_component_to_type(comp->binary.left, rtype);
                if (ns == NULL)
                {
                    result = NULL;
                    break;
                }

                result = itd_translate_component_to_type(comp->binary.right, rtype);

                if (result != NULL)
                    itd_prepend_namespace_to_type(result, ns);

            }

            break;

        case ICT_TPREFIX_BINARY:

            if (comp->binary.right->type == ICT_TEMPLATE_ARGS)
            {
                name = itd_translate_component(comp->binary.left, NULL);
                name = itd_translate_component(comp->binary.right, name);

                result = g_class_enum_type_new(CEK_CLASS, name);

            }

            else
            {
                if (comp->binary.left != NULL)
                {
                    ns = itd_translate_component_to_type(comp->binary.left, rtype);
                    if (ns == NULL)
                    {
                        result = NULL;
                        break;
                    }

                }
                else
                    ns = NULL;

                result = itd_translate_component_to_type(comp->binary.right, rtype);

                if (result != NULL)
                {
                    if (ns != NULL)
                        itd_prepend_namespace_to_type(result, ns);
                }
                else
                {
                    if (ns != NULL)
                        g_object_unref(G_OBJECT(ns));
                }

            }

            break;

        case ICT_OPERATOR_NAME:
            name = itd_translate_component(comp, NULL);
            result = g_class_enum_type_new(CEK_STRUCT, name);
            break;

        case ICT_SPECIAL_NAME_VTABLE:

            ns = itd_translate_component_to_type(comp->unary, rtype);

            if (ns == NULL)
                result = NULL;

            else
            {
                result = g_class_enum_type_new(CEK_VIRTUAL_TABLE, NULL);
                itd_prepend_namespace_to_type(result, ns);
            }

            break;

        case ICT_SPECIAL_NAME_VSTRUCT:

            ns = itd_translate_component_to_type(comp->unary, rtype);

            if (ns == NULL)
                result = NULL;

            else
            {
                result = g_class_enum_type_new(CEK_VIRTUAL_STRUCT, NULL);
                itd_prepend_namespace_to_type(result, ns);
            }

            break;

        case ICT_NON_VIRTUAL_OFFSET:
        case ICT_VIRTUAL_OFFSET:
        case ICT_DOUBLE_OFFSET:
            result = NULL;
            break;

        case ICT_FUNCTION_THUNK:

            if (!itd_translate_component_to_offset(comp->binary.right, &off0))
            {
                result = NULL;
                break;
            }

            result = itd_translate_component_to_type(comp->binary.left, rtype);

            if (result != NULL)
                result = g_override_type_new(result, &off0);

            break;

        case ICT_FUNCTION_COVARIANT_THUNK:

            if (!itd_translate_component_to_offset(comp->ternary.second, &off0))
            {
                result = NULL;
                break;
            }

            if (!itd_translate_component_to_offset(comp->ternary.third, &off1))
            {
                result = NULL;
                break;
            }

            result = itd_translate_component_to_type(comp->ternary.first, rtype);

            if (result != NULL)
                result = g_override_type_new_with_covariant(result, &off0, &off1);

            break;

        case ICT_CONSTRUCTOR:
            if (rtype != NULL)
                *rtype = RTT_CONSTRUCTOR;
            result = NULL;
            break;

        case ICT_DESTRUCTOR:
            if (rtype != NULL)
                *rtype = RTT_DESTRUCTOR;
            result = NULL;
            break;

        case ICT_TYPE:
        case ICT_VENDOR_TYPE:
            result = g_data_type_dup(comp->dtype);
            break;

        case ICT_QUALIFIED_TYPE:
            result = itd_translate_component_to_type(comp->qualified.sub, rtype);
            if (result != NULL)
                g_data_type_add_qualifier(result, comp->qualified.qualifier);
            break;

        case ICT_POINTER_TO:
            result = itd_translate_component_to_type(comp->unary, rtype);
            if (result != NULL && !G_IS_PROTO_TYPE(result))
                result = g_encapsulated_type_new(ECT_POINTER, result);
            break;

        case ICT_REFERENCE_TO:
            result = itd_translate_component_to_type(comp->unary, rtype);
            if (result != NULL)
                result = g_encapsulated_type_new(ECT_REFERENCE, result);
            break;

        case ICT_RVALUE_REFERENCE_TO:
            result = itd_translate_component_to_type(comp->unary, rtype);
            if (result != NULL)
                result = g_encapsulated_type_new(ECT_RVALUE_REF, result);
            break;

        case ICT_COMPLEX_PAIR:
            result = itd_translate_component_to_type(comp->unary, rtype);
            if (result != NULL)
                result = g_encapsulated_type_new(ECT_COMPLEX, result);
            break;

        case ICT_IMAGINARY:
            result = itd_translate_component_to_type(comp->unary, rtype);
            if (result != NULL)
                result = g_encapsulated_type_new(ECT_IMAGINARY, result);
            break;

        case ICT_FUNCTION_TYPE:

            result = g_proto_type_new();

            assert(comp->function.args->type == ICT_TYPES_LIST);

            for (iter = comp->function.args; iter != NULL && result != NULL; iter = iter->binary.right)
            {
                assert(iter->type == ICT_TYPES_LIST);

                arg = itd_translate_component_to_type(iter->binary.left, rtype);

                if (arg == NULL)
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

                else
                {
                    if (iter == comp->function.args)
                    {
                        g_proto_type_set_return_type(G_PROTO_TYPE(result), arg);
                        g_object_unref(G_OBJECT(arg));
                    }

                    else
                    {
                        g_proto_type_add_arg(G_PROTO_TYPE(result), arg);
                        g_object_unref(G_OBJECT(arg));
                    }

                }

            }

            break;

        case ICT_FUNCTION_ENCODING:
            result = NULL;
            break;

        case ICT_ARRAY:

            members = itd_translate_component_to_type(comp->array.atype, rtype);

            if (members == NULL)
                result = NULL;

            else
            {
                result = g_array_type_new(members);

                if (comp->array.numbered_dim)
                    g_array_type_set_dimension_number(G_ARRAY_TYPE(result), comp->array.dim_number);

                else if (comp->array.dim_expr != NULL)
                    g_array_type_set_dimension_expression(G_ARRAY_TYPE(result),
                                                          itd_translate_component(comp->array.dim_expr, NULL));

                else
                    g_array_type_set_empty_dimension(G_ARRAY_TYPE(result));

            }

            break;

        case ICT_POINTER_TO_MEMBER:

            ns = itd_translate_component_to_type(comp->pmember.class, rtype);

            if (ns == NULL)
                result = NULL;

            else
            {
                result = itd_translate_component_to_type(comp->pmember.member, rtype);

                if (result == NULL)
                    g_object_unref(G_OBJECT(ns));

                else
                    itd_prepend_namespace_to_type(result, ns);

            }

            break;

        case ICT_TEMPLATE_PARAM:
            result = itd_translate_component_to_type(comp->unary, rtype);
            break;

        case ICT_TEMPLATE_ARGS:

            assert(comp->unary->type == ICT_TYPES_LIST || comp->unary->type == ICT_PACKED_EMPTY);

            result = g_template_type_new();

            for (iter = comp->unary; iter != NULL && result != NULL; iter = iter->binary.right)
            {
                if (iter->type == ICT_PACKED_EMPTY)
                    continue;

                assert(iter->type == ICT_TYPES_LIST);

                param = itd_translate_component_to_type(iter->binary.left, rtype);

                if (param == NULL)
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }
                else
                {
                    g_template_type_add_param(G_TEMPLATE_TYPE(result), param);
                    g_object_unref(G_OBJECT(param));
                }

            }

            break;

        case ICT_TYPES_LIST:
        case ICT_PACKED_EMPTY:

            /**
             * Les listes doient être rassemblées par l'appelant !
             */

            assert(false);
            result = NULL;
            break;

        case ICT_EXPR_LIST:

            /**
             * Les listes doient être rassemblées par l'appelant !
             */

            assert(false);
            result = NULL;
            break;

        case ICT_OPERATED_EXPRESSION:
            value = itd_translate_component(comp, NULL);
            result = g_expr_type_new(value);
            free(value);
            break;

        case ICT_STD_SUBST:
            result = g_data_type_dup(comp->dtype);
            break;

        case ICT_COUNT:
            assert(false);
            result = NULL;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comp = composant Itanium à traduire en routine.              *
*                                                                             *
*  Description : Traduit les composants de contexte Itanium en routine.       *
*                                                                             *
*  Retour      : Traduction en routine décodée.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *itd_translate_component_to_routine(const itanium_component *comp)
{
    GBinRoutine *result;                    /* Routine à retourner         */
    itanium_component *name;                /* Désignation de la routine   */
    RoutineType rtype;                      /* Type déclaré de routine     */
    bool has_ret;                           /* Type de retour présent ?    */
    char *desc;                             /* Description humaine         */
    GDataType *ns;                          /* Espace de noms de la routine*/
    itanium_component *args;                /* Liste de ses arguments      */
    itanium_component *iter;                /* Boucle de parcours          */
    GDataType *type;                        /* Type d'un argument          */
    GBinVariable *arg;                      /* Argument à ajouter          */

    if (comp->type != ICT_FUNCTION_ENCODING)
        goto bad_encoding;

    result = g_binary_routine_new();

    /* Nom de la routine */

    name = comp->binary.left;

    rtype = RTT_CLASSIC;

    /**
     * A la fin de § 5.1.3 ("Operator Encodings") est précisé :
     *
     *    If the conversion operator is a member template, the result type will
     *    appear before the template parameters.
     *
     * On note donc cette particularité.
     */

    has_ret = (name->type == ICT_TEMPLATE_NAME_ARGS);

    switch (name->type)
    {
        /**
         * Seules les productions de itd_name() sont valides ici.
         * On écarte volontairement les noms qualifiés ICT_QUALIFIED_TYPE.
         */

        case ICT_NESTED_NAME:
        case ICT_TEMPLATE_NAME_ARGS:
        case ICT_STD_UNSCOPED_NAME:
        case ICT_NAME:

            type = itd_translate_component_to_type(name, &rtype);
            if (type == NULL) goto unsupported_encoding;

            ns = g_data_type_get_namespace(type);

            g_data_type_set_namespace(type, NULL, NULL);

            if (G_IS_TEMPLATE_TYPE(type))
                g_binary_routine_set_typed_name(result, type);

            else
            {
                desc = g_data_type_to_string(type, true);

                g_object_unref(G_OBJECT(type));

                g_binary_routine_set_name(result, desc);

            }

            if (ns != NULL)
                g_binary_routine_set_namespace(result, ns, strdup("::"));

            break;

        case ICT_OPERATOR_NAME:
            g_binary_routine_set_name(result, itd_translate_component(name, NULL));
            break;

        default:
            goto unsupported_encoding;
            break;

    }

    g_binary_routine_set_type(result, rtype);

    /* Liste d'arguments */

    args = comp->binary.right;

    if (args->type != ICT_TYPES_LIST)
        goto unsupported_encoding;

    for (iter = args; iter != NULL; iter = iter->binary.right)
    {
        type = itd_translate_component_to_type(iter->binary.left, NULL);

        if (type == NULL)
            goto unsupported_encoding;

        if (iter == args && has_ret)
            g_binary_routine_set_return_type(result, type);

        else
        {
            arg = g_binary_variable_new(type);
            g_binary_routine_add_arg(result, arg);
        }

    }

    return result;

 unsupported_encoding:

    g_object_unref(G_OBJECT(result));

 bad_encoding:

    return NULL;

}
