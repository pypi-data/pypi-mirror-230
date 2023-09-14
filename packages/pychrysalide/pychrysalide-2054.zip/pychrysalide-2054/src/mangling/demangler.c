
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.c - décodage des noms d'éléments
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


#include <assert.h>


#include "demangler-int.h"



/* Initialise la classe des décodeurs de désignations. */
static void g_compiler_demangler_class_init(GCompDemanglerClass *);

/* Initialise une instance de décodeur de désignations. */
static void g_compiler_demangler_init(GCompDemangler *);

/* Supprime toutes les références externes. */
static void g_compiler_demangler_dispose(GCompDemangler *);

/* Procède à la libération totale de la mémoire. */
static void g_compiler_demangler_finalize(GCompDemangler *);



/* Indique le type défini pour un décodeur de désignations. */
G_DEFINE_TYPE(GCompDemangler, g_compiler_demangler, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des décodeurs de désignations.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_compiler_demangler_class_init(GCompDemanglerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_compiler_demangler_dispose;
    object->finalize = (GObjectFinalizeFunc)g_compiler_demangler_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = instance à initialiser.                          *
*                                                                             *
*  Description : Initialise une instance de décodeur de désignations.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_compiler_demangler_init(GCompDemangler *demangler)
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

static void g_compiler_demangler_dispose(GCompDemangler *demangler)
{
    G_OBJECT_CLASS(g_compiler_demangler_parent_class)->dispose(G_OBJECT(demangler));

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

static void g_compiler_demangler_finalize(GCompDemangler *demangler)
{
    G_OBJECT_CLASS(g_compiler_demangler_parent_class)->finalize(G_OBJECT(demangler));

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

char *g_compiler_demangler_get_key(const GCompDemangler *demangler)
{
    char *result;                           /* Désignation à renvoyer      */
    GCompDemanglerClass *class;             /* Classe de l'instance        */

    class = G_COMP_DEMANGLER_GET_CLASS(demangler);

    if (class->get_key == NULL)
    {
        assert(false);
        result = NULL;
    }

    else
        result = class->get_key(demangler);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = décodeur à consulter pour le résultat.           *
*                                                                             *
*  Description : Indique le motif de séparation des espaces de noms.          *
*                                                                             *
*  Retour      : Chaîne de caractères.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_compiler_demangler_get_ns_separator(const GCompDemangler *demangler)
{
    const char *result;                     /* Chaîne à retourner          */

    result = G_COMP_DEMANGLER_GET_CLASS(demangler)->ns_sep;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = décodeur à solliciter pour l'opération.          *
*                desc      = chaîne de caractères à décoder.                  *
*                                                                             *
*  Description : Tente de décoder une chaîne de caractères donnée en type.    *
*                                                                             *
*  Retour      : Instance obtenue ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_compiler_demangler_decode_type(const GCompDemangler *demangler, const char *desc)
{
    GDataType *result;                      /* Construction à remonter     */
    GType ctx_type;                         /* Type de contexte adapté     */
    GDemanglingContext *context;            /* Espace de travail dédié     */

    ctx_type = G_COMP_DEMANGLER_GET_CLASS(demangler)->context_type;

    context = g_object_new(ctx_type, NULL);

    result = g_demangling_context_decode_type(context, desc);

    g_object_unref(G_OBJECT(context));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = décodeur à solliciter pour l'opération.          *
*                desc      = chaîne de caractères à décoder.                  *
*                                                                             *
*  Description : Tente de décoder une chaîne de caractères donnée en routine. *
*                                                                             *
*  Retour      : Instance obtenue ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_compiler_demangler_decode_routine(const GCompDemangler *demangler, const char *desc)
{
    GBinRoutine *result;                    /* Construction à remonter     */
    GType ctx_type;                         /* Type de contexte adapté     */
    GDemanglingContext *context;            /* Espace de travail dédié     */

    ctx_type = G_COMP_DEMANGLER_GET_CLASS(demangler)->context_type;

    context = g_object_new(ctx_type, NULL);

    result = g_demangling_context_decode_routine(context, desc);

    g_object_unref(G_OBJECT(context));

    return result;

}
