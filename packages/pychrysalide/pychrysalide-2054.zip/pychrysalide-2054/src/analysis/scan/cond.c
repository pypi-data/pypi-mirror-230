
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cond.c - expression conditionnelle validant la présence de motifs donnés
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "cond.h"


#include "cond-int.h"



/* Initialise la classe des recherches dans du binaire. */
static void g_match_condition_class_init(GMatchConditionClass *);

/* Initialise une instance de recherche dans du binaire. */
static void g_match_condition_init(GMatchCondition *);

/* Supprime toutes les références externes. */
static void g_match_condition_dispose(GMatchCondition *);

/* Procède à la libération totale de la mémoire. */
static void g_match_condition_finalize(GMatchCondition *);



/* Indique le type défini pour une expression de validation. */
G_DEFINE_TYPE(GMatchCondition, g_match_condition, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des recherches dans du binaire.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_condition_class_init(GMatchConditionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    klass->resolve = NULL;
    klass->resolve_as_num = NULL;
    klass->analyze = NULL;

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_match_condition_dispose;
    object->finalize = (GObjectFinalizeFunc)g_match_condition_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cond = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de recherche dans du binaire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_condition_init(GMatchCondition *cond)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cond = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_condition_dispose(GMatchCondition *cond)
{
    G_OBJECT_CLASS(g_match_condition_parent_class)->dispose(G_OBJECT(cond));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cond = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_condition_finalize(GMatchCondition *cond)
{
    G_OBJECT_CLASS(g_match_condition_parent_class)->finalize(G_OBJECT(cond));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cond = condition à consulter.                                *
*                                                                             *
*  Description : Indique le statut d'une condition de validation.             *
*                                                                             *
*  Retour      : Validation de la condition considérée.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_match_condition_resolve(const GMatchCondition *cond)
{
    bool result;                            /* Bilan à retourner           */
    GMatchConditionClass *class;            /* Classe à activer            */
    unsigned long long number;              /* Valeur à considérer         */

    class = G_MATCH_CONDITION_GET_CLASS(cond);

    if (class->resolve != NULL)
        result = class->resolve(cond);

    else if (class->resolve_as_num != NULL)
    {
        number = class->resolve_as_num(cond);
        result = (number > 0);
    }

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cond = condition à consulter.                                *
*                                                                             *
*  Description : Indique le statut d'une condition de validation.             *
*                                                                             *
*  Retour      : Forme numérique de la condition considérée pour validation.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned long long g_match_condition_resolve_as_number(const GMatchCondition *cond)
{
    unsigned long long result;              /* Valeur à retourner          */
    GMatchConditionClass *class;            /* Classe à activer            */

    class = G_MATCH_CONDITION_GET_CLASS(cond);

    result = class->resolve_as_num(cond);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cond = condition à considérer.                               *
*                data = données binaires brutes à considérer.                 *
*                size = quantité de ces données.                              *
*                pos  = position du point d'étude courant.                    *
*                full = force une recherche pleine et entière.                *
*                                                                             *
*  Description : Avance vers la validation d'une condition, si besoin est.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_match_condition_analyze(const GMatchCondition *cond, const bin_t *data, phys_t size, phys_t pos, bool full)
{
    GMatchConditionClass *class;            /* Classe à activer            */

    class = G_MATCH_CONDITION_GET_CLASS(cond);

    class->analyze(cond, data, size, pos, full);

}
