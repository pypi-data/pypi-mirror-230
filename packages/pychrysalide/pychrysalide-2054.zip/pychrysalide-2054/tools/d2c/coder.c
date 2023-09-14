
/* Chrysalide - Outil d'analyse de fichiers binaires
 * coder.c - lecture automatisée des spécifications d'architecture
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


#include "coder.h"


#include <assert.h>
#include <fcntl.h>
#include <libgen.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>


#include "helpers.h"



/* -------------------------- CONSTRUCTION SELON COMMANDES -------------------------- */


/* Suivi des constructions */
struct _rented_coder
{
    const char *input;                      /* Fichier de définitions      */

    pre_processor *pp;                      /* Pré-processeur avec macros  */

    char *copyright;                        /* Récupération des droits     */
    char *ins;                              /* Désignation humaine         */
    char separator;                         /* Caractère de séparation     */
    char *raw_details;                      /* Eventuels compléments bruts */
    char *details;                          /* Eventuels compléments       */

    instr_id *id;                           /* Gestionnaire d'identifiant  */
    instr_desc *desc;                       /* Gestionnaire de description */

    bool useless;                           /* Instruction non utilisée    */

    encoding_spec **specs;                  /* Définitions déjà en place   */
    size_t specs_count;                     /* Nombre de ces définitions   */
    encoding_spec *cur_spec;                /* Définition courante         */

};



/* --------------------------- REPRESENTATION D'ENCODAGES --------------------------- */


/* Détermine le nombre de bits analysés lors d'un désassemblage. */
static unsigned int get_bit_width_for_encoding_spec(const rented_coder *, const string_exch *);



/* --------------------------- GENERATIONS DE CODE SOURCE --------------------------- */


/* Ouvre un fichier principal en écriture pour y placer du code. */
static int open_code_file(const rented_coder *, const char *, const char *, bool *);

/* Ouvre un fichier global en écriture pour y placer du code. */
static int open_header_file(const char *, const char *, const char *, bool *);

/* Imprime dans un flux donné un commentaire de propriété. */
static void write_header_file_license(int, const output_info *, const char *, const char *);

/* Imprime dans un flux donné un commentaire de propriété. */
static void write_code_file_license(int, const output_info *, const char *, const char *);

/* Initialise le contenu utile du fichier des instructions. */
static void init_coder_opcodes_file(int, const output_info *, const char *);

/* Initialise le contenu utile d'un fichier d'instructions. */
static void init_coder_code_file(int, const char *);

/* Centralise l'impression du nom de fonction de désassemblage. */
static void write_read_function_name(const rented_coder *, const output_info *, int, const string_exch *);

/* Génère ou complète un fichier contenant le code C principal. */
static bool output_coder_raw(const rented_coder *, const output_info *, const string_exch *, const encoding_spec *, int, int);

/* Génère ou complète un fichier contenant le code C principal. */
static bool output_coder_main_raw(const rented_coder *, const output_info *, const string_exch *, int, int);

/* Génère ou complète un fichier contenant le code C principal. */
static bool output_coder_format(const rented_coder *, const output_info *, const string_exch *, const encoding_spec *, int, int);

/* Initialise le contenu utile du fichier des identifiants. */
static void init_coder_identifiers_file(int, const output_info *);

/* Initialise le contenu utile du fichier des sous-identifiants. */
static void init_coder_sub_identifiers_file(int, const output_info *);

/* Initialise le contenu utile du fichier des mots clefs. */
static void init_coder_keywords_file(int, const output_info *);

/* Initialise le contenu utile du fichier des décrochages. */
static void init_coder_hooks_file(int, const output_info *);

/* Initialise le contenu utile du fichier des descriptions. */
static void init_coder_descriptions_file(int, const output_info *);



