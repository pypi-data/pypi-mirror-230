
/* Chrysalide - Outil d'analyse de fichiers binaires
 * access.c - accès aux modules Python en cours d'enregistrement
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


#include "access.h"


#include <stdlib.h>
#include <string.h>


#include <common/sort.h>



/* Lien entre un module et sa désignation */
typedef struct _module_access
{
    const char *path;                       /* Chemin d'accès              */
    PyObject *mod;                          /* Module Python en place      */

} module_access;


/* Conservation de tous les accès */
static module_access *_pychrysalide_modules = NULL;
static size_t _pychrysalide_count = 0;


/* Effectue la comparaison entre deux accès à des modules. */
static int compare_python_module_accesses(const module_access *, const module_access *);



/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier accès à analyser.                                *
*                b = second accès à analyser.                                 *
*                                                                             *
*  Description : Effectue la comparaison entre deux accès à des modules.      *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_python_module_accesses(const module_access *a, const module_access *b)
{
    int result;                             /* Bilan à retourner           */

    result = strcmp(a->path, b->path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'accès à un module Python.                    *
*                mod  = module Python en question.                            *
*                                                                             *
*  Description : Enregistre une référence à un module Python en chargement.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_access_to_python_module(const char *path, PyObject *mod)
{
    module_access access;                   /* Nouvel enregistrement       */

    access.path = path;
    access.mod = mod;

    _pychrysalide_modules = qinsert(_pychrysalide_modules, &_pychrysalide_count,
                                    sizeof(module_access), (__compar_fn_t)compare_python_module_accesses,
                                    &access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'accès à un module Python.                    *
*                                                                             *
*  Description : Fournit la référence à un module Python défini.              *
*                                                                             *
*  Retour      : Module Python correspondant, ou NULL si aucun de trouvé.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *get_access_to_python_module(const char *path)
{
    PyObject *result;                       /* Référence à renvoyer        */
    module_access key;                      /* Définition à retrouver      */
    module_access *access;                  /* Accès trouvé à consulter    */

    key.path = path;

    access = bsearch(&key, _pychrysalide_modules, _pychrysalide_count,
                     sizeof(module_access), (__compar_fn_t)compare_python_module_accesses);

    if (access != NULL)
        result = access->mod;
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Supprime tous les accès rapide aux modules Python.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clear_all_accesses_to_python_modules(void)
{
    if (_pychrysalide_modules != NULL)
        free(_pychrysalide_modules);

}
