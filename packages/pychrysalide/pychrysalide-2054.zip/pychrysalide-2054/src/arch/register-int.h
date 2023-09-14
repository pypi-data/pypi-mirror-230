
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register-int.h - définitions internes pour la représentation générique d'un registre
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _ARCH_REGISTER_INT_H
#define _ARCH_REGISTER_INT_H


#include "register.h"
#include "../analysis/storage/serialize-int.h"



/* Produit une empreinte à partir d'un registre. */
typedef guint (* reg_hash_fc) (const GArchRegister *);

/* Compare un registre avec un autre. */
typedef int (* reg_compare_fc) (const GArchRegister *, const GArchRegister *);

/* Traduit un registre en version humainement lisible. */
typedef void (* reg_print_fc) (const GArchRegister *, GBufferLine *);

/* Indique si le registre correspond à ebp ou similaire. */
typedef bool (* reg_is_base_pointer_fc) (const GArchRegister *);

/* Indique si le registre correspond à esp ou similaire. */
typedef bool (* reg_is_stack_pointer_fc) (const GArchRegister *);

/* Charge un contenu depuis une mémoire tampon. */
typedef bool (* load_register_fc) (GArchRegister *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
typedef bool (* store_register_fc) (GArchRegister *, GObjectStorage *, packed_buffer_t *);


/* Représentation d'un registre (instance) */
struct _GArchRegister
{
    GObject parent;                         /* A laisser en premier        */

};

/* Représentation d'un registre (classe) */
struct _GArchRegisterClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    reg_hash_fc hash;                       /* Production d'empreinte      */
    reg_compare_fc compare;                 /* Comparaison de registres    */
    reg_print_fc print;                     /* Impression du registre      */
    reg_is_base_pointer_fc is_bp;           /* Correspondance avec ebp     */
    reg_is_stack_pointer_fc is_sp;          /* Correspondance avec esp     */

    load_register_fc load;                  /* Chargement depuis un tampon */
    store_register_fc store;                /* Conservation dans un tampon */

};



#endif  /* _ARCH_REGISTER_INT_H */
