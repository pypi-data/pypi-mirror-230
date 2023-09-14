
/* Chrysalide - Outil d'analyse de fichiers binaires
 * export_graph.h - prototypes pour l'assistant d'exportation de vues graphiques
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


#ifndef _GUI_DIALOGS_EXPORT_GRAPH_H
#define _GUI_DIALOGS_EXPORT_GRAPH_H


#include <gtk/gtk.h>


#include "../../analysis/binary.h"
#include "../../gtkext/gtkgraphdisplay.h"



/* Crée et affiche un assistant d'aide à l'exportation. */
void run_graph_export_assistant(GLoadedBinary *, GtkGraphDisplay *, GtkWindow *);



#endif  /* _GUI_DIALOGS_EXPORT_GRAPH_H */
