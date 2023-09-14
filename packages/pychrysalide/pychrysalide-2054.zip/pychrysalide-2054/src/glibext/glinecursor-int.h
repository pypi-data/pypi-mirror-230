
/* Chrysalide - Outil d'analyse de fichiers binaires
 * glinecursor-int.h - définitions internes propres au suivi de positions
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _GLIBEXT_GLINECURSOR_INT_H
#define _GLIBEXT_GLINECURSOR_INT_H


#include "glinecursor.h"
#include "notifier.h"



/* Réalise la copie d'un suivi d'emplacements. */
typedef GLineCursor * (* duplicate_cursor_fc) (const GLineCursor *);

/* Compare deux suivis d'emplacements. */
typedef int (* compare_cursor_fc) (const GLineCursor *, const GLineCursor *);

/* Détermine si la position de suivi est pertinente ou non. */
typedef bool (* is_cursor_valid_fc) (const GLineCursor *);

/* Construit une étiquette de représentation d'un suivi. */
typedef char * (* build_cursor_label_fc) (const GLineCursor *);

/* Affiche une position dans une barre de statut. */
typedef void (* show_cursor_status_fc) (const GLineCursor *, GtkStatusStack *, GLoadedContent *);

/* Exporte la définition d'un emplacement dans un flux réseau. */
typedef bool (* serialize_cursor_fc) (const GLineCursor *, packed_buffer_t *);

/* Importe la définition d'un emplacement depuis un flux réseau. */
typedef bool (* unserialize_cursor_fc) (GLineCursor *, packed_buffer_t *);

/* Donne les éléments requis pour la construction d'une table. */
typedef char *(* create_cursor_db_table_fc) (const char *);

/* Charge les valeurs utiles pour une localisation. */
typedef bool (* load_cursor_fc) (GLineCursor *, const char *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
typedef bool (* store_cursor_fc) (const GLineCursor *, const char *, bound_value **, size_t *);


/* Suivi de positions dans un panneau de chargement (instance) */
struct _GLineCursor
{
    GObject parent;                         /* A laisser en premier        */

};

/* Suivi de positions dans un panneau de chargement (classe) */
struct _GLineCursorClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    duplicate_cursor_fc duplicate;          /* Copie de curseur            */
    compare_cursor_fc compare;              /* Comparaison d'emplacements  */
    is_cursor_valid_fc is_valid;            /* Certificat de validité      */
    build_cursor_label_fc build_label;      /* Obtention d'une étiquette   */
    show_cursor_status_fc show_status;      /* Affichage dans une barre    */

    serialize_cursor_fc serialize;          /* Sauvegarde d'un emplacement */
    unserialize_cursor_fc unserialize;      /* Chargement d'un emplacement */

    create_cursor_db_table_fc create_db;    /* Création de table           */
    load_cursor_fc load;                    /* Chargement de valeurs       */
    store_cursor_fc store;                  /* Préparation d'enregistrement*/

};



#endif  /* _GLIBEXT_GLINECURSOR_INT_H */
