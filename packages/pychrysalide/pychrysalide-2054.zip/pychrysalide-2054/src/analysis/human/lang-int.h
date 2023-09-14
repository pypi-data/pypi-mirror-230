
/* Chrysalide - Outil d'analyse de fichiers binaires
 * lang-int.h - prototypes utiles aux traductions en langages de haut niveau
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_HUMAN_LANG_INT_H
#define _ANALYSIS_HUMAN_LANG_INT_H


#include "lang.h"



/* Complète du texte pour en faire un vrai commentaire. */
typedef void (* encapsulate_comment_fc) (const GCodingLanguage *, char **);

/* Complète du texte pour en faire de vrais commentaires. */
typedef void (* encapsulate_comments_fc) (const GCodingLanguage *, char ***, size_t *);


/* Traduction générique en langage humain (instance) */
struct _GCodingLanguage
{
    GObject parent;                         /* A laisser en premier        */

};

/* Traduction générique en langage humain (classe) */
struct _GCodingLanguageClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    encapsulate_comment_fc encaps_comment;  /* Encadrement de commentaire */
    encapsulate_comments_fc encaps_comments;/* Encadrement de commentaires */

};



#endif  /* _ANALYSIS_HUMAN_LANG_INT_H */
