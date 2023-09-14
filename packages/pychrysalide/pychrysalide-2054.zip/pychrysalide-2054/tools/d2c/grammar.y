
%{

#include <getopt.h>//////
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>

#include "decl.h"
#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(rented_coder *, char *, char *);

/* Affiche des indications sur l'utilisation du programme. */
static void show_usage(const char *);

/* Prépare le traitement d'un contenu en l'affichant en mémoire. */
static void *map_input_data(const char *, size_t *);

%}


%code requires {

#include "coder.h"
#include "helpers.h"
#include "syntax.h"
#include "args/decl.h"
#include "assert/decl.h"
#include "bits/decl.h"
#include "conv/decl.h"
#include "format/decl.h"
#include "hooks/decl.h"
#include "id/decl.h"
#include "pattern/decl.h"
#include "rules/decl.h"


#define handle_coder_id(c, r)                                       \
    ({                                                              \
        instr_id *__id;                                             \
        bool __status;                                              \
        __id = get_coder_instruction_id(c);                         \
        __status = load_id_from_raw_line(__id, r);                  \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_desc(c, r)                                     \
    ({                                                              \
        instr_desc *__desc;                                         \
        __desc = get_coder_instruction_desc(c);                     \
        set_instruction_description(__desc, r);                     \
    })

#define handle_coder_format(c, r)                                   \
    ({                                                              \
        encoding_spec *__spec;                                      \
        operands_format *__format;                                  \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __format = get_format_in_encoding_spec(__spec);             \
        __status = load_format_from_raw_line(__format, r);          \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_bits(c, e, r)                                  \
    ({                                                              \
        encoding_spec *__spec;                                      \
        coding_bits *__bits;                                        \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __bits = get_bits_in_encoding_spec(__spec);                 \
        __status = load_bits_from_raw_line(__bits, e, r);           \
        if (!__status) YYABORT;                                     \
    })

#define push_coder_new_syntax(c)                                    \
    ({                                                              \
        encoding_spec *__spec;                                      \
        __spec = get_current_encoding_spec(c);                      \
        push_new_encoding_syntax(__spec);                           \
    })

#define handle_coder_subid(c, r)                                    \
    ({                                                              \
        encoding_spec *__spec;                                      \
        encoding_syntax *__syntax;                                  \
        instr_id *__subid;                                          \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __syntax = get_current_encoding_syntax(__spec);             \
        __subid = get_encoding_syntax_subid(__syntax);              \
        __status = load_id_from_raw_line(__subid, r);               \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_assertions(c, r)                               \
    ({                                                              \
        encoding_spec *__spec;                                      \
        encoding_syntax *__syntax;                                  \
        disass_assert *__dassert;                                   \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __syntax = get_current_encoding_syntax(__spec);             \
        __dassert = get_assertions_for_encoding_syntax(__syntax);   \
        __status = load_assertions_from_raw_block(__dassert, r);    \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_conversions(c, r)                              \
    ({                                                              \
        encoding_spec *__spec;                                      \
        encoding_syntax *__syntax;                                  \
        conv_list *__list;                                          \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __syntax = get_current_encoding_syntax(__spec);             \
        __list = get_conversions_in_encoding_syntax(__syntax);      \
        __status = load_convs_from_raw_block(__list, r);            \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_asm(c, r)                                      \
    ({                                                              \
        encoding_spec *__spec;                                      \
        encoding_syntax *__syntax;                                  \
        asm_pattern *__pattern;                                     \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __syntax = get_current_encoding_syntax(__spec);             \
        __pattern = get_asm_pattern_in_encoding_syntax(__syntax);   \
        __status = load_asm_pattern_from_raw_line(__pattern, r);    \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_rules(c, r)                                    \
    ({                                                              \
        encoding_spec *__spec;                                      \
        encoding_syntax *__syntax;                                  \
        decoding_rules *__rules;                                    \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __syntax = get_current_encoding_syntax(__spec);             \
        __rules = get_rules_in_encoding_syntax(__syntax);           \
        __status = load_rules_from_raw_block(__rules, r);           \
        if (!__status) YYABORT;                                     \
    })

#define handle_coder_hooks(c, r)                                    \
    ({                                                              \
        encoding_spec *__spec;                                      \
        instr_hooks *__hooks;                                       \
        bool __status;                                              \
        __spec = get_current_encoding_spec(c);                      \
        __hooks = get_hooks_in_encoding_spec(__spec);               \
        __status = load_hooks_from_raw_line(__hooks, r);            \
        if (!__status) YYABORT;                                     \
    })

}

%union {

    char character;                         /* Simple caractère isolé      */
    char *string;                           /* Chaîne de caractères #1     */
    const char *cstring;                    /* Chaîne de caractères #2     */

    int integer;                            /* Valeur entière              */

}


/**
 * Cf.
 * http://stackoverflow.com/questions/34418381/how-to-reference-lex-or-parse-parameters-in-flex-rules/34420950
 */

%define api.pure full

%parse-param { rented_coder *coder } { char *temp }
%lex-param { char *temp }

%code provides {

#define YY_DECL \
    int d2c_lex(YYSTYPE *yylvalp, char *temp)

YY_DECL;

}


%token COPYRIGHT
%token TITLE
%token INS_NAME INS_SEP INS_DETAILS
%token ID SUBID
%token DESC

%token ENCODING
%token TYPE NUMBER
%token ENC_START ENC_END

%token FORMAT UNUSED
%token WORD HALF
%token SYNTAX
%token ASSERT CONV ASM
%token HOOKS
%token RULES

%token RAW_LINE RAW_BLOCK


%type <string> COPYRIGHT INS_NAME
%type <character> INS_SEP
%type <cstring> INS_DETAILS

%type <string> TYPE
%type <integer> NUMBER

%type <cstring> RAW_LINE RAW_BLOCK


%%


input : name id desc encodings
      | name id encodings

name : COPYRIGHT TITLE INS_NAME                     { save_notes_for_coder(coder, $1, $3, '\0', NULL); }
     | COPYRIGHT TITLE INS_NAME INS_SEP INS_DETAILS { save_notes_for_coder(coder, $1, $3, $4, $5); }

id : ID RAW_LINE { handle_coder_id(coder, $2); }

desc : DESC RAW_BLOCK { handle_coder_desc(coder, $2); }

encodings : /* empty */
          | encoding encodings

encoding : ENCODING TYPE NUMBER format_encoding { push_encoding_spec(coder, $2, $3); }
         | ENCODING format_encoding { push_encoding_spec(coder, NULL, -1); }
         | ENCODING TYPE NUMBER raw_encoding { push_encoding_spec(coder, $2, $3); }


/* Définitions à l'aide d'un format défini */

format_encoding : format format_content
                | unused_format

format : FORMAT RAW_LINE { handle_coder_format(coder, $2); }

unused_format : UNUSED RAW_LINE { handle_coder_format(coder, $2); mark_coder_as_useless(coder); }

format_content : /* empty */
               | SYNTAX { push_coder_new_syntax(coder); } format_syntax format_content
               | hooks format_content

format_syntax : /* empty */
              | rules format_syntax


/* Définitions à l'aide de données brutes */

raw_encoding : bitfield raw_content

bitfield : HALF RAW_LINE { handle_coder_bits(coder, 16, $2); }
         | WORD RAW_LINE { handle_coder_bits(coder, 32, $2); }

raw_content : /* empty */
            | SYNTAX { push_coder_new_syntax(coder); } raw_syntax raw_content
            | hooks raw_content

raw_syntax : /* empty */
           | subid raw_syntax
           | assertions raw_syntax
           | conversions raw_syntax
           | asm raw_syntax
           | rules raw_syntax

subid : SUBID RAW_LINE { handle_coder_subid(coder, $2); }

assertions : ASSERT RAW_BLOCK { handle_coder_assertions(coder, $2); }

conversions : CONV RAW_BLOCK { handle_coder_conversions(coder, $2); }

asm : ASM RAW_LINE { handle_coder_asm(coder, $2); }


/* Définitions communes */

rules : RULES RAW_BLOCK { handle_coder_rules(coder, $2); }

hooks : HOOKS RAW_BLOCK { handle_coder_hooks(coder, $2); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : coder = codeur impliqué dans le processus.                   *
*                temp  = zone de travail à destination des lectures manuelles.*
*                msg   = message d'erreur.                                    *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(rented_coder *coder, char *temp, char *msg)
{
	printf("YYERROR line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin du fichier à charger en mémoire.           *
*                length   = taille de l'espace mémoie à mettre en place. [OUT]*
*                                                                             *
*  Description : Prépare le traitement d'un contenu en l'affichant en mémoire.*
*                                                                             *
*  Retour      : Adresse valide ou MAP_FAILED en cas d'échec.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *map_input_data(const char *filename, size_t *length)
{
    void *result;                           /* Espace mémoire à retourner  */
    int fd;                                 /* Descripteur du fichier      */
    struct stat info;                       /* Informations sur le fichier */
    int ret;                                /* Bilan d'un appel            */

    result = NULL;

    fd = open(filename, O_RDONLY);
    if (fd == -1)
    {
        perror("open");
        goto mid_exit;
    }

    ret = fstat(fd, &info);
    if (ret == -1)
    {
        perror("fstat");
        goto mid_exit_with_fd;
    }

    *length = info.st_size;

    result = mmap(NULL, *length, PROT_READ, MAP_PRIVATE, fd, 0);
    if (result == MAP_FAILED)
    {
        perror("mmap");
        goto mid_exit_with_fd;
    }

 mid_exit_with_fd:

    close(fd);

 mid_exit:

    return result;


}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin d'accès à un fichier à traiter.            *
*                pp       = préprocesseur déjà chargé à intégrer.             *
*                                                                             *
*  Description : Charge en mémoire la définition contenue dans un fichier.    *
*                                                                             *
*  Retour      : Définition chargée ou NULL en cas d'erreur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

rented_coder *process_definition_file(const char *filename, pre_processor *pp)
{
    rented_coder *result;                   /* Codeur à briffer et renvoyer*/
    size_t length;                          /* Nombre d'octets à traiter   */
    char *content;                          /* Contenu brut à analyser     */
    char *temp;                             /* Zone de travail temporaire  */
    YY_BUFFER_STATE state;                  /* Contexte d'analyse          */
    int status;                             /* Bilan d'une analyse         */

    content = map_input_data(filename, &length);
    if (content == MAP_FAILED)
    {
        result = NULL;
        goto exit;
    }

    result = create_coder(pp);
    set_coder_input_file(result, filename);

    temp = (char *)calloc(length, sizeof(char));

    state = d2c__scan_bytes(content, length);

    status = yyparse(result, temp);

    if (status == EXIT_FAILURE)
    {
        delete_coder(result);
        result = NULL;
    }

    yy_delete_buffer(state);

    free(temp);

    munmap(content, length);

 exit:

    return result;

}