/* ---------------------------------------------------------------------------------- */
/*                            CONSTRUCTION SELON COMMANDES                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : pp = préprocesseur déjà chargé à intégrer.                   *
*                                                                             *
*  Description : Débute la définition d'une fonction de désassemblage.        *
*                                                                             *
*  Retour      : Gestionnaire mis en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

rented_coder *create_coder(pre_processor *pp)
{
    rented_coder *result;                   /* Structure à renvoyer        */

    result = (rented_coder *)calloc(1, sizeof(rented_coder));

    result->pp = pp;

    result->id = create_instruction_id();
    result->desc = create_instruction_description();

    result->cur_spec = create_encoding_spec();

    result->useless = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Supprime le codeur de la mémoire.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_coder(rented_coder *coder)
{
    size_t i;                               /* Boucle de parcours          */

    delete_pre_processor(coder->pp);

    if (coder->ins != NULL)
        free(coder->ins);

    if (coder->raw_details != NULL)
    {
        free(coder->raw_details);
        free(coder->details);
    }

    delete_instruction_id(coder->id);
    delete_instruction_description(coder->desc);

    for (i = 0; i < coder->specs_count; i++)
        delete_encoding_spec(coder->specs[i]);

    if (coder->specs != NULL)
        free(coder->specs);

    delete_encoding_spec(coder->cur_spec);

    free(coder);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Indique le fichier de définition considéré en entrée.        *
*                                                                             *
*  Retour      : Fichier de définition à interpréter.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_coder_input_file(const rented_coder *coder)
{
    return coder->input;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                input = fichier de définitions à venir lire.                 *
*                                                                             *
*  Description : Spécifie le fichier de définition à prendre en entrée.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_coder_input_file(rented_coder *coder, const char *input)
{
    coder->input = input;

}



/* ---------------------------------------------------------------------------------- */
/*                               INFORMATIONS GENERALES                               */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : coder   = gestion par la machine en remplacement de l'humain.*
*                copy    = droits de copie en anglais.                        *
*                ins     = désignation humaine de l'instruction.              *
*                sep     = caractère de séparation avant les détails.         *
*                details = compléments d'informations éventuels ou NULL.      *
*                                                                             *
*  Description : Enregistre les contours d'une instruction d'assemblage.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void save_notes_for_coder(rented_coder *coder, char *copy, char *ins, char sep, const char *details)
{
    coder->copyright = copy;
    coder->ins = make_string_lower(ins);

    coder->separator = sep;

    if (details != NULL)
    {
        coder->raw_details = strdup(details);
        coder->details = make_callable(details, true);
    }
    else
    {
        coder->raw_details = strdup("");
        coder->details = strdup("");
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Fournit la désignation nominale d'une instruction.           *
*                                                                             *
*  Retour      : Désignation nominale à libérer de la mémoire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_coder_nominal_name(const rented_coder *coder)
{
    char *result;                           /* Désignation à retourner     */
    int ret;                                /* Bilan de construction       */

    if (coder->separator == '\0')
        result = strdup(coder->ins);

    else
    {
        ret = asprintf(&result, "%s%c%s", coder->ins, coder->separator, coder->raw_details);

        if (ret == -1)
            result = NULL;

    }

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Fournit la désignation complète d'une instruction.           *
*                                                                             *
*  Retour      : Désignation complète à libérer de la mémoire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_coder_code_name(const rented_coder *coder)
{
    char *result;                           /* Désignation à retourner     */
    char *keyword;                          /* Mot clef appelable en code  */
    char *details;                          /* Compléments de distinction  */
    int ret;                                /* Bilan de construction       */

    keyword = make_callable(coder->ins, false);

    if (coder->separator == '\0')
        result = keyword;

    else
    {
        details = make_callable(coder->raw_details, true);

        ret = asprintf(&result, "%s%s", keyword, details);

        free(keyword);

        free(details);

        if (ret == -1)
            result = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Fournit le gestionnaire des définitions d'identifiant.       *
*                                                                             *
*  Retour      : Structure assurant la définition d'identifiant.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_id *get_coder_instruction_id(const rented_coder *coder)
{
    return coder->id;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Fournit le gestionnaire de description d'identifiant.        *
*                                                                             *
*  Retour      : Structure assurant la description d'identifiant.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_desc *get_coder_instruction_desc(const rented_coder *coder)
{
    return coder->desc;

}



/* ---------------------------------------------------------------------------------- */
/*                             REPRESENTATION D'ENCODAGES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Fournit un lien vers les spécifications courantes.           *
*                                                                             *
*  Retour      : Spécification en cours d'édition.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

encoding_spec *get_current_encoding_spec(const rented_coder *coder)
{
    return coder->cur_spec;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder  = gestion par la machine en remplacement de l'humain. *
*                prefix = distinction principale entre les définitions.       *
*                index  = distinction secondaire entre les définitions.       *
*                                                                             *
*  Description : Enregistre une définition supplémentaire.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void push_encoding_spec(rented_coder *coder, char *prefix, unsigned int index)
{
    encoding_spec *spec;                    /* Définition à compléter      */

    spec = coder->cur_spec;

    if (prefix != NULL)
        define_encoding_spec_code_name(spec, prefix, index);

    coder->specs = (encoding_spec **)realloc(coder->specs, ++coder->specs_count * sizeof(encoding_spec *));
    coder->specs[coder->specs_count - 1] = spec;

    coder->cur_spec = create_encoding_spec();

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder    = gestion automatique de l'écriture de code.        *
*                enc_name = désignation du type d'encodage visé.              *
*                                                                             *
*  Description : Détermine le nombre de bits analysés lors d'un désassemblage.*
*                                                                             *
*  Retour      : Nombre de bits interprété.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static unsigned int get_bit_width_for_encoding_spec(const rented_coder *coder, const string_exch *enc_name)
{
    unsigned int result;                    /* Taille à retourner          */
    size_t i;                               /* Boucle de parcours          */
    encoding_spec *spec;                    /* Définition à traiter        */
    coding_bits *bits;                      /* Gestionnaire de bits        */

    result = -1;

    for (i = 0; i < coder->specs_count; i++)
    {
        spec = coder->specs[i];

        if (!has_encoding_spec_prefix(spec, enc_name->src))
            continue;

        bits = get_bits_in_encoding_spec(spec);
        result = count_coded_bits(bits);
        break;

    }

    /**
     * Rien n'a été trouvé à faire...
     * Cette situation doit normalement être écartée par l'appelant,
     * afin d'éviter de constituer des fichiers vides.
     */
    assert(result != -1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                                                                             *
*  Description : Marque une instruction comme non utilisée.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void mark_coder_as_useless(rented_coder *coder)
{
    coder->useless = true;

}



/* ---------------------------------------------------------------------------------- */
/*                             GENERATIONS DE CODE SOURCE                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Crée la désignation principale d'une instruction.            *
*                                                                             *
*  Retour      : Identifiant à libérer après usage.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_coder_main_identifier(const rented_coder *coder, const output_info *info)
{
    char *result;                           /* Chaîne construite à renvoyer*/
    char *filename;                         /* Nom de fichier modifiable   */
    char *sub;                              /* Compartimentage à insérer   */
    char *name;                             /* Désignation à manipuler     */
    int ret;                                /* Bilan d'une construction    */

    result = NULL;

    if (info->filename_reuse > 0)
    {
        filename = strdup(coder->input);

        sub = basename(filename);

        if (info->filename_reuse < strlen(sub))
            sub[info->filename_reuse] = '\0';

    }

    name = get_coder_code_name(coder);
    if (name == NULL) goto exit;

    make_string_upper(name);

    if (info->filename_reuse > 0)
        ret = asprintf(&result, "%s_%s_%s", info->id_prefix, sub, name);
    else
        ret = asprintf(&result, "%s_%s", info->id_prefix, name);

    free(name);

    if (ret == -1)
        result = NULL;

 exit:

    if (info->filename_reuse > 0)
        free(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder  = gestion par la machine en remplacement de l'humain. *
*                path   = chemin du répertoire de sortie.                     *
*                prefix = type d'encodage à répercuter sur le nom de fichier. *
*                new    = dit si l'opération a abouti à une création. [OUT]   *
*                                                                             *
*  Description : Ouvre un fichier principal en écriture pour y placer du code.*
*                                                                             *
*  Retour      : Descripteur du fichier ouvert ou -1 en cas d'échec.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int open_code_file(const rented_coder *coder, const char *path, const char *prefix, bool *new)
{
    int result;                             /* Descripteur à retourner     */
    char *group;                            /* Regroupement des similarités*/
    char *sep;                              /* Eventuelle séparation       */
    char *pathname;                         /* Chemin d'accès à constituer */
    int ret;                                /* Test d'existence du fichier */
    int flags;                              /* Mode d'accès au fichier     */

    group = strdup(coder->ins);

    sep = index(group, '-');

    if (sep != NULL)
        *sep = '\0';

    if (prefix != NULL)
        ret = asprintf(&pathname, "%s%s_%s.c", path, prefix, group);
    else
        ret = asprintf(&pathname, "%s%s.c", path, group);

    free(group);

    if (ret == -1)
    {
        result = -1;
        goto exit;
    }

    ret = access(pathname, F_OK);

    *new = (ret != 0);

    if (*new)
        flags = O_WRONLY | O_CREAT;
    else
        flags = O_WRONLY | O_APPEND;

    result = open(pathname, flags, 0644);
    if (result == -1) perror("open()");

    free(pathname);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path   = chemin du répertoire de sortie.                     *
*                prefix = type d'encodage à répercuter sur le nom de fichier. *
*                name   = nom du fichier ciblé par l'opération.               *
*                new    = indique si l'opération a créé le fichier. [OUT]     *
*                                                                             *
*  Description : Ouvre un fichier global en écriture pour y placer du code.   *
*                                                                             *
*  Retour      : Descripteur du fichier ouvert ou -1 en cas d'échec.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int open_header_file(const char *path, const char *prefix, const char *name, bool *new)
{
    int result;                             /* Descripteur à retourner     */
    char *pathname;                         /* Chemin d'accès à constituer */
    int ret;                                /* Test d'existence du fichier */
    int flags;                              /* Mode d'accès au fichier     */

    if (prefix != NULL)
        ret = asprintf(&pathname, "%s%s_%s.h", path, prefix, name);
    else
        ret = asprintf(&pathname, "%s%s.h", path, name);

    if (ret == -1)
    {
        result = -1;
        goto exit;
    }

    ret = access(pathname, F_OK);

    *new = (ret != 0);

    if (*new)
        flags = O_WRONLY | O_CREAT;
    else
        flags = O_WRONLY | O_APPEND;

    result = open(pathname, flags, 0644);
    if (result == -1) perror("open()");

    free(pathname);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd   = flux ouvert en écriture mis à disposition.            *
*                info = précisions quant à la génération.                     *
*                name = nom du fichier ciblé par l'opération.                 *
*                msg  = complément d'information à faire paraître.            *
*                                                                             *
*  Description : Imprime dans un flux donné un commentaire de propriété.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void write_header_file_license(int fd, const output_info *info, const char *name, const char *msg)
{
    time_t seconds;                         /* Temps écoulé depuis T0      */
    struct tm cur_date;                     /* Informations sur la date    */

    time(&seconds);
    localtime_r(&seconds, &cur_date);

    dprintf(fd, "\n");

    dprintf(fd, "/* Chrysalide - Outil d'analyse de fichiers binaires\n");
    dprintf(fd, " * %s.h - %s %s\n", name, msg, info->arch);
    dprintf(fd, " *\n");
    dprintf(fd, " * Copyright (C) %d Cyrille Bagard\n", 1900 + cur_date.tm_year);
    dprintf(fd, " *\n");
    dprintf(fd, " *  This file is part of Chrysalide.\n");
    dprintf(fd, " *\n");
    dprintf(fd, " *  Chrysalide is free software; you can redistribute it and/or modify\n");
    dprintf(fd, " *  it under the terms of the GNU General Public License as published by\n");
    dprintf(fd, " *  the Free Software Foundation; either version 3 of the License, or\n");
    dprintf(fd, " *  (at your option) any later version.\n");
    dprintf(fd, " *\n");
    dprintf(fd, " *  Chrysalide is distributed in the hope that it will be useful,\n");
    dprintf(fd, " *  but WITHOUT ANY WARRANTY; without even the implied warranty of\n");
    dprintf(fd, " *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n");
    dprintf(fd, " *  GNU General Public License for more details.\n");
    dprintf(fd, " *\n");
    dprintf(fd, " *  You should have received a copy of the GNU General Public License\n");
    dprintf(fd, " *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.\n");
    dprintf(fd, " */\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd        = flux ouvert en écriture mis à disposition.       *
*                info      = précisions quant à la génération.                *
*                name      = nom du fichier ciblé par l'opération.            *
*                copyright = droits d'auteur à faire valoir.                  *
*                                                                             *
*  Description : Imprime dans un flux donné un commentaire de propriété.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void write_code_file_license(int fd, const output_info *info, const char *name, const char *copyright)
{
    dprintf(fd, "\n");

    dprintf(fd, "/* Chrysalide - Outil d'analyse de fichiers binaires\n");
    dprintf(fd, " * %s.c - traduction d'instructions %s\n", name, info->arch);
    dprintf(fd, " *\n");
    dprintf(fd, " * %s\n", copyright);
    dprintf(fd, " *\n");
    dprintf(fd, " *  This file is part of Chrysalide.\n");
    dprintf(fd, " *\n");
    dprintf(fd, " *  Chrysalide is free software; you can redistribute it and/or modify\n");
    dprintf(fd, " *  it under the terms of the GNU General Public License as published by\n");
    dprintf(fd, " *  the Free Software Foundation; either version 3 of the License, or\n");
    dprintf(fd, " *  (at your option) any later version.\n");
    dprintf(fd, " *\n");
    dprintf(fd, " *  Chrysalide is distributed in the hope that it will be useful,\n");
    dprintf(fd, " *  but WITHOUT ANY WARRANTY; without even the implied warranty of\n");
    dprintf(fd, " *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n");
    dprintf(fd, " *  GNU General Public License for more details.\n");
    dprintf(fd, " *\n");
    dprintf(fd, " *  You should have received a copy of the GNU General Public License\n");
    dprintf(fd, " *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.\n");
    dprintf(fd, " */\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd     = flux ouvert en écriture mis à disposition.          *
*                info   = précisions quant à la génération.                   *
*                prefix = préfixe lié à une sous-branche de l'architecture.   *
*                                                                             *
*  Description : Initialise le contenu utile du fichier des instructions.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_opcodes_file(int fd, const output_info *info, const char *prefix)
{
    char *sub;                              /* Sous-partie à intégrer      */

    if (prefix != NULL)
    {
        sub = strdup(prefix);
        make_string_upper(sub);

        dprintf(fd, "#ifndef _%s_%s_OPCODES_H\n", info->guard, sub);
        dprintf(fd, "#define _%s_%s_OPCODES_H\n", info->guard, sub);

        free(sub);

    }

    else
    {
        dprintf(fd, "#ifndef _%s_OPCODES_H\n", info->guard);
        dprintf(fd, "#define _%s_OPCODES_H\n", info->guard);
    }

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "##INCLUDES##\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd     = flux ouvert en écriture mis à disposition.          *
*                prefix = type d'encodage à répercuter sur un nom de fichier. *
*                                                                             *
*  Description : Initialise le contenu utile d'un fichier d'instructions.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_code_file(int fd, const char *prefix)
{
    if (prefix != NULL)
        dprintf(fd, "#include \"%s_opcodes.h\"\n", prefix);
    else
        dprintf(fd, "#include \"opcodes.h\"\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "##INCLUDES##\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Génère ou complète un fichier contenant le code C principal. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool output_coder_body(const rented_coder *coder, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    const string_exch *enc_name;            /* Type d'encodage visé        */
    size_t j;                               /* Boucle de parcours #2       */
    int header_fd;                          /* Fichier de déclarations     */
    char *file;                             /* Nom de fichier final        */
    int ret;                                /* Bilan d'une construction    */
    bool header_new;                        /* Note une création d'entête  */
    int code_fd;                            /* Fichier de définitions      */
    bool code_new;                          /* Note une création de code   */

    result = true;

    for (i = 0; i < count_encodings(coder->pp) && result; i++)
    {
        enc_name = find_encoding(coder->pp, i);

        for (j = 0; j < coder->specs_count && result; j++)
        {
            /* On s'assure qu'il existe bien une version pour l'encodage visé... */
            if (!has_encoding_spec_prefix(coder->specs[j], enc_name->src))
                continue;

            header_fd = open_header_file(info->opcodes_dir, enc_name->dest, "opcodes", &header_new);
            if (header_fd == -1)
            {
                result = false;
                break;
            }

            if (header_new)
            {
                if (enc_name->dest == NULL)
                    file = strdup("opcodes");
                else
                {
                    ret = asprintf(&file, "%s_opcodes", enc_name->dest);

                    if (ret == -1)
                    {
                        result = false;
                        goto close_header;
                    }

                }

                write_header_file_license(header_fd, info, file, "prototypes pour la traduction d'instructions");

                free(file);

                init_coder_opcodes_file(header_fd, info, enc_name->dest);

            }

            code_fd = open_code_file(coder, info->opcodes_dir, enc_name->dest, &code_new);
            if (code_fd == -1)
            {
                result = false;
                goto close_header;
            }

            if (code_new)
            {
                if (enc_name->dest == NULL)
                    file = strdup(coder->ins);
                else
                {
                    ret = asprintf(&file, "%s_%s", enc_name->dest, coder->ins);

                    if (ret == -1)
                    {
                        result = false;
                        goto close_code;
                    }

                }

                write_code_file_license(code_fd, info, file, coder->copyright);

                free(file);

                init_coder_code_file(code_fd, enc_name->dest);

            }
            else
                dprintf(code_fd, "\n");

            switch (info->type)
            {
                case IOT_UNDEFINED:
                    assert(false);
                    result = false;
                    break;

                case IOT_RAW:
                    result = output_coder_raw(coder, info, enc_name, coder->specs[j], header_fd, code_fd);
                    break;

                case IOT_FORMAT:
                    assert(j == 0);
                    assert(enc_name->dest == NULL);
                    result = output_coder_format(coder, info, enc_name, coder->specs[j], header_fd, code_fd);
                    break;

            }

 close_code:

            close(code_fd);

 close_header:

            close(header_fd);

        }

        /* La suite ne concerne que les formats bruts aboutis... */
        if (!result) break;
        if (info->type != IOT_RAW) continue;

        for (j = 0; j < coder->specs_count; j++)
        {
            /* On s'assure de retrouver une version de l'encodage visé juste avant... */
            if (!has_encoding_spec_prefix(coder->specs[j], enc_name->src))
                continue;

            header_fd = open_header_file(info->opcodes_dir, enc_name->dest, "opcodes", &header_new);
            if (header_fd == -1)
            {
                result = false;
                break;
            }

            assert(!header_new);

            code_fd = open_code_file(coder, info->opcodes_dir, enc_name->dest, &code_new);
            if (code_fd == -1)
            {
                result = false;
                close(header_fd);
                break;
            }

            assert(!code_new);

            result = output_coder_main_raw(coder, info, enc_name, header_fd, code_fd);

            close(code_fd);
            close(header_fd);

            break;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion automatique de l'écriture de code.           *
*                info  = précisions quant à la génération.                    *
*                fd    = flux ouvert en écriture.                             *
*                enc   = encodage choisi comme sous-ensemble d'architecture.  *
*                                                                             *
*  Description : Centralise l'impression du nom de fonction de désassemblage. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void write_read_function_name(const rented_coder *coder, const output_info *info, int fd, const string_exch *enc)
{
    char *arch;                             /* Architecture à traiter      */
    char *filename;                         /* Nom de fichier modifiable   */
    char *sub;                              /* Compartimentage à insérer   */
    char *name;                             /* Désignation à manipuler     */

    /* Préparations */

    arch = strdup(info->arch_cn);
    make_string_lower(arch);

    if (info->filename_reuse > 0)
    {
        filename = strdup(coder->input);

        sub = basename(filename);

        if (info->filename_reuse < strlen(sub))
            sub[info->filename_reuse] = '\0';

        make_string_lower(sub);

    }

    name = get_coder_code_name(coder);
    if (name == NULL) goto exit;

    /* Impressions */

    if (enc->dest == NULL)
        dprintf(fd, "%s_read_instr", arch);
    else
        dprintf(fd, "%s_read_%s_instr", arch, enc->dest);

    if (info->filename_reuse > 0)
        dprintf(fd, "_%s", sub);

    dprintf(fd, "_%s", name);

    /* Sortie propre */

    free(name);

 exit:

    if (info->filename_reuse > 0)
        free(filename);

    free(arch);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder    = gestion automatique de l'écriture de code.        *
*                info     = précisions quant à la génération.                 *
*                enc_name = désignation du type d'encodage visé.              *
*                encoding = sélection de l'encodage à traiter.                *
*                hfd      = flux ouvert en écriture pour les déclarations.    *
*                cfd      = flux ouvert en écriture pour les définitions.     *
*                                                                             *
*  Description : Génère ou complète un fichier contenant le code C principal. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool output_coder_raw(const rented_coder *coder, const output_info *info, const string_exch *enc_name, const encoding_spec *encoding, int hfd, int cfd)
{
    bool result;                            /* Bilan à retourner           */
    char *arch;                             /* Architecture à traiter      */
    char *prefix;                           /* Préfixe employé en suffixe  */
    coding_bits *bits;                      /* Gestionnaire de bits        */
    unsigned int wide;                      /* Taille des mots             */
    size_t maxlen;                          /* Taille à compléter          */
    char *constant;                         /* Définition d'une constante  */

    arch = strdup(info->arch_cn);
    make_string_lower(arch);

    prefix = build_encoding_spec_prefix(encoding);

    result = (prefix != NULL);
    if (!result) goto exit;

    bits = get_bits_in_encoding_spec(encoding);
    wide = count_coded_bits(bits);

    /* Désassemblage : déclaration */

    if (info->export)
    {
        dprintf(hfd, "/* Décode une forme d'instruction de type '%s'. */\n", coder->ins);

        dprintf(hfd, "GArchInstruction *");
        write_read_function_name(coder, info, hfd, enc_name);
        dprintf(hfd, "_%s", prefix);

        dprintf(hfd, "(");
        dprintf(hfd, "uint%u_t raw", wide);
        dprintf(hfd, ");\n");

        dprintf(hfd, "\n");

    }

    /* Désassemblage : définitions */

    dprintf(cfd, "/******************************************************************************\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Paramètres  : raw = données brutes à analyser.                             *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Description : Décode une forme d'instruction de type '%s'.", coder->ins);

    maxlen = 20 - strlen(coder->ins);

    if (maxlen < 20)
        dprintf(cfd, "%*s\n", (int)maxlen, "*");
    else
        dprintf(cfd, "*\n");

    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Remarques   : -                                                            *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "******************************************************************************/\n");

    dprintf(cfd, "\n");

    if (!info->export)
        dprintf(cfd, "static ");

    dprintf(cfd, "GArchInstruction *");
    write_read_function_name(coder, info, cfd, enc_name);
    dprintf(cfd, "_%s", prefix);

    dprintf(cfd, "(");
    dprintf(cfd, "uint%u_t raw", wide);
    dprintf(cfd, ")");

    dprintf(cfd, "\n");
    dprintf(cfd, "{");
    dprintf(cfd, "\n");

    constant = build_coder_main_identifier(coder, info);
    if (constant == NULL)
    {
        result = false;
        goto exit;
    }

    result = write_encoding_spec_raw_disass(encoding, cfd, arch, constant, coder->pp);

    free(constant);

    dprintf(cfd, "}\n");
    dprintf(cfd, "\n");

    /* Conclusion */

 exit:

    free(prefix);

    free(arch);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder    = gestion automatique de l'écriture de code.        *
*                info     = précisions quant à la génération.                 *
*                enc_name = désignation du type d'encodage visé.              *
*                hfd      = flux ouvert en écriture pour les déclarations.    *
*                cfd      = flux ouvert en écriture pour les définitions.     *
*                                                                             *
*  Description : Génère ou complète un fichier contenant le code C principal. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool output_coder_main_raw(const rented_coder *coder, const output_info *info, const string_exch *enc_name, int hfd, int cfd)
{
    bool result;                            /* Bilan à retourner           */
    unsigned int wide;                      /* Taille des mots             */
    size_t maxlen;                          /* Taille à compléter          */
    bool first;                             /* Note un premier appel       */
    size_t i;                               /* Boucle de parcours          */
    char *prefix;                           /* Préfixe employé en suffixe  */

    result = false;

    wide = get_bit_width_for_encoding_spec(coder, enc_name);

    /* Désassemblage : déclaration */

    dprintf(hfd, "/* Décode une instruction de type '%s'. */\n", coder->ins);

    dprintf(hfd, "GArchInstruction *");
    write_read_function_name(coder, info, hfd, enc_name);

    dprintf(hfd, "(");
    dprintf(hfd, "uint%u_t raw", wide);
    dprintf(hfd, ");\n");

    dprintf(hfd, "\n");

    /* Désassemblage : définitions */

    dprintf(cfd, "/******************************************************************************\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Paramètres  : raw = données brutes à analyser.                             *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Description : Décode une instruction de type '%s'.", coder->ins);

    maxlen = 28 - strlen(coder->ins);

    if (maxlen < 28)
        dprintf(cfd, "%*s\n", (int)maxlen, "*");
    else
        dprintf(cfd, "*\n");

    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Remarques   : -                                                            *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "******************************************************************************/\n");

    dprintf(cfd, "\n");

    dprintf(cfd, "GArchInstruction *");
    write_read_function_name(coder, info, cfd, enc_name);

    dprintf(cfd, "(");
    dprintf(cfd, "uint%u_t raw", wide);
    dprintf(cfd, ")");

    dprintf(cfd, "\n");
    dprintf(cfd, "{");
    dprintf(cfd, "\n");

    dprintf(cfd, "\tGArchInstruction *result;               /* Instruction créée à renvoyer*/\n");
    dprintf(cfd, "\n");

    first = true;

    for (i = 0; i < coder->specs_count; i++)
    {
        if (!has_encoding_spec_prefix(coder->specs[i], enc_name->src))
            continue;

        prefix = build_encoding_spec_prefix(coder->specs[i]);

        result = (prefix != NULL);
        if (!result) break;

        if (first)
        {
            dprintf(cfd, "\tresult = ");
            write_read_function_name(coder, info, cfd, enc_name);
            dprintf(cfd, "_%s(raw);\n", prefix);

            dprintf(cfd, "\n");

            first = false;

        }
        else
        {
            dprintf(cfd, "\tif (result == NULL)\n");

            dprintf(cfd, "\t\tresult = ");
            write_read_function_name(coder, info, cfd, enc_name);
            dprintf(cfd, "_%s(raw);\n", prefix);

            dprintf(cfd, "\n");

        }

        free(prefix);

    }

    dprintf(cfd, "\treturn result;\n");
    dprintf(cfd, "\n");

    dprintf(cfd, "}\n");
    dprintf(cfd, "\n");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder    = gestion automatique de l'écriture de code.        *
*                info     = précisions quant à la génération.                 *
*                enc_name = désignation du type d'encodage visé.              *
*                encoding = sélection de l'encodage à traiter.                *
*                hfd      = flux ouvert en écriture pour les déclarations.    *
*                cfd      = flux ouvert en écriture pour les définitions.     *
*                                                                             *
*  Description : Génère ou complète un fichier contenant le code C principal. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool output_coder_format(const rented_coder *coder, const output_info *info, const string_exch *enc_name, const encoding_spec *encoding, int hfd, int cfd)
{
    bool result;                            /* Bilan à retourner           */
    char *arch;                             /* Architecture à traiter      */
    size_t maxlen;                          /* Taille à compléter          */
    char *constant;                         /* Définition d'une constante  */

    arch = strdup(info->arch_cn);
    make_string_lower(arch);

    /* Désassemblage : déclaration */

    dprintf(hfd, "/* Décode une instruction de type '%s'. */\n", coder->ins);

    dprintf(hfd, "GArchInstruction *");
    write_read_function_name(coder, info, hfd, enc_name);

    dprintf(hfd, "(");
    dprintf(hfd, "const GArchProcessor *, GProcContext *, const GBinContent *, ");
    dprintf(hfd, "vmpa2t *, GExeFormat *");
    dprintf(hfd, ");\n");

    dprintf(hfd, "\n");

    /* Désassemblage : définitions */

    dprintf(cfd, "/******************************************************************************\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Paramètres  : proc    = processeur de l'architecture d'exécution.          *\n");
    dprintf(cfd, "*                ctx     = contexte associé à la phase de désassemblage.      *\n");
    dprintf(cfd, "*                content = flux de données à analyser.                        *\n");
    dprintf(cfd, "*                pos     = position courante dans ce flux. [OUT]              *\n");
    dprintf(cfd, "*                format  = format du fichier contenant le code.               *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Description : Décode une instruction de type '%s'.", coder->ins);

    maxlen = 28 - strlen(coder->ins);

    if (maxlen < 28)
        dprintf(cfd, "%*s\n", (int)maxlen, "*");
    else
        dprintf(cfd, "*\n");

    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "*  Remarques   : -                                                            *\n");
    dprintf(cfd, "*                                                                             *\n");
    dprintf(cfd, "******************************************************************************/\n");

    dprintf(cfd, "\n");

    dprintf(cfd, "GArchInstruction *");
    write_read_function_name(coder, info, cfd, enc_name);

    dprintf(cfd, "(");
    dprintf(cfd, "const GArchProcessor *proc, GProcContext *ctx, const GBinContent *content, ");
    dprintf(cfd, "vmpa2t *pos, GExeFormat *format");
    dprintf(cfd, ")");

    dprintf(cfd, "\n");
    dprintf(cfd, "{");
    dprintf(cfd, "\n");

    constant = build_coder_main_identifier(coder, info);
    if (constant == NULL)
    {
        result = false;
        goto exit;
    }

    result = write_encoding_spec_format_disass(encoding, cfd, arch, constant, info->fmt_prefix);

    free(constant);

    dprintf(cfd, "}\n");
    dprintf(cfd, "\n");

    /* Conclusion */

 exit:

    free(arch);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pathname = chemin d'accès au fichier à traiter.              *
*                info     = précisions quant à la génération.                 *
*                                                                             *
*  Description : Finalise le contenu utile du fichier des instructions.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fini_coder_opcodes_file(const char *pathname, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ouvert en écriture     */
    char *temp;                             /* Zone de travail temporaire  */
    char *base;                             /* Identification de fichier   */

    result = false;

    fd = open(pathname, O_WRONLY | O_APPEND, 0644);
    if (fd == -1)
    {
        perror("open()");
        goto fcif_exit;
    }

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    temp = strdup(pathname);
    base = basename(temp);

    base[strlen(base) - 2] = '\0';

    make_string_upper(base);

    dprintf(fd, "#endif  /* _%s_%s_H */\n", info->guard, base);

    free(temp);

    result = true;

 fcif_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd   = flux ouvert en écriture mis à disposition.            *
*                info = précisions quant à la génération.                     *
*                                                                             *
*  Description : Initialise le contenu utile du fichier des identifiants.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_identifiers_file(int fd, const output_info *info)
{
    dprintf(fd, "#ifndef _%s_IDENTIFIERS_H\n", info->guard);
    dprintf(fd, "#define _%s_IDENTIFIERS_H\n", info->guard);

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "/* Enumération de tous les opcodes */\n");
    dprintf(fd, "typedef enum _%sOpcodes\n", info->arch_cn);
    dprintf(fd, "{\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Génère ou complète un fichier constituant les identifiants.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool output_coder_identifier(const rented_coder *coder, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    bool created;                           /* Note une création           */
    int fd;                                 /* Flux ouvert en écriture     */
    char *constant;                         /* Définition d'une constante  */
    char *name;                             /* Désignation à manipuler     */
    instr_id *id;                           /* Gestionnaire d'identifiant  */
    unsigned int iid;                       /* Identifiant unique attribué */
    char *comment;                          /* Contenu du commentaire      */
    int ret;                                /* Bilan d'une construction    */
    char *aligned;                          /* Adaptation pour l'alignement*/

    result = false;

    /* Ouverture de la destination */

    fd = open_header_file(info->opcodes_dir, NULL, "identifiers", &created);
    if (fd == -1) goto exit;

    if (created)
    {
        write_header_file_license(fd, info, "identifiers", "définition des identifiants uniques pour");
        init_coder_identifiers_file(fd, info);
    }

    /* Définition du commentaire */

    name = get_coder_nominal_name(coder);

    if (name == NULL)
        goto failure_1;

    id = get_coder_instruction_id(coder);
    iid = get_instruction_id_value(id);

    ret = asprintf(&comment, "%s (0x%0*x)", name, info->id_len, iid);

    free(name);

    if (ret == -1)
        goto failure_1;

    /* Constitution de la constante et impression de la ligne */

    constant = build_coder_main_identifier(coder, info);

    if (constant == NULL)
        goto failure_2;

    ret = asprintf(&aligned, "%s,", constant);

    free(constant);

    if (ret == -1)
        goto failure_2;

    dprintf(fd, "    %-40s/* %-28s*/\n", aligned, comment);

    free(aligned);

    result = true;

 failure_2:

    free(comment);

 failure_1:

    close(fd);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pathname = chemin d'accès au fichier à traiter.              *
*                info     = précisions quant à la génération.                 *
*                                                                             *
*  Description : Finalise le contenu utile du fichier des identifiants.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fini_coder_identifiers_file(const char *pathname, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ouvert en écriture     */

    result = false;

    fd = open(pathname, O_WRONLY | O_APPEND, 0644);
    if (fd == -1)
    {
        perror("open()");
        goto fcif_exit;
    }

    dprintf(fd, "\n");
    dprintf(fd, "    %s_COUNT\n", info->id_prefix);
    dprintf(fd, "\n");

    dprintf(fd, "} %sOpcodes;\n", info->arch_cn);

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "#endif  /* _%s_IDENTIFIERS_H */\n", info->guard);

    result = true;

 fcif_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd   = flux ouvert en écriture mis à disposition.            *
*                info = précisions quant à la génération.                     *
*                                                                             *
*  Description : Initialise le contenu utile du fichier des sous-identifiants.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_sub_identifiers_file(int fd, const output_info *info)
{
    dprintf(fd, "#ifndef _%s_SUBIDENTIFIERS_H\n", info->guard);
    dprintf(fd, "#define _%s_SUBIDENTIFIERS_H\n", info->guard);

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "/* Enumération de tous les opcodes */\n");
    dprintf(fd, "typedef enum _%sSyntax\n", info->arch_cn);
    dprintf(fd, "{\n");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Génère ou complète un fichier créant les sous-identifiants.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool output_coder_sub_identifier(const rented_coder *coder, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    bool created;                           /* Note une création           */
    int fd;                                 /* Flux ouvert en écriture     */
    char *constant;                         /* Définition d'une constante  */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    /* Ouverture de la destination */

    fd = open_header_file(info->opcodes_dir, NULL, "subidentifiers", &created);
    if (fd == -1) goto exit;

    if (created)
    {
        write_header_file_license(fd, info, "subidentifiers", "définition des sous-identifiants uniques pour");
        init_coder_sub_identifiers_file(fd, info);
    }

    /* Impression des sous-identifiants */

    constant = build_coder_main_identifier(coder, info);
    if (constant == NULL) goto exit;

    result = true;

    for (i = 0; i < coder->specs_count && result; i++)
        result = write_encoding_spec_subid(coder->specs[i], fd, constant);

    free(constant);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pathname = chemin d'accès au fichier à traiter.              *
*                info     = précisions quant à la génération.                 *
*                                                                             *
*  Description : Finalise le contenu utile du fichier des sous-identifiants.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fini_coder_sub_identifiers_file(const char *pathname, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ouvert en écriture     */

    result = false;

    fd = open(pathname, O_WRONLY | O_APPEND, 0644);
    if (fd == -1)
    {
        perror("open()");
        goto fcif_exit;
    }

    dprintf(fd, "\n");
    dprintf(fd, "    %s_ENC_COUNT\n", info->id_prefix);
    dprintf(fd, "\n");

    dprintf(fd, "} %sSyntax;\n", info->arch_cn);

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "#endif  /* _%s_SUBIDENTIFIERS_H */\n", info->guard);

    result = true;

 fcif_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd   = flux ouvert en écriture mis à disposition.            *
*                info = précisions quant à la génération.                     *
*                                                                             *
*  Description : Initialise le contenu utile du fichier des mots clefs.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_keywords_file(int fd, const output_info *info)
{
    char *larch;                            /* Architecture en minuscules  */

    dprintf(fd, "#ifndef _%s_KEYWORDS_H\n", info->guard);
    dprintf(fd, "#define _%s_KEYWORDS_H\n", info->guard);

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    switch (info->type)
    {
        case IOT_UNDEFINED:
            assert(false);
            break;

        case IOT_RAW:
            dprintf(fd, "#include \"subidentifiers.h\"\n");
            break;

        case IOT_FORMAT:
            dprintf(fd, "#include \"identifiers.h\"\n");
            break;

    }

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    larch = strdup(info->arch_cn);
    make_string_lower(larch);

    dprintf(fd, "/* Enumération de tous les mots clefs */\n");
    dprintf(fd, "static char *_%s_keywords[%s_%sCOUNT] = {\n",
            larch, info->id_prefix, info->type == IOT_RAW ? "ENC_" : "");
    dprintf(fd, "\n");

    free(larch);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Génère ou complète un fichier constituant les mots clefs.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool output_coder_keyword(const rented_coder *coder, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    bool created;                           /* Note une création           */
    int fd;                                 /* Flux ouvert en écriture     */
    char *constant;                         /* Définition d'une constante  */
    size_t i;                               /* Boucle de parcours          */
    char *name;                             /* Désignation à manipuler     */

    result = false;

    /* S'il n'y a pas lieu de traiter l'instruction */

    if (coder->useless)
    {
        result = true;
        goto exit;
    }

    /* Ouverture de la destination */

    fd = open_header_file(info->opcodes_dir, NULL, "keywords", &created);
    if (fd == -1) goto exit;

    if (created)
    {
        write_header_file_license(fd, info, "keywords", "définition des mots clefs des instructions");
        init_coder_keywords_file(fd, info);
    }

    /* Lancement des impressions */

    constant = build_coder_main_identifier(coder, info);
    if (constant == NULL) goto failure;

    result = true;

    for (i = 0; i < coder->specs_count && result; i++)
        switch (info->type)
        {
            case IOT_UNDEFINED:
                assert(false);
                result = false;
                break;

            case IOT_RAW:
                result = write_encoding_spec_keywords(coder->specs[i], fd, constant);
                break;

            case IOT_FORMAT:
                assert(i == 0);

                /* Impression de la colonne */

                dprintf(fd, "\t[%s] = ", constant);

                /* Impression du mot clef */

                name = get_coder_nominal_name(coder);

                result = (name != NULL);

                if (result)
                {
                    dprintf(fd, "\"%s\",\n", name);

                    free(name);

                }

                break;

        }

    free(constant);

 failure:

    close(fd);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pathname = chemin d'accès au fichier à traiter.              *
*                info     = précisions quant à la génération.                 *
*                                                                             *
*  Description : Finalise le contenu utile du fichier des mots clefs.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fini_coder_keywords_file(const char *pathname, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ouvert en écriture     */

    result = false;

    fd = open(pathname, O_WRONLY | O_APPEND, 0644);
    if (fd == -1)
    {
        perror("open()");
        goto fckf_exit;
    }

    dprintf(fd, "\n");
    dprintf(fd, "};\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "#endif  /* _%s_KEYWORDS_H */\n", info->guard);

    result = true;

 fckf_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd   = flux ouvert en écriture mis à disposition.            *
*                info = précisions quant à la génération.                     *
*                                                                             *
*  Description : Initialise le contenu utile du fichier des décrochages.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_hooks_file(int fd, const output_info *info)
{
    char *larch;                            /* Architecture en minuscules  */

    dprintf(fd, "#ifndef _%s_HOOKS_H\n", info->guard);
    dprintf(fd, "#define _%s_HOOKS_H\n", info->guard);

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    switch (info->type)
    {
        case IOT_UNDEFINED:
            assert(false);
            break;

        case IOT_RAW:
            dprintf(fd, "#include \"subidentifiers.h\"\n");
            break;

        case IOT_FORMAT:
            dprintf(fd, "#include \"identifiers.h\"\n");
            break;

    }

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "##INCLUDES##\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    larch = strdup(info->arch_cn);
    make_string_lower(larch);

    dprintf(fd, "/* Définitions des décrochages pour l'établissement d'instructions */\n");
    dprintf(fd, "static const instr_hook_fc _%s_hooks[%s_%sCOUNT][IPH_COUNT] = {\n",
            larch, info->id_prefix, info->type == IOT_RAW ? "ENC_" : "");
    dprintf(fd, "\n");

    free(larch);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Génère ou complète un fichier constituant les décrochages.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool output_coder_hooks(const rented_coder *coder, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    bool created;                           /* Note une création           */
    int fd;                                 /* Flux ouvert en écriture     */
    char *constant;                         /* Définition d'une constante  */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    /* S'il n'y a pas lieu de traiter l'instruction */

    if (coder->useless)
    {
        result = true;
        goto exit;
    }

    /* Ouverture de la destination */

    fd = open_header_file(info->opcodes_dir, NULL, "hooks", &created);
    if (fd == -1) goto exit;

    if (created)
    {
        write_header_file_license(fd, info, "hooks", "définition des décrochages pour instructions");
        init_coder_hooks_file(fd, info);
    }

    /* Lancement des impressions */

    constant = build_coder_main_identifier(coder, info);
    if (constant == NULL) goto exit;

    result = true;

    for (i = 0; i < coder->specs_count && result; i++)
        switch (info->type)
        {
            case IOT_UNDEFINED:
                assert(false);
                result = false;
                break;

            case IOT_RAW:
                result = write_encoding_spec_hooks(coder->specs[i], fd, constant, true);
                break;

            case IOT_FORMAT:
                assert(i == 0);
                result = write_encoding_spec_hooks(coder->specs[i], fd, constant, false);
                break;

        }

    free(constant);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pathname = chemin d'accès au fichier à traiter.              *
*                info     = précisions quant à la génération.                 *
*                                                                             *
*  Description : Finalise le contenu utile du fichier des décrochages.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fini_coder_hooks_file(const char *pathname, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ouvert en écriture     */

    result = false;

    fd = open(pathname, O_WRONLY | O_APPEND, 0644);
    if (fd == -1)
    {
        perror("open()");
        goto fchf_exit;
    }

    dprintf(fd, "\n");
    dprintf(fd, "};\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "#endif  /* _%s_HOOKS_H */\n", info->guard);

    result = true;

 fchf_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd   = flux ouvert en écriture mis à disposition.            *
*                info = précisions quant à la génération.                     *
*                                                                             *
*  Description : Initialise le contenu utile du fichier des descriptions.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_coder_descriptions_file(int fd, const output_info *info)
{
    char *larch;                            /* Architecture en minuscules  */

    dprintf(fd, "#ifndef _%s_DESCRIPTIONS_H\n", info->guard);
    dprintf(fd, "#define _%s_DESCRIPTIONS_H\n", info->guard);

    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "#include \"identifiers.h\"\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    larch = strdup(info->arch_cn);
    make_string_lower(larch);

    dprintf(fd, "/* Enumération de tous les mots clefs */\n");
    dprintf(fd, "static char *_%s_descriptions[%s_COUNT] = {\n", larch, info->id_prefix);
    dprintf(fd, "\n");

    free(larch);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = gestion par la machine en remplacement de l'humain.  *
*                info  = précisions quant à la génération.                    *
*                                                                             *
*  Description : Génère ou complète un fichier constituant les descriptions.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool output_coder_description(const rented_coder *coder, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    bool created;                           /* Note une création           */
    int fd;                                 /* Flux ouvert en écriture     */
    char *constant;                         /* Définition d'une constante  */
    char *name;                             /* Désignation à manipuler     */

    result = false;

    /* S'il n'y a pas lieu de traiter l'instruction */

    if (coder->useless)
    {
        result = true;
        goto exit;
    }

    /* Ouverture de la destination */

    fd = open_header_file(info->opcodes_dir, NULL, "descriptions", &created);
    if (fd == -1) goto exit;

    if (created)
    {
        write_header_file_license(fd, info, "descriptions", "définition des descriptions des instructions");
        init_coder_descriptions_file(fd, info);
    }

    /* Impression de la colonne */

    constant = build_coder_main_identifier(coder, info);
    if (constant == NULL) goto exit;

    dprintf(fd, "\t[%s] = ", constant);

    free(constant);

    /* Impression du mot clef */

    name = get_coder_nominal_name(coder);
    if (name == NULL) goto exit;

    dprintf(fd, "\"");

    write_instruction_description(coder->desc, fd);

    dprintf(fd, "\",\n");

    free(name);

    result = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pathname = chemin d'accès au fichier à traiter.              *
*                info     = précisions quant à la génération.                 *
*                                                                             *
*  Description : Finalise le contenu utile du fichier des descriptions.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fini_coder_descriptions_file(const char *pathname, const output_info *info)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ouvert en écriture     */

    result = false;

    fd = open(pathname, O_WRONLY | O_APPEND, 0644);
    if (fd == -1)
    {
        perror("open()");
        goto fckf_exit;
    }

    dprintf(fd, "\n");
    dprintf(fd, "};\n");

    dprintf(fd, "\n");
    dprintf(fd, "\n");
    dprintf(fd, "\n");

    dprintf(fd, "#endif  /* _%s_DESCRIPTIONS_H */\n", info->guard);

    result = true;

 fckf_exit:

    return result;

}
