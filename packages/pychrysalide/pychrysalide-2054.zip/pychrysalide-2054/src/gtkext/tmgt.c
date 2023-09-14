
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tmgt.c - compléments utiles à la mise en place d'arborescences
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "tmgt.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../common/extstr.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : entry  = zone de texte avec un nouveau filtre d'affichage.   *
*                filter = expression régulière de filtrage à constituer. [OUT]*
*                                                                             *
*  Description : Met à jour un filtre selon un contenu recherché.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_regex_on_search_entry_changed(GtkSearchEntry *entry, char **filter)
{
    const gchar *text;                      /* Texte de l'utilisateur      */
    bool has_error;                         /* Détecttion d'une erreur     */
    regex_t exp;                            /* Expression régulière créée  */
    int ret;                                /* Bilan de mise en place      */
    GtkStyleContext *context;               /* Contexte du thème actuel    */

    if (*filter != NULL)
        free(*filter);

    /* Validation et exportation des résultats */

    text = gtk_entry_get_text(GTK_ENTRY(entry));

    if (strlen(text) == 0)
    {
        has_error = false;
        *filter = NULL;
    }

    else
    {
        ret = regcomp(&exp, text, REG_EXTENDED | REG_ICASE);

        has_error = (ret != 0);

        if (has_error)
            *filter = NULL;

        else
        {
            *filter = strdup(text);
            regfree(&exp);
        }

    }

    /* Indication à l'écran */

    context = gtk_widget_get_style_context(GTK_WIDGET(entry));

    if (has_error)
        gtk_style_context_add_class(context, "filter-error");
    else
        gtk_style_context_remove_class(context, "filter-error");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filter  = expression régulière servant de filtre.            *
*                content = contenu textuel à analyser.                        *
*                match   = zone pointant vers une correspondance. [OUT]       *
*                                                                             *
*  Description : Détermine si un contenu correspond à un filtre donné.        *
*                                                                             *
*  Retour      : true si le contenu est qualifié pour un affichage, ou false. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_content_matching(const regex_t *filter, const char *content, regmatch_t *match)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan du filtrage           */

    if (filter == NULL)
    {
        memset(match, 0, sizeof(regmatch_t));
        result = true;
    }

    else
    {
        ret = regexec(filter, content, 1, match, 0);
        result = (ret != REG_NOMATCH);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw   = bribe de texte à traiter.                            *
*                match = portion de texte à mettre en évidence.               *
*                start = position du texte brute dans l'étiquette complète.   *
*                                                                             *
*  Description : Met en évidence le texte recherché en cas de correspondance. *
*                                                                             *
*  Retour      : Texte final destiné à être inséré, à libérer après usage.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_highlighted_name(const char *raw, const regmatch_t *match, size_t start)
{
    char *result;                           /* Construction à retourner    */
    size_t len;                             /* Taille du texte d'entrée    */
    regmatch_t selection;                   /* Sélection relative au texte */
    char *valid;                            /* Retouche partielle          */

    len = strlen(raw);

    /* Si aucune sélection ou texte hors champ... */

    if ((match->rm_eo - match->rm_so) == 0 || (start + len) <= match->rm_so || match->rm_eo < start)
    {
        result = strdup(raw);
        result = strrpl(result, "<", "&lt;");
    }

    /* Sinon, il y a forcément correspondance quelque part ! */

    else
    {
        /* Adaptations */

        if (match->rm_so < start)
            selection.rm_so = 0;
        else
            selection.rm_so = match->rm_so - start;

        selection.rm_eo = match->rm_eo - start;

        if (selection.rm_eo > len)
            selection.rm_eo = len;

        /* Impressions */

        if (selection.rm_so > 0)
        {
            result = strndup(raw, selection.rm_so);
            result = strrpl(result, "<", "&lt;");
        }
        else
            result = NULL;

        result = stradd(result, "<b>");

        valid = strndup(&raw[selection.rm_so], selection.rm_eo - selection.rm_so);
        valid = strrpl(valid, "<", "&lt;");

        result = stradd(result, valid);

        free(valid);

        result = stradd(result, "</b>");

        valid = strdup(&raw[selection.rm_eo]);
        valid = strrpl(valid, "<", "&lt;");

        result = stradd(result, valid);

        free(valid);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store = organisation des données sous forme arborescente.    *
*                iter  = position du noeud courant à traiter.                 *
*                show  = visibilité à obtenir pour le noeud final.            *
*                                                                             *
*  Description : Met à jour l'affichage des noeuds en fonction des besoin.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_node_visibility(GtkTreeStore *store, GtkTreeIter *iter, gint column, bool show)
{
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    gint matched_col;                       /* Colonne de visibilité       */
    gint points_col;                        /* Colonne des points          */
    guint points;                           /* Compteur de besoins         */
    GtkTreeIter parent;                     /* Position de noeuf parent    */
    gboolean further;                       /* Poursuite de remontée       */

    model = GTK_TREE_MODEL(store);

    matched_col = column;
    points_col = column + 1;

    /* Enumération des besoins */

    gtk_tree_model_get(model, iter, points_col, &points, -1);

    if (show)
        points++;

    else
    {
        assert(points > 0);
        points--;
    }

    gtk_tree_store_set(store, iter, points_col, points, -1);

    /* Adaptation de l'affichage */

    if (show)
    {
        if (points == 1)
            gtk_tree_store_set(store, iter, matched_col, true, -1);
    }

    else
    {
        if (points == 0)
            gtk_tree_store_set(store, iter, matched_col, false, -1);
    }

    /* Eventuel étage supérieur */

    further = gtk_tree_model_iter_parent(model, &parent, iter);

    if (further)
        update_node_visibility(store, &parent, column, show);

}
