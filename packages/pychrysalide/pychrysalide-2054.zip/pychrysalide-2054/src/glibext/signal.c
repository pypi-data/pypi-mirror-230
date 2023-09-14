
/* Chrysalide - Outil d'analyse de fichiers binaires
 * signal.c - encadrement des signaux supplémentaire par rapport à celui de la GLib
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


#include "signal.h"


#include <assert.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdbool.h>
#include <gobject/gvaluecollector.h>



/* Prototype pour le transfert d'exécution. */
typedef void (* GSignalCallback) (gpointer, ...);


/* Informations concernant une diffusion de signal */
typedef struct _gsignal_wrapper_info
{
    gpointer instance;                      /* Instance GLib initiatrice   */

    GClosure *closure;                      /* Glue pour les appels        */

    GType return_type;                      /* Type de la valeur retournée */
    guint n_params;                         /* Nombre de paramètres        */
    const GType *param_types;               /* Type des paramètres associés*/

    GValue return_value;                    /* Valeur de retour            */
    GValue instance_and_params[0];          /* Instance & paramètres       */

} gsignal_wrapper_info;


/* Transmet un signal dans le contexte principal. */
static gboolean to_main_wrapper(gsignal_wrapper_info *);

/* Réceptionne un signal et redirige son exécution. */
static void carry_signal_to_main_thread(gsignal_wrapper_info *, ...);



/******************************************************************************
*                                                                             *
*  Paramètres  : info = collecteur d'informations sur la diffusion.           *
*                                                                             *
*  Description : Transmet un signal dans le contexte principal.               *
*                                                                             *
*  Retour      : FALSE / G_SOURCE_REMOVE pour arrêter la transmission.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean to_main_wrapper(gsignal_wrapper_info *info)
{
    g_closure_invoke(info->closure, NULL/*&info->return_value*/,
                     info->n_params + 1, info->instance_and_params,
                     NULL);

    return G_SOURCE_REMOVE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = collecteur d'informations sur la diffusion.           *
*                ...  = arguments poussés par la GLib sur la pile.            *
*                                                                             *
*  Description : Réceptionne un signal et redirige son exécution.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void carry_signal_to_main_thread(gsignal_wrapper_info *info, ...)
{
    GValue *param_values;                   /* Paramètres d'appel          */
    va_list ap;                             /* Liste d'arguments sur pile  */
    guint i;                                /* Boucle de parcours          */
    bool static_scope;                      /* Portée des arguments        */
    gchar *error;                           /* Eventuelle erreur inattendue*/

    //g_value_init(&info->return_value, info->return_type & ~G_SIGNAL_TYPE_STATIC_SCOPE);

    if (G_IS_VALUE(info->instance_and_params))
        g_value_unset(info->instance_and_params);

    g_value_init(info->instance_and_params, G_TYPE_FROM_INSTANCE(info->instance));
    g_value_set_instance(info->instance_and_params, info->instance);

    param_values = info->instance_and_params + 1;

    va_start(ap, info);

    error = NULL;

    for (i = 0; i < info->n_params; i++)
    {
        if (G_IS_VALUE(param_values + i))
            g_value_unset(param_values + i);

        static_scope = info->param_types[i] & G_SIGNAL_TYPE_STATIC_SCOPE;

        G_VALUE_COLLECT_INIT(param_values + i,
                             info->param_types[i] & ~G_SIGNAL_TYPE_STATIC_SCOPE,
                             ap, static_scope ? G_VALUE_NOCOPY_CONTENTS : 0,
                             &error);

        if (error != NULL)
        {
            fprintf(stderr, "%s: %s", G_STRLOC, error);
            g_free(error);
            break;
        }

    }

    va_end(ap);

    if (error == NULL)
        g_idle_add_full(G_PRIORITY_HIGH_IDLE, (GSourceFunc)to_main_wrapper, info, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instance = object GLib à l'origine de l'émission.            *
*                signal   = identification du signal à réceptionner.          *
*                handler  = fonction C servant de réceptacle.                 *
*                data     = éventuelle donnée de l'utilisateur à ajouter.     *
*                marshal  = précise la fonction de transfert des arguments.   *
*                flags    = fournit quelques indications supplémentaires.     *
*                                                                             *
*  Description : Reproduit le comportement de la fonction g_signal_connect(). *
*                                                                             *
*  Retour      : Identifiant supérieur zéro en cas de succès.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gulong _g_signal_connect_to_main(gpointer instance, const gchar *signal, GCallback handler, gpointer data, GClosureMarshal marshal, GConnectFlags flags)
{
    guint signal_id;                        /* Identifiant du signal visé  */
    GSignalQuery query;                     /* Information sur le signal   */
    gsignal_wrapper_info *info;             /* Encapsulation des données   */

    /* Collection d'informations */

    signal_id = g_signal_lookup(signal, G_TYPE_FROM_INSTANCE(instance));

    g_signal_query(signal_id, &query);
    assert(query.signal_id != 0);

    /* Allocation adaptée */

    info = calloc(1, sizeof(gsignal_wrapper_info) + sizeof(GValue) * (query.n_params + 1));

    info->instance = instance;

    if (flags & G_CONNECT_SWAPPED)
        info->closure = g_cclosure_new_swap(handler, data, NULL);
    else
        info->closure = g_cclosure_new(handler, data, NULL);

    g_closure_ref(info->closure);
    g_closure_sink(info->closure);

    g_closure_set_marshal(info->closure, marshal);

    info->return_type = query.return_type;
    info->n_params = query.n_params;
    info->param_types = query.param_types;

    assert(query.return_type == G_TYPE_NONE);

    return g_signal_connect_swapped(instance, signal, G_CALLBACK(carry_signal_to_main_thread), info);

}
