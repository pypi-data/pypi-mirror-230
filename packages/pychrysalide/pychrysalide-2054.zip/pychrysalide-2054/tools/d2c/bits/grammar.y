
%{

#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(coding_bits *, char *);

%}


%code requires {

#include "decl.h"

}


%union {

    char *string;                           /* Chaîne de caractères        */
    int integer;                            /* Valeur numérique entière    */

}


%define api.pure full

%parse-param { coding_bits *bits }

%code provides {

#define YY_DECL \
    int bits_lex(YYSTYPE *yylvalp)

YY_DECL;

}


%token NAME SIZE BIT

%type <string> NAME
%type <integer> SIZE BIT


%%


bitfield : /* empty */
         | NAME SIZE bitfield   { register_named_field_in_bits(bits, $1, $2); }
         | BIT bitfield         { register_bit_in_bits(bits, $1); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : bits = structure impliquée dans le processus.                *
*                msg  = message d'erreur.                                     *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(coding_bits *bits, char *msg)
{
	printf("bits yyerror line %d: %s\n", yyget_lineno(), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits     = structure à constituer à partir de données lues.  *
*                expected = nombre de bits définis à attendre.                *
*                raw      = données brutes à analyser.                        *
*                                                                             *
*  Description : Interprête des données relatives à un champ de bits.         *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_bits_from_raw_line(coding_bits *bits, unsigned int expected, const char *raw)
{
    bool result;                            /* Bilan à faire remonter      */
    YY_BUFFER_STATE state;                  /* Support d'analyse           */
    int status;                             /* Bilan de l'analyse          */

    state = yy_scan_string(raw);

    status = yyparse(bits);

    result = (status == 0);

    yy_delete_buffer(state);

    if (result && count_coded_bits(bits) != expected)
    {
        fprintf(stderr, "Unexpected word size: %u vs %u\n", count_coded_bits(bits), expected);
        result = false;
    }

    return result;

}
