
/* Chrysalide - Outil d'analyse de fichiers binaires
 * support.c - recherche des chemins d'accès aux fichiers
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "support.h"


#include <malloc.h>


#include "../core/paths.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : filename = nom de fichier seul comme indice.                 *
*                                                                             *
*  Description : Construit une image à partir d'un nom de fichier.            *
*                                                                             *
*  Retour      : Elément mis en place ou NULL en cas d'erreur.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *get_image_from_file(const char *filename)
{
    GtkWidget *result;                      /* Instance à retourner        */
    char *fullname;                         /* Chemin d'accès complet      */

    fullname = find_pixmap_file(filename);

    if (fullname != NULL)
    {
        result = gtk_image_new_from_file(fullname);
        free(fullname);

        gtk_widget_show(result);

    }
    else result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = nom de fichier seul comme indice.                 *
*                                                                             *
*  Description : Construit un tampon d'image à partir d'un nom de fichier.    *
*                                                                             *
*  Retour      : Elément mis en place ou NULL en cas d'erreur.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GdkPixbuf *get_pixbuf_from_file(const char *filename)
{
    GdkPixbuf *result;                      /* Instance à retourner        */
    char *fullname;                         /* Chemin d'accès complet      */

    fullname = find_pixmap_file(filename);

    if (fullname != NULL)
    {
        result = gdk_pixbuf_new_from_file(fullname, NULL);
        free(fullname);
    }
    else result = NULL;

    return result;

}
