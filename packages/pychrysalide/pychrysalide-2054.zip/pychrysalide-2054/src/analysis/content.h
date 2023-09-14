
/* Chrysalide - Outil d'analyse de fichiers binaires
 * content.h - prototypes pour la lecture de données binaires quelconques
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


#ifndef _ANALYSIS_CONTENT_H
#define _ANALYSIS_CONTENT_H


#include <stdbool.h>
#include <glib-object.h>


#include "cattribs.h"
#include "../arch/vmpa.h"
#include "../common/endianness.h"
#include "../common/leb128.h"



#define G_TYPE_BIN_CONTENT             (g_binary_content_get_type())
#define G_BIN_CONTENT(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BIN_CONTENT, GBinContent))
#define G_BIN_CONTENT_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_BIN_CONTENT, GBinContentIface))
#define G_IS_BIN_CONTENT(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BIN_CONTENT))
#define G_IS_BIN_CONTENT_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_BIN_CONTENT))
#define G_BIN_CONTENT_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_BIN_CONTENT, GBinContentIface))


/* Accès à un contenu binaire quelconque (coquille vide) */
typedef struct _GBinContent GBinContent;

/* Accès à un contenu binaire quelconque (interface) */
typedef struct _GBinContentIface GBinContentIface;


/* Détermine le type d'une interface pour la lecture de binaire. */
GType g_binary_content_get_type(void) G_GNUC_CONST;

/* Associe un ensemble d'attributs au contenu binaire. */
void g_binary_content_set_attributes(GBinContent *, GContentAttributes *);

/* Fournit l'ensemble des attributs associés à un contenu. */
GContentAttributes *g_binary_content_get_attributes(const GBinContent *);

/* Donne l'origine d'un contenu binaire. */
GBinContent *g_binary_content_get_root(GBinContent *);

/* Fournit le nom associé au contenu binaire. */
char *g_binary_content_describe(const GBinContent *, bool);

/* Fournit une empreinte unique (SHA256) pour les données. */
const gchar *g_binary_content_get_checksum(GBinContent *);

/* Détermine le nombre d'octets lisibles. */
phys_t g_binary_content_compute_size(const GBinContent *);

/* Détermine la position initiale d'un contenu. */
void g_binary_content_compute_start_pos(const GBinContent *, vmpa2t *);

/* Détermine la position finale d'un contenu. */
void g_binary_content_compute_end_pos(const GBinContent *, vmpa2t *);

/* Avance la tête de lecture d'une certaine quantité de données. */
bool g_binary_content_seek(const GBinContent *, vmpa2t *, phys_t);

/* Donne accès à une portion des données représentées. */
const bin_t *g_binary_content_get_raw_access(const GBinContent *, vmpa2t *, phys_t);

/* Fournit une portion des données représentées. */
bool g_binary_content_read_raw(const GBinContent *, vmpa2t *, phys_t, bin_t *);

/* Lit un nombre non signé sur quatre bits. */
bool g_binary_content_read_u4(const GBinContent *, vmpa2t *, bool *, uint8_t *);

/* Lit un nombre non signé sur un octet. */
bool g_binary_content_read_u8(const GBinContent *, vmpa2t *, uint8_t *);

/* Lit un nombre non signé sur deux octets. */
bool g_binary_content_read_u16(const GBinContent *, vmpa2t *, SourceEndian, uint16_t *);

/* Lit un nombre non signé sur quatre octets. */
bool g_binary_content_read_u32(const GBinContent *, vmpa2t *, SourceEndian, uint32_t *);

/* Lit un nombre non signé sur huit octets. */
bool g_binary_content_read_u64(const GBinContent *, vmpa2t *, SourceEndian, uint64_t *);


#define g_binary_content_read_s4(c, a, l, v) g_binary_content_read_u4(c, a, l, (uint8_t *)v)
#define g_binary_content_read_s8(c, a, v) g_binary_content_read_u8(c, a, (uint8_t *)v)
#define g_binary_content_read_s16(c, a, e, v) g_binary_content_read_u16(c, a, e, (uint16_t *)v)
#define g_binary_content_read_s32(c, a, e, v) g_binary_content_read_u32(c, a, e, (uint32_t *)v)
#define g_binary_content_read_s64(c, a, e, v) g_binary_content_read_u64(c, a, e, (uint64_t *)v)


/* Lit un nombre non signé encodé au format LEB128. */
bool g_binary_content_read_uleb128(const GBinContent *, vmpa2t *, uleb128_t *);

/* Lit un nombre signé encodé au format LEB128. */
bool g_binary_content_read_leb128(const GBinContent *, vmpa2t *, leb128_t *);



#endif  /* _ANALYSIS_CONTENT_H */
