
/* Chrysalide - Outil d'analyse de fichiers binaires
 * field.c - manipulation des champs de classe du format DEX
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


#include "field.h"


#include "dex-int.h"
#include "pool.h"



/* Champ d'une classe Dex (instance) */
struct _GDexField
{
    GObject parent;                         /* A laisser en premier        */

    GBinVariable *variable;                 /* Représentation interne      */

    encoded_field info;                     /* Propriétés de la méthode    */

};

/* Champ d'une classe Dex (classe) */
struct _GDexFieldClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Procède à l'initialisation des champs de classe Dex. */
static void g_dex_field_class_init(GDexFieldClass *);

/* Procède à l'initialisation d'un champ de classe Dex. */
static void g_dex_field_init(GDexField *);

/* Supprime toutes les références externes. */
static void g_dex_field_dispose(GDexField *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_field_finalize(GDexField *);



/* Détermine le type d'une fielde issue du code source. */
G_DEFINE_TYPE(GDexField, g_dex_field, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GLib à initialiser.              *
*                                                                             *
*  Description : Procède à l'initialisation des champs de classe Dex.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_field_class_init(GDexFieldClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_field_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_field_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = composant GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation d'un champ de classe Dex.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_field_init(GDexField *field)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_field_dispose(GDexField *field)
{
    if (field->variable != NULL)
        g_object_unref(G_OBJECT(field->variable));

    G_OBJECT_CLASS(g_dex_field_parent_class)->dispose(G_OBJECT(field));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_field_finalize(GDexField *field)
{
    G_OBJECT_CLASS(g_dex_field_parent_class)->finalize(G_OBJECT(field));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = représentation interne du format DEX à consulter.   *
*                seed   = graine des informations à extraire.                 *
*                last   = dernier indice utilisé (à mettre à jour). [OUT]     *
*                                                                             *
*  Description : Crée une nouvelle représentation de champ de classe.         *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexField *g_dex_field_new(GDexFormat *format, const encoded_field *seed, uleb128_t *last)
{
    GDexField *result;                      /* Composant à retourner       */
    GDexPool *pool;                         /* Table de ressources         */
    GBinVariable *variable;                 /* Variable de représentation  */

    *last += seed->field_idx_diff;

    pool = g_dex_format_get_pool(format);

    variable = g_dex_pool_get_field(pool, *last);

    g_object_unref(G_OBJECT(pool));

    if (variable == NULL)
        return NULL;

    result = g_object_new(G_TYPE_DEX_FIELD, NULL);

    result->variable = variable;

    result->info = *seed;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = représentation interne du champ à consulter.         *
*                                                                             *
*  Description : Fournit les indications Dex concernant le champ de classe.   *
*                                                                             *
*  Retour      : Données brutes du binaire.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const encoded_field *g_dex_field_get_dex_info(const GDexField *field)
{
    return &field->info;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = représentation interne du format DEX à consulter.    *
*                                                                             *
*  Description : Fournit la variable Chrysalide correspondant au champ.       *
*                                                                             *
*  Retour      : Instance de routine mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinVariable *g_dex_field_get_variable(const GDexField *field)
{
    GBinVariable *result;                   /* Instance à retourner        */

    result = field->variable;

    g_object_ref(G_OBJECT(result));

    return result;

}
