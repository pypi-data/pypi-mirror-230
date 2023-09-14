
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pproc.c - remplacements à la volée de chaînes de caractères
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


#include "pproc.h"


#include <malloc.h>
#include <string.h>



/* Pré-processeur avec support des macros */
struct _pre_processor
{
    string_exch *encodings;                 /* Traductions d'encodages     */
    size_t encodings_count;                 /* Nombre de ces traductions   */

    string_exch *macros;                    /* Remplacements de chaînes    */
    size_t macros_count;                    /* Nombre de ces remplacements */

    const char **op_producers;              /* Producteurs d'opérandes     */
    size_t op_prod_count;                   /* Quantité de producteurs     */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau pre-processeur pour le support des macros.   *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

pre_processor *create_pre_processor(void)
{
    pre_processor *result;                  /* Définition vierge à renvoyer*/

    result = (pre_processor *)calloc(1, sizeof(pre_processor));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp = pré-processeur à libérer de la mémoire.                 *
*                                                                             *
*  Description : Supprime de la mémoire un pré-processeur et ses macros.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_pre_processor(pre_processor *pp)
{
    if (pp->encodings != NULL)
        free(pp->encodings);

    if (pp->macros != NULL)
        free(pp->macros);

    free(pp);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp = pré-processeur dont le contenu est à compléter.         *
*                                                                             *
*  Description : Enregistre une correspondance nule en matière d'encodage.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_empty_encoding(pre_processor *pp)
{
    string_exch *encoding;                  /* Traduction à conserver      */

    pp->encodings = (string_exch *)realloc(pp->encodings, ++pp->encodings_count * sizeof(string_exch));

    encoding = &pp->encodings[pp->encodings_count - 1];

    encoding->src = NULL;
    encoding->dest = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp   = pré-processeur dont le contenu est à compléter.       *
*                src  = chaîne à remplacer dans les définitions.              *
*                dest = chaîne de remplacement.                               *
*                                                                             *
*  Description : Enregistre une correspondance en matière d'encodage.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_encoding(pre_processor *pp, const char *src, const char *dest)
{
    string_exch *encoding;                  /* Traduction à conserver      */

    pp->encodings = (string_exch *)realloc(pp->encodings, ++pp->encodings_count * sizeof(string_exch));

    encoding = &pp->encodings[pp->encodings_count - 1];

    encoding->src = src;
    encoding->dest = dest;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp = pré-processeur dont le contenu est à consulter.         *
*                                                                             *
*  Description : Indique le nombre de catégories d'encodages enregistrées.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t count_encodings(const pre_processor *pp)
{
    return pp->encodings_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp    = pré-processeur dont le contenu est à consulter.      *
*                index = indice de l'encodage à retourner.                    *
*                                                                             *
*  Description : Fournit une catégorie d'encodage donnée.                     *
*                                                                             *
*  Retour      : Correspondance à consulter uniquement.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const string_exch *find_encoding(const pre_processor *pp, size_t index)
{
    return &pp->encodings[index];

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp   = pré-processeur dont le contenu est à compléter.       *
*                src  = chaîne à remplacer dans les définitions.              *
*                dest = chaîne de remplacement.                               *
*                                                                             *
*  Description : Constitue la matière d'un système de macros.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void define_macro(pre_processor *pp, const char *src, const char *dest)
{
    string_exch *macro;                     /* Nouvelle macro à constituer */

    pp->macros = (string_exch *)realloc(pp->macros, ++pp->macros_count * sizeof(string_exch));

    macro = &pp->macros[pp->macros_count - 1];

    macro->src = src;
    macro->dest = dest;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp  = pré-processeur dont le contenu est à consulter.        *
*                src = chaîne à remplacer dans les définitions.               *
*                                                                             *
*  Description : Recherche l'existence d'une macro pour un remplacement.      *
*                                                                             *
*  Retour      : Eventuelle correspondance trouvée.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *find_macro(const pre_processor *pp, const char *src)
{
    const char *result;                     /* Trouvaille à renvoyer       */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < pp->macros_count && result == NULL; i++)
        if (strcmp(pp->macros[i].src, src) == 0)
            result = pp->macros[i].dest;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp   = pré-processeur dont le contenu est à compléter.       *
*                func = fonction produisant un opérande final.                *
*                                                                             *
*  Description : Mémorise une fonction comme produisant un opérateur final.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_as_operand_producer(pre_processor *pp, const char *func)
{
    pp->op_producers = (const char **)realloc(pp->op_producers, ++pp->op_prod_count * sizeof(const char **));

    pp->op_producers[pp->op_prod_count - 1] = func;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pp   = pré-processeur dont le contenu est à consulter.       *
*                func = fonction dont la nature du résultat est recherchée.   *
*                                                                             *
*  Description : Détermine si une fonction produit un opérande ou non.        *
*                                                                             *
*  Retour      : true si la fonction fournie produit un opérande final.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_operand_producer(const pre_processor *pp, const char *func)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    for (i = 0; i < pp->op_prod_count && !result; i++)
        result = (strcmp(pp->op_producers[i], func) == 0);

    return result;

}
