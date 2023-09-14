
/* Chrysalide - Outil d'analyse de fichiers binaires
 * lang.c - traduction en language d'assembleur classique
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


#include "../lang-int.h"
#include "../../../common/extstr.h"



/* Traduction d'éléments en language d'assembleur (instance) */
struct _GAsmLanguage
{
    GCodingLanguage parent;                 /* A laisser en premier        */

};

/* Traduction d'éléments en language d'assembleur (classe) */
struct _GAsmLanguageClass
{
    GCodingLanguageClass parent;            /* A laisser en premier        */

};


/* Initialise la classe des traductions en langage d'assembleur. */
static void g_asm_language_class_init(GAsmLanguageClass *);

/* Initialise une traduction d'éléments en langage d'assembleur. */
static void g_asm_language_init(GAsmLanguage *);

/* Supprime toutes les références externes. */
static void g_asm_language_dispose(GAsmLanguage *);

/* Procède à la libération totale de la mémoire. */
static void g_asm_language_finalize(GAsmLanguage *);

/* Complète du texte pour en faire un vrai commentaire. */
static void g_asm_language_encapsulate_comment(const GAsmLanguage *, char **);

/* Complète du texte pour en faire de vrais commentaires. */
static void g_asm_language_encapsulate_comments(const GAsmLanguage *, char ***, size_t *);



/* Indique le type défini pour une traduction en langage d'assembleur. */
G_DEFINE_TYPE(GAsmLanguage, g_asm_language, G_TYPE_CODING_LANGUAGE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des traductions en langage d'assembleur.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_asm_language_class_init(GAsmLanguageClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GCodingLanguageClass *lang;             /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_asm_language_dispose;
    object->finalize = (GObjectFinalizeFunc)g_asm_language_finalize;

    lang = G_CODING_LANGUAGE_CLASS(klass);

    lang->encaps_comment = (encapsulate_comment_fc)g_asm_language_encapsulate_comment;
    lang->encaps_comments = (encapsulate_comments_fc)g_asm_language_encapsulate_comments;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : lang = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une traduction d'éléments en langage d'assembleur.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_asm_language_init(GAsmLanguage *lang)
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

static void g_asm_language_dispose(GAsmLanguage *lang)
{
    G_OBJECT_CLASS(g_asm_language_parent_class)->dispose(G_OBJECT(lang));

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

static void g_asm_language_finalize(GAsmLanguage *lang)
{
    G_OBJECT_CLASS(g_asm_language_parent_class)->finalize(G_OBJECT(lang));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une instance de traduction en langage d'assembleur.     *
*                                                                             *
*  Retour      : Instance mis en place et prête à emploi.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCodingLanguage *g_asm_language_new(void)
{
    GAsmLanguage *result;                   /* Instance à retourner        */

    result = g_object_new(G_TYPE_ASM_LANGUAGE, NULL);

    return G_CODING_LANGUAGE(result);

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

static void g_asm_language_encapsulate_comment(const GAsmLanguage *lang, char **text)
{
    *text = strprep(*text, "; ");

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

static void g_asm_language_encapsulate_comments(const GAsmLanguage *lang, char ***text, size_t *count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < *count; i++)
        (*text)[i] = strprep((*text)[i], "; ");

}
