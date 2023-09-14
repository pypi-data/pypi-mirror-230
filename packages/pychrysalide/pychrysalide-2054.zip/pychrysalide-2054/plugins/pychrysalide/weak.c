
/* Chrysalide - Outil d'analyse de fichiers binaires
 * weak.c - définition de symboles qui n'ont pas leur place dans la version autonome
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "weak.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                msg   = nouveau message de statut à copier.                  *
*                max   = taille de la plage à parcourir.                      *
*                                                                             *
*  Description : Démarre le suivi d'une nouvelle activité.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

activity_id_t gtk_status_stack_add_activity(GtkStatusStack *stack, const char *msg, unsigned long max)
{
    return ~0lu;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                id    = identifiant de l'activité à cibler.                  *
*                extra = nouvelle échéance supplémentaire des traitements.    *
*                                                                             *
*  Description : Etend la portée des travaux d'une nouvelle activité.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_extend_activity(GtkStatusStack *stack, activity_id_t id, unsigned long extra)
{
    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                id    = identifiant de l'activité à cibler.                  *
*                msg   = nouveau message de statut à copier.                  *
*                                                                             *
*  Description : Actualise les informations concernant une activité.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_update_activity(GtkStatusStack *stack, activity_id_t id, const char *msg)
{
    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                id    = identifiant de l'activité à cibler.                  *
*                inc   = nouvelle valeur pour une progression donnée.         *
*                                                                             *
*  Description : Actualise la progression d'une activité.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_update_activity_value(GtkStatusStack *stack, activity_id_t id, unsigned long inc)
{
    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                                                                             *
*  Description : Met fin au suivi d'une activité donnée.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_remove_activity(GtkStatusStack *stack, activity_id_t id)
{
    ;

}
