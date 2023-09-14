
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processors.c - enregistrement et fourniture des architectures supportées
 *
 * Copyright (C) 2015-2020 Cyrille Bagard
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


#include "processors.h"


#include <assert.h>
#include <malloc.h>
#include <pthread.h>
#include <string.h>


#include "../arch/instructions/raw.h"
#include "../arch/instructions/undefined.h"
#include "../arch/operands/immediate.h"
#include "../arch/operands/register.h"
#include "../arch/operands/target.h"



/* Cache des singletons d'opérandes */
static GSingletonFactory *__operands_factory = NULL;

/* Caractéristiques d'un processeur */
typedef struct _proc_t
{
    char *key;                              /* Clef pour un accès rapide   */
    GType type;                             /* Type à manipuler en interne */

} proc_t;


/* Mémorisation des types de processeurs enregistrés */
static proc_t *_processors_definitions = NULL;
static size_t _processors_definitions_count = 0;

/* Verrou pour des accès atomiques */
G_LOCK_DEFINE_STATIC(_pdef_access);


/* Retrouve l'enregistrement correspondant à une architecture. */
static proc_t *find_processor_by_key(const char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Assure l'enregistrement de types pour les caches à charger.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_arch_gtypes(void)
{
    g_type_ensure(G_TYPE_RAW_INSTRUCTION);
    g_type_ensure(G_TYPE_UNDEF_INSTRUCTION);

    g_type_ensure(G_TYPE_IMM_OPERAND);
    g_type_ensure(G_TYPE_REGISTER_OPERAND);
    g_type_ensure(G_TYPE_TARGET_OPERAND);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Met en place le fournisseur d'instances uniques d'opérandes. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_operands_factory(void)
{
    assert(__operands_factory == NULL);

    __operands_factory = g_singleton_factory_new();

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'usine à opérandes pour toutes les instructions.    *
*                                                                             *
*  Retour      : Producteur d'instances uniques.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSingletonFactory *get_operands_factory(void)
{
    GSingletonFactory *result;              /* Usine à renvoyer            */

    result = __operands_factory;

    g_object_ref(G_OBJECT(result));

    return result;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Supprime le fournisseur d'instances uniques d'opérandes.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_operands_factory(void)
{
    assert(__operands_factory != NULL);

    g_clear_object(&__operands_factory);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type GLib représentant le type à instancier.          *
*                                                                             *
*  Description : Enregistre un processeur pour une architecture donnée.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_processor_type(GType type)
{
    bool result;                            /* Bilan à retourner           */
    GArchProcessor *proc;                   /* Instance pour consultation  */
    char *key;                              /* Désignation associée        */
    proc_t *new;                            /* Nouvel élément à définir    */

    result = false;

    proc = g_object_new(type, NULL);

    key = g_arch_processor_get_key(proc);
    if (key == NULL) goto done;

    G_LOCK(_pdef_access);

    new = find_processor_by_key(key);

    if (new != NULL)
        free(key);

    else
    {
        _processors_definitions = realloc(_processors_definitions,
                                          ++_processors_definitions_count * sizeof(proc_t));

        new = &_processors_definitions[_processors_definitions_count - 1];

        new->key = key;
        new->type = type;

        result = true;

    }

    G_UNLOCK(_pdef_access);

 done:

    g_object_unref(G_OBJECT(proc));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge toutes les définitions de processeurs.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_processors_definitions(void)
{
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_pdef_access);

    for (i = 0; i < _processors_definitions_count; i++)
        free(_processors_definitions[i].key);

    if (_processors_definitions != NULL)
        free(_processors_definitions);

    _processors_definitions = NULL;
    _processors_definitions_count = 0;

    G_UNLOCK(_pdef_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : count = taille de la liste retournée. [OUT]                  *
*                                                                             *
*  Description : Fournit la liste des processeurs d'architecture disponibles. *
*                                                                             *
*  Retour      : Liste de nom technique des processeurs enregistrés.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char **get_all_processor_keys(size_t *count)
{
    char **result;                          /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_pdef_access);

    result = malloc(_processors_definitions_count * sizeof(char *));
    *count = _processors_definitions_count;

    for (i = 0; i < _processors_definitions_count; i++)
        result[i] = strdup(_processors_definitions[i].key);

    G_UNLOCK(_pdef_access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key = nom technique du processeur recherché.                 *
*                                                                             *
*  Description : Retrouve l'enregistrement correspondant à une architecture.  *
*                                                                             *
*  Retour      : Définition trouvée ou NULL en cas d'échec.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static proc_t *find_processor_by_key(const char *key)
{
    proc_t *result;                         /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    /**
     * Le verrou d'accès global doit être posé !
     */

    result = NULL;

    if (key != NULL)
        for (i = 0; i < _processors_definitions_count; i++)
            if (strcmp(_processors_definitions[i].key, key) == 0)
                result = &_processors_definitions[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key = nom technique du processeur recherché.                 *
*                                                                             *
*  Description : Fournit le processeur d'architecture correspondant à un nom. *
*                                                                             *
*  Retour      : Processeur d'architecture trouvé.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchProcessor *get_arch_processor_for_key(const char *key)
{
    GArchProcessor *result;                 /* Instance à retourner        */
    proc_t *def;                            /* Définition d'architecture   */

    G_LOCK(_pdef_access);

    def = find_processor_by_key(key);

    if (def == NULL)
        result = NULL;
    else
        result = g_object_new(def->type, NULL);

    G_UNLOCK(_pdef_access);

    return result;

}
