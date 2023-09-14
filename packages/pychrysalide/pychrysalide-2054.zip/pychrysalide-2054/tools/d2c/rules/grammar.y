
%{

#include "tokens.h"
#include "../helpers.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(decoding_rules *, char *);

%}


%code requires {

#include "decl.h"
#include "../args/decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères #1     */
    const char *cstring;                    /* Chaîne de caractères #2     */

    cond_expr *expr;                        /* Expression de déclenchement */
    rule_action raction;                    /* Action et éléments associés */
}


%define api.pure full

%parse-param { decoding_rules *rules }

%code provides {

#define YY_DECL \
    int rules_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token IF EXPR_START EXPR_END THEN

%token SEE CALL CHK_CALL UNPREDICTABLE

%token NAME

%token EQUAL BINVAL HEXVAL

%token AND AND_LOG

%token RAW_LINE


%type <string> NAME

%type <cstring> RAW_LINE

%type <expr> rule_cond
%type <string> BINVAL HEXVAL
%type <raction> action


%%


rules_list : /* empty */
           | rules_list rule

rule : IF EXPR_START rule_cond EXPR_END THEN action { register_conditional_rule(rules, $3, &$6); }
     | action                                       { register_conditional_rule(rules, NULL, &$1); }

rule_cond : NAME                { $$ = build_named_cond_expression($1); }
          | NAME EQUAL BINVAL   { $$ = build_simple_cond_expression($1, CCT_EQUAL, $3, true); }
          | NAME EQUAL HEXVAL   { $$ = build_simple_cond_expression($1, CCT_EQUAL, $3, false); }
          | NAME AND_LOG BINVAL { $$ = build_simple_cond_expression($1, CCT_AND, $3, true); }
          | NAME AND_LOG HEXVAL { $$ = build_simple_cond_expression($1, CCT_AND, $3, false); }
          | EXPR_START rule_cond EXPR_END AND EXPR_START rule_cond EXPR_END
                                { $$ = build_composed_cond_expression($2, COT_AND, $6); }

action : UNPREDICTABLE      { $$.type = CAT_UNPREDICTABLE; }
       | CALL RAW_LINE      {
                                right_op_t rop;
                                bool status;

                                status = load_call_from_raw_line(&rop, $2);
                                if (!status) YYABORT;

                                $$.type = CAT_CALL; $$.callee = rop.func; $$.args = rop.args;

                            }
       | CHK_CALL RAW_LINE  {
                                right_op_t rop;
                                bool status;

                                status = load_call_from_raw_line(&rop, $2);
                                if (!status) YYABORT;

                                $$.type = CAT_CHECKED_CALL; $$.callee = rop.func; $$.args = rop.args;

                            }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : rules = structure impliquée dans le processus.               *
*                msg   = message d'erreur.                                    *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(decoding_rules *rules, char *msg)
{
	printf("yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rules = structure à constituer à partir de données lues.     *
*                raw   = données brutes à analyser.                           *
*                                                                             *
*  Description : Interprête des données relatives à un bloc règles.           *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_rules_from_raw_block(decoding_rules *rules, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(rules);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
