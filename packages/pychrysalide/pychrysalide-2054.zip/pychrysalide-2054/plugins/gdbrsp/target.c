
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target.c - gestion des éléments propres à l'architecture reconnue par GDB
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


#include "target.h"


#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "utils.h"
#include "../../common/cpp.h"
#include "../../common/extstr.h"
#include "../../common/xml.h"



/* Définitions de registres */

typedef struct _arch_register_t
{
    char *name;                             /* Nom de registre             */
    unsigned int size;                      /* Taille en bits              */

} arch_register_t;

typedef struct _target_cpu_t
{
    char *label;                            /* Désignation de l'ensemble   */

    arch_register_t *regs;                  /* Définition des registres    */
    unsigned int count;                     /* Quantité de ces définitions */

} target_cpu_t;


/* Indications quant à l'interfaçage client/serveur GDB (instance) */
struct _GGdbTarget
{
    GObject parent;                         /* A laisser en premier        */

    target_cpu_t **defs;                    /* Liste de définitions        */
    size_t count;                           /* Taille de cette même liste  */

    bool read_single_register;              /* Lecture spécifique permise ?*/
    bool write_single_register;             /* Ecriture spécifique valide ?*/

};

/* Indications quant à l'interfaçage client/serveur GDB (classe) */
struct _GGdbTargetClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des détails d'interfaçage GDB. */
static void g_gdb_target_class_init(GGdbTargetClass *);

/* Procède à l'initialisation des détails d'interfaçage GDB. */
static void g_gdb_target_init(GGdbTarget *);

/* Supprime toutes les références externes. */
static void g_gdb_target_dispose(GGdbTarget *);

/* Procède à la libération totale de la mémoire. */
static void g_gdb_target_finalize(GGdbTarget *);

/* Charge la définition d'un groupe de registres. */
static bool g_gdb_target_load_register_definition(GGdbTarget *, GGdbStream *, const char *);

/* Recherche l'indice correspondant à un registre donné. */
static bool g_gdb_target_find_register_index(const GGdbTarget *, const char *, unsigned int *);

/* Recherche la position correspondant à un registre donné. */
static bool g_gdb_target_find_register_offset(const GGdbTarget *, unsigned int, size_t *);



