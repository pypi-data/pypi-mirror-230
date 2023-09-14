
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - fourniture de contexte aux phases de décodage Dex
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


#include "context.h"


#include <mangling/context-int.h>


#include "shorty.h"
#include "type.h"



/* Contexte de décodage Dex (instance) */
struct _GDexDemangling
{
    GDemanglingContext parent;              /* A laisser en premier        */

};

/* Contexte de décodage Dex (classe) */
struct _GDexDemanglingClass
{
    GDemanglingContextClass parent;         /* A laisser en premier        */

};


/* Initialise la classe des contextes de décodage. */
static void g_dex_demangling_class_init(GDexDemanglingClass *);

/* Initialise une instance de contexte pour décodage. */
static void g_dex_demangling_init(GDexDemangling *);

/* Supprime toutes les références externes. */
static void g_dex_demangling_dispose(GDexDemangling *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_demangling_finalize(GDexDemangling *);

/* Décode une définition de type pour Dex. */
static GDataType *g_dex_demangling_decode_type(GDexDemangling *);

/* Décode une définition de routine pour Dex. */
static GBinRoutine *g_dex_demangling_decode_routine(GDexDemangling *);



/* Indique le type défini pour un contexte de décodage. */
G_DEFINE_TYPE(GDexDemangling, g_dex_demangling, G_TYPE_DEMANGLING_CONTEXT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de décodage.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangling_class_init(GDexDemanglingClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDemanglingContextClass *context;       /* Version de base du contexte */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_demangling_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_demangling_finalize;

    context = G_DEMANGLING_CONTEXT_CLASS(klass);

    context->decode_type = (decode_type_fc)g_dex_demangling_decode_type;
    context->decode_routine = (decode_routine_fc)g_dex_demangling_decode_routine;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contexte pour décodage.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangling_init(GDexDemangling *context)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangling_dispose(GDexDemangling *context)
{
    G_OBJECT_CLASS(g_dex_demangling_parent_class)->dispose(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_demangling_finalize(GDexDemangling *context)
{
    G_OBJECT_CLASS(g_dex_demangling_parent_class)->finalize(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                                                                             *
*  Description : Décode une définition de type pour Dex.                      *
*                                                                             *
*  Retour      : Nouvelle instance créée ou NULL en cas d'erreur fatale.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *g_dex_demangling_decode_type(GDexDemangling *context)
{
    GDataType *result;                      /* Type construit à retourner  */
    GDemanglingContext *base;               /* Autre version du contexte   */

    base = G_DEMANGLING_CONTEXT(context);

    result = dtd_type_descriptor(&base->buffer);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                                                                             *
*  Description : Décode une définition de routine pour Dex.                   *
*                                                                             *
*  Retour      : Nouvelle instance créée ou NULL en cas d'erreur fatale.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinRoutine *g_dex_demangling_decode_routine(GDexDemangling *context)
{
    GBinRoutine *result;                    /* Routine en place à retourner*/
    GDemanglingContext *base;               /* Autre version du contexte   */

    base = G_DEMANGLING_CONTEXT(context);

    result = dsd_shorty_descriptor(&base->buffer);

    return result;

}
