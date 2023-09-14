
/* Chrysalide - Outil d'analyse de fichiers binaires
 * match.c - sauvegarde d'une correspondance identifiée de motif
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


#include "match.h"


#include "match-int.h"



/* Initialise la classe des correspondances de motifs. */
static void g_scan_match_class_init(GScanMatchClass *);

/* Initialise une instance de correspondance de motif trouvée. */
static void g_scan_match_init(GScanMatch *);

/* Supprime toutes les références externes. */
static void g_scan_match_dispose(GScanMatch *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_match_finalize(GScanMatch *);



/* Indique le type défini pour un correspondance de motif identifiée. */
G_DEFINE_TYPE(GScanMatch, g_scan_match, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des correspondances de motifs.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_match_class_init(GScanMatchClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_match_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_match_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de correspondance de motif trouvée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_match_init(GScanMatch *match)
{
    match->source = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_match_dispose(GScanMatch *match)
{
    g_clear_object(&match->source);

    G_OBJECT_CLASS(g_scan_match_parent_class)->dispose(G_OBJECT(match));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_match_finalize(GScanMatch *match)
{
    G_OBJECT_CLASS(g_scan_match_parent_class)->finalize(G_OBJECT(match));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = définition de correspondance à consulter.            *
*                                                                             *
*  Description : Indique la source du motif d'origine recherché.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSearchPattern *g_scan_match_get_source(const GScanMatch *match)
{
    GSearchPattern *result;                 /* Source à retourner          */

    result = match->source;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = définition de correspondance à manipuler.            *
*                fd    = canal d'écriture.                                    *
*                                                                             *
*  Description : Affiche une correspondance au format texte.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_match_output_to_text(const GScanMatch *match, int fd)
{
    GScanMatchClass *class;                 /* Classe à activer            */

    class = G_SCAN_MATCH_GET_CLASS(match);

    class->to_text(match, fd);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = définition de correspondance à manipuler.            *
*                                                                             *
*  Description : Convertit une correspondance en texte.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_match_convert_as_text(const GScanMatch *match)
{
    /* TODO */

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match    = définition de correspondance à manipuler.         *
*                padding  = éventuel bourrage initial à placer ou NULL.       *
*                level    = profondeur actuelle.                              *
*                fd       = canal d'écriture.                                 *
*                trailing = impose une virgule finale ?                       *
*                                                                             *
*  Description : Affiche une correspondance au format JSON.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_match_output_to_json(const GScanMatch *match, const sized_string_t *padding, unsigned int level, int fd, bool trailing)
{
    unsigned int i;                         /* Boucle de parcours          */
    GScanMatchClass *class;                 /* Classe à activer            */

    /* Introduction */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "{\n", 2);

    /* Affichage du contenu */

    class = G_SCAN_MATCH_GET_CLASS(match);

    class->to_json(match, padding, level + 1, fd);

    /* Conclusion */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    if (trailing)
        write(fd, "},\n", 3);
    else
        write(fd, "}\n", 2);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = définition de correspondance à manipuler.            *
*                                                                             *
*  Description : Convertit une correspondance en JSON.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_match_convert_as_json(const GScanMatch *match)
{
    /* TODO */

}
