
/* Chrysalide - Outil d'analyse de fichiers binaires
 * empty.c - conservation d'une correspondance entre attribut et binaire
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


#include "empty.h"


#include <assert.h>
#include <stdarg.h>
#include <string.h>


#include "empty-int.h"



/* ------------------ DEFINITION D'UNE ZONE DE CORRESPONDANCE VIDE ------------------ */


/* Initialise la classe des zones de correspondance vides. */
static void g_record_empty_class_init(GRecordEmptyClass *);

/* Initialise une zone de correspondance vide. */
static void g_record_empty_init(GRecordEmpty *);

/* Supprime toutes les références externes. */
static void g_record_empty_dispose(GRecordEmpty *);

/* Procède à la libération totale de la mémoire. */
static void g_record_empty_finalize(GRecordEmpty *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Calcule ou fournit la zone couverte par une correspondance. */
static void g_record_empty_get_range(const GRecordEmpty *, mrange_t *);



/* ---------------------------------------------------------------------------------- */
/*                    DEFINITION D'UNE ZONE DE CORRESPONDANCE VIDE                    */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une zone de correspondance vide. */
G_DEFINE_TYPE(GRecordEmpty, g_record_empty, G_TYPE_MATCH_RECORD);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des zones de correspondance vides.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_empty_class_init(GRecordEmptyClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GMatchRecordClass *record;              /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_record_empty_dispose;
    object->finalize = (GObjectFinalizeFunc)g_record_empty_finalize;

    record = G_MATCH_RECORD_CLASS(klass);

    record->get_range = (get_record_range_fc)g_record_empty_get_range;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : empty = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une zone de correspondance vide.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_empty_init(GRecordEmpty *empty)
{
    init_vmpa(&empty->pos, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : empty = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_empty_dispose(GRecordEmpty *empty)
{
    G_OBJECT_CLASS(g_record_empty_parent_class)->dispose(G_OBJECT(empty));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : empty = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_empty_finalize(GRecordEmpty *empty)
{
    G_OBJECT_CLASS(g_record_empty_parent_class)->finalize(G_OBJECT(empty));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parser  = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                pos     = emplacement de la zone vide à construire.          *
*                                                                             *
*  Description : Crée une zone de correspondance vide à une position donnée.  *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRecordEmpty *g_record_empty_new(GKaitaiParser *parser, GBinContent *content, const vmpa2t *pos)
{
    GRecordEmpty *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_RECORD_EMPTY, NULL);

    if (!g_record_empty_create(result, parser, content, pos))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : empty   = correspondance à initialiser pleinement.           *
*                parser  = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                pos     = emplacement de la zone vide à construire.          *
*                                                                             *
*  Description : Met en place une zone de correspondance vide.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_empty_create(GRecordEmpty *empty, GKaitaiParser *parser, GBinContent *content, const vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = g_match_record_create(G_MATCH_RECORD(empty), parser, content);

    if (result)
        copy_vmpa(&empty->pos, pos);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : empty  = correspondance à consulter.                         *
*                range = zone de couverture déterminée. [OUT]                 *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_empty_get_range(const GRecordEmpty *empty, mrange_t *range)
{
    init_mrange(range, &empty->pos, 0);

}
