
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list.c - conservation d'une liste de correspondance avec du binaire
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


#include "list.h"


#include <assert.h>
#include <malloc.h>


#include "list-int.h"



/* ------------------ DEFINITION D'UNE SEQUENCE DE CORRESPONDANCES ------------------ */


/* Initialise la classe des listes de correspondances. */
static void g_record_list_class_init(GRecordListClass *);

/* Initialise une série de correspondances attributs/binaire. */
static void g_record_list_init(GRecordList *);

/* Supprime toutes les références externes. */
static void g_record_list_dispose(GRecordList *);

/* Procède à la libération totale de la mémoire. */
static void g_record_list_finalize(GRecordList *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Calcule ou fournit la zone couverte par une correspondance. */
static void g_record_list_get_range(const GRecordList *, mrange_t *);

/* Recherche la correspondance associée à un identifiant. */
static GMatchRecord *g_record_list_find_by_name(GRecordList *, const char *, size_t, unsigned int);

/* Transforme une énumération en constante entière. */
static bool g_record_list_resolve_enum(const GRecordList *, const sized_string_t *, const sized_string_t *, resolved_value_t *);



/* ---------------------------------------------------------------------------------- */
/*                    DEFINITION D'UNE SEQUENCE DE CORRESPONDANCES                    */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une série de correspondances entre attributes et binaire. */
G_DEFINE_TYPE(GRecordList, g_record_list, G_TYPE_MATCH_RECORD);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des listes de correspondances.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_list_class_init(GRecordListClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GMatchRecordClass *record;              /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_record_list_dispose;
    object->finalize = (GObjectFinalizeFunc)g_record_list_finalize;

    record = G_MATCH_RECORD_CLASS(klass);

    record->get_range = (get_record_range_fc)g_record_list_get_range;
    record->find = (find_record_by_name_fc)g_record_list_find_by_name;
    record->resolve = (resolve_record_enum_fc)g_record_list_resolve_enum;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une série de correspondances attributs/binaire.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_list_init(GRecordList *list)
{
    list->children = NULL;
    list->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_list_dispose(GRecordList *list)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < list->count; i++)
        g_clear_object(&list->children[i]);

    G_OBJECT_CLASS(g_record_list_parent_class)->dispose(G_OBJECT(list));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_list_finalize(GRecordList *list)
{
    if (list->children != NULL)
        free(list->children);

    G_OBJECT_CLASS(g_record_list_parent_class)->finalize(G_OBJECT(list));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                pos     = début de la zone de couverture de la liste.        *
*                                                                             *
*  Description : Crée une nouvelle série de correspondances attribut/binaire. *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRecordList *g_record_list_new(GKaitaiAttribute *attrib, GBinContent *content, const vmpa2t *pos)
{
    GRecordList *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_RECORD_LIST, NULL);

    if (!g_record_list_create(result, attrib, content, pos))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list    = correspondance à initialiser pleinement.           *
*                attrib  = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                                                                             *
*  Description : Met en place une série de correspondances attribut/binaire.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_list_create(GRecordList *list, GKaitaiAttribute *attrib, GBinContent *content, const vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = g_match_record_create(G_MATCH_RECORD(list), G_KAITAI_PARSER(attrib), content);

    if (result)
        copy_vmpa(&list->pos, pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de correspondances attribut/binaire.         *
*                                                                             *
*  Description : Dénombre le nombre de correspondances enregistrées.          *
*                                                                             *
*  Retour      : Taille de la liste représentée.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_record_list_count_records(const GRecordList *list)
{
    size_t result;                          /* Quantité à retourner        */

    result = list->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list   = ensemble de correspondances attribut/binaire.       *
*                record = sous-corresponde à intégrer.                        *
*                                                                             *
*  Description : Ajoute une correspondance supplémentaire à une série.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_record_list_add_record(GRecordList *list, GMatchRecord *record)
{
    list->children = realloc(list->children, ++list->count * sizeof(GMatchRecord));

    list->children[list->count - 1] = record;
    g_object_ref(G_OBJECT(record));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = ensemble de correspondances attribut/binaire.        *
*                index = indice de la correspondance visée.                   *
*                                                                             *
*  Description : Fournit un élément ciblé dans la liste de correspondances.   *
*                                                                             *
*  Retour      : Instance de correspondance particulière, voire NULL.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMatchRecord *g_record_list_get_record(const GRecordList *list, size_t index)
{
    GMatchRecord *result;                   /* Instance à retourner        */

    if (index < list->count)
    {
        result = list->children[index];
        g_object_ref(G_OBJECT(result));
    }
    else
        result = NULL;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = correspondance à consulter.                          *
*                range = zone de couverture déterminée. [OUT]                 *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_list_get_range(const GRecordList *list, mrange_t *range)
{
    vmpa2t start;                           /* Position de départ          */
    mrange_t range_0;                       /* Première zone couverte      */
    mrange_t range_n;                       /* Dernière zone couverte      */
    vmpa2t end;                             /* Position de d'arrivée       */
    phys_t length;                          /* Taille de zone couverte     */

    assert(list->count > 0);

    if (list->count == 0)
    {
        init_vmpa(&start, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);
        init_mrange(range, &start, VMPA_NO_PHYSICAL);
    }

    else
    {
        g_match_record_get_range(list->children[0], &range_0);
        g_match_record_get_range(list->children[list->count - 1], &range_n);

        copy_vmpa(&start, get_mrange_addr(&range_0));

        compute_mrange_end_addr(&range_n, &end);
        length = compute_vmpa_diff(&start, &end);

        init_mrange(range, &start, length);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = ensemble de correspondances attribut/binaire.        *
*                name  = désignation de l'élément recherché.                  *
*                len   = taille de cette désignation.                         *
*                level  = profondeur maximale à atteindre (fond : 0).         *
*                                                                             *
*  Description : Recherche la correspondance associée à un identifiant.       *
*                                                                             *
*  Retour      : Correspondance trouvée ou NULL.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GMatchRecord *g_record_list_find_by_name(GRecordList *list, const char *name, size_t len, unsigned int level)
{
    GMatchRecord *result;                   /* Correspondance à renvoyer   */
    GMatchRecordClass *class;               /* Classe parente normalisée   */
    size_t i;                               /* Boucle de parcours          */

    class = G_MATCH_RECORD_CLASS(g_record_list_parent_class);

    result = class->find(G_MATCH_RECORD(list), name, len, level);

    if (level > 0)
    {
        for (i = 0; i < list->count && result == NULL; i++)
            result = g_match_record_find_by_name(list->children[i], name, len, level);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = ensemble de correspondances attribut/binaire.        *
*                name  = désignation de l'élément recherché.                  *
*                label = étiquette de l'élément constant à traduire.          *
*                value = valeur entière correspondante. [OUT]                 *
*                                                                             *
*  Description : Transforme une énumération en constante entière.             *
*                                                                             *
*  Retour      : Bilan de l'opération : true si la résolution est réalisée.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_record_list_resolve_enum(const GRecordList *list, const sized_string_t *name, const sized_string_t *label, resolved_value_t *value)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    /**
     * Comme les types peuvent être sélectionnés dynamiquement, le parcours
     * de l'ensemble des sous-noeuds doit être effectué.
     */

    result = false;

    for (i = 0; i < list->count && !result; i++)
        result = g_match_record_resolve_enum(list->children[i], name, label, value);

    return result;

}
