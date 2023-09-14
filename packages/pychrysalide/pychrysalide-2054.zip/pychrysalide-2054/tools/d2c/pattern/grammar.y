
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(asm_pattern *, char *);

%}


%code requires {

#include "decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères        */

}


%define api.pure full

%parse-param { asm_pattern *pattern }

%code provides {

#define YY_DECL \
    int pattern_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token OPERAND

%type <string> OPERAND


%%


operands : /* empty */
         | operands OPERAND { register_asm_pattern_item(pattern, $2); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = structure impliquée dans le processus.             *
*                msg     = message d'erreur.                                  *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(asm_pattern *pattern, char *msg)
{
	printf("syntax yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = structure à constituer à partir de données lues.   *
*                raw     = données brutes à analyser.                         *
*                                                                             *
*  Description : Interprête des données liées à une définition de syntaxe.    *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_asm_pattern_from_raw_line(asm_pattern *pattern, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(pattern);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
