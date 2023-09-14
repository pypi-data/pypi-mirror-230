
/* Chrysalide - Outil d'analyse de fichiers binaires
 * updating-int.h - définitions internes propres aux mise à jour de panneaux
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


#ifndef _GUI_PANELS_UPDATING_INT_H
#define _GUI_PANELS_UPDATING_INT_H


#include "updating.h"



/* Prépare une opération de mise à jour de panneau. */
typedef bool (* setup_updatable_cb) (const GUpdatablePanel *, unsigned int, size_t *, void **, char **);

/* Obtient le groupe de travail dédié à une mise à jour. */
typedef wgroup_id_t (* get_updatable_group_cb) (const GUpdatablePanel *);

/* Bascule l'affichage d'un panneau avant mise à jour. */
typedef void (* introduce_updatable_cb) (const GUpdatablePanel *, unsigned int, void *);

/* Réalise une opération de mise à jour de panneau. */
typedef void (* process_updatable_cb) (const GUpdatablePanel *, unsigned int, GtkStatusStack *, activity_id_t, void *);

/* Bascule l'affichage d'un panneau après mise à jour. */
typedef void (* conclude_updatable_cb) (GUpdatablePanel *, unsigned int, void *);

/* Supprime les données dynamiques utilisées à la mise à jour. */
typedef void (* clean_updatable_data_cb) (const GUpdatablePanel *, unsigned int, void *);


/* Mécanisme de mise à jour d'un panneau (interface) */
struct _GUpdatablePanelIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    /* Méthodes virtuelles */

    setup_updatable_cb setup;               /* Préparation des traitements */
    get_updatable_group_cb get_group;       /* Obtention du groupe dédié   */
    introduce_updatable_cb introduce;       /* Changement d'affichage #0   */
    process_updatable_cb process;           /* Mise à jour d'affichage     */
    conclude_updatable_cb conclude;         /* Changement d'affichage #1   */
    clean_updatable_data_cb clean;          /* Nettoyage des données       */

};


/* Redéfinition */
typedef GUpdatablePanelIface GUpdatablePanelInterface;



#endif  /* _GUI_PANELS_UPDATING_INT_H */
