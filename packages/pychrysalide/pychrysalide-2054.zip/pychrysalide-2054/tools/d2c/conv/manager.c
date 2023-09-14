
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - substitutions de valeurs depuis un contenu binaire
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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
#include <ctype.h>
#include <malloc.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>


#include "../helpers.h"
#include "../qckcall.h"



/* ---------------------------- CONVERSION DES ARGUMENTS ---------------------------- */


/* Fonction de conversion */
struct _conv_func
{
    char *dest;                             /* Variable de destination     */

    bool is_expr;                           /* Choix du contenu réel       */

    union
    {
        arg_expr_t *expr;                   /* Valeur expressive directe   */

        struct
        {
            char *name;                     /* Fonction de conversion      */
            arg_list_t *args;               /* Liste des arguments         */

        };

    };

    bool used_as_inter;                     /* Variable intermédiaire ?    */
    bool used_as_op;                        /* Opérande finale d'instruct° */
    bool declared;                          /* Expression déjà déclarée ?  */
    bool defined;                           /* Expression déjà définie ?   */

};


/* Indique si l'utilisation en intermédiaire est brute ou non. */
static bool is_conv_func_raw_as_inter(const conv_func *);



/* ---------------------------- ENSEMBLES DE CONVERSIONS ---------------------------- */


/* Liste des fonctions de conversions présentes */
struct _conv_list
{
    conv_func **functions;                 /* Fonctions de conversion     */
    size_t func_count;                     /* Nombre de ces fonctions     */

};



/* ---------------------------------------------------------------------------------- */
/*                              CONVERSION DES ARGUMENTS                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = désignation de la variable de destination.            *
*                expr = expression dont la valeur est à assigner.             *
*                                                                             *
*  Description : Définit une conversion à partir d'une simple expression.     *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

conv_func *make_conv_from_expr(char *dest, arg_expr_t *expr)
{
    conv_func *result;                      /* Conversion à retourner      */

    result = (conv_func *)calloc(1, sizeof(conv_func));

    result->dest = make_string_lower(dest);

    result->is_expr = true;
    result->expr = expr;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = désignation de la variable de destination.            *
*                func = nom de la fonction assurant le calcul de valeur.      *
*                args = argument(s) à fournir à cette fonction.               *
*                                                                             *
*  Description : Définit une conversion à partir d'une function à appeler.    *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

