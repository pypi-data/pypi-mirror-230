
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gdb.c - débogage à l'aide de gdb.
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


#include "gdb.h"



#include <assert.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>


#include "gdb-int.h"
#include "helpers.h"
#include "helpers_arm.h"
#include "helpers_arm64.h"
#include "tcp.h"
#include "utils.h"
#include "../../common/cpp.h"
#include "../../format/format.h"








/* Initialise la classe du débogueur utilisant gdb. */
static void g_gdb_debugger_class_init(GGdbDebuggerClass *);

/* Procède à l'initialisation du débogueur utilisant gdb. */
static void g_gdb_debugger_init(GGdbDebugger *);

/* Supprime toutes les références externes. */
static void g_gdb_debugger_dispose(GGdbDebugger *);

/* Procède à la libération totale de la mémoire. */
static void g_gdb_debugger_finalize(GGdbDebugger *);


/* Met en marche le débogueur utilisant un serveur GDB. */
static bool g_gdb_debugger_run(GGdbDebugger *);

/* Remet en marche le débogueur utilisant un serveur GDB. */
//static bool g_gdb_debugger_resume(GGdbDebugger *);

/* Tue le débogueur utilisant un serveur GDB. */
static bool g_gdb_debugger_kill(GGdbDebugger *);






/* --------------------------- ENTREES / SORTIES BASIQUES --------------------------- */


/* Lit une valeur quelconque à une adresse arbitraire.  */
static bool g_gdb_debugger_read_memory(GGdbDebugger *, virt_t, size_t, ...);

/* Ecrit une valeur quelconque à une adresse arbitraire.  */
static bool g_gdb_debugger_write_memory(GGdbDebugger *, virt_t, size_t, ...);

/* Liste l'ensemble des registres appartenant à un groupe. */
static char **g_gdb_debugger_get_register_names(const GGdbDebugger *, const char *, size_t *);

/* Indique la taille associée à un registre donné. */
static unsigned int g_gdb_debugger_get_register_size(const GGdbDebugger *, const char *);

/* Effectue la lecture d'un registre donné. */
static bool g_gdb_debugger_read_register(GGdbDebugger *, const char *, size_t, ...);

/* Effectue l'écriture d'un registre donné. */
static bool g_gdb_debugger_write_register(GGdbDebugger *, const char *, size_t, ...);



/* ------------------------- MANIPULATION DE L'ETAT COURANT ------------------------- */


/* Détermine le point d'exécution courant. */
static bool g_gdb_debugger_get_current_pc(GGdbDebugger *, virt_t *);

/* Remonte la pile d'appels jusqu'au point courant. */
static bool g_gdb_debugger_compute_call_stack(GGdbDebugger *, virt_t **, size_t *);



/* --------------------------- GESTION DES POINTS D'ARRET --------------------------- */


/* Ajoute un point d'arrêt basique en mémoire. */
static gdb_breakpoint *g_gdb_debugger_enable_memory_breakpoint(GGdbDebugger *, virt_t);

/* Retire un point d'arrêt basique en mémoire. */
static bool g_gdb_debugger_disable_memory_breakpoint(GGdbDebugger *, gdb_breakpoint *);



/* -------------------------- CONTROLE DU FLOT D'EXECUTION -------------------------- */


/* Redémarre le processus de débogage lié à un serveur GDB. */
static bool g_gdb_debugger_restart(GGdbDebugger *);

/* Remet en marche le débogueur utilisant un serveur GDB. */
static bool g_gdb_debugger_resume(GGdbDebugger *);












/* Détermine l'identifiant du thread principal courant. */
static char *g_gdb_debugger_get_active_thread(GGdbDebugger *);






/* ------------------------ ACCUEIL D'EVENEMENTS ASYNCHRONES ------------------------ */








