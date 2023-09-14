
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(disass_assert *, char *);

%}


%code requires {

#include "decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères        */

    struct
    {
        char *field;                        /* Nom de champ de bits        */
        DisassCondOp op;                    /* Opération impliquée         */
        char *value;                        /* Valeur soumise à condition  */

    } cond_info;

}


%define api.pure full

%parse-param { disass_assert *dassert }

%code provides {

#define YY_DECL \
    int assert_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token CR
%token EQ NE
%token AND OR
%token FIELD VALUE

%type <cond_info> condition
%type <string> FIELD
%type <string> VALUE


%%


assert : /* empty */
       | conditions assert

conditions : condition               { register_disass_assert(dassert, DCG_UNIQ, $1.field, $1.op, $1.value); }
           | condition AND and_conds { extend_disass_assert(dassert, $1.field, $1.op, $1.value); }
           | condition OR or_conds   { extend_disass_assert(dassert, $1.field, $1.op, $1.value); }

and_conds : condition                { register_disass_assert(dassert, DCG_AND, $1.field, $1.op, $1.value); }
          | condition AND and_conds  { extend_disass_assert(dassert, $1.field, $1.op, $1.value); }

or_conds : condition                 { register_disass_assert(dassert, DCG_OR, $1.field, $1.op, $1.value); }
         | condition AND or_conds    { extend_disass_assert(dassert, $1.field, $1.op, $1.value); }

condition : FIELD EQ VALUE           { $$.field = $1; $$.op = DCO_EQ; $$.value = $3; }
          | FIELD NE VALUE           { $$.field = $1; $$.op = DCO_NE; $$.value = $3; }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = structure impliquée dans le processus.             *
*                msg     = message d'erreur.                                  *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(disass_assert *dassert, char *msg)
{
	printf("assert yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dassert = structure à constituer à partir de données lues.   *
*                raw     = données brutes à analyser.                         *
*                                                                             *
*  Description : Interprête des données relatives à une série de conditions.  *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_assertions_from_raw_block(disass_assert *dassert, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(dassert);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
