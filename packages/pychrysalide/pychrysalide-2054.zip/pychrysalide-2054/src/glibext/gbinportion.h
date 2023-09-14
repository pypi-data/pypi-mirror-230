
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binportion.h - prototypes pour la représentation graphique de portions de binaire
 *
 * Copyright (C) 2013-2019 Cyrille Bagard
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


#ifndef _GLIBEXT_BINPORTION_H
#define _GLIBEXT_BINPORTION_H


#include <glib-object.h>
#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include "../arch/vmpa.h"
#include "../common/fnv1a.h"



/* ------------------------------- PORTION DE BINAIRE ------------------------------- */


/**
 * Couleurs de représentation.
 */

#define BPC_RAW             "binportion-raw"
#define BPC_CODE            "binportion-code"
#define BPC_DATA            "binportion-data"
#define BPC_DATA_RO         "binportion-data-ro"
#define BPC_DISASS_ERROR    "binportion-disassembly-error"


#define G_TYPE_BIN_PORTION                (g_binary_portion_get_type())
#define G_BIN_PORTION(obj)                (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BIN_PORTION, GBinPortion))
#define G_IS_BIN_PORTION(obj)             (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BIN_PORTION))
#define G_BIN_PORTION_CLASS(klass)        (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BIN_PORTION, GBinPortionClass))
#define G_IS_BIN_PORTION_CLASS(klass)     (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BIN_PORTION))
#define G_BIN_PORTION_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BIN_PORTION, GBinPortionClass))


/* Portion de données binaires quelconques (instance) */
typedef struct _GBinPortion GBinPortion;

/* Portion de données binaires quelconques (classe) */
typedef struct _GBinPortionClass GBinPortionClass;


/* Droits d'accès à une portion */
typedef enum _PortionAccessRights
{
    PAC_NONE    = (0 << 0),                 /* Aucun                       */
    PAC_READ    = (1 << 0),                 /* Lecture                     */
    PAC_WRITE   = (1 << 1),                 /* Ecriture                    */
    PAC_EXEC    = (1 << 2)                  /* Exécution                   */

} PortionAccessRights;


#define PAC_ALL ((PortionAccessRights)(PAC_READ | PAC_WRITE | PAC_EXEC))


/* Indique le type défini par la GLib pour les portions de données binaires. */
GType g_binary_portion_get_type(void);

/* Crée une description de partie de code vierge. */
GBinPortion *g_binary_portion_new(const char *, const vmpa2t *, phys_t);

/* Etablit la comparaison ascendante entre deux portions. */
int g_binary_portion_compare(const GBinPortion **, const GBinPortion **);

#ifdef INCLUDE_GTK_SUPPORT

/* Attribue à la portion une éventuelle image de représentation. */
void g_binary_portion_set_icon(GBinPortion *, cairo_surface_t *);

/* Fournit une éventuelle image de représentation de portion. */
cairo_surface_t *g_binary_portion_get_icon(const GBinPortion *);

#endif

/* Attribue une description humaine à une partie de code. */
void g_binary_portion_set_desc(GBinPortion *, const char *);

/* Fournit la description attribuée à une partie de code. */
const char *g_binary_portion_get_desc(const GBinPortion *);

/* Fournit l'emplacement d'une partie de code binaire. */
const mrange_t *g_binary_portion_get_range(const GBinPortion *);

/* Assure qu'une portion ne dépasse pas une position donnée. */
bool g_binary_portion_limit_range(GBinPortion *, phys_t);

/* Définit la nature de la portion en terme d'originalité. */
void g_binary_portion_mark_as_continued(GBinPortion *, bool);

/* Indique la nature de la portion en terme d'originalité. */
bool g_binary_portion_is_continuation(const GBinPortion *);

/* Définit les droits associés à une partie de code. */
void g_binary_portion_set_rights(GBinPortion *, PortionAccessRights);

/* Fournit les droits associés à une partie de code. */
PortionAccessRights g_binary_portion_get_rights(const GBinPortion *);

#ifdef INCLUDE_GTK_SUPPORT

/* Prépare une astuce concernant une portion pour son affichage. */
void g_binary_portion_query_tooltip(GBinPortion *, GtkTooltip *);

/* Représente la portion sur une bande dédiée. */
void g_binary_portion_draw(const GBinPortion *, GtkStyleContext *, cairo_t *, const GdkRectangle *);

#endif

/* Procède à l'inclusion d'une portion dans une autre. */
void g_binary_portion_include(GBinPortion *, GBinPortion *);

/* Sens des visites */
typedef enum _BinaryPortionVisit
{
    BPV_ENTER,                              /* Arrivée sur une branche     */
    BPV_SHOW,                               /* Visite d'une feuille        */
    BPV_EXIT                                /* Départ d'une branche        */

} BinaryPortionVisit;


/* Fonction appelée à chaque visite de portion.*/
typedef bool (* visit_portion_fc) (GBinPortion *, GBinPortion *, BinaryPortionVisit, void *);

/* Parcourt un ensemble de portions binaires. */
bool g_binary_portion_visit(GBinPortion *, visit_portion_fc, void *);



/* ------------------------ PARCOURS D'ENSEMBLES DE PORTIONS ------------------------ */


#ifdef INCLUDE_GTK_SUPPORT

/* Compte le nombre de portions présentes dans une arborescence. */
size_t g_binary_portion_count(const GBinPortion *);

/* Recherche la portion présente à un point donné. */
GBinPortion *g_binary_portion_find_at_pos(GBinPortion *, gint, GdkRectangle *);

#endif

/* Recherche la portion présente à une adresse donnée. */
GBinPortion *g_binary_portion_find_at_addr(GBinPortion *, const vmpa2t *);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la position correspondant à une adresse donnée. */
bool get_binary_portion_addr_from_pos(GBinPortion *, gint, const GdkRectangle *, vmpa2t *);

/* Fournit l'adresse correspondant à une position donnée. */
bool get_binary_portion_pos_from_addr(GBinPortion *, const vmpa2t *, const GdkRectangle *, gint *);

/* Prépare une astuce concernant une portion pour son affichage. */
gboolean query_tooltip_for_binary_portion(GBinPortion *, gint, gint, const GdkRectangle *, GtkTooltip *);

#endif

/* Fournit l'emplacement correspondant à une position physique. */
bool g_binary_portion_translate_offset_into_vmpa(const GBinPortion *, phys_t, vmpa2t *);

/* Fournit l'emplacement correspondant à une adresse virtuelle. */
bool g_binary_portion_translate_address_into_vmpa(const GBinPortion *, virt_t, vmpa2t *);



#endif  /* _GLIBEXT_BINPORTION_H */