/* Indique le type défini par la GLib pour le débogueur gdb. */
G_DEFINE_TYPE(GGdbDebugger, g_gdb_debugger, G_TYPE_BINARY_DEBUGGER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe de débogueur à initialiser.                   *
*                                                                             *
*  Description : Initialise la classe du débogueur utilisant gdb.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_debugger_class_init(GGdbDebuggerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GBinaryDebuggerClass *parent;           /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_gdb_debugger_dispose;
    object->finalize = (GObjectFinalizeFunc)g_gdb_debugger_finalize;

    parent = G_BINARY_DEBUGGER_CLASS(klass);

    parent->read_mem = (read_mem_any_fc)g_gdb_debugger_read_memory;
    parent->write_mem = (write_mem_any_fc)g_gdb_debugger_write_memory;
    parent->get_reg_names = (get_reg_names_fc)g_gdb_debugger_get_register_names;
    parent->get_reg_size = (get_reg_size_fc)g_gdb_debugger_get_register_size;
    parent->read_reg = (read_write_reg_any_fc)g_gdb_debugger_read_register;
    parent->write_reg = (read_write_reg_any_fc)g_gdb_debugger_write_register;

    parent->get_current_pc = (get_current_pc_fc)g_gdb_debugger_get_current_pc;
    parent->get_call_stack = (get_call_stack_fc)g_gdb_debugger_compute_call_stack;

    parent->enable_bp = (enable_mem_bp_fc)g_gdb_debugger_enable_memory_breakpoint;
    parent->disable_bp = (disable_mem_bp_fc)g_gdb_debugger_disable_memory_breakpoint;

    parent->restart = (restart_debugger_fc)g_gdb_debugger_restart;
    parent->resume = (resume_debugger_fc)g_gdb_debugger_resume;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance de débogueur à préparer.                 *
*                                                                             *
*  Description : Procède à l'initialisation du débogueur utilisant gdb.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_debugger_init(GGdbDebugger *debugger)
{
    GBinaryDebugger *parent;                /* Instance parente            */

    parent = G_BINARY_DEBUGGER(debugger);

    parent->run = (basic_debugger_fc)g_gdb_debugger_run;
    //parent->resume = (resume_debugger_fc)g_gdb_debugger_resume;
    parent->kill = (basic_debugger_fc)g_gdb_debugger_kill;

    //parent->get_reg_values = (get_register_values_fc)get_register_values_using_gdb_debugger;

    //debugger->cond = g_cond_new();
    //debugger->mutex = g_mutex_new();


    // FIXME
    //debugger->compute_cstack = compute_call_stack_for_arm64;
    //debugger->fill_mem_bp = fill_memory_breakpoint_cmd_for_arm64;




}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_debugger_dispose(GGdbDebugger *debugger)
{
    if (debugger->stream != NULL)
        g_object_unref(G_OBJECT(debugger->stream));

    if (debugger->support != NULL)
        g_object_unref(G_OBJECT(debugger->support));

    if (debugger->target != NULL)
        g_object_unref(G_OBJECT(debugger->target));

    G_OBJECT_CLASS(g_gdb_debugger_parent_class)->dispose(G_OBJECT(debugger));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_debugger_finalize(GGdbDebugger *debugger)
{
    G_OBJECT_CLASS(g_gdb_debugger_parent_class)->finalize(G_OBJECT(debugger));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire représenter à déboguer.                     *
*                server = nom ou adresse du serveur à contacter.              *
*                port   = port de connexion.                                  *
*                                                                             *
*  Description : Crée un débogueur utilisant un serveur GDB distant.          *
*                                                                             *
*  Retour      : Instance de débogueur mise en place ou NULL.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinaryDebugger *g_gdb_debugger_new(GLoadedBinary *binary, const char *server, unsigned short port)
{
    GGdbDebugger *result;                   /* Débogueur à retourner       */
    GExeFormat *format;                     /* Format du binaire chargé    */
    const char *arch;                       /* Architecture d'exécution    */
    GArchProcessor *proc;                   /* Processeur lié au binaire   */
    char service[sizeof(XSTR(UINT16_MAX)) + 1]; /* Conversion requise      */

    result = g_object_new(G_TYPE_GDB_DEBUGGER, NULL);

    G_BINARY_DEBUGGER(result)->binary = binary;
    g_object_ref(G_OBJECT(binary));

    /* Propriétés de la cible */

    format = g_loaded_binary_get_format(binary);

    result->endian = g_binary_format_get_endianness(G_BIN_FORMAT(format));

    arch = g_exe_format_get_target_machine(format);

    if (strcmp(arch, "armv7") == 0)
        result->ops = get_arm_operations();
    else
        result->ops = NULL;

    g_object_unref(G_OBJECT(format));

    if (result->ops == NULL)
        goto ggdn_error;

    proc = g_loaded_binary_get_processor(binary);

    result->msize = g_arch_processor_get_memory_size(proc);

    g_object_unref(G_OBJECT(proc));

    /* Mise en place des modules auxialiaires */

    snprintf(service, sizeof(service), "%hu", port);

    result->stream = g_gdb_tcp_client_new(server, service, result);
    if (result->stream == NULL) goto ggdn_error;

    result->support = g_gdb_support_new(result->stream);

    result->target = g_gdb_target_new(result->stream);
    if (result->target == NULL) goto ggdn_error;

    return G_BINARY_DEBUGGER(result);

 ggdn_error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}








/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à lancer.                               *
*                                                                             *
*  Description : Met en marche le débogueur utilisant un serveur GDB.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_run(GGdbDebugger *debugger)
{



    GGdbPacket *packet;

    bool test;

    const char *data;
    size_t len;


    int sig;
    vmpa_t addr;
    pid_t thread;


    debugger->stream = g_gdb_tcp_client_new("127.0.0.1", "6666", NULL);
    if (debugger->stream == NULL) return false;


    printf("Connection done !\n");



    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "?");


    test = g_gdb_stream_send_packet(debugger->stream, packet);



    printf(" >> Paquet '%s' bien envoyé ? %s\n", "?", test ? "oui" : "non");



    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    packet = g_gdb_stream_recv_packet(debugger->stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    printf(" << Réception de '%s'\n", data);





    get_stop_reply_sig_info(packet, &sig, &addr, &thread, SRE_LITTLE);

    g_signal_emit_by_name(debugger, "halted", sig, addr, thread);



    return true;

}




/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                                                                             *
*  Description : Tue le débogueur utilisant un serveur GDB.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_kill(GGdbDebugger *debugger)
{


#if 0
    int ret;                                /* Bilan de l'appel système    */

    ret = kill(debugger->child, SIGKILL);
    if (ret != 0) perror("kill");

    debugger->child = 0;

    g_mutex_lock(debugger->mutex);
    debugger->run_again = TRUE;
    g_cond_signal(debugger->cond);
    g_mutex_unlock(debugger->mutex);
#endif
    return true;

}









/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                                                                             *
*  Description : Détermine l'identifiant du thread principal courant.         *
*                                                                             *
*  Retour      : Identifiant du thread actif principal ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_gdb_debugger_get_active_thread(GGdbDebugger *debugger)
{
    char *result;                           /* Identifiant à renvoyer      */
    GGdbPacket *packet;                     /* Paquet de communication     */
    bool status;                            /* Bilan d'une communication   */
    const char *data;                       /* Données reçues à analyser   */
    const char *start;                      /* Début d'identification      */
    const char *end;                        /* Fin d'identification        */

    result = NULL;

    /* Envoi de la requête */

    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "?");

    status = g_gdb_stream_send_packet(debugger->stream, packet);

    if (!status)
        goto ggdgat_exit;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(debugger->stream);

    g_gdb_packet_get_data(packet, &data, NULL, NULL);

    start = strstr(data, "thread:");
    if (start == NULL) goto ggdgat_exit;

    start += sizeof("thread:") - 1 /* '\0' */;

    end = strstr(start, ";");
    if (end == NULL) goto ggdgat_exit;

    result = strndup(start, end - start);

 ggdgat_exit:

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    return result;

}




















/* ---------------------------------------------------------------------------------- */
/*                             ENTREES / SORTIES BASIQUES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                addr     = emplacement en mémoire à venir consulter.         *
*                size     = taille des données mises en jeu.                  *
*                ...      = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Lit une valeur quelconque à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_read_memory(GGdbDebugger *debugger, virt_t addr, size_t size, ...)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    char cmd[1 + VMPA_MAX_LEN + 3];         /* Commande à émettre          */
    GGdbPacket *packet;                     /* Paquet de communication     */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de données reçues  */
    va_list ap;                             /* Liste variable d'arguments  */
    uint8_t *val8;                          /* Valeur sur 8 bits           */
    uint16_t *val16;                        /* Valeur sur 16 bits          */
    uint16_t conv16;                        /* Valeur adaptée sur 16 bits  */
    uint32_t *val32;                        /* Valeur sur 32 bits          */
    uint32_t conv32;                        /* Valeur adaptée sur 32 bits  */
    uint64_t *val64;                        /* Valeur sur 64 bits          */
    uint64_t conv64;                        /* Valeur adaptée sur 64 bits  */

    /* Envoi de la requête */

    cmd[0] = 'm';

    result = translate_virt_to_hex(debugger, addr, &cmd[1]);

    switch (size)
    {
        case 8:
            strcat(cmd, ",1");
            break;

        case 16:
            strcat(cmd, ",2");
            break;

        case 32:
            strcat(cmd, ",4");
            break;

        case 64:
            strcat(cmd, ",8");
            break;

        default:
            assert(false);
            result = false;
            goto ggdrm_exit;
            break;

    }

    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, cmd);

    result = g_gdb_stream_send_packet(debugger->stream, packet);

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    if (!result)
        goto ggdrm_exit;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(debugger->stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    if (is_error_code(data, len))
    {
        result = false;
        goto ggdrm_error;
    }

    va_start(ap, size);

    switch (size)
    {
        case 8:
            val8 = va_arg(ap, uint8_t *);
            result = hex_to_u8(data, val8);
            break;

        case 16:
            val16 = va_arg(ap, uint16_t *);
            result = hex_to_u16(data, &conv16);
            *val16 = from_u16(&conv16, debugger->endian);
            break;

        case 32:
            val32 = va_arg(ap, uint32_t *);
            result = hex_to_u32(data, &conv32);
            *val32 = from_u32(&conv32, debugger->endian);
            break;

        case 64:
            val64 = va_arg(ap, uint64_t *);
            result = hex_to_u64(data, &conv64);
            *val64 = from_u64(&conv64, debugger->endian);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    va_end(ap);

 ggdrm_error:

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

 ggdrm_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler.                            *
*                addr     = emplacement en mémoire à venir consulter.         *
*                size     = taille des données mises en jeu.                  *
*                ...      = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Lit une valeur quelconque à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_write_memory(GGdbDebugger *debugger, virt_t addr, size_t size, ...)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    char cmd[1 + 3 * VMPA_MAX_LEN + 3];     /* Commande à émettre          */
    va_list ap;                             /* Liste variable d'arguments  */
    const uint8_t *val8;                    /* Valeur sur 8 bits           */
    const uint16_t *val16;                  /* Valeur sur 16 bits          */
    uint16_t conv16;                        /* Valeur adaptée sur 16 bits  */
    const uint32_t *val32;                  /* Valeur sur 32 bits          */
    uint32_t conv32;                        /* Valeur adaptée sur 32 bits  */
    const uint64_t *val64;                  /* Valeur sur 64 bits          */
    uint64_t conv64;                        /* Valeur adaptée sur 64 bits  */
    char hexval[17];                        /* Valeur sous forme hexa      */
    GGdbPacket *packet;                     /* Paquet de communication     */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de données reçues  */

    /* Envoi de la requête */

    cmd[0] = 'M';

    result = translate_virt_to_hex(debugger, addr, &cmd[1]);

    va_start(ap, size);

    switch (size)
    {
        case 8:
            val8 = va_arg(ap, uint8_t *);
            result = u8_to_hex(val8, hexval);

            strcat(cmd, ",1:");
            strcat(cmd, hexval);
            break;

        case 16:
            val16 = va_arg(ap, uint16_t *);
            conv16 = to_u16(val16, debugger->endian);
            result = u16_to_hex(&conv16, hexval);

            strcat(cmd, ",2:");
            strcat(cmd, hexval);
            break;

        case 32:
            val32 = va_arg(ap, uint32_t *);
            conv32 = to_u32(val32, debugger->endian);
            result = u32_to_hex(&conv32, hexval);

            strcat(cmd, ",4:");
            strcat(cmd, hexval);
            break;

        case 64:
            val64 = va_arg(ap, uint64_t *);
            conv64 = to_u64(val64, debugger->endian);
            result = u16_to_hex(&conv64, hexval);

            strcat(cmd, ",8:");
            strcat(cmd, hexval);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    if (!result)
        goto ggdwm_exit;

    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, cmd);

    result = g_gdb_stream_send_packet(debugger->stream, packet);

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    if (!result)
        goto ggdwm_exit;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(debugger->stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    if (len == 3 && data[0] == 'E')
    {
        result = false;
        goto ggdrm_error;
    }

 ggdrm_error:

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

 ggdwm_exit:

    va_end(ap);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                group    = éventuel groupe de registres ciblé ou NULL.       *
*                count    = nombre d'éléments dans la liste de noms. [OUT]    *
*                                                                             *
*  Description : Liste l'ensemble des registres appartenant à un groupe.      *
*                                                                             *
*  Retour      : Liste de noms à libérer de la mémoire après utilisation.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char **g_gdb_debugger_get_register_names(const GGdbDebugger *debugger, const char *group, size_t *count)
{
    return g_gdb_target_get_register_names(debugger->target, group, count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                name     = désignation du registre visé.                     *
*                                                                             *
*  Description : Indique la taille associée à un registre donné.              *
*                                                                             *
*  Retour      : Taille en bits, ou 0 si le registre n'a pas été trouvé.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static unsigned int g_gdb_debugger_get_register_size(const GGdbDebugger *debugger, const char *name)
{
    return g_gdb_target_get_register_size(debugger->target, name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                reg      = désignation humaine du register à consulter.      *
*                size     = taille des données mises en jeu.                  *
*                ...      = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Effectue la lecture d'un registre donné.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_read_register(GGdbDebugger *debugger, const char *reg, size_t size, ...)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    va_list ap;                             /* Liste variable d'arguments  */
    uint8_t *val8;                          /* Valeur sur 8 bits           */
    uint16_t *val16;                        /* Valeur sur 16 bits          */
    uint32_t *val32;                        /* Valeur sur 32 bits          */
    uint64_t *val64;                        /* Valeur sur 64 bits          */

    va_start(ap, size);

    switch (size)
    {
        case 8:
            val8 = va_arg(ap, uint8_t *);
            result = g_gdb_target_read_register(debugger->target, debugger->stream, debugger->endian,
                                                reg, 8, val8);
            break;

        case 16:
            val16 = va_arg(ap, uint16_t *);
            result = g_gdb_target_read_register(debugger->target, debugger->stream, debugger->endian,
                                                reg, 16, val16);
            break;

        case 32:
            val32 = va_arg(ap, uint32_t *);
            result = g_gdb_target_read_register(debugger->target, debugger->stream, debugger->endian,
                                                reg, 32, val32);
            break;

        case 64:
            val64 = va_arg(ap, uint64_t *);
            result = g_gdb_target_read_register(debugger->target, debugger->stream, debugger->endian,
                                                reg, 64, val64);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    va_end(ap);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler.                            *
*                reg      = désignation humaine du register à consulter.      *
*                size     = taille des données mises en jeu.                  *
*                ...      = emplacement de la valeur à écrire.                *
*                                                                             *
*  Description : Effectue l'écriture d'un registre donné.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_write_register(GGdbDebugger *debugger, const char *reg, size_t size, ...)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    va_list ap;                             /* Liste variable d'arguments  */
    const uint8_t *val8;                    /* Valeur sur 8 bits           */
    const uint16_t *val16;                  /* Valeur sur 16 bits          */
    const uint32_t *val32;                  /* Valeur sur 32 bits          */
    const uint64_t *val64;                  /* Valeur sur 64 bits          */

    va_start(ap, size);

    switch (size)
    {
        case 8:
            val8 = va_arg(ap, const uint8_t *);
            result = g_gdb_target_write_register(debugger->target, debugger->stream, debugger->endian,
                                                 reg, 8, val8);
            break;

        case 16:
            val16 = va_arg(ap, const uint16_t *);
            result = g_gdb_target_write_register(debugger->target, debugger->stream, debugger->endian,
                                                 reg, 16, val16);
            break;

        case 32:
            val32 = va_arg(ap, const uint32_t *);
            result = g_gdb_target_write_register(debugger->target, debugger->stream, debugger->endian,
                                                 reg, 32, val32);
            break;

        case 64:
            val64 = va_arg(ap, const uint64_t *);
            result = g_gdb_target_write_register(debugger->target, debugger->stream, debugger->endian,
                                                 reg, 64, val64);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    va_end(ap);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           MANIPULATION DE L'ETAT COURANT                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                pc       = adresse de l'instruction courante. [OUT]          *
*                                                                             *
*  Description : Détermine le point d'exécution courant.                      *
*                                                                             *
*  Retour      : Bilan de la récupération.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_get_current_pc(GGdbDebugger *debugger, virt_t *pc)
{
    bool result;                            /* Bilan à retourner           */

    result = debugger->ops->get_pc(debugger, pc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger  = débogueur à consulter.                           *
*                callstack = pile d'appels reconstituée. [OUT]                *
*                size      = taille de cette pile. [OUT]                      *
*                                                                             *
*  Description : Remonte la pile d'appels jusqu'au point courant.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_compute_call_stack(GGdbDebugger *debugger, virt_t **callstack, size_t *size)
{
    bool result;                            /* Bilan global à retourner    */

    if (debugger->ops->compute_cstack != NULL)
        result = debugger->ops->compute_cstack(debugger, callstack, size);

    else
        result = false;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             GESTION DES POINTS D'ARRET                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                addr     = emplacement du point mémoire à traiter.           *
*                                                                             *
*  Description : Ajoute un point d'arrêt basique en mémoire.                  *
*                                                                             *
*  Retour      : Structure de suivi mise en place pour l'occasion, voire NULL.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gdb_breakpoint *g_gdb_debugger_enable_memory_breakpoint(GGdbDebugger *debugger, virt_t addr)
{
    gdb_breakpoint *result;                 /* Nouveau suivi à retourner   */
    char cmd[3 + VMPA_MAX_LEN + 3];         /* Commande à émettre          */
    bool status;                            /* Bilan d'une opération       */
    const char *kind;                       /* Taille spécifique du point  */
    GGdbPacket *packet;                     /* Paquet de communication     */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de données reçues  */
    GBinaryDebugger *dbg;                   /* Autre version du débogueur  */
    const uint8_t *bp;                      /* Données du point d'arrêt    */
    size_t bp_len;                          /* Quantité de ces données     */
    uint8_t memory[16];                     /* Sauvegarde de la mémoire    */

    result = NULL;

    /* Si l'utilisation de la commande dédiée est possible */
    if (1)  //////// TODO
    {
        /* Envoi de la requête */

        strcpy(cmd, "Z0,");

        status = translate_virt_to_hex(debugger, addr, &cmd[3]);

        if (!status)
            goto ggdemb_exit;

        kind = debugger->ops->get_bp_kind(debugger, addr);

        if (kind == NULL)
            goto ggdemb_exit;

        strcat(cmd, kind);

        packet = g_gdb_stream_get_free_packet(debugger->stream);

        g_gdb_packet_start_new_command(packet);
        g_gdb_packet_append(packet, cmd);

        status = g_gdb_stream_send_packet(debugger->stream, packet);

        g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

        if (!status)
            goto ggdemb_exit;

        /* Réception de la réponse */

        packet = g_gdb_stream_recv_packet(debugger->stream);

        g_gdb_packet_get_data(packet, &data, &len, NULL);

        if (is_error_code(data, len))
        {
            g_gdb_stream_mark_packet_as_free(debugger->stream, packet);
            goto ggdemb_fallback;
        }

        if (strcmp(data, "OK") != 0)
        {
            g_gdb_stream_mark_packet_as_free(debugger->stream, packet);
            goto ggdemb_fallback;
        }

        g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

        /* Constitution d'un dossier de suivi */

        result = (gdb_breakpoint *)malloc(sizeof(gdb_breakpoint));

        result->is_z = true;

        result->kind = kind;

    }

    else
    {

 ggdemb_fallback:

        dbg = G_BINARY_DEBUGGER(debugger);

        /* Détermination du point d'arrêt */

        bp = debugger->ops->get_bp_data(debugger, addr, &bp_len);

        assert(bp_len <= 16);

        /* Sauvegarde de la mémoire courante */

        status = g_binary_debugger_read_memory_data(dbg, addr, memory, bp_len);

        if (!status) goto ggdemb_exit;

        /* Application du point d'arrêt */

        status = g_binary_debugger_write_memory_data(dbg, addr, bp, bp_len);

        if (!status) goto ggdemb_exit;

        /* Constitution d'un dossier de suivi */

        result = (gdb_breakpoint *)malloc(sizeof(gdb_breakpoint));

        result->is_z = false;

        memcpy(result->memory, memory, bp_len);
        result->len = bp_len;

    }

    init_raw_breakpoint((raw_breakpoint *)result, addr);

 ggdemb_exit:

    return result;
}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                bp       = point d'arrêt à traiter.                          *
*                                                                             *
*  Description : Retire un point d'arrêt basique de la mémoire ciblée.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_disable_memory_breakpoint(GGdbDebugger *debugger, gdb_breakpoint *bp)
{
    bool result;                            /* Bilan à retourner           */
    char cmd[3 + VMPA_MAX_LEN + 3];         /* Commande à émettre          */
    bool status;                            /* Bilan d'une opération       */
    GGdbPacket *packet;                     /* Paquet de communication     */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de données reçues  */
    GBinaryDebugger *dbg;                   /* Autre version du débogueur  */

    result = false;

    /* Si l'utilisation de la commande dédiée est requise */
    if (bp->is_z)
    {
        /* Envoi de la requête */

        strcpy(cmd, "z0,");

        status = translate_virt_to_hex(debugger, bp->raw.addr, &cmd[3]);

        if (!status)
            goto ggddmb_exit;

        strcat(cmd, bp->kind);

        packet = g_gdb_stream_get_free_packet(debugger->stream);

        g_gdb_packet_start_new_command(packet);
        g_gdb_packet_append(packet, cmd);

        status = g_gdb_stream_send_packet(debugger->stream, packet);

        g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

        if (!status)
            goto ggddmb_exit;

        /* Réception de la réponse */

        packet = g_gdb_stream_recv_packet(debugger->stream);

        g_gdb_packet_get_data(packet, &data, &len, NULL);

        if (is_error_code(data, len))
        {
            g_gdb_stream_mark_packet_as_free(debugger->stream, packet);
            goto ggddmb_exit;
        }

        if (strcmp(data, "OK") != 0)
        {
            g_gdb_stream_mark_packet_as_free(debugger->stream, packet);
            goto ggddmb_exit;
        }

        g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

        result = true;

    }

    else
    {
        dbg = G_BINARY_DEBUGGER(debugger);

        result = g_binary_debugger_write_memory_data(dbg, bp->raw.addr, bp->memory, bp->len);

    }

 ggddmb_exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                            CONTROLE DU FLOT D'EXECUTION                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à redémarrer.                           *
*                                                                             *
*  Description : Redémarre le processus de débogage lié à un serveur GDB.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_restart(GGdbDebugger *debugger)
{
    bool result;                            /* Bilan à retourner           */
    GGdbPacket *packet;                     /* Paquet de communication     */
    return true;
    /* Envoi de la requête */

    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "R00");

    result = g_gdb_stream_send_packet(debugger->stream, packet);

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                                                                             *
*  Description : Remet en marche le débogueur utilisant un serveur GDB.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_debugger_resume(GGdbDebugger *debugger)
{
    bool result;                            /* Bilan à retourner           */
    //char *id;                               /* Identifiant de thread       */
    GGdbPacket *packet;                     /* Paquet de communication     */
    //const char *data;                       /* Données reçues à analyser   */

    static bool _twice = false;


    if (!_twice && 0)
    {

    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "$QPassSignals:e;10;14;17;1a;1b;1c;21;24;25;2c;4c;");

    result = g_gdb_stream_send_packet(debugger->stream, packet);

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    if (!result)
        goto ggdhmb_exit;

    }






    /* Envoi de la requête */

    /*
    id = g_gdb_debugger_get_active_thread(debugger);
    if (id == NULL) return false;

    printf("ID : %s\n", id);
    */

    /*
    id = g_gdb_support_get_id(debugger->support);
    if (id == NULL) return false;

    printf("ID : %s\n", id);
    */

    packet = g_gdb_stream_get_free_packet(debugger->stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "vCont;c:-1");
    //g_gdb_packet_append(packet, "vCont;c:p256f.-1");


    /*
    if (_twice)
    {
    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "vCont;c:p");
    g_gdb_packet_append(packet, id);
    g_gdb_packet_append(packet, ".");
    g_gdb_packet_append(packet, id);
    }
    else
    {
        _twice = true;
    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "vCont;c:p");
    g_gdb_packet_append(packet, id);
    g_gdb_packet_append(packet, ".-1");
    }
    */





    result = g_gdb_stream_send_packet(debugger->stream, packet);

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);

    if (!result)
        goto ggdhmb_exit;

    /* Réception de la réponse */
    /*
    packet = g_gdb_stream_recv_packet(debugger->stream);

    g_gdb_packet_get_data(packet, &data, NULL, NULL);

    printf("Ack cont...\n");

    //result = (strcmp(data, "OK") == 0);

    g_gdb_stream_mark_packet_as_free(debugger->stream, packet);
    */
 ggdhmb_exit:

    _twice = true;

    return result;

}














/* ---------------------------------------------------------------------------------- */
/*                          ACCUEIL D'EVENEMENTS ASYNCHRONES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance liée à un débogueur GDB à manipuler.     *
*                signum   = indentifiant du signal concerné.                  *
*                                                                             *
*  Description : Réagit à la réception d'un signal par le programme étudié.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_debugger_receive_signal_reply(GGdbDebugger *debugger, int signum)
{
    virt_t pc;                              /* Position courante du CPU    */
    bool status;                            /* Bilan d'une opération       */
    GBinaryDebugger *base;                  /* Version basique du débogueur*/

    base = G_BINARY_DEBUGGER(debugger);

    status = g_binary_debugger_get_current_pc(base, &pc);

    if (!status)
        pc = VMPA_NO_VIRTUAL;

    on_binary_debugger_stopped(base, pc);

    g_signal_emit_by_name(debugger, "signaled", signum);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance liée à un débogueur GDB à manipuler.     *
*                status   = indication d'état à la sortie.                    *
*                pid      = éventuel identifiant de processus concerné ou -1. *
*                                                                             *
*  Description : Réagit à la sortie d'exécution d'un programme étudié.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_debugger_receive_exit_reply(GGdbDebugger *debugger, int status, pid_t pid)
{
    GBinaryDebugger *base;                  /* Version basique du débogueur*/

    base = G_BINARY_DEBUGGER(debugger);

    on_binary_debugger_finished(base, pid);

    g_signal_emit_by_name(debugger, "exited", status, pid);

}
