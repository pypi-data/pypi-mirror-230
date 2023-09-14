
/* Chrysalide - Outil d'analyse de fichiers binaires
 * status.h - prototypes pour l'affichage d'informations de statut dans la fenêtre principale
 *
 * Copyright (C) 2013-2020 Cyrille Bagard
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


#ifndef _GUI_STATUS_H
#define _GUI_STATUS_H


#include "item.h"



#define STATUS_INFO_ID "status"


#define G_TYPE_STATUS_INFO               g_status_info_get_type()
#define G_STATUS_INFO(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_status_info_get_type(), GStatusInfo))
#define G_IS_STATUS_INFO(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_status_info_get_type()))
#define G_STATUS_INFO_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_STATUS_INFO, GStatusInfoClass))
#define G_IS_STATUS_INFO_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_STATUS_INFO))
#define G_STATUS_INFO_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_STATUS_INFO, GStatusInfoClass))


/* Barre de statut de la fenêtre principale (instance) */
typedef struct _GStatusInfo GStatusInfo;

/* Barre de statut de la fenêtre principale (classe) */
typedef struct _GStatusInfoClass GStatusInfoClass;


/* Indique le type défini pour la barre de statut de la fenêtre principale. */
GType g_status_info_get_type(void);

/* Compose la barre de statut principale. */
GEditorItem *g_status_info_new(void);



#endif  /* _GUI_STATUS_H */
