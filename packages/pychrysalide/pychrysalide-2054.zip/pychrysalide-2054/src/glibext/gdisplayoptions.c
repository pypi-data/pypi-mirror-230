
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gdisplayoptions.h - options de rendus des lignes de code
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


#include "gdisplayoptions.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "chrysamarshal.h"



/* Options de représentation (instance) */
struct _GDisplayOptions
{
    GObject parent;                         /* A laisser en premier        */

    char **names;                           /* Désignations des options    */
    bool *values;                           /* Valeurs des options         */
    size_t count;                           /* Nombre de ces options       */

};

/* Options de représentation (classe) */
struct _GDisplayOptionsClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* value_changed) (const GDisplayOptions *, gsize, gboolean);

};


/* Initialise la classe des options pour le rendu des lignes. */
static void g_display_options_class_init(GDisplayOptionsClass *);

/* Initialise une instance d'options pour le rendu des lignes. */
static void g_display_options_init(GDisplayOptions *);

/* Supprime toutes les références externes. */
static void g_display_options_dispose(GDisplayOptions *);

/* Procède à la libération totale de la mémoire. */
static void g_display_options_finalize(GDisplayOptions *);



/* Indique le type défini pour une ligne de représentation. */
G_DEFINE_TYPE(GDisplayOptions, g_display_options, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des options pour le rendu des lignes.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_display_options_class_init(GDisplayOptionsClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_display_options_dispose;
    object->finalize = (GObjectFinalizeFunc)g_display_options_finalize;

    /**
     * Note : il n'existe pas de G_TYPE_GSIZE.
     *
     * Or la documentation précise :
     *
     *    typedef unsigned long gsize;
     *
     */

    g_signal_new("value-changed",
                 G_TYPE_DISPLAY_OPTIONS,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GDisplayOptionsClass, value_changed),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__ULONG_BOOLEAN,
                 G_TYPE_NONE, 2, G_TYPE_ULONG, G_TYPE_BOOLEAN);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'options pour le rendu des lignes.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_display_options_init(GDisplayOptions *options)
{
    options->names = NULL;
    options->values = NULL;
    options->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_display_options_dispose(GDisplayOptions *options)
{
    G_OBJECT_CLASS(g_display_options_parent_class)->dispose(G_OBJECT(options));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_display_options_finalize(GDisplayOptions *options)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < options->count; i++)
        free(options->names[i]);

    if (options->names != NULL)
        free(options->names);

    if (options->values != NULL)
        free(options->values);

    G_OBJECT_CLASS(g_display_options_parent_class)->finalize(G_OBJECT(options));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un groupe d'options pour le rendu des lignes.           *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDisplayOptions *g_display_options_new(void)
{
    GDisplayOptions *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_DISPLAY_OPTIONS, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : template = modèle de groupe à copier.                        *
*                                                                             *
*  Description : Copie un groupe d'options pour le rendu des lignes.          *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDisplayOptions *g_display_options_dup(const GDisplayOptions *template)
{
    GDisplayOptions *result;                /* Structure à retourner       */
    size_t count;                           /* Nombre d'options à copier   */
    size_t i;                               /* Boucle de parcours          */

    result = g_display_options_new();

    count = g_display_options_count(template);

    for (i = 0; i < count; i++)
        g_display_options_add(result, template->names[i], template->values[i]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = options à consulter.                               *
*                                                                             *
*  Description : Dénombre la quantité d'options représentées.                 *
*                                                                             *
*  Retour      : Quantité positive ou nulle.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_display_options_count(const GDisplayOptions *options)
{
    size_t result;                          /* Quantité à retourner        */

    result = options->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = options à compléter.                               *
*                name    = désignation humaine de la nouvelle option.         *
*                value   = valeur initiale de l'option à ajouter.             *
*                                                                             *
*  Description : Ajoute une nouvelle option à l'ensemble.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_display_options_add(GDisplayOptions *options, const char *name, bool value)
{
    options->count++;

    options->names = (char **)realloc(options->names, options->count * sizeof(char *));
    options->values = (bool *)realloc(options->values, options->count * sizeof(bool));

    options->names[options->count - 1] = strdup(name);
    options->values[options->count - 1] = value;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = options à consulter.                               *
*                index   = indice de l'option concernée.                      *
*                                                                             *
*  Description : Fournit la désignation d'une option donnée.                  *
*                                                                             *
*  Retour      : Nom humainement lisible.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_display_options_get_name(const GDisplayOptions *options, size_t index)
{
    char *result;                           /* Désignation à retourner     */

    assert(index < options->count);

    if (index < options->count)
        result = options->names[index];

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = options à consulter.                               *
*                index   = indice de l'option concernée.                      *
*                                                                             *
*  Description : Fournit la valeur d'une option donnée.                       *
*                                                                             *
*  Retour      : Valeur attribuée.                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_display_options_get(const GDisplayOptions *options, size_t index)
{
    bool result;                            /* Valeur à renvoyer           */

    assert(index < options->count);

    if (index < options->count)
        result = options->values[index];

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = options à mettre à jour.                           *
*                index   = indice de l'option concernée.                      *
*                value   = nouvelle valeur à intégrer.                        *
*                                                                             *
*  Description : Définit la valeur d'une option donnée.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_display_options_set(GDisplayOptions *options, size_t index, bool value)
{
    bool changed;                           /* Note un changement          */

    assert(index < options->count);

    if (index < options->count)
    {
        changed = (options->values[index] != value);
        options->values[index] = value;
    }

    else
        changed = false;

    if (changed)
        g_signal_emit_by_name(options, "value-changed", index, value);

}
