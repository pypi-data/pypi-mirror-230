
/* Chrysalide - Outil d'analyse de fichiers binaires
 * coder.h - prototypes pour la lecture automatisée des spécifications d'architecture
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _TOOLS_D2C_CODER_H
#define _TOOLS_D2C_CODER_H


#include <stdbool.h>


#include "encoding.h"
#include "pproc.h"
#include "desc/manager.h"
#include "id/manager.h"



/* Suivi des constructions */
typedef struct _rented_coder rented_coder;



/* -------------------------- CONSTRUCTION SELON COMMANDES -------------------------- */


/* Débute la définition d'une fonction de désassemblage. */
rented_coder *create_coder(pre_processor *);

/* Supprime le codeur de la mémoire. */
void delete_coder(rented_coder *);

/* Indique le fichier de définition considéré en entrée. */
const char *get_coder_input_file(const rented_coder *);

/* Spécifie le fichier de définition à prendre en entrée. */
void set_coder_input_file(rented_coder *, const char *);



/* ----------------------------- INFORMATIONS GENERALES ----------------------------- */


/* Enregistre les contours d'une instruction d'assemblage. */
void save_notes_for_coder(rented_coder *, char *, char *, char, const char *);

/* Fournit la désignation nominale d'une instruction. */
char *get_coder_nominal_name(const rented_coder *);

/* Fournit la désignation complète d'une instruction. */
char *get_coder_code_name(const rented_coder *);

/* Fournit le gestionnaire des définitions d'identifiant. */
instr_id *get_coder_instruction_id(const rented_coder *);

/* Fournit le gestionnaire de description d'identifiant. */
instr_desc *get_coder_instruction_desc(const rented_coder *);



/* --------------------------- REPRESENTATION D'ENCODAGES --------------------------- */


/* Fournit un lien vers les spécifications courantes. */
encoding_spec *get_current_encoding_spec(const rented_coder *);

/* Enregistre une définition supplémentaire. */
void push_encoding_spec(rented_coder *, char *, unsigned int);

/* Marque une instruction comme non utilisée. */
void mark_coder_as_useless(rented_coder *coder);



/* --------------------------- GENERATIONS DE CODE SOURCE --------------------------- */


/* Type d'entrée/sortie attendues */
typedef enum _InputOutputType
{
    IOT_UNDEFINED,                          /* Type non défini             */
    IOT_RAW,                                /* Lecture de contenu brut     */
    IOT_FORMAT                              /* Définition d'opérandes      */

} InputOutputType;

/* Regroupement des informations utiles à la génération */
typedef struct _output_info
{
    char *opcodes_dir;                      /* Répertoire pour les opcodes */

    InputOutputType type;                   /* Type des définitions (E/S)  */
    const char *arch;                       /* Architecture à traiter      */
    const char *arch_cn;                    /* Nom de code de l'archi.     */
    const char *guard;                      /* Portion de macro globale    */

    const char *fmt_prefix;                 /* Préfixe pour les opérandes  */

    const char *id_prefix;                  /* Préfixe pour les constantes */
    int id_len;                             /* Largeur des identifiants    */

    bool export;                            /* Exportation dans les entêtes*/
    size_t filename_reuse;                  /* Taille d'une extention      */

} output_info;


/* Crée la désignation principale d'une instruction. */
char *build_coder_main_identifier(const rented_coder *, const output_info *);

/* Génère ou complète un fichier contenant le code C principal. */
bool output_coder_body(const rented_coder *, const output_info *);

/* Finalise le contenu utile du fichier des instructions. */
bool fini_coder_opcodes_file(const char *, const output_info *);

/* Génère ou complète un fichier constituant les identifiants. */
bool output_coder_identifier(const rented_coder *, const output_info *);

/* Finalise le contenu utile du fichier des identifiants. */
bool fini_coder_identifiers_file(const char *, const output_info *);

/* Génère ou complète un fichier créant les sous-identifiants. */
bool output_coder_sub_identifier(const rented_coder *, const output_info *);

/* Finalise le contenu utile du fichier des sous-identifiants. */
bool fini_coder_sub_identifiers_file(const char *, const output_info *);

/* Génère ou complète un fichier constituant les mots clefs. */
bool output_coder_keyword(const rented_coder *, const output_info *);

/* Finalise le contenu utile du fichier des mots clefs. */
bool fini_coder_keywords_file(const char *, const output_info *);

/* Génère ou complète un fichier constituant les décrochages. */
bool output_coder_hooks(const rented_coder *, const output_info *);

/* Finalise le contenu utile du fichier des décrochages. */
bool fini_coder_hooks_file(const char *, const output_info *);

/* Génère ou complète un fichier constituant les descriptions. */
bool output_coder_description(const rented_coder *, const output_info *);

/* Finalise le contenu utile du fichier des descriptions. */
bool fini_coder_descriptions_file(const char *, const output_info *);



#endif  /* _TOOLS_D2C_CODER_H */
