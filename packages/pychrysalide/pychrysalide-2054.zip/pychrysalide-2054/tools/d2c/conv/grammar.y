
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(conv_list *, char *);

%}


%code requires {

#include "decl.h"
#include "../args/decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères #1     */
    const char *cstring;                    /* Chaîne de caractères #2     */

    conv_func *subst;                       /* Fonction de conversion      */

}


%define api.pure full

%parse-param { conv_list *list }

%code provides {

#define YY_DECL \
    int conv_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token NAME
%token EQ
%token RAW_LINE

%type <string> NAME
%type <cstring> RAW_LINE

%type <subst> substitution


%%


substitutions : /* empty */
              | substitutions substitution { register_conversion(list, $2); }

substitution : NAME EQ RAW_LINE {
                                    right_op_t rop;
                                    bool status;

                                    status = load_args_from_raw_line(&rop, $3);
                                    if (!status) YYABORT;

                                    if (rop.func == NULL)
                                        $$ = make_conv_from_expr($1, rop.expr);
                                    else
                                        $$ = make_conv_from_func($1, rop.func, rop.args);

                                }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : list = structure impliquée dans le processus.                *
*                msg  = message d'erreur.                                     *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(conv_list *list, char *msg)
{
	printf("yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = structure à constituer à partir de données lues.      *
*                raw  = données brutes à analyser.                            *
*                                                                             *
*  Description : Interprête des données relatives à un bloc de conversions.   *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_convs_from_raw_block(conv_list *list, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(list);

    result = (status == 0);

    yy_delete_buffer(state);

    return result;

}
