
/* Chrysalide - Outil d'analyse de fichiers binaires
 * component-int.h - prototypes internes pour la description des composants Itanium
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


#ifndef _PLUGINS_ITANIUM_COMPONENT_INT_H
#define _PLUGINS_ITANIUM_COMPONENT_INT_H


#include "component.h"



/* Composant extrait de l'encodage */
struct _itanium_component
{
    ItaniumComponentType type;              /* Type de composant           */

    unsigned int refcount;                  /* Compteur de références      */

    union
    {
        /* ICT_NAME */
        struct
        {
            const char *str;
            size_t len;

        } s_name;

        /* ICT_OPERATOR_NAME */
        struct
        {
            ItaniumOperatorType otype;      /* Sélection dans l'union      */

            union
            {
                itanium_operator_info info; /* Opérateur simple            */
                itanium_component *trans;   /* Type transtypé              */

            };

        } operator;

        /* ICT_NON_VIRTUAL_OFFSET */
        /* ICT_VIRTUAL_OFFSET */
        ssize_t offset;                     /* Décalage de fonction        */

        /* ICT_TYPE */
        /* ICT_VENDOR_TYPE */
        /* ICT_STD_SUBST */
        GDataType *dtype;                   /* Type instancié              */

        /* ICT_QUALIFIED_TYPE */
        struct
        {
            itanium_component *sub;         /* Sous-élément                */
            TypeQualifier qualifier;        /* Propriétés supplémentaires  */

        } qualified;

        /* ICT_FUNCTION_TYPE */
        struct
        {
            bool extern_c;                  /* Nature de la fonction       */
            itanium_component *args;        /* Liste des arguments         */

        } function;

        /* ICT_ARRAY */
        struct
        {
            bool numbered_dim;              /* Dimension numérique         */
            union
            {
                ssize_t dim_number;         /* Taille du tableau           */
                itanium_component *dim_expr;/* La même, en expression      */
            };

            itanium_component *atype;       /* Type du tableau             */

        } array;

        /* ICT_POINTER_TO_MEMBER */
        struct
        {
            itanium_component *class;       /* Classe d'appatenance        */
            itanium_component *member;      /* Membre représenté           */

        } pmember;

        /* ICT_* */
        struct
        {
            itanium_component *left;        /* Elément premier             */
            itanium_component *right;       /* Elément second              */

        } binary;

        /* ICT_* */
        struct
        {
            itanium_component *first;       /* Elément premier             */
            itanium_component *second;      /* Elément second              */
            itanium_component *third;       /* Elément troisième           */

        } ternary;

        /* ICT_* */
        itanium_component *unary;           /* Sous-élément                */

    };

};



#endif  /* _PLUGINS_ITANIUM_COMPONENT_INT_H */
