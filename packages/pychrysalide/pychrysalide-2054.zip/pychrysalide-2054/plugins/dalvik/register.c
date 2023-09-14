
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.c - aides auxiliaires relatives aux registres Dalvik
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "register.h"


#include <malloc.h>
#include <stdio.h>


#include <arch/register-int.h>
#include <common/sort.h>
#include <core/columns.h>



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Représentation d'un registre Dalvik (instance) */
struct _GDalvikRegister
{
    GArchRegister parent;                   /* Instance parente            */

    uint16_t index;                         /* Indice du registre          */

};


/* Représentation d'un registre Dalvik (classe) */
struct _GDalvikRegisterClass
{
    GArchRegisterClass parent;              /* Classe parente              */

};


#define MAX_REGNAME_LEN 8


/* Initialise la classe des registres Dalvik. */
static void g_dalvik_register_class_init(GDalvikRegisterClass *);

/* Initialise une instance de registre Dalvik. */
static void g_dalvik_register_init(GDalvikRegister *);

/* Supprime toutes les références externes. */
static void g_dalvik_register_dispose(GDalvikRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_register_finalize(GDalvikRegister *);

/* Crée une réprésentation de registre Dalvik. */
static GArchRegister *_g_dalvik_register_new(uint16_t);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Produit une empreinte à partir d'un registre. */
static guint g_dalvik_register_hash(const GDalvikRegister *);

/* Compare un registre avec un autre. */
static int g_dalvik_register_compare(const GDalvikRegister *, const GDalvikRegister *);

/* Traduit un registre en version humainement lisible. */
static void g_dalvik_register_print(const GDalvikRegister *, GBufferLine *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_dalvik_register_load(GDalvikRegister *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_dalvik_register_store(GDalvikRegister *, GObjectStorage *, packed_buffer_t *);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Conservation des registres utilisés */
static GArchRegister **_dalvik_registers = NULL;
static size_t _dreg_count = 0;
G_LOCK_DEFINE_STATIC(_dreg_mutex);


/* Fournit le singleton associé à un registre Dalvik. */
static GArchRegister *get_dalvik_register(uint16_t);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre Dalvik. */
G_DEFINE_TYPE(GDalvikRegister, g_dalvik_register, G_TYPE_ARCH_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres Dalvik.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_class_init(GDalvikRegisterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchRegisterClass *reg;                /* Classe de haut niveau       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_register_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_register_finalize;

    reg = G_ARCH_REGISTER_CLASS(klass);

    reg->hash = (reg_hash_fc)g_dalvik_register_hash;
    reg->compare = (reg_compare_fc)g_dalvik_register_compare;
    reg->print = (reg_print_fc)g_dalvik_register_print;

    reg->load = (load_register_fc)g_dalvik_register_load;
    reg->store = (store_register_fc)g_dalvik_register_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre Dalvik.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_init(GDalvikRegister *reg)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_dispose(GDalvikRegister *reg)
{
    G_OBJECT_CLASS(g_dalvik_register_parent_class)->dispose(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_finalize(GDalvikRegister *reg)
{
    G_OBJECT_CLASS(g_dalvik_register_parent_class)->finalize(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : index = indice du registre correspondant.                    *
*                                                                             *
*  Description : Crée une réprésentation de registre Dalvik.                  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *_g_dalvik_register_new(uint16_t index)
{
    GDalvikRegister *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_DALVIK_REGISTER, NULL);

    result->index = index;

    return G_ARCH_REGISTER(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : index = indice du registre correspondant.                    *
*                                                                             *
*  Description : Crée une réprésentation de registre Dalvik.                  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchRegister *g_dalvik_register_new(uint16_t index)
{
    GArchRegister *result;                  /* Structure à retourner       */

    result = get_dalvik_register(index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre à consulter.                                  *
*                                                                             *
*  Description : Fournit l'indice d'un registre Dalvik.                       *
*                                                                             *
*  Retour      : Inditifiant représentant le registre.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint16_t g_dalvik_register_get_index(const GDalvikRegister *reg)
{
    return reg->index;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = opérande à consulter pour le calcul.                   *
*                                                                             *
*  Description : Produit une empreinte à partir d'un registre.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_dalvik_register_hash(const GDalvikRegister *reg)
{
    return reg->index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier opérande à consulter.                            *
*                b = second opérande à consulter.                             *
*                                                                             *
*  Description : Compare un registre avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_dalvik_register_compare(const GDalvikRegister *a, const GDalvikRegister *b)
{
    int result;                             /* Bilan à retourner           */

    result = sort_unsigned_long(a->index, b->index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg  = registre à transcrire.                                *
*                line = ligne tampon où imprimer l'opérande donné.            *
*                                                                             *
*  Description : Traduit un registre en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_print(const GDalvikRegister *reg, GBufferLine *line)
{
    char key[MAX_REGNAME_LEN];              /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */

    klen = snprintf(key, MAX_REGNAME_LEN, "v%hu", reg->index);

    g_buffer_line_append_text(line, DLC_ASSEMBLY, key, klen, RTT_REGISTER, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg     = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_dalvik_register_load(GDalvikRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *parent;             /* Classe parente à consulter  */

    parent = G_ARCH_REGISTER_CLASS(g_dalvik_register_parent_class);

    result = parent->load(G_ARCH_REGISTER(reg), storage, pbuf);

    if (result)
        result = extract_packed_buffer(pbuf, &reg->index, sizeof(uint16_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg     = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_dalvik_register_store(GDalvikRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *parent;             /* Classe parente à consulter  */

    parent = G_ARCH_REGISTER_CLASS(g_dalvik_register_parent_class);

    result = parent->store(G_ARCH_REGISTER(reg), storage, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, &reg->index, sizeof(uint16_t), true);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          GESTION SOUS FORME DE SINGLETONS                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : index = indice du registre correspondant.                    *
*                                                                             *
*  Description : Fournit le singleton associé à un registre Dalvik.           *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *get_dalvik_register(uint16_t index)
{
    GArchRegister *result;                  /* Structure à retourner       */
    size_t new_count;                       /* Nouvelle taille à considérer*/
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_dreg_mutex);

    if (index >= _dreg_count)
    {
        new_count = index + 1;

        _dalvik_registers = realloc(_dalvik_registers, new_count * sizeof(GArchRegister *));

        for (i = _dreg_count; i < new_count; i++)
            _dalvik_registers[i] = NULL;

        _dreg_count = new_count;

    }

    if (_dalvik_registers[index] == NULL)
        _dalvik_registers[index] = _g_dalvik_register_new(index);

    result = _dalvik_registers[index];

    G_UNLOCK(_dreg_mutex);

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Vide totalement le cache des registres Dalvik.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clean_dalvik_register_cache(void)
{
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_dreg_mutex);

    for (i = 0; i < _dreg_count; i++)
        g_clear_object(&_dalvik_registers[i]);

    if (_dalvik_registers != NULL)
        free(_dalvik_registers);

    _dalvik_registers = NULL;
    _dreg_count = 0;

    G_UNLOCK(_dreg_mutex);

}
