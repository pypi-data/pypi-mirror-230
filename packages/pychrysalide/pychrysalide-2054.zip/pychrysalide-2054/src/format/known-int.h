
/* Chrysalide - Outil d'analyse de fichiers binaires
 * known-int.h - prototypes utiles aux formats binaires reconnus
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


#ifndef _FORMAT_KNOWN_INT_H
#define _FORMAT_KNOWN_INT_H


#include "known.h"
#include "../analysis/storage/storage.h"



/* Indique la désignation interne du format. */
typedef char * (* known_get_key_fc) (const GKnownFormat *);

/* Fournit une description humaine du format. */
typedef char * (* known_get_desc_fc) (const GKnownFormat *);

/*Assure l'interprétation d'un format en différé. */
typedef bool (* known_analyze_fc) (GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Réalise un traitement post-désassemblage. */
typedef void (* known_complete_analysis_fc) (GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Charge un format depuis une mémoire tampon. */
typedef bool (* load_known_fc) (GKnownFormat *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un format dans une mémoire tampon. */
typedef bool (* store_known_fc) (GKnownFormat *, GObjectStorage *, packed_buffer_t *);


/* Format binaire générique (instance) */
struct _GKnownFormat
{
    GObject parent;                         /* A laisser en premier        */

    GBinContent *content;                   /* Contenu binaire à étudier   */

};

/* Format binaire générique (classe) */
struct _GKnownFormatClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    known_get_key_fc get_key;               /* Désignation interne         */
    known_get_desc_fc get_desc;             /* Désignation humaine         */

    known_analyze_fc analyze;               /* Interprétation du format    */
    known_complete_analysis_fc complete;    /* Terminaison d'analyse       */

    load_known_fc load;                     /* Chargement depuis un tampon */
    store_known_fc store;                   /* Conservation dans un tampon */

};



#endif  /* _FORMAT_KNOWN_INT_H */
