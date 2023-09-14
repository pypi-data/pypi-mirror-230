
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.h - prototypes pour un assistanat dans la manipulation des paquets GDB
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


#ifndef _DEBUG_GDBRSP_HELPERS_H
#define _DEBUG_GDBRSP_HELPERS_H


#include "gdb.h"
#include "packet.h"



/* Traduit une adresse en chaîne hexadécimale pour GDB. */
bool translate_virt_to_hex(const GGdbDebugger *, virt_t, char *);






/* -------------------------- PAQUETS DES REPONSES D'ARRET -------------------------- */


/* Récupère les informations liées à un arrêt suite à signal. */
bool get_stop_reply_sig_info(const GGdbPacket *, int *, vmpa_t *, pid_t *, SourceEndian);



/* ---------------------------------------------------------------------------------- */
/*                            PAQUETS DES REPONSES D'ARRET                            */
/* ---------------------------------------------------------------------------------- */










#endif  /* _DEBUG_GDBRSP_HELPERS_H */