conv_func *make_conv_from_func(char *dest, char *func, arg_list_t *args)
{
    conv_func *result;                      /* Conversion à retourner      */

    result = (conv_func *)calloc(1, sizeof(conv_func));

    result->dest = make_string_lower(dest);

    result->is_expr = false;
    result->name = func;
    result->args = args;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = éléments de conversion à supprimer de la mémoire.     *
*                                                                             *
*  Description : Libère de la mémoire une conversion enregistrée.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_conv_func(conv_func *func)
{
    if (func->is_expr)
        delete_arg_expr(func->expr);

    else
    {
        free(func->name);
        delete_arg_list(func->args);
    }

    free(func);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = fonction de conversion à consulter.                   *
*                                                                             *
*  Description : Indique la variable de destination d'une conversion.         *
*                                                                             *
*  Retour      : Désignation humaine de la variable de destination.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_conv_dest_name(const conv_func *func)
{
    return func->dest;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = fonction de conversion à consulter.                   *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                size = taille déterminée avec précision. [OUT]               *
*                                                                             *
*  Description : Détermine la taille en bits du résultat d'une fonction.      *
*                                                                             *
*  Retour      : true si la taille a pu être déterminée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool compute_conv_func_size(const conv_func *func, const coding_bits *bits, const conv_list *list, unsigned int *size)
{
    bool result;                            /* Bilan à retourner           */

    result = func->is_expr;

    if (result)
        result = compute_arg_expr_size(func->expr, bits, list, size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func  = fonction de conversion à manipuler.                  *
*                inter = note un résultat de conversion comme intermédiaire.  *
*                bits  = gestionnaire des bits d'encodage.                    *
*                list  = liste de l'ensemble des fonctions de conversion.     *
*                                                                             *
*  Description : Marque les champs utilisés par une fonction de conversion.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mark_conv_func(conv_func *func, bool inter, const coding_bits *bits, const conv_list *list)
{
    bool result;                            /* Bilan à remonter            */

    if (inter)
        func->used_as_inter = true;
    else
    {
        assert(!func->is_expr);
        func->used_as_op = true;
    }

    if (func->is_expr)
        result = ensure_arg_expr_content_fully_marked(func->expr, bits, list);
    else
        result = ensure_arg_list_content_fully_marked(func->args, bits, list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = fonction de conversion à consulter.                   *
*                                                                             *
*  Description : Indique si l'utilisation en intermédiaire est brute ou non.  *
*                                                                             *
*  Retour      : true si une variable brute est à manipuler, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_conv_func_raw_as_inter(const conv_func *func)
{
    bool result;                            /* Résultat à faire remonter   */

    if (func->is_expr)
        result = true;
    else
        result = (strcmp(func->name, "UInt") == 0);

    return result;

}




/******************************************************************************
*                                                                             *
*  Paramètres  : func  = fonction de conversion à manipuler.                  *
*                fd    = descripteur d'un flux ouvert en écriture.            *
*                inter = note un résultat de conversion comme intermédiaire.  *
*                                                                             *
*  Description : Imprime la désignation de la destination d'une conversion.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void write_conv_func(conv_func *func, int fd, bool inter)
{
    bool as_raw;                            /* Choix logique du format     */

    if (inter)
        as_raw = is_conv_func_raw_as_inter(func);
    else
        as_raw = false;

    if (as_raw)
        dprintf(fd, "val_%s", func->dest);
    else
        dprintf(fd, "op_%s", func->dest);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = fonction de conversion à manipuler.                   *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                bits = gestionnaire des bits d'encodage.                     *
*                list = liste de l'ensemble des fonctions de conversion.      *
*                tab  = décalage éventuel selon l'inclusion.                  *
*                                                                             *
*  Description : Déclare les variables associées à une fonction de conversion.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool declare_conv_func(conv_func *func, int fd, const coding_bits *bits, const conv_list *list, const char *tab)
{
    bool result;                            /* Bilan à remonter            */
    bool as_raw;                            /* Choix logique du format     */
    unsigned int wide;                      /* Taille des mots             */
    off_t start;                            /* Point de départ dans le code*/
    off_t end;                              /* Point d'arrivée dans le code*/

    assert(func->used_as_inter || func->used_as_op);

    /**
     * Si la fonction a déjà été définie lors d'un précédent besoin...
     */
    if (func->declared) return true;

    if (func->is_expr)
        result = ensure_arg_expr_content_fully_declared(func->expr, fd, bits, list, tab);

    else
        result = ensure_arg_list_content_fully_declared(func->args, fd, bits, list, tab);

    if (result)
    {
        if (func->used_as_inter)
        {
            as_raw = is_conv_func_raw_as_inter(func);

            /**
             * Si la variable intermédiaire n'est pas brute, deux cas de figure
             * sont possibles :
             *
             *    - la variable est un objet purement intermédiaire.
             *    - la variable est un object qui sera également utilisé en opérande.
             *
             * Dans les deux cas, on laisse la déclaration en tant qu'opérande
             * rédiger la déclaration car il s'agit de déclarations identiques.
             */

            if (as_raw)
            {
                wide = count_coded_bits(bits);

                start = lseek(fd, 0, SEEK_CUR);

                dprintf(fd, "\t%suint%u_t ", tab, wide);

                write_conv_func(func, fd, true);

                dprintf(fd, ";");

                end = lseek(fd, 0, SEEK_CUR);

                dprintf(fd, "%*s", (tab[0] == '\0' ? 42 : 39) - (int)(end - start), "/");
                dprintf(fd, "* Champ brut à décoder        */\n");

            }

        }

        if (func->used_as_op || (func->used_as_inter && !as_raw))
        {
            start = lseek(fd, 0, SEEK_CUR);

            dprintf(fd, "\t%sGArchOperand *", tab);

            write_conv_func(func, fd, false);

            dprintf(fd, ";");

            end = lseek(fd, 0, SEEK_CUR);

            dprintf(fd, "%*s", (tab[0] == '\0' ? 42 : 39) - (int)(end - start), "/");
            dprintf(fd, "* Opérande à intégrer         */\n");

        }

    }

    func->declared = result;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func     = fonction de conversion à manipuler.               *
*                fd       = descripteur d'un flux ouvert en écriture.         *
*                bits     = gestionnaire des bits d'encodage.                 *
*                list     = liste de l'ensemble des fonctions de conversion.  *
*                tab      = décalage éventuel selon l'inclusion.              *
*                optional = indique si l'opérande finale est optionnelle.     *
*                exit     = exprime le besoin d'une voie de sortie. [OUT]     *
*                                                                             *
*  Description : Définit les variables associées à une fonction de conversion.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_conv_func(conv_func *func, int fd, const coding_bits *bits, const conv_list *list, const char *tab, bool optional, bool *exit)
{
    bool result;                            /* Bilan à remonter            */
    bool as_raw;                            /* Choix logique du format     */

    /**
     * Si la fonction a déjà été définie lors d'un précédent besoin...
     */
    if (func->defined)
    {
        /**
         * La question de la propriété d'un opérande se pose si un opérande
         * est partagé entre plusieurs propriétaires.
         *
         * Le second usage de cet opérande, détecté ici, doit conduire à
         * une incrémentation de son compteur de références, via un appel à
         * g_object_ref(), si une instance GObject est manipulée.
         *
         * Or ce n'est jusqu'à présent jamais le cas. Les doubles usages sont
         * issus de constructions via les fonctions suivantes :
         *
         *   - UInt ;
         *   - SingleWordVector ;
         *   - DoubleWordVector.
         *
         * La mise en place d'une incrémentation des objets est donc reportée
         * au moment où elle sera utile.
         */

#ifndef NDEBUG

        if (!func->is_expr)
        {
            if (strcmp(func->name, "UInt") != 0
                && strcmp(func->name, "SingleWordVector") != 0
                && strcmp(func->name, "DoubleWordVector") != 0)
            {
                assert(false);
            }

        }

#endif

        return true;

    }

    if (func->is_expr)
        result = ensure_arg_expr_content_fully_defined(func->expr, fd, bits, list, tab, exit);
    else
        result = ensure_arg_list_content_fully_defined(func->args, fd, bits, list, tab, exit);

    if (result)
    {
        if (func->used_as_inter)
        {
            as_raw = is_conv_func_raw_as_inter(func);

            /**
             * Se référer au besoin aux commentaires de declare_conv_func().
             */

            if (as_raw)
            {
                dprintf(fd, "\t%s", tab);

                write_conv_func(func, fd, true);

                dprintf(fd, " = ");

                if (func->is_expr)
                    result = define_arg_expr(func->expr, fd, bits, list);

                else
                {
                    assert(strcmp(func->name, "UInt") == 0);
                    assert(get_arg_list_size(func->args) == 1);

                    result = define_arg_list(func->args, fd, bits, list);

                }

                dprintf(fd, ";\n");
                dprintf(fd, "\n");

            }

        }

        if (func->used_as_op || (func->used_as_inter && !as_raw))
        {
            dprintf(fd, "\t%s", tab);

            write_conv_func(func, fd, false);

            dprintf(fd, " = %s(", func->name);

            result = define_arg_list(func->args, fd, bits, list);

            dprintf(fd, ");\n");

            if (optional)
            {
                if (as_raw && !func->used_as_op)
                {
                    fprintf(stderr, "%s can not be optional and used as intermediate value at the same time!\n",
                            func->dest);

                    result = false;

                }

            }

            else
            {
                dprintf(fd, "\t%sif (", tab);

                write_conv_func(func, fd, false);

                dprintf(fd, " == NULL) goto bad_exit;\n");

                *exit = true;

            }

            dprintf(fd, "\n");

        }

        func->defined = result;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              ENSEMBLES DE CONVERSIONS                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouvelle liste vierge de fonctions de conversion.    *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

conv_list *create_conv_list(void)
{
    conv_list *result;                       /* Définition vierge à renvoyer*/

    result = (conv_list *)calloc(1, sizeof(conv_list));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de fonctions de conversion à supprimer.      *
*                                                                             *
*  Description : Supprime de la mémoire une de fonctions de conversion.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_conv_list(conv_list *list)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < list->func_count; i++)
        delete_conv_func(list->functions[i]);

    if (list->functions != NULL)
        free(list->functions);

    free(list);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de fonctions de conversion à compléter.         *
*                func = nom de la fonction assurant le calcul de valeur.      *
*                                                                             *
*  Description : Enregistre une function de conversion du brut à l'utile.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_conversion(conv_list *list, conv_func *func)
{
    list->functions = (conv_func **)realloc(list->functions, ++list->func_count * sizeof(conv_func *));

    list->functions[list->func_count - 1] = func;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de fonctions de conversion à consulter.         *
*                name = désignation humaine du champ à retrouver.             *
*                                                                             *
*  Description : Recherche un résultat précis dans une liste de fonctions.    *
*                                                                             *
*  Retour      : Structure associée au résulat trouvé ou NULL en cas d'échec. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

conv_func *find_named_conv_in_list(const conv_list *list, const char *name)
{
    conv_func *result;                      /* Fonction à retourner        */
    size_t i;                               /* Boucle de parcours          */
    const char *dest;                       /* Nom de variable existante   */

    result = NULL;

    for (i = 0; i < list->func_count && result == NULL; i++)
    {
        dest = get_conv_dest_name(list->functions[i]);

        if (strcmp(dest, name) == 0)
            result = list->functions[i];

    }

    return result;

}
