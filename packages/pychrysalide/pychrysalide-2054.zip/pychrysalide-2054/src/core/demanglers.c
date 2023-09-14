
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demanglers.c - enregistrement et fourniture des décodeurs proprosés
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "demanglers.h"


#include <string.h>



/* Caractéristiques d'un processeur */
typedef struct _demangler_t
{
    char *key;                              /* Clef pour un accès rapide   */
    GType type;                             /* Type à manipuler en interne */

} demangler_t;


/* Mémorisation des types de décodeurs enregistrés */
static demangler_t *_demanglers_definitions = NULL;
static size_t _demanglers_definitions_count = 0;

/* Verrou pour des accès atomiques */
G_LOCK_DEFINE_STATIC(_ddef_access);


/* Retrouve l'enregistrement correspondant à un décodeur. */
static demangler_t *find_demangler_by_key(const char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type GLib représentant le type à instancier.          *
*                                                                             *
*  Description : Enregistre un décodeur répondant à une appellation donnée.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_demangler_type(GType type)
{
    bool result;                            /* Bilan à retourner           */
    GCompDemangler *demangler;              /* Instance pour consultation  */
    char *key;                              /* Désignation associée        */
    demangler_t *new;                       /* Nouvel élément à définir    */

    result = false;

    demangler = g_object_new(type, NULL);

    key = g_compiler_demangler_get_key(demangler);
    if (key == NULL) goto done;

    G_LOCK(_ddef_access);

    new = find_demangler_by_key(key);

    if (new != NULL)
        free(key);

    else
    {
        _demanglers_definitions = (demangler_t *)realloc(_demanglers_definitions,
                                                         ++_demanglers_definitions_count * sizeof(demangler_t));

        new = &_demanglers_definitions[_demanglers_definitions_count - 1];

        new->key = strdup(key);
        new->type = type;

        result = true;

    }

    G_UNLOCK(_ddef_access);

 done:

    g_object_unref(G_OBJECT(demangler));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge toutes les définitions de décodeurs.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_demanglers_definitions(void)
{
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_ddef_access);

    for (i = 0; i < _demanglers_definitions_count; i++)
        free(_demanglers_definitions[i].key);

    if (_demanglers_definitions != NULL)
        free(_demanglers_definitions);

    _demanglers_definitions = NULL;
    _demanglers_definitions_count = 0;

    G_UNLOCK(_ddef_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key = nom technique du décodeur recherché.                   *
*                                                                             *
*  Description : Retrouve l'enregistrement correspondant à un décodeur.       *
*                                                                             *
*  Retour      : Définition trouvée ou NULL en cas d'échec.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static demangler_t *find_demangler_by_key(const char *key)
{
    demangler_t *result;                         /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    /**
     * Le verrou d'accès global doit être posé !
     */

    result = NULL;

    if (key != NULL)
        for (i = 0; i < _demanglers_definitions_count; i++)
            if (strcmp(_demanglers_definitions[i].key, key) == 0)
                result = &_demanglers_definitions[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key = nom technique du décodeur recherché.                   *
*                                                                             *
*  Description : Fournit le décodeur de désignations correspondant à un type. *
*                                                                             *
*  Retour      : Décodeur trouvé et mis en place ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCompDemangler *get_compiler_demangler_for_key(const char *key)
{
    GCompDemangler *result;                 /* Instance à retourner        */
    demangler_t *def;                       /* Définition de décodeur      */

    G_LOCK(_ddef_access);

    def = find_demangler_by_key(key);

    if (def == NULL)
        result = NULL;
    else
        result = g_object_new(def->type, NULL);

    G_UNLOCK(_ddef_access);

    return result;

}
