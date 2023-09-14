
/* Chrysalide - Outil d'analyse de fichiers binaires
 * buffercache-int.h - définitions internes d'affichage à la demande d'un ensemble de lignes
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _GLIBEXT_BUFFERCACHE_INT_H
#define _GLIBEXT_BUFFERCACHE_INT_H


#include "buffercache.h"



/* --------------------- FONCTIONS AUXILIAIRES DE MANIPULATIONS --------------------- */


/* Informations rattachées à la génération d'une ligne */
typedef struct _generator_link
{
    GLineGenerator *instance;               /* Fournisseur de contenu      */
    size_t repeat;                          /* Compteur de successions     */

} generator_link;

/* Suivi interne de l'état d'une ligne */
typedef struct _cache_info
{
    union
    {
        generator_link generator;           /* Générateur unique           */
        generator_link *generators;         /* Liste de générateurs        */
    };
    size_t count;                           /* Taille de cette liste       */

    GBufferLine *line;                      /* Ligne en place ou NULL      */

    BufferLineFlags extra_flags;            /* Propriétés supplémentaires  */

} cache_info;



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


/* Tampon pour gestion de lignes optimisée (instance) */
struct _GBufferCache
{
    GObject parent;                         /* A laisser en premier        */

    GBinContent *content;                   /* Contenu binaire global      */

#ifdef INCLUDE_GTK_SUPPORT
    GWidthTracker *tracker;                 /* Suivi des largeurs          */
#endif

    cache_info *lines;                      /* Liste des lignes intégrées  */
    size_t count;                           /* Quantité en cache           */
    size_t used;                            /* Quantité utilisée           */
    GRWLock access;                         /* Verrou de protection        */

};

/* Tampon pour gestion de lignes optimisée (classe) */
struct _GBufferCacheClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    gint line_height;                       /* Hauteur maximale des lignes */
    gint left_margin;                       /* Marge gauche + espace       */
    gint text_pos;                          /* Début d'impression du code  */

    /* Signaux */

    void (* size_changed) (GBufferCache *, bool, size_t, size_t);

    void (* line_updated) (GBufferCache *, size_t);

};



#endif  /* _GLIBEXT_BUFFERCACHE_INT_H */
