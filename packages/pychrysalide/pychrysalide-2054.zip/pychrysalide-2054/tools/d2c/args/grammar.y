
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(right_op_t *, unsigned int *, char *);


%}


%code requires {

#include "decl.h"

}


%union {

    right_op_t operand;                     /* Construction finale         */

    char *string;                           /* Chaîne de caractères        */
    int integer;                            /* Valeur numérique entière    */

    arg_list_t *args;                       /* Liste d'arguments           */
    arg_expr_t *arg;                        /* Argument multi-usages       */
    ConvUnaryOperation un_op;               /* Opération unaire            */
    ConvBinaryOperation bin_op;             /* Opération bianire           */

}


%define api.pure full

%parse-param { right_op_t *operand } { unsigned int *init_token }
%lex-param { unsigned int *init_token }

%code provides {

#define YY_DECL \
    int args_lex(YYSTYPE *yylvalp, unsigned int *init_token)

YY_DECL;

}


%token FORCE_EXPR FORCE_CALL ALLOW_ALL
%token NAME
%token NUMBER BINVAL HEXVAL STRING
%token COMMA COLON OP CP
%token NOT AND_LOG EOR LSHIFT EQ NE
%token AND_BOOL OR_BOOL


%type <string> NAME
%type <integer> NUMBER
%type <string> BINVAL HEXVAL STRING

%type <operand> call
%type <args> arg_list
%type <arg> arg_expr arg_logical_expr arg_composed
%type <un_op> arg_expr_un_op
%type <bin_op> arg_expr_bin_op
%type <string> arg_field


%%


right_op : FORCE_EXPR arg_expr  { operand->func = NULL; operand->expr = $2; }
         | FORCE_CALL call      { *operand = $2; }
         | arg_expr             { operand->func = NULL; operand->expr = $1; }
         | call                 { *operand = $1; }

call : NAME OP arg_list CP { $$.func = $1; $$.args = $3; }

arg_list : /* empty */             { $$ = build_empty_arg_list(); }
         | arg_expr                { $$ = build_arg_list($1); }
         | arg_list COMMA arg_expr { $$ = extend_arg_list($1, $3); }

arg_expr : NAME                                     { $$ = build_arg_expr_from_name($1); }
          | NUMBER                                  { $$ = build_arg_expr_from_number($1); }
          | BINVAL                                  { $$ = build_arg_expr_from_binval($1); }
          | HEXVAL                                  { $$ = build_arg_expr_from_hexval($1); }
          | STRING                                  { $$ = build_arg_expr_from_string($1); }
          | arg_logical_expr                        { $$ = $1; }
          | arg_composed                            { $$ = $1; }
          | OP arg_expr CP                          { $$ = $2; }
          | arg_expr_un_op arg_expr                 { $$ = build_unary_arg_expr($2, $1); }
          | arg_expr EQ arg_expr                    { $$ = build_conditional_arg_expr($1, $3, true); }
          | arg_expr NE arg_expr                    { $$ = build_conditional_arg_expr($1, $3, false); }
          | arg_expr arg_expr_bin_op arg_expr       { $$ = build_binary_arg_expr($1, $3, $2); }

arg_expr_un_op : NOT { $$ = CUO_NOT; }

arg_expr_bin_op : AND_LOG   { $$ = CBO_AND; }
                | EOR       { $$ = CBO_EOR; }
                | LSHIFT    { $$ = CBO_LSHIFT; }

arg_logical_expr : arg_expr AND_BOOL arg_expr           { $$ = build_logical_arg_expr($1, $3, true); }
                 | arg_logical_expr AND_BOOL arg_expr   { $$ = build_logical_arg_expr($1, $3, true); }
                 | arg_expr OR_BOOL arg_expr            { $$ = build_logical_arg_expr($1, $3, false); }
                 | arg_logical_expr OR_BOOL arg_expr    { $$ = build_logical_arg_expr($1, $3, false); }

arg_composed : arg_field COLON arg_field    { $$ = build_composed_arg_expr($1, $3); }
             | arg_composed COLON arg_field { $$ = extend_composed_arg_expr($1, $3); }

arg_field : NAME   { $$ = $1; }
          | BINVAL { $$ = $1; }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : operand    = structure impliquée dans le processus.          *
*                init_token = éventuel jeton d'initialisation ou NULL.        *
*                msg        = message d'erreur.                               *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(right_op_t *operand, unsigned int *init_token, char *msg)
{
	printf("args yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = structure à constituer à partir de données lues.   *
*                raw     = données brutes à analyser.                         *
*                                                                             *
*  Description : Interprête des données relatives un opérande de droite.      *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_args_from_raw_line(right_op_t *operand, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(operand, (unsigned int []) { ALLOW_ALL });

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = structure à constituer à partir de données lues.   *
*                raw     = données brutes à analyser.                         *
*                                                                             *
*  Description : Interprête des données relatives à un appel avec arguments.  *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_call_from_raw_line(right_op_t *operand, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(operand, (unsigned int []) { FORCE_CALL });

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
