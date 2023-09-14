
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.h - prototypes pour l'ajout des constantes liées aux bases de données
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_PYCHRYSALIDE_ANALYSIS_DB_CONSTANTS_H
#define _PLUGINS_PYCHRYSALIDE_ANALYSIS_DB_CONSTANTS_H


#include <Python.h>
#include <stdbool.h>


/* Définit les constantes relatives au protocole. */
bool define_db_protocol_constants(PyTypeObject *);

/* Définit les constantes pour les éléments de base de données. */
bool define_db_item_constants(PyTypeObject *);

/* Définit les constantes pour les serveurs de données. */
bool define_hub_server_constants(PyTypeObject *);

/* Définit les constantes pour les indications de chargement. */
bool define_loading_status_hint_constants(PyTypeObject *);



#endif  /* _PLUGINS_PYCHRYSALIDE_ANALYSIS_DB_CONSTANTS_H */