/* Indique le type défini par la GLib pour les détails d'interfaçage GDB. */
G_DEFINE_TYPE(GGdbTarget, g_gdb_target, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe de débogueur à initialiser.                   *
*                                                                             *
*  Description : Initialise la classe des détails d'interfaçage GDB.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_target_class_init(GGdbTargetClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_gdb_target_dispose;
    object->finalize = (GObjectFinalizeFunc)g_gdb_target_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = instance de débogueur à préparer.                   *
*                                                                             *
*  Description : Procède à l'initialisation des détails d'interfaçage GDB.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_target_init(GGdbTarget *target)
{
    target->defs = NULL;
    target->count = 0;

    target->read_single_register = true;
    target->write_single_register = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_target_dispose(GGdbTarget *target)
{
    G_OBJECT_CLASS(g_gdb_target_parent_class)->dispose(G_OBJECT(target));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_target_finalize(GGdbTarget *target)
{
    G_OBJECT_CLASS(g_gdb_target_parent_class)->finalize(G_OBJECT(target));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication ouvert avec le débogueur.     *
*                                                                             *
*  Description : Crée une définition des détails d'interfaçage GDB.           *
*                                                                             *
*  Retour      : Instance de détails mise en place ou NULL.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbTarget *g_gdb_target_new(GGdbStream *stream)
{
    GGdbTarget *result;                     /* Débogueur à retourner       */
    GGdbPacket *packet;                     /* Paquet de communication GDB */
    bool status;                            /* Bilan d'une communication   */

    const char *data;                       /* Données reçues du serveur   */
    size_t len;                             /* Quantité de ces données     */
    char *xmldata;                          /* Données modifiables         */
    xmlDocPtr xdoc;                         /* Document XML récupéré       */
    xmlXPathContextPtr context;             /* Contexte d'analyse associé  */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    unsigned int i;                         /* Boucle de parcours          */
    char *access;                           /* Chemin d'accès à un élément */
    char *xmlref;                           /* Référence de définitions    */




    result = NULL;


    //goto end;

    //goto skip;


    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    //g_gdb_packet_append(packet, "qTargeted:multiprocess+;xmlRegisters");
    g_gdb_packet_append(packet, "qXfer:features:read:target.xml:0,3fff");

    //g_gdb_packet_append(packet, "qTargeted:multiprocess+;swbreak+;hwbreak+;qRelocInsn+;fork-events+;vfork-events+;exec-events+;vContTargeted+;QThreadEvents+;no-resumed+");



    status = g_gdb_stream_send_packet(stream, packet);
    if (!status) goto ggtn_failed;




    g_gdb_stream_mark_packet_as_free(stream, packet);

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    printf(" << Réception de '%s'\n", data);

    /* Marqueur de fin placé au début ?! */
    if (data[0] != 'l')
        goto ggtn_failed;

    xmldata = strdup(data + 1);

    /**
     * On cherche à éviter la déconvenue suivante avec la libxml2 :
     *
     *    noname.xml:12: namespace error : Namespace prefix xi on include is not defined
     *      <xi:include href="aarch64-core.xml"/>
     */

    xmldata = strrpl(xmldata, "xi:include", "include");

    if (!load_xml_from_memory(xmldata, len - 1, &xdoc, &context))
        goto ggtn_failed;


    result = g_object_new(G_TYPE_GDB_TARGET, NULL);


    xobject = get_node_xpath_object(context, "/target/include");

    for (i = 0; i < XPATH_OBJ_NODES_COUNT(xobject); i++)
    {
        asprintf(&access, "/target/include[position()=%u]", i + 1);

        xmlref = get_node_prop_value(context, access, "href");

        free(access);

        if (xmlref != NULL)
        {
            printf("REF>> %s\n", xmlref);
            /*static bool */g_gdb_target_load_register_definition(result, stream, xmlref);

            free(xmlref);

        }

    }

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    close_xml_file(xdoc, context);

    free(xmldata);










    //result = g_object_new(G_TYPE_GDB_TARGET, NULL);


 ggtn_failed:

    g_gdb_stream_mark_packet_as_free(stream, packet);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                stream = flux de communication ouvert avec le débogueur.     *
*                name   = désignation des définitions de registres à charger. *
*                                                                             *
*  Description : Charge la définition d'un groupe de registres.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_target_load_register_definition(GGdbTarget *target, GGdbStream *stream, const char *name)
{
    bool result;                            /* Bilan à retourner           */
    GGdbPacket *packet;                     /* Paquet de communication GDB */
    bool status;                            /* Bilan d'une communication   */
    const char *data;                       /* Données reçues du serveur   */
    size_t len;                             /* Quantité de ces données     */
    xmlDocPtr xdoc;                         /* Document XML récupéré       */
    xmlXPathContextPtr context;             /* Contexte d'analyse associé  */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    target_cpu_t *def;                      /* Nouvelle définition à lire  */
    unsigned int i;                         /* Boucle de parcours          */
    char *access;                           /* Chemin d'accès à un élément */
    char *type;                             /* Espèce de définition        */

    result = false;

    /* Envoi de la requête */

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);

    g_gdb_packet_append(packet, "qXfer:features:read:");
    g_gdb_packet_append(packet, name);
    g_gdb_packet_append(packet, ":0,3fff");

    status = g_gdb_stream_send_packet(stream, packet);
    if (!status) goto ggtlrd_failed;

    g_gdb_stream_mark_packet_as_free(stream, packet);

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    //printf(">>>> '%s'\n", data);

    /* Marqueur de fin placé au début ?! */
    if (data[0] != 'l')
        goto ggtlrd_failed;

    if (!load_xml_from_memory(data + 1, len - 1, &xdoc, &context))
        goto ggtlrd_failed;

    /* Chargement des définitions */

    xobject = get_node_xpath_object(context, "/feature/*");

    def = (target_cpu_t *)calloc(1, sizeof(target_cpu_t));

    def->count = XPATH_OBJ_NODES_COUNT(xobject);
    def->regs = (arch_register_t *)calloc(def->count, sizeof(arch_register_t));

    for (i = 0; i < XPATH_OBJ_NODES_COUNT(xobject); i++)
    {
        asprintf(&access, "/feature/*[position()=%u]", i + 1);

        type = get_node_name(context, access);

        if (strcmp(type, "reg") == 0)
        {
            def->regs[i].name = get_node_prop_value(context, access, "name");
            def->regs[i].size = atoi(get_node_prop_value(context, access, "bitsize"));

            //printf("load reg '%s' (%u)\n", def->regs[i].name, def->regs[i].size);

        }

        free(type);

        free(access);

    }

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    close_xml_file(xdoc, context);

    /* Intégration finale */

    target->defs = (target_cpu_t **)realloc(target->defs, ++target->count * sizeof(target_cpu_t *));

    target->defs[target->count - 1] = def;

 ggtlrd_failed:

    g_gdb_stream_mark_packet_as_free(stream, packet);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                group  = éventuel groupe de registres ciblé ou NULL.         *
*                count  = nombre d'éléments dans la liste de noms. [OUT]      *
*                                                                             *
*  Description : Liste l'ensemble des registres appartenant à un groupe.      *
*                                                                             *
*  Retour      : Liste de noms à libérer de la mémoire après utilisation.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char **g_gdb_target_get_register_names(const GGdbTarget *target, const char *group, size_t *count)
{
    char **result;                          /* Désignations à retourner    */
    unsigned int i;                         /* Boucle de parcours #1       */
    const target_cpu_t *rgrp;               /* Groupe de registres         */
    unsigned int j;                         /* Boucle de parcours #2       */

    result = NULL;

    for (i = 0; i < target->count && result == NULL; i++)
    {
        rgrp = target->defs[i];

        if (group != NULL)
        {
            if (strcmp(rgrp->label, group) != 0)
                continue;
        }

        *count = rgrp->count;

        result = (char **)calloc(*count, sizeof(char *));

        for (j = 0; j < *count; j++)
            result[j] = strdup(rgrp->regs[j].name);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                name   = désignation du registre visé.                       *
*                                                                             *
*  Description : Indique la taille associée à un registre donné.              *
*                                                                             *
*  Retour      : Taille en bits, ou 0 si le registre n'a pas été trouvé.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int g_gdb_target_get_register_size(const GGdbTarget *target, const char *name)
{
    unsigned int result;                    /* Taille en bits  à retourner */
    unsigned int i;                         /* Boucle de parcours #1       */
    const target_cpu_t *rgrp;               /* Groupe de registres         */
    unsigned int j;                         /* Boucle de parcours #2       */

    result = 0;

    for (i = 0; i < target->count && result == 0; i++)
    {
        rgrp = target->defs[i];

        for (j = 0; j < rgrp->count; j++)
            if (strcmp(rgrp->regs[j].name, name) == 0)
                result = rgrp->regs[j].size;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                reg    = désignation humaine du register à consulter.        *
*                index  = indice correspondant au registre pour GDB. [OUT]    *
*                                                                             *
*  Description : Recherche l'indice correspondant à un registre donné.        *
*                                                                             *
*  Retour      : Bilan de l'opération : trouvaille ou échec ?                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_target_find_register_index(const GGdbTarget *target, const char *reg, unsigned int *index)
{
    bool result;                            /* Bilan à retourner           */
    unsigned int i;                         /* Boucle de parcours #1       */
    unsigned int j;                         /* Boucle de parcours #2       */

    result = false;

    *index = 0;

    for (i = 0; i < target->count && !result; i++)
        for (j = 0; j < target->defs[i]->count && !result; j++)
        {
            if (strcmp(target->defs[i]->regs[j].name, reg) == 0)
                result = true;
            else
                (*index)++;
        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                index  = indice correspondant au registre pour GDB.          *
*                offset = position de valeur du registre dans du texte. [OUT] *
*                                                                             *
*  Description : Recherche la position correspondant à un registre donné.     *
*                                                                             *
*  Retour      : Bilan de l'opération : trouvaille ou échec ?                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_target_find_register_offset(const GGdbTarget *target, unsigned int index, size_t *offset)
{
    unsigned int i;                         /* Boucle de parcours #1       */
    unsigned int j;                         /* Boucle de parcours #2       */

    *offset = 0;

    for (i = 0; i < target->count && index > 0; i++)
        for (j = 0; j < target->defs[i]->count && index > 0; j++)
        {
            assert(target->defs[i]->regs[j].size % 4 == 0);

            *offset += target->defs[i]->regs[j].size / 4;

            index--;

        }

    return (index == 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                stream = flux de communication ouvert avec le débogueur.     *
*                endian = boutisme de la cible.                               *
*                reg    = désignation humaine du register à consulter.        *
*                size   = taille des données mises en jeu.                    *
*                ...    = emplacement de la valeur lue à conserver. [OUT]     *
*                                                                             *
*  Description : Effectue la lecture d'un registre donné.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_gdb_target_read_register(GGdbTarget *target, GGdbStream *stream, SourceEndian endian, const char *reg, size_t size, ...)
{
    bool result;                            /* Bilan à retourner           */
    unsigned int index;                     /* Indice du registre ciblé    */
    GGdbPacket *packet;                     /* Paquet de communication     */
    char cmd[sizeof(XSTR(UINT_MAX)) + 1];   /* Elément de requête          */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de ces données     */
    const char *raw;                        /* Début de zone à relire      */
    size_t offset;                          /* Position dans la masse      */
    va_list ap;                             /* Liste variable d'arguments  */
    uint8_t *val8;                          /* Valeur sur 8 bits           */
    uint16_t *val16;                        /* Valeur sur 16 bits          */
    uint16_t conv16;                        /* Valeur adaptée sur 16 bits  */
    uint32_t *val32;                        /* Valeur sur 32 bits          */
    uint32_t conv32;                        /* Valeur adaptée sur 32 bits  */
    uint64_t *val64;                        /* Valeur sur 64 bits          */
    uint64_t conv64;                        /* Valeur adaptée sur 64 bits  */

    result = g_gdb_target_find_register_index(target, reg, &index);
    if (!result) goto ggtrr_error;

    /**
     * Essai avec la méthode précise.
     */

    if (!target->read_single_register)
        goto read_all_register_fallback;

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "p");

    snprintf(cmd, sizeof(cmd), "%x", index);
    g_gdb_packet_append(packet, cmd);

    result = g_gdb_stream_send_packet(stream, packet);

    g_gdb_stream_mark_packet_as_free(stream, packet);

    if (!result)
        goto ggtrr_error;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    if (len != 0 && !is_error_code(data, len))
        raw = data;

    else
    {
        target->read_single_register = false;

        g_gdb_stream_mark_packet_as_free(stream, packet);

 read_all_register_fallback:

        /**
         * Utilisation de la méthode de masse au besoin...
         */

        packet = g_gdb_stream_get_free_packet(stream);

        g_gdb_packet_start_new_command(packet);
        g_gdb_packet_append(packet, "g");

        result = g_gdb_stream_send_packet(stream, packet);

        g_gdb_stream_mark_packet_as_free(stream, packet);

        if (!result)
            goto ggtrr_error;

        /* Réception de la réponse */

        packet = g_gdb_stream_recv_packet(stream);

        g_gdb_packet_get_data(packet, &data, &len, NULL);

        result = g_gdb_target_find_register_offset(target, index, &offset);

        if (!result || offset > len)
            goto ggtrr_exit;

        raw = data + offset;
        len -= offset;

    }

    /* Lecture finale de la valeur recherchée */

    va_start(ap, size);

    switch (size)
    {
        case 8:
            val8 = va_arg(ap, uint8_t *);
            result = hex_to_u8(raw, val8);
            break;

        case 16:
            val16 = va_arg(ap, uint16_t *);
            result = hex_to_u16(raw, &conv16);
            *val16 = from_u16(&conv16, endian);
            break;

        case 32:
            val32 = va_arg(ap, uint32_t *);
            result = hex_to_u32(raw, &conv32);
            *val32 = from_u32(&conv32, endian);
            break;

        case 64:
            val64 = va_arg(ap, uint64_t *);
            result = hex_to_u64(raw, &conv64);
            *val64 = from_u64(&conv64, endian);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    va_end(ap);

 ggtrr_exit:

    g_gdb_stream_mark_packet_as_free(stream, packet);

 ggtrr_error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble d'informations liées à l'architecture.     *
*                stream = flux de communication ouvert avec le débogueur.     *
*                endian = boutisme de la cible.                               *
*                reg    = désignation humaine du register à consulter.        *
*                size   = taille des données mises en jeu.                    *
*                ...    = emplacement de la valeur à écrire.                  *
*                                                                             *
*  Description : Effectue l'écriture d'un registre donné.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_gdb_target_write_register(GGdbTarget *target, GGdbStream *stream, SourceEndian endian, const char *reg, size_t size, ...)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    va_list ap;                             /* Liste variable d'arguments  */
    const uint8_t *val8;                    /* Valeur sur 8 bits           */
    const uint16_t *val16;                  /* Valeur sur 16 bits          */
    uint16_t conv16;                        /* Valeur adaptée sur 16 bits  */
    const uint32_t *val32;                  /* Valeur sur 32 bits          */
    uint32_t conv32;                        /* Valeur adaptée sur 32 bits  */
    const uint64_t *val64;                  /* Valeur sur 64 bits          */
    uint64_t conv64;                        /* Valeur adaptée sur 64 bits  */
    char hexval[17];                        /* Valeur sous forme hexa      */
    unsigned int index;                     /* Indice du registre ciblé    */
    GGdbPacket *packet;                     /* Paquet de communication     */
    char cmd[sizeof(XSTR(UINT_MAX)) + 1];   /* Elément de requête          */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de ces données     */
    char *new;                              /* Nouvelles valeurs générales */
    size_t offset;                          /* Position dans la masse      */

    /* Tronc commun : récupération de la valeur */

    va_start(ap, size);

    switch (size)
    {
        case 8:
            val8 = va_arg(ap, uint8_t *);
            result = u8_to_hex(val8, hexval);
            break;

        case 16:
            val16 = va_arg(ap, uint16_t *);
            conv16 = to_u16(val16, endian);
            result = u16_to_hex(&conv16, hexval);
            break;

        case 32:
            val32 = va_arg(ap, uint32_t *);
            conv32 = to_u32(val32, endian);
            result = u32_to_hex(&conv32, hexval);
            break;

        case 64:
            val64 = va_arg(ap, uint64_t *);
            conv64 = to_u64(val64, endian);
            result = u16_to_hex(&conv64, hexval);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    va_end(ap);

    if (!result)
        goto ggtwr_error;

    /* Préparation de la suite */

    result = g_gdb_target_find_register_index(target, reg, &index);
    if (!result) goto ggtwr_error;

    /**
     * Essai avec la méthode précise.
     */

    if (!target->write_single_register)
        goto write_all_register_fallback;

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "P");

    snprintf(cmd, sizeof(cmd), "%x", index);
    g_gdb_packet_append(packet, cmd);

    g_gdb_packet_append(packet, "=");

    g_gdb_packet_append(packet, hexval);

    result = g_gdb_stream_send_packet(stream, packet);

    g_gdb_stream_mark_packet_as_free(stream, packet);

    if (!result)
        goto ggtwr_error;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    if (is_error_code(data, len) || strcmp(data, "OK") != 0)
    {
        target->write_single_register = false;

        g_gdb_stream_mark_packet_as_free(stream, packet);

 write_all_register_fallback:

        /**
         * Utilisation de la méthode de masse au besoin...
         */

        /* Lecture de l'ensemble des registres */

        packet = g_gdb_stream_get_free_packet(stream);

        g_gdb_packet_start_new_command(packet);
        g_gdb_packet_append(packet, "g");

        result = g_gdb_stream_send_packet(stream, packet);

        g_gdb_stream_mark_packet_as_free(stream, packet);

        if (!result)
            goto ggtwr_error;

        /* Réception de la réponse et mise à jour */

        packet = g_gdb_stream_recv_packet(stream);

        g_gdb_packet_get_data(packet, &data, &len, NULL);

        result = g_gdb_target_find_register_offset(target, index, &offset);

        if (!result || offset > len)
            goto ggtwr_exit;

        new = (char *)malloc(len);

        memcpy(new, data, len);
        memcpy(new + offset, hexval, strlen(hexval));

        g_gdb_stream_mark_packet_as_free(stream, packet);

        /* Ecrasement de tous les registres */

        packet = g_gdb_stream_get_free_packet(stream);

        g_gdb_packet_start_new_command(packet);
        g_gdb_packet_append(packet, "G");

        g_gdb_packet_append(packet, new);
        free(new);

        result = g_gdb_stream_send_packet(stream, packet);

        g_gdb_stream_mark_packet_as_free(stream, packet);

        if (!result)
            goto ggtwr_error;

        /* Réception de la réponse */

        packet = g_gdb_stream_recv_packet(stream);

        g_gdb_packet_get_data(packet, &data, &len, NULL);

        result = (!is_error_code(data, len) && strcmp(data, "OK") == 0);

    }

 ggtwr_exit:

    g_gdb_stream_mark_packet_as_free(stream, packet);

 ggtwr_error:

    return result;

}
