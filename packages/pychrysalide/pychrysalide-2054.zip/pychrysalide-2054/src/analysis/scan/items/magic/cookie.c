
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cookie.c - chargement des motifs de reconnaissance de contenus
 *
 * Copyright (C) 2023 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "cookie.h"


#include <assert.h>


#include <i18n.h>


#include "../../../../core/logs.h"



/* Référence des bibliothèques de reconnaissance */
static magic_t __magic_cookie = 0;



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Charge les motifs de reconnaissance de contenus.             *
*                                                                             *
*  Retour      : Bilan de l'opération de chargemement.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_magic_cookie(void)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan d'une opération       */

    __magic_cookie = magic_open(0);

    ret = magic_load(__magic_cookie, NULL);
    result = (ret != -1);

    if (!result)
        log_variadic_message(LMT_EXT_ERROR, _("cannot load magic database: %s"), magic_error(__magic_cookie));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge les motifs de reconnaissance de contenus.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_magic_cookie(void)
{
    magic_close(__magic_cookie);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : flags = forme de reconnaissance à préparer.                  *
*                                                                             *
*  Description : Fournit la référence aux mécanismes de reconnaissance.       *
*                                                                             *
*  Retour      : Cookie prêt à emploi.                                        * 
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

magic_t get_magic_cookie(int flags)
{
    magic_t result;                         /* Référence à retourner       */
#ifndef NDEBUG
    int ret;                                /* Bilan de la préparation     */
#endif

    result = __magic_cookie;
    assert(result != 0);

#ifndef NDEBUG
    ret = magic_setflags(result, flags);
    assert(ret != -1);
#else
    magic_setflags(result, flags);
#endif

    return result;

}
