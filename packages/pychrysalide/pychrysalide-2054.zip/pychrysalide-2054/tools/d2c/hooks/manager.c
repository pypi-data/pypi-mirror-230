
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - prise en compte d'une syntaxe du langage d'assemblage
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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



/* Paramèter d'une fonction de renvoi */
typedef struct _instr_func
{
    char *type;                             /* Type de fonction définie    */
    char *name;                             /* Désignation humaine         */

} instr_func;

/* Liste des fonctions de renvoi pour une instruction */
struct _instr_hooks
{
    instr_func *funcs;                      /* Liste de fonctions présentes*/
    size_t func_count;                      /* Taille de cette liste       */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une liste de fonctions à lier à une instruction.        *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_hooks *create_instr_hooks(void)
{
    instr_hooks *result;                    /* Définition vierge à renvoyer*/

    result = (instr_hooks *)calloc(1, sizeof(instr_hooks));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hooks = gestionnaire d'un ensemble de fonctions associées.   *
*                                                                             *
*  Description : Supprime de la mémoire une liste de fonctions liées.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_instr_hooks(instr_hooks *hooks)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < hooks->func_count; i++)
    {
        free(hooks->funcs[i].type);
        free(hooks->funcs[i].name);
    }

    if (hooks->funcs != NULL)
        free(hooks->funcs);

    free(hooks);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hooks = gestionnaire d'un ensemble de fonctions associées.   *
*                type  = type de fonction à enregistrer pour une instruction. *
*                name  = désignation de la fonction à associer.               *
*                                                                             *
*  Description : Enregistre l'utilité d'une fonction pour une instruction.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_hook_function(instr_hooks *hooks, char *type, char *name)
{
    instr_func *func;                       /* Nouvelle prise en compte    */

    hooks->funcs = (instr_func *)realloc(hooks->funcs, ++hooks->func_count * sizeof(instr_func));

    func = &hooks->funcs[hooks->func_count - 1];

    func->type = make_string_upper(type);
    func->name = strdup(name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hooks = gestionnaire d'un ensemble de fonctions associées.   *
*                                                                             *
*  Description : Indique si des décrochages sont définis.                     *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_hook_functions(const instr_hooks *hooks)
{
    bool result;                            /* Bilan à retourner           */

    result = (hooks->func_count > 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hooks = gestionnaire d'un ensemble de fonctions associées.   *
*                fd    = descripteur d'un flux ouvert en écriture.            *
*                                                                             *
*  Description : Imprime une liste de décrochages spécifiés.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_hook_functions(const instr_hooks *hooks, int fd)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    const instr_func *func;                 /* Nouvelle prise en compte    */

    static const char *hook_types[] = {
        "FETCH",
        "LINK",
        "POST"
    };

    const instr_func *find_hook_by_name(const instr_hooks *list, const char *type)
    {
        const instr_func *hook;             /* Trouvaille à retourner      */
        size_t k;                           /* Boucle de parcours #2       */

        hook = NULL;

        for (k = 0; k < list->func_count && hook == NULL; k++)
            if (strcmp(list->funcs[k].type, type) == 0)
                hook = &list->funcs[k];

        return hook;

    }

    result = true;

    assert(has_hook_functions(hooks));

    for (i = 0; i < (sizeof(hook_types) / sizeof(hook_types[0])); i++)
    {
        func = find_hook_by_name(hooks, hook_types[i]);

        dprintf(fd, "\t\t[IPH_%s] = (instr_hook_fc)%s,\n", hook_types[i], func != NULL ? func->name : "NULL");

    }

    return result;

}
