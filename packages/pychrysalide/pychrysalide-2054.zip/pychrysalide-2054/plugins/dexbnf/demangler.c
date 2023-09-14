
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.c - décodage des noms d'éléments Dex
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


#include "demangler.h"


#include <mangling/demangler-int.h>


#include "context.h"



/* Décodeur de désignations Dex (instance) */
struct _GDexDemangler
{
    GCompDemangler parent;                  /* A laisser en premier        */

};

/* Décodeur de désignations Dex (classe) */
struct _GDexDemanglerClass
{
    GCompDemanglerClass parent;             /* A laisser en premier        */

};


/* Initialise la classe des décodeurs de désignations. */
static void g_dex_demangler_class_init(GDexDemanglerClass *);

/* Initialise une instance de décodeur de désignations. */
static void g_dex_demangler_init(GDexDemangler *);

/* Supprime toutes les références externes. */
static void g_dex_demangler_dispose(GDexDemangler *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_demangler_finalize(GDexDemangler *);

/* Fournit la désignation interne du décodeur de désignations. */
static char *g_dex_demangler_get_key(const GDexDemangler *);



/* Indique le type défini pour un décodeur de désignations. */
G_DEFINE_TYPE(GDexDemangler, g_dex_demangler, G_TYPE_COMP_DEMANGLER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des décodeurs de désignations Dex.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangler_class_init(GDexDemanglerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GCompDemanglerClass *demangler;         /* Version parente basique     */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_demangler_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_demangler_finalize;

    demangler = G_COMP_DEMANGLER_CLASS(klass);

    demangler->get_key = (get_demangler_key_fc)g_dex_demangler_get_key;
    demangler->can_demangle = (can_be_demangled_fc)NULL;

    demangler->ns_sep = ".";
    demangler->context_type = G_TYPE_DEX_DEMANGLING;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = instance à initialiser.                          *
*                                                                             *
*  Description : Initialise une instance de décodeur de désignations Dex.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangler_init(GDexDemangler *demangler)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangler_dispose(GDexDemangler *demangler)
{
    G_OBJECT_CLASS(g_dex_demangler_parent_class)->dispose(G_OBJECT(demangler));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangler_finalize(GDexDemangler *demangler)
{
    G_OBJECT_CLASS(g_dex_demangler_parent_class)->finalize(G_OBJECT(demangler));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Met en place un nouveau décodeur de symboles pour Dex.       *
*                                                                             *
*  Retour      : Instance obtenue ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCompDemangler *g_dex_demangler_new(void)
{
    GDexDemangler *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_DEX_DEMANGLER, NULL);

    return G_COMP_DEMANGLER(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = décodeur à consulter.                            *
*                                                                             *
*  Description : Fournit la désignation interne du décodeur de désignations.  *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_dex_demangler_get_key(const GDexDemangler *demangler)
{
    char *result;                           /* Désignation à renvoyer      */

    result = strdup("dex");

    return result;

}
