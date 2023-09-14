
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named.c - manipulation de composants nommés
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


#include "named.h"


#include "named-int.h"



/* Procède à l'initialisation de l'interface de génération. */
static void g_named_widget_default_init(GNamedWidgetInterface *);



/* Détermine le type d'une interface pour les composants nommés. */
G_DEFINE_INTERFACE(GNamedWidget, g_named_widget, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_named_widget_default_init(GNamedWidgetInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant nommé à consulter.                        *
*                lname  = précise s'il s'agit d'une version longue ou non.    *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_named_widget_get_name(const GNamedWidget *widget, bool lname)
{
    char *result;                           /* Désignation à retourner     */
    GNamedWidgetIface *iface;               /* Interface utilisée          */

    iface = G_NAMED_WIDGET_GET_IFACE(widget);

    result = iface->get_name(widget, lname);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant nommé à consulter.                        *
*                                                                             *
*  Description : Fournit le composant associé à un composant nommé.           *
*                                                                             *
*  Retour      : Composant graphique GTK.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *g_named_widget_get_widget(const GNamedWidget *widget)
{
    GtkWidget *result;                      /* Composant GTK à renvoyer    */
    GNamedWidgetIface *iface;               /* Interface utilisée          */

    iface = G_NAMED_WIDGET_GET_IFACE(widget);

    result = iface->get_widget(widget);

    return result;

}
