
/* Chrysalide - Outil d'analyse de fichiers binaires
 * options-int.h - prototypes internes pour le rassemblement des options d'analyse communiquées par le donneur d'ordre
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_OPTIONS_INT_H
#define _ANALYSIS_SCAN_OPTIONS_INT_H


#include "options.h"



/* Rassemblement d'options d'analyses (instance) */
struct _GScanOptions
{
    GObject parent;                         /* A laisser en premier        */

    GType data_backend;                     /* Choix du moteur d'analyse   */

    bool print_json;                        /* Sortie au format json ?     */
    bool print_strings;                     /* Affichage de correspondances*/
    bool print_stats;                       /* Affichage de statistiques ? */

};

/* Rassemblement d'options d'analyses (classe) */
struct _GScanOptionsClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _ANALYSIS_SCAN_OPTIONS_INT_H */
