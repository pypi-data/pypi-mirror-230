
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(instr_hooks *, char *);

%}


%code requires {

#include "decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères        */

}


%define api.pure full

%parse-param { instr_hooks *hooks }

%code provides {

#define YY_DECL \
    int hooks_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token NAME EQ

%type <string> NAME


%%


hookings : /* empty */
         | hookings hooking

hooking : NAME EQ NAME { register_hook_function(hooks, $1, $3); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : hooks = structure impliquée dans le processus.               *
*                msg   = message d'erreur.                                    *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(instr_hooks *hooks, char *msg)
{
	printf("hooks yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hooks = structure à constituer à partir de données lues.     *
*                raw   = données brutes à analyser.                           *
*                                                                             *
*  Description : Interprête des données relatives à un champ de bits.         *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_hooks_from_raw_line(instr_hooks *hooks, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(hooks);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
