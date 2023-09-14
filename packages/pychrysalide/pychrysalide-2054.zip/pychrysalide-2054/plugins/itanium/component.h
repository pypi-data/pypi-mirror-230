
/* Chrysalide - Outil d'analyse de fichiers binaires
 * component.h - prototypes pour la représentation des composants extraits de l'ABI C++ Itanium
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


#ifndef _PLUGINS_ITANIUM_COMPONENT_H
#define _PLUGINS_ITANIUM_COMPONENT_H


#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <sys/types.h>


#include <analysis/routine.h>
#include <analysis/type.h>



/* Type de composants */
typedef enum _ItaniumComponentType
{
    /**
     * Chaîne de caractère, terminée par un octet nul.
     */
    ICT_NAME,

    /**
     * Nom avec préfixe standard.
     * Le nom en question est placé dans le champ unary.
     */
    ICT_STD_UNSCOPED_NAME,

    /**
     * Noms imbriqués, en deux parties : 'binary'.
     * En cas de préfixe nul, le composant gauche peut être nul.
     */
    ICT_NESTED_NAME,

    /**
     * Noms imbriqués, en deux parties : 'binary'.
     * C'est normalement le seul réceptacle pour les composants issus
     * de itd_template_args (sur la branche droite).
     */
    ICT_TEMPLATE_NAME_ARGS,

    /**
     * Type avec préfixes : deux éléments, dans 'binary'
     */
    ICT_PREFIX_BINARY,

    /**
     * Préfixes à deux éléments.
     * En cas de préfixe nul, le composant gauche peut être nul.
     */
    ICT_TPREFIX_BINARY,

    /**
     * Encodage d'un nom d'opérateur, consigné dans 'operator'.
     */
    ICT_OPERATOR_NAME,

    /**
     * Particularité des notions d'objets. Les informations utiles
     * sont rassemblées dans le champ unary.
     */
    ICT_SPECIAL_NAME_VTABLE,
    ICT_SPECIAL_NAME_VSTRUCT,

    /**
     * Fonctions virtuelles.
     *  -> décalage : 'offset'.
     *  -> double décalage : 'binary'.
     *  -> fonctions simples : 'binary'.
     *  -> fonctions complexes : 'ternary'.
     */
    ICT_NON_VIRTUAL_OFFSET,
    ICT_VIRTUAL_OFFSET,
    ICT_DOUBLE_OFFSET,
    ICT_FUNCTION_THUNK,
    ICT_FUNCTION_COVARIANT_THUNK,

    /**
     * Constructeur ou destructeur, sans plus de détail.
     */
    ICT_CONSTRUCTOR,
    ICT_DESTRUCTOR,

    /**
     * Type instanciable dans le programme.
     */
    ICT_TYPE,

    /**
     * Simple distinction de ICT_TYPE, pour la distinction lors des candidatures
     * aux substitutions.
     */
    ICT_VENDOR_TYPE,

    /**
     * Type qualifié ; les infos utilies sont explicitement
     * conservées dans le champ qualified.
     */
    ICT_QUALIFIED_TYPE,

    /**
     * Différentes références vers un sous-type.
     * Le champ impacté est 'unary'.
     */
    ICT_POINTER_TO,
    ICT_REFERENCE_TO,
    ICT_RVALUE_REFERENCE_TO,
    ICT_COMPLEX_PAIR,
    ICT_IMAGINARY,

    /**
     * Prototype de fonction.
     * Le champ impacté est 'function'.
     */
    ICT_FUNCTION_TYPE,

    /**
     * Fonction (nom + retour/paramètres), sous forme binaire :
     *  -> left = function name
     *  -> right = bare-function-type
     */
    ICT_FUNCTION_ENCODING,

    /**
     * Définition d'un tableau. Les indications de dimensions peuvent
     * prendre plusieurs formes, et sont rassemblées dans le champ array.
     */
    ICT_ARRAY,

    /**
     * Pointeur vers un membre. Comme l'espace de noms associé est encodé
     * de façon spéciale, un champ est dédié à ce composant : pmember.
     */
    ICT_POINTER_TO_MEMBER,

    /**
     * Argument de template. Utile pour les candidatures aux substitutions.
     * 'unary' renvoie vers le composant utile.
     */
    ICT_TEMPLATE_PARAM,

    /**
     * Liste d'arguments pour templates, à encadrer par des chevrons.
     * 'unary' pointe vers la liste des éléments.
     */
    ICT_TEMPLATE_ARGS,

    /**
     * Liste de types, sous forme binaire :
     *  -> left = élément de la liste de types.
     *  -> right = reste de la liste de types.
     */
    ICT_TYPES_LIST,

    /**
     * Paramètres compressés de patron non définis.
     * (cf. règle <template-arg> ::= J <template-arg>* E )
     */
    ICT_PACKED_EMPTY,

    /**
     * Liste d'expressions, sous forme binaire comme pour ICT_TYPES_LIST :
     *  -> left = élément de la liste de types.
     *  -> right = reste de la liste de types.
     */
    ICT_EXPR_LIST,

    /**
     * Liste de types, sous forme binaire :
     *  -> left = composant d'opérateur.
     *  -> right = liste d'expressions.
     */
    ICT_OPERATED_EXPRESSION,

    /**
     * Substitution avec préfixe standard. Le résultat est prêt dans le champ
     * dtype.
     */
    ICT_STD_SUBST,

    ICT_COUNT

} ItaniumComponentType;


