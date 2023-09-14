
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ids.h - prototypes pour l'annotation des références aux chaînes de caractères et identifiants
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _PLUGINS_READDEX_IDS_H
#define _PLUGINS_READDEX_IDS_H


#include <format/preload.h>
#include <glibext/notifier.h>
#include <plugins/dex/format.h>



/* Charge tous les symboles de l'en-tête DEX. */
bool annotate_dex_string_ids(const GDexFormat *, GPreloadInfo *, GtkStatusStack *);

/* Commente les définitions des identifiants de types. */
bool annotate_dex_type_ids(const GDexFormat *, GPreloadInfo *, GtkStatusStack *);

/* Commente les définitions des identifiants de prototypes. */
bool annotate_dex_proto_ids(const GDexFormat *, GPreloadInfo *, GtkStatusStack *);

/* Commente les définitions des identifiants de champs. */
bool annotate_dex_field_ids(const GDexFormat *, GPreloadInfo *, GtkStatusStack *);

/* Commente les définitions des identifiants de méthodes. */
bool annotate_dex_method_ids(const GDexFormat *, GPreloadInfo *, GtkStatusStack *);



#endif  /* _PLUGINS_READDEX_IDS_H */
