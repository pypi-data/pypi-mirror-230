
/* Chrysalide - Outil d'analyse de fichiers binaires
 * logs.c - diffusion de messages d'alerte ou informatifs
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "logs.h"


#include <malloc.h>
#include <string.h>


#include "../common/extstr.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../gui/core/items.h"
#   include "../gui/panels/log.h"
#endif



/* ------------------------ EMISSIONS DE MESSAGES CLASSIQUES ------------------------ */


/* Tranche d'allocation pour les messages complexes */
#define VARIADIC_LOG_BUFSIZE 256

/* Conserve le niveau de filtre des messages */
static LogMessageType _verbosity = LMT_COUNT;


/* Affiche un message dans le terminal courant. */
static void print_message_without_gui(LogMessageType, const char *);



/* ---------------------------------------------------------------------------------- */
/*                          EMISSIONS DE MESSAGES CLASSIQUES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit la verbosité des messages système.                   *
*                                                                             *
*  Retour      : Plus faible niveau des types de message affichés.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

LogMessageType get_log_verbosity(void)
{
    return _verbosity;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : level = plus faible niveau des types de message affichés.    *
*                                                                             *
*  Description : Définit la verbosité des messages système.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_log_verbosity(LogMessageType level)
{
    _verbosity = level;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = espèce du message à ajouter.                          *
*                msg  = message à faire apparaître à l'écran.                 *
*                                                                             *
*  Description : Affiche un message dans le journal des messages système.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void log_simple_message(LogMessageType type, const char *msg)
{
#ifdef INCLUDE_GTK_SUPPORT
    GEditorItem *item;                      /* Eventuel affichage présent  */
#endif

    if (type >= _verbosity)
    {
#ifdef INCLUDE_GTK_SUPPORT

        item = find_editor_item_by_type(G_TYPE_LOG_PANEL);

        if (item != NULL)
        {
            g_log_panel_add_message(G_LOG_PANEL(item), type, msg);
            g_object_unref(G_OBJECT(item));
        }

        else

#endif

            print_message_without_gui(type, msg);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fmt  = format du message à faire apparaître à l'écran.       *
*                args = éventuels arguments venant compléter le message.      *
*                                                                             *
*  Description : Construit un message pour le journal des messages système.   *
*                                                                             *
*  Retour      : Message prêt à emploi à libérer après usage.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_variadic_message(const char *fmt, va_list args)
{
    char *result;                           /* Tampon constitué à renvoyer */
    size_t len;                             /* Taille tampon disponible    */
    int ret;                                /* Bilan d'une impression      */
    char *ptr;                              /* Nouvelle allocation         */
    va_list ap;                             /* Liste d'arguments variable  */

    len = VARIADIC_LOG_BUFSIZE;
    result = calloc(len, sizeof(char));

    while (result != NULL)
    {
        va_copy(ap, args);
        ret = vsnprintf(result, len, fmt, ap);
        va_end(ap);

        if (ret >= 0 && ret < len) break;

        else
        {
            if (ret > -1) len += 1;     /* glibc 2.1 */
            else len *= 2;              /* glibc 2.0 */

            if ((ptr = realloc(result, len)) == NULL)
            {
                free(result);
                result = NULL;
            }
            else result = ptr;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = espèce du message à ajouter.                          *
*                fmt  = format du message à faire apparaître à l'écran.       *
*                ...  = éventuels arguments venant compléter le message.      *
*                                                                             *
*  Description : Affiche un message dans le journal des messages système.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void log_variadic_message(LogMessageType type, const char *fmt, ...)
{
    va_list ap;                             /* Liste d'arguments variable  */
    char *buffer;                           /* Tampon du msg reconstitué   */

    va_start(ap, fmt);
    buffer = build_variadic_message(fmt, ap);
    va_end(ap);

    if (buffer != NULL)
    {
        log_simple_message(type, buffer);

        free(buffer);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = espèce du message à ajouter.                          *
*                msg  = message à faire apparaître à l'écran.                 *
*                                                                             *
*  Description : Affiche un message dans le terminal courant.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void print_message_without_gui(LogMessageType type, const char *msg)
{
    char *formatted;                        /* Copie formatée du message   */
    const char *prefix;                     /* Introduction de la ligne    */

    formatted = strdup(msg);

#define FOREGROUND_LIGHT_GRAY "\e[37m"
#define FOREGROUND_RED "\e[91m"

#define BACKGROUND_RED "\e[101m"

#define BOLD "\e[1m"
#define ITALIC "\e[3m"

#define RESET "\e[0m"

    switch (type)
    {
        case LMT_INFO:
        default:
            prefix = "i";
            break;

        case LMT_PROCESS:
            prefix = FOREGROUND_LIGHT_GRAY "*" RESET;
            break;

        case LMT_WARNING:
            prefix = FOREGROUND_RED "!" RESET;
            break;

        case LMT_BAD_BINARY:
        case LMT_ERROR:
        case LMT_EXT_ERROR:
            prefix = BACKGROUND_RED "!" RESET;
            break;

    }

    formatted = strrpl(formatted, "<b>", BOLD);
    formatted = strrpl(formatted, "</b>", RESET);

    formatted = strrpl(formatted, "<i>", ITALIC);
    formatted = strrpl(formatted, "</i>", RESET);

    printf("[%s] %s\n", prefix, formatted);

    free(formatted);

}
