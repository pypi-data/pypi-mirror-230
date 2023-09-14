
/* Chrysalide - Outil d'analyse de fichiers binaires
 * semantic.c - prise en charge personnalisée de la bibliothèque C
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "semantic.h"


#include <plugins/elf/format.h>
#include <plugins/self.h>


#include "exit.h"



DEFINE_CHRYSALIDE_PLUGIN("CSem", "Semantic information relative to the libc",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE(""),
                         NO_REQ, AL(PGA_DISASSEMBLY_HOOKED_POST));



/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                binary  = binaire dont le contenu est en cours de traitement.*
*                status  = barre de statut à tenir informée.                  *
*                context = contexte de désassemblage.                         *
*                                                                             *
*  Description : Exécute une action pendant un désassemblage de binaire.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT void chrysalide_plugin_process_disassembly_event(const GPluginModule *plugin, PluginAction action, GLoadedBinary *binary, GtkStatusStack *status, GProcContext *context)
{
    if (action == PGA_DISASSEMBLY_HOOKED_POST)
    {
        /* Traitement de appels à exit() ou fonctions similaires */
        mark_exit_calls_as_return_instructions(binary);

    }

}
