
/* Chrysalide - Outil d'analyse de fichiers binaires
 * speed.c - mesure de temps d'exécution internes
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


#include "speed.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <sys/time.h>


#include <i18n.h>


#include <common/extstr.h>
#include <plugins/self.h>



DEFINE_CHRYSALIDE_PLUGIN("SpeedMeasure", "Tracker of time spent for disassembling code",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE(""),
                         NO_REQ, AL(PGA_FORMAT_ANALYSIS_STARTED, PGA_FORMAT_ANALYSIS_ENDED,
                                    PGA_FORMAT_POST_ANALYSIS_STARTED, PGA_FORMAT_POST_ANALYSIS_ENDED,
                                    PGA_DISASSEMBLY_STARTED, PGA_DISASSEMBLY_ENDED));


/* Mémorisation des résultats de chronométrages */
typedef struct _speed_measure
{
    unsigned long usages[2];                /* Taux d'utilisation du CPU   */

} speed_measure;


/* Affiche une mesure de temps écoulé. */
static void show_elapsed_time(const char *, const speed_measure *);



/******************************************************************************
*                                                                             *
*  Paramètres  : title   = désignation humaine de la mesure menée.            *
*                measure = mesure de temps écoulé.                            *
*                                                                             *
*  Description : Affiche une mesure de temps écoulé.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void show_elapsed_time(const char *title, const speed_measure *measure)
{
    char *tmp;                              /* Construction temporaire     */
    double seconds;                         /* Secondes écoulées           */
    unsigned long minutes;                  /* Minutes écoulées            */
    unsigned long hours;                    /* Heures écoulées             */
    char *msg;                              /* Message à faire passer      */

    tmp = NULL;

    seconds = (double)(measure->usages[1] - measure->usages[0]) / 1000000;

    if (seconds > 60)
    {
        minutes = seconds / 60;
        seconds -= minutes * 60;
    }
    else
        minutes = 0;

    if (minutes > 60)
    {
        hours = minutes / 60;
        minutes %= 60;
    }
    else
        hours = 0;

    msg = strdup(title);

    if (hours > 0)
    {
        asprintf(&tmp, " %lu", hours);
        msg = stradd(msg, tmp);
        free(tmp);

        msg = stradd(msg, _("h"));

    }

    if (minutes > 0)
    {
        asprintf(&tmp, " %lu", minutes);
        msg = stradd(msg, tmp);
        free(tmp);

        msg = stradd(msg, _("m"));

    }

    if (seconds > 0.01)
    {
        asprintf(&tmp, " %.2f", seconds);
        msg = stradd(msg, tmp);
        free(tmp);

        msg = stradd(msg, _("s"));

    }

    if (tmp != NULL)
        log_plugin_simple_message(LMT_INFO, msg);

    free(msg);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Procède à une opération liée à l'analyse d'un format.        *
*                                                                             *
*  Retour      : Bilan de l'exécution du traitement.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_handle_binary_format_analysis(const GPluginModule *plugin, PluginAction action, GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    speed_measure *measure;                 /* Suivi des progressions      */
    struct timeval point;                   /* Point de mesure courant     */

    switch (action)
    {
        case PGA_FORMAT_ANALYSIS_STARTED:
        case PGA_FORMAT_POST_ANALYSIS_STARTED:

            measure = (speed_measure *)calloc(1, sizeof(speed_measure));
            g_object_set_data(G_OBJECT(format), "speed_measure", measure);

            gettimeofday(&point, NULL);
            measure->usages[0] = point.tv_sec * 1000000 + point.tv_usec;

            break;

        case PGA_FORMAT_ANALYSIS_ENDED:
        case PGA_FORMAT_POST_ANALYSIS_ENDED:

            measure = (speed_measure *)g_object_get_data(G_OBJECT(format), "speed_measure");

            gettimeofday(&point, NULL);
            measure->usages[1] = point.tv_sec * 1000000 + point.tv_usec;

            if (action == PGA_FORMAT_ANALYSIS_ENDED)
                show_elapsed_time(_("Whole elapsed time for format analysis:"), measure);
            else
                show_elapsed_time(_("Whole elapsed time for format post-analysis:"), measure);

            g_object_set_data(G_OBJECT(format), "speed_measure", NULL);
            free(measure);

            break;

        default:
            assert(false);
            break;

    }

    return true;

}


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
    speed_measure *measure;                 /* Suivi des progressions      */
    struct timeval point;                   /* Point de mesure courant     */

    switch (action)
    {
        case PGA_DISASSEMBLY_STARTED:

            measure = (speed_measure *)calloc(1, sizeof(speed_measure));
            g_object_set_data(G_OBJECT(binary), "speed_measure", measure);

            gettimeofday(&point, NULL);
            measure->usages[0] = point.tv_sec * 1000000 + point.tv_usec;

            break;

        case PGA_DISASSEMBLY_ENDED:

            measure = (speed_measure *)g_object_get_data(G_OBJECT(binary), "speed_measure");

            gettimeofday(&point, NULL);
            measure->usages[1] = point.tv_sec * 1000000 + point.tv_usec;

            show_elapsed_time(_("Whole elapsed time for disassembly:"), measure);

            g_object_set_data(G_OBJECT(binary), "speed_measure", NULL);
            free(measure);

            break;

        default:
            assert(false);
            break;

    }

}
