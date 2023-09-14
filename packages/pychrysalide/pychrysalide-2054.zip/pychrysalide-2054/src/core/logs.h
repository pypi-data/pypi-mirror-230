
/* Chrysalide - Outil d'analyse de fichiers binaires
 * logs.h - prototypes pour la diffusion de messages d'alerte ou informatifs
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _CORE_LOGS_H
#define _CORE_LOGS_H


#include <dlfcn.h>
#include <errno.h>
#include <netdb.h>
#include <stdarg.h>
#include <string.h>
#include <openssl/err.h>


#include <i18n.h>



/* Type de messages disponibles */
typedef enum _LogMessageType
{
    LMT_INFO,                               /* Information sur l'exécution */
    LMT_PROCESS,                            /* Début de tâche quelconque   */
    LMT_WARNING,                            /* Avertissment à remonter     */
    LMT_BAD_BINARY,                         /* Binaire malformé            */
    LMT_ERROR,                              /* Erreur de traitement interne*/
    LMT_EXT_ERROR,                          /* Erreur de traitement externe*/

    LMT_COUNT

} LogMessageType;



/* ------------------------ EMISSIONS DE MESSAGES CLASSIQUES ------------------------ */


/* Fournit la verbosité des messages système. */
LogMessageType get_log_verbosity(void);

/* Définit la verbosité des messages système. */
void set_log_verbosity(LogMessageType);

/* Affiche un message dans le journal des messages système. */
void log_simple_message(LogMessageType, const char *);

/* Construit un message pour le journal des messages système. */
char *build_variadic_message(const char *, va_list);

/* Affiche un message dans le journal des messages système. */
void log_variadic_message(LogMessageType, const char *, ...);



/* ------------------------ REMONTEE D'EVENEMENTS INATTENDUS ------------------------ */


#define LOG_ERROR(tp, msg) \
    log_variadic_message(tp, "[%s:%u] %s", __FUNCTION__, __LINE__, msg)

#if (_POSIX_C_SOURCE >= 200112L) && ! _GNU_SOURCE

#   define STRERROR_SAFE(buf, ptr)                                                                      \
    do                                                                                                  \
    {                                                                                                   \
        strerror_r(errno, buf, sizeof(buf));                                                            \
        ptr = buf;                                                                                      \
    }                                                                                                   \
    while (0)

#else

#   define STRERROR_SAFE(buf, ptr)                                                                      \
    ptr = strerror_r(errno, buf, sizeof(buf))                                                           \

#endif

#define LOG_ERROR_N(func)                                                                               \
    do                                                                                                  \
    {                                                                                                   \
        char __msg[1024];                                                                               \
        const char *__msg_ptr;                                                                          \
        STRERROR_SAFE(__msg, __msg_ptr);                                                                \
        log_variadic_message(LMT_EXT_ERROR, "[%s:%u] %s: %s", __FUNCTION__, __LINE__, func, __msg_ptr); \
    }                                                                                                   \
    while (0)

#define LOG_ERROR_DL_N(func)                                                                            \
    do                                                                                                  \
    {                                                                                                   \
        const char *__msg_ptr;                                                                          \
        __msg_ptr = dlerror();                                                                          \
        if (__msg_ptr == NULL)                                                                          \
            __msg_ptr = "???";                                                                          \
        log_variadic_message(LMT_EXT_ERROR, "[%s:%u] %s: %s", __FUNCTION__, __LINE__, func, __msg_ptr); \
    }                                                                                                   \
    while (0)

#define LOG_ERROR_GAI_N(func, errcode)                                                                  \
    do                                                                                                  \
    {                                                                                                   \
        char __msg[1024];                                                                               \
        const char *__msg_ptr;                                                                          \
        if (errcode == EAI_SYSTEM)                                                                      \
            STRERROR_SAFE(__msg, __msg_ptr);                                                            \
        else                                                                                            \
            __msg_ptr = gai_strerror(errcode);                                                          \
        log_variadic_message(LMT_EXT_ERROR, "[%s:%u] %s: %s", __FUNCTION__, __LINE__, func, __msg_ptr); \
    }                                                                                                   \
    while (0)

#define LOG_ERROR_REGCOMP(preg, errcode)                                                                \
    do                                                                                                  \
    {                                                                                                   \
        char __msg[1024];                                                                               \
        regerror(errcode, preg, __msg, sizeof(__msg));                                                  \
        log_variadic_message(LMT_EXT_ERROR, "[%s:%u] regcomp: %s", __FUNCTION__, __LINE__, __msg);      \
    }                                                                                                   \
    while (0)

#define LOG_ERROR_OPENSSL                                                                               \
    do                                                                                                  \
    {                                                                                                   \
        unsigned long __err;                                                                            \
        const char *__msg;                                                                              \
        __err = ERR_get_error();                                                                        \
        __msg = ERR_reason_error_string(__err);                                                         \
        if (__msg != NULL)                                                                              \
            log_variadic_message(LMT_EXT_ERROR, "[%s:%u] %s", __FUNCTION__, __LINE__, __msg);           \
        else                                                                                            \
            log_variadic_message(LMT_EXT_ERROR, "[%s:%u] unamed error", __FUNCTION__, __LINE__);        \
    }                                                                                                   \
    while (0)

#define LOG_ERROR_SQLITE(db, func)                                                                      \
    do                                                                                                  \
    {                                                                                                   \
        const char *__msg;                                                                              \
        __msg = (db != NULL ? sqlite3_errmsg(db) : "unabled to allocate memory");                       \
        log_variadic_message(LMT_EXT_ERROR, "[%s:%u] %s: %s", __FUNCTION__, __LINE__, func, __msg);     \
    }                                                                                                   \
    while (0)



#endif  /* _CORE_LOGS_H */
