
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cattribs.c - rassemblement des attributs utiles au chargement d'un contenu binaire
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "cattribs.h"


#include <malloc.h>
#include <string.h>


#include "../glibext/configuration.h"



/* Ensemble d'attributs pour contenu binaire (instance) */
struct _GContentAttributes
{
    GObject parent;                         /* A laisser en premier        */

    GGenConfig **configs;                   /* Paramètres par niveaux      */
    size_t count;                           /* Quantité de ces niveaux     */

};

/* Ensemble d'attributs pour contenu binaire (classe) */
struct _GContentAttributesClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des ensembles d'attributs pour contenus. */
static void g_content_attributes_class_init(GContentAttributesClass *);

/* Initialise un ensemble d'attributs pour contenu binaire. */
static void g_content_attributes_init(GContentAttributes *);

/* Supprime toutes les références externes. */
static void g_content_attributes_dispose(GContentAttributes *);

/* Procède à la libération totale de la mémoire. */
static void g_content_attributes_finalize(GContentAttributes *);



/* Indique le type défini pour un ensemble d'attributs de contenu binaire. */
G_DEFINE_TYPE(GContentAttributes, g_content_attributes, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des ensembles d'attributs pour contenus.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_attributes_class_init(GContentAttributesClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_content_attributes_dispose;
    object->finalize = (GObjectFinalizeFunc)g_content_attributes_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un ensemble d'attributs pour contenu binaire.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_attributes_init(GContentAttributes *attribs)
{
    attribs->configs = malloc(sizeof(GGenConfig *));
    attribs->count = 1;

    attribs->configs[0] = g_generic_config_new();

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attribs = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_attributes_dispose(GContentAttributes *attribs)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < attribs->count; i++)
        g_clear_object(&attribs->configs[i]);

    G_OBJECT_CLASS(g_content_attributes_parent_class)->dispose(G_OBJECT(attribs));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attribs = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_attributes_finalize(GContentAttributes *attribs)
{
    free(attribs->configs);

    G_OBJECT_CLASS(g_content_attributes_parent_class)->finalize(G_OBJECT(attribs));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path     = chemin d'accès à un contenu à charger.            *
*                filename = nom de fichier embarqué.                          *
*                                                                             *
*  Description : Construit un ensemble d'attribut pour contenu binaire.       *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentAttributes *g_content_attributes_new(const char *path, char **filename)
{
    GContentAttributes *result;             /* Adresse à retourner         */
    GGenConfig *config;                     /* Niveau de config. courant   */
    const char *iter;                       /* Boucle de parcours          */
    const char *next;                       /* Prochain marqueur rencontré */
    char *part;                             /* Clef et sa valeur           */
    char *eq;                               /* Signe '=' rencontré         */

    if (filename != NULL)
        *filename = NULL;

    result = g_object_new(G_TYPE_CONTENT_ATTRIBUTES, NULL);

    iter = strchr(path, '&');

    if (iter == NULL)
    {
        if (strlen(path) && filename != NULL)
            *filename = strdup(path);
    }

    else
    {
        if (iter != path)
        {
            if (filename != NULL)
                *filename = strndup(path, iter - path);
        }

        config = result->configs[0];

        do
        {
            iter++;

            next = strchr(iter, '&');

            if (next == NULL)
                next = path + strlen(path);

            /* Présence de deux '&' consécutifs */
            if (iter == next)
            {
                result->configs = realloc(result->configs, ++result->count * sizeof(GGenConfig *));

                result->configs[result->count - 1] = g_generic_config_new();

                config = result->configs[result->count - 1];

            }

            /* Traitement d'une nouvelle combinaison */
            else
            {
                part = strndup(iter, next - iter);

                eq = strchr(part, '=');

                if (eq != NULL)
                {
                    *eq = '\0';

                    if (eq[1] != '\0')
                        g_generic_config_create_or_udpdate_param(config, part, CPT_STRING, NULL, eq + 1);

                }

                free(part);

            }

            iter = strchr(iter, '&');

        }
        while (iter != NULL);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attribs = ensemble d'attributs de contenu à consulter.       *
*                count   = taille de la liste de clefs renvoyées. [OUT]       *
*                                                                             *
*  Description : Fournit l'ensemble des clefs d'un ensemble d'attributs.      *
*                                                                             *
*  Retour      : Liste de clefs des attributes conservés dans l'ensemble.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char **g_content_attributes_get_keys(const GContentAttributes *attribs, size_t *count)
{
    const char **result;                    /* Liste à retourner           */
    GList *list;                            /* Liste de paramètres         */
    GList *iter;                            /* Boucle de parcours          */
    GCfgParam *param;                       /* Paramètre d'un ensemble     */
    const char *key;                        /* Clef d'un paramètre         */

    result = NULL;
    *count = 0;

    g_generic_config_rlock(attribs->configs[0]);

    list = g_generic_config_list_params(attribs->configs[0]);

    for (iter = g_list_first(list); iter != NULL; iter = g_list_next(iter))
    {
        param = G_CFG_PARAM(iter->data);

        key = g_config_param_get_path(param);

        result = realloc(result, ++(*count) * sizeof(char *));

        result[*count - 1] = strdup(key);

    }

    g_generic_config_runlock(attribs->configs[0]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attribs = ensemble d'attributs de contenu à consulter.       *
*                key     = désignation de l'attribut visé par la procédure.   *
*                                                                             *
*  Description : Indique la valeur d'un attribut appartenant à un ensemble.   *
*                                                                             *
*  Retour      : Valeur de l'attribut recherché, s'il a été trouvé.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_content_attributes_get_value(const GContentAttributes *attribs, const char *key)
{
    const char *result;                     /* Trouvaille à retourner      */
    bool status;

    status = g_generic_config_get_value(attribs->configs[0], key, &result);

    if (!status)
        result = NULL;

    return result;

}
