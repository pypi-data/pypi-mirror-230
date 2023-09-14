
/* Chrysalide - Outil d'analyse de fichiers binaires
 * errors.h - prototypes pour le panneau listant les erreurs au désassemblage
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#ifndef _GUI_PANELS_ERRORS_H
#define _GUI_PANELS_ERRORS_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_ERRORS_ID "errors"


#define G_TYPE_ERROR_PANEL               g_error_panel_get_type()
#define G_ERROR_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ERROR_PANEL, GErrorPanel))
#define G_IS_ERROR_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ERROR_PANEL))
#define G_ERROR_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ERROR_PANEL, GErrorPanelClass))
#define G_IS_ERROR_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ERROR_PANEL))
#define G_ERROR_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ERROR_PANEL, GErrorPanelClass))


/* Panneau de présentation des erreurs recontrées (instance) */
typedef struct _GErrorPanel GErrorPanel;

/* Panneau de présentation des erreurs recontrées (classe) */
typedef struct _GErrorPanelClass GErrorPanelClass;


/* Indique le type défini pour un panneau d'affichage des erreurs. */
GType g_error_panel_get_type(void);

/* Crée un panneau présentant la liste des erreurs rencontrées. */
GPanelItem *g_error_panel_new(void);



#endif  /* _GUI_PANELS_ERRORS_H */
