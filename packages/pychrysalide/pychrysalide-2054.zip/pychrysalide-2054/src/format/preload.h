
/* Chrysalide - Outil d'analyse de fichiers binaires
 * preload.h - prototypes pour le préchargement d'instructions à partir d'un format
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


#ifndef _FORMAT_PRELOAD_H
#define _FORMAT_PRELOAD_H


#include <glib-object.h>


#include "../analysis/db/items/comment.h"
#include "../arch/instruction.h"



#define G_TYPE_PRELOAD_INFO             g_preload_info_get_type()
#define G_PRELOAD_INFO(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PRELOAD_INFO, GPreloadInfo))
#define G_IS_PRELOAD_INFO(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PRELOAD_INFO))
#define G_PRELOAD_INFO_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PRELOAD_INFO, GPreloadInfoClass))
#define G_IS_PRELOAD_INFO_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PRELOAD_INFO))
#define G_PRELOAD_INFO_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PRELOAD_INFO, GPreloadInfoClass))


/* Préchargement d'origine formatée (instance) */
typedef struct _GPreloadInfo GPreloadInfo;

/* Préchargement d'origine formatée (classe) */
typedef struct _GPreloadInfoClass GPreloadInfoClass;


/* Indique le type défini pour un préchargement à partir d'un format. */
GType g_preload_info_get_type(void);

/* Crée une nouvelle collecte d'informations préchargées. */
GPreloadInfo *g_preload_info_new(void);

/* Copie le contenu d'une collecte d'informations préchargées. */
void g_preload_info_copy(GPreloadInfo *, GPreloadInfo *);

/* Verrouille les accès à la liste des instructions. */
void g_preload_info_lock_instructions(GPreloadInfo *);

/* Déverrouille les accès à la liste des instructions. */
void g_preload_info_unlock_instructions(GPreloadInfo *);

/* Ajoute une instruction supplémentaire aux préchargements. */
bool g_preload_info_add_instruction(GPreloadInfo *, GArchInstruction *);

/* Ajoute une instruction supplémentaire aux préchargements. */
bool _g_preload_info_add_instruction(GPreloadInfo *, GArchInstruction *);

/* Détermine si une instruction existe sur un espace donné. */
bool _g_preload_info_has_instruction_for(GPreloadInfo *, const mrange_t *);

/* Détermine si une instruction est présente à un point donné. */
bool _g_preload_info_has_instruction_at(GPreloadInfo *, const vmpa2t *);

/* Indique la quantité d'instructions préchargées disponibles. */
size_t _g_preload_info_count_instructions(const GPreloadInfo *);

/* Fournit une instruction préchargée donnée. */
GArchInstruction *_g_preload_info_grab_instruction(const GPreloadInfo *, size_t);

/* Dépile une instruction présente dans les préchargements. */
GArchInstruction *g_preload_info_pop_instruction(GPreloadInfo *);

/* Retire des préchargements toutes les instructions. */
void _g_preload_info_drain_instructions(GPreloadInfo *);

/* Verrouille les accès à la liste des commentaires. */
void g_preload_info_lock_comments(GPreloadInfo *);

/* Déverrouille les accès à la liste des commentaires. */
void g_preload_info_unlock_comments(GPreloadInfo *);

/* Ajoute un commentaire supplémentaire aux préchargements. */
void g_preload_info_add_comment(GPreloadInfo *, GDbComment *);

/* Ajoute un commentaire supplémentaire aux préchargements. */
void _g_preload_info_add_comment(GPreloadInfo *, GDbComment *);

/* Recherche un commentaire dans des préchargements. */
GDbComment *_g_preload_info_find_comment_at(GPreloadInfo *, const vmpa2t *);

/* Recherche un commentaire dans des préchargements. */
GDbComment *g_preload_info_find_comment_at(GPreloadInfo *, const vmpa2t *, size_t *);

/* Remplace un commentaire par un autre à un emplacement donné. */
void g_preload_info_replace_comment_at(GPreloadInfo *, size_t, GDbComment *);

/* Indique la quantité de commentaires préchargés disponibles. */
size_t _g_preload_info_count_comments(const GPreloadInfo *);

/* Fournit un commentaire préchargé donné. */
GDbComment *_g_preload_info_grab_comment(const GPreloadInfo *, size_t);

/* Retire des préchargements tous les commentaires. */
void _g_preload_info_drain_comments(GPreloadInfo *);



#endif  /* _FORMAT_PRELOAD_H */
