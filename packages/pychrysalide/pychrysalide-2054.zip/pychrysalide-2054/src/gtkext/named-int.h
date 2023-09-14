
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named-int.h - définitions internes propres à la préparation de composants à l'affichage avec leurs noms
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


#ifndef _GTK_NAMED_INT_H
#define _GTK_NAMED_INT_H


#include "named.h"



/* Préparation d'un composant pour affichage avec ses noms (instance) */
struct _GtkBuiltNamedWidget
{
    GObject parent;                         /* A laisser en premier        */

    char *name;                             /* Description courte          */
    char *lname;                            /* Description longue          */

    /**
     * La gestion générique du constructeur repose sur quelques
     * prérequis quant à l'enregistrement de composants :
     *
     *    - "box" doit être le support de panneau à intégrer.
     *
     *    - pour les contenus actualisables, une pile de composants
     *      "stack" doit contenir un support "content" pour le
     *      contenu principal et un support "mask" qui prend le
     *      relais pendant les opérations de mise à jour.
     */

    GtkBuilder *builder;                    /* Constructeur utilisé        */

};

/* Préparation d'un composant pour affichage avec ses noms (classe) */
struct _GtkBuiltNamedWidgetClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _GTK_NAMED_INT_H */