/* Catégories d'opérateurs */
typedef enum _ItaniumOperatorType
{
    IOT_SIMPLE,                             /* Présent dans la liste       */
    IOT_CAST,                               /* Conversion forcée           */
    IOT_VENDOR                              /* Défini par un vendeur       */

} ItaniumOperatorType;


/* Enregistrement des opérateurs */
typedef struct _itanium_operator_info
{
    const char *code;                       /* Nom encodé                  */
    const char *name;                       /* Désignation humaine         */
    size_t name_len;                        /* Taille du nom humain        */
    int args;                               /* Nombre d'arguments          */

} itanium_operator_info;


/* Composant extrait de l'encodage */
typedef struct _itanium_component itanium_component;



/* Incrémente le nombre d'utilisation du composant. */
void itd_ref_comp(itanium_component *);

/* Décrémente le nombre d'utilisation du composant. */
void itd_unref_comp(itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_with_type(ItaniumComponentType);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_name(const char *, size_t);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_operator(const itanium_operator_info *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_cast_operator(itanium_component *);

/* Donne des indications quant à un opérateur Itanium. */
const void *itd_get_operator_info(const itanium_component *, ItaniumOperatorType *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_offset(ItaniumComponentType, ssize_t);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_type(GDataType *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_qualified_type(itanium_component *, TypeQualifier);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_function_type(bool, itanium_component *);

/* Indique si une fonction est externalisée en C. */
bool itd_is_external_function(const itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_array_with_dim_number(ssize_t, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_array_with_dim_expr(itanium_component *, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_pointer_to_memeber_type(itanium_component *, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_unary(ItaniumComponentType, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_binary(ItaniumComponentType, itanium_component *, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_append_right_to_binary(ItaniumComponentType, itanium_component *, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_merge_list_right_to_binary(ItaniumComponentType, itanium_component *, itanium_component *);

/* Construit un composant dans un contexte Itanium. */
itanium_component *itd_make_ternary(ItaniumComponentType, itanium_component *, itanium_component *, itanium_component *);

/* Modifie légèrement le type d'un composant donné. */
void itd_set_type(itanium_component *, ItaniumComponentType);

/* Fournit le type d'un composant issu d'un contexte Itanium. */
ItaniumComponentType itd_get_component_type(const itanium_component *);

/* Traduit les composants de contexte Itanium. */
char *itd_translate_component(const itanium_component *, char *);

/* Traduit les composants de contexte Itanium en type. */
GDataType *itd_translate_component_to_type(const itanium_component *, RoutineType *);

/* Traduit les composants de contexte Itanium en routine. */
GBinRoutine *itd_translate_component_to_routine(const itanium_component *);



#endif  /* _PLUGINS_ITANIUM_COMPONENT_H */
