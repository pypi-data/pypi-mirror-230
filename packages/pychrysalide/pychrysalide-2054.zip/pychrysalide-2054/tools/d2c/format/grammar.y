
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(operands_format *, char *);

%}


%code requires {

#include "decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères        */

}


%define api.pure full

%parse-param { operands_format *format }

%code provides {

#define YY_DECL \
    int format_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token OPS_TYPE OR

%type <string> OPS_TYPE



%%


types : type
      | type OR types

type : OPS_TYPE { add_operands_format_type(format, $1); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : format = structure impliquée dans le processus.              *
*                msg    = message d'erreur.                                   *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(operands_format *format, char *msg)
{
	printf("bits yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = structure à constituer à partir de données lues.    *
*                raw    = données brutes à analyser.                          *
*                                                                             *
*  Description : Interprête des données relatives à une définition de format. *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_format_from_raw_line(operands_format *format, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(format);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
