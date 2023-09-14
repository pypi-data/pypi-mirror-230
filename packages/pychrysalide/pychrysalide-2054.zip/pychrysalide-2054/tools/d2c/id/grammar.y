
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(instr_id *, char *);

%}


%code requires {

#include "decl.h"

}


%union {

    unsigned int value;                     /* Valeur numérique            */

}


%define api.pure full

%parse-param { instr_id *id }

%code provides {

#define YY_DECL \
    int id_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token VALUE

%type <value> VALUE



%%


id : VALUE { set_instruction_id_value(id, $1); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : id  = structure impliquée dans le processus.                 *
*                msg = message d'erreur.                                      *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(instr_id *id, char *msg)
{
	printf("id yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id  = structure à constituer à partir de données lues.       *
*                raw = données brutes à analyser.                             *
*                                                                             *
*  Description : Interprête des données relatives à un identifiant.           *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_id_from_raw_line(instr_id *id, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(id);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
