
/* Chrysalide - Outil d'analyse de fichiers binaires
 * signal.h - prototypes pour un encadrement des signaux supplémentaire par rapport à celui de la GLib
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _GLIBEXT_SIGNAL_H
#define _GLIBEXT_SIGNAL_H


#include <glib-object.h>
#include <gobject/gclosure.h>
#include <glib/gdataset.h>
#include <glib/glist.h>
#include <gobject/gsignal.h>



/* Reproduit le comportement de la fonction g_signal_connect(). */
gulong _g_signal_connect_to_main(gpointer, const gchar *, GCallback, gpointer, GClosureMarshal, GConnectFlags);


#define g_signal_connect_to_main(instance, signal, handler, data, marshal) \
    _g_signal_connect_to_main(instance, signal, handler, data, marshal, 0)

#define g_signal_connect_to_main_swapped(instance, signal, handler, data, marshal) \
    _g_signal_connect_to_main(instance, signal, handler, data, marshal, G_CONNECT_SWAPPED)



#endif  /* _GLIBEXT_SIGNAL_H */
