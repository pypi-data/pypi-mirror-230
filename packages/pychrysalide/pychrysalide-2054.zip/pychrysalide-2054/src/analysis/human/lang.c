
/* Chrysalide - Outil d'analyse de fichiers binaires
 * lang.c - traduction en langages de haut niveau
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#include "lang.h"


#include "lang-int.h"



/* Initialise la classe des traductions en langage humain. */
static void g_coding_language_class_init(GCodingLanguageClass *);

/* Initialise une instance de traduction en langage humain. */
static void g_coding_language_init(GCodingLanguage *);

/* Supprime toutes les références externes. */
static void g_coding_language_dispose(GCodingLanguage *);

/* Procède à la libération totale de la mémoire. */
static void g_coding_language_finalize(GCodingLanguage *);



/* Indique le type défini pour une traduction en langage humain. */
G_DEFINE_TYPE(GCodingLanguage, g_coding_language, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des traductions en langage humain.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_coding_language_class_init(GCodingLanguageClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_coding_language_dispose;
    object->finalize = (GObjectFinalizeFunc)g_coding_language_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de traduction en langage humain.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_coding_language_init(GCodingLanguage *lang)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_coding_language_dispose(GCodingLanguage *lang)
{
    G_OBJECT_CLASS(g_coding_language_parent_class)->dispose(G_OBJECT(lang));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_coding_language_finalize(GCodingLanguage *lang)
{
    G_OBJECT_CLASS(g_coding_language_parent_class)->finalize(G_OBJECT(lang));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang  = langage de haut niveau à manipuler.                  *
*                text  = adresse de la ligne à compléter. [OUT]               *
*                                                                             *
*  Description : Complète du texte pour en faire un vrai commentaire.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_coding_language_encapsulate_comment(const GCodingLanguage *lang, char **text)
{
    G_CODING_LANGUAGE_GET_CLASS(lang)->encaps_comment(lang, text);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang  = langage de haut niveau à manipuler.                  *
*                text  = adresse du tableau de lignes à conserver. [OUT]      *
*                count = adresse de la taille du tableau fourni. [OUT]        *
*                                                                             *
*  Description : Complète du texte pour en faire de vrais commentaires.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_coding_language_encapsulate_comments(const GCodingLanguage *lang, char ***text, size_t *count)
{
    G_CODING_LANGUAGE_GET_CLASS(lang)->encaps_comments(lang, text, count);

}
