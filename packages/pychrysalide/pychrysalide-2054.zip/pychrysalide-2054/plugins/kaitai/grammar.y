
%{

#include "expression.h"
#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(yyscan_t, const kaitai_scope_t *, resolved_value_t *, const char *);

/* Interprète une expression en une valeur quelconque. */
static bool _resolve_kaitai_expression_as_any(const kaitai_scope_t *, const char *, size_t, resolved_value_t *);

/* Traduit les éventuels champs impliqués dans une expression. */
static bool reduce_resolved_kaitai_expression(resolved_value_t *);


%}


%code requires {

#define YY_TYPEDEF_YY_SCANNER_T
typedef void *yyscan_t;

#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <glib.h>

#include "expression.h"
#include "record.h"
#include "records/item.h"
#include "records/list.h"
#include "records/value.h"

}

%union {

    resolved_value_t value;                 /* Valeur portée               */

    unsigned long long unsigned_integer;    /* Valeur entière #1           */
    signed long long signed_integer;        /* Valeur entière #2           */
    double floating_number;                 /* Valeur à virgule flottante  */
    sized_string_t sized_cstring;           /* Chaîne de caractères        */
    char byte;                              /* Octet unique                */

}


/**
 * Cf.
 * http://stackoverflow.com/questions/34418381/how-to-reference-lex-or-parse-parameters-in-flex-rules/34420950
 */

%define api.pure full

%parse-param { yyscan_t yyscanner } { const kaitai_scope_t *locals } { resolved_value_t *resolved }
%lex-param { yyscan_t yyscanner }

%code provides {

#define YY_DECL \
    int kaitai_lex(YYSTYPE *yylval_param, yyscan_t yyscanner)

YY_DECL;



#define SET_ERR(out)    \
    out.type = GVT_ERROR

#define EXIT_WITH_ERR(out, lbl)                 \
    do                                          \
    {                                           \
        SET_ERR(out);                           \
        goto exit_ ## lbl;                      \
    }                                           \
    while (0)

#define CHECK_TYPE(arg, tp, out, lbl)               \
    if (arg.type != tp) EXIT_WITH_ERR(out, lbl)

#define CHECK_TYPES(arg, tp1, tp2, out, lbl)        \
    if (arg.type != tp1 && arg.type != tp2) EXIT_WITH_ERR(out, lbl)

#define REDUCE_EXPR(arg, out, lbl)                  \
    if (!reduce_resolved_kaitai_expression(&arg))   \
        EXIT_WITH_ERR(out, lbl)

#define REDUCE_NUMERIC_EXPR(arg, out, lbl)                          \
    if (!reduce_resolved_kaitai_expression(&arg))                   \
        EXIT_WITH_ERR(out, lbl);                                    \
    if (arg.type == GVT_SIGNED_INTEGER && arg.signed_integer >= 0)  \
    {                                                               \
        arg.unsigned_integer = arg.signed_integer;                  \
        arg.type = GVT_UNSIGNED_INTEGER;                            \
    }


#define ARITHMETIC_ADD_CODE(op1, op2, out, lbl)                                         \
    switch (op1.type)                                                                   \
    {                                                                                   \
        case GVT_UNSIGNED_INTEGER:                                                      \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                       \
            {                                                                           \
                out.unsigned_integer = op1.unsigned_integer + op2.unsigned_integer;     \
                out.type = GVT_UNSIGNED_INTEGER;                                        \
            }                                                                           \
            else if (op2.type == GVT_SIGNED_INTEGER)                                    \
            {                                                                           \
                if (op1.unsigned_integer < -op2.signed_integer)                         \
                {                                                                       \
                    out.signed_integer = op1.unsigned_integer + op2.signed_integer;     \
                    out.type = GVT_SIGNED_INTEGER;                                      \
                }                                                                       \
                else                                                                    \
                {                                                                       \
                    out.unsigned_integer = op1.unsigned_integer + op2.signed_integer;   \
                    out.type = GVT_UNSIGNED_INTEGER;                                    \
                }                                                                       \
            }                                                                           \
            else if (op2.type == GVT_FLOAT)                                             \
            {                                                                           \
                out.floating_number = op1.unsigned_integer + op2.floating_number;       \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else EXIT_WITH_ERR(out, lbl);                                               \
            break;                                                                      \
                                                                                        \
        case GVT_SIGNED_INTEGER:                                                        \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                       \
            {                                                                           \
                if (-op1.signed_integer > op2.unsigned_integer)                         \
                {                                                                       \
                    out.signed_integer = op1.signed_integer + op2.unsigned_integer;     \
                    out.type = GVT_SIGNED_INTEGER;                                      \
                }                                                                       \
                else                                                                    \
                {                                                                       \
                    out.unsigned_integer = op1.signed_integer + op2.unsigned_integer;   \
                    out.type = GVT_UNSIGNED_INTEGER;                                    \
                }                                                                       \
            }                                                                           \
            else if (op2.type == GVT_SIGNED_INTEGER)                                    \
            {                                                                           \
                out.signed_integer = op1.signed_integer + op2.signed_integer;           \
                out.type = GVT_SIGNED_INTEGER;                                          \
            }                                                                           \
            else if (op2.type == GVT_FLOAT)                                             \
            {                                                                           \
                out.floating_number = op1.signed_integer + op2.floating_number;         \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else EXIT_WITH_ERR(out, lbl);                                               \
            break;                                                                      \
                                                                                        \
        case GVT_FLOAT:                                                                 \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                       \
            {                                                                           \
                out.floating_number = op1.floating_number + op2.unsigned_integer;       \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else if (op2.type == GVT_SIGNED_INTEGER)                                    \
            {                                                                           \
                out.floating_number = op1.floating_number + op2.signed_integer;         \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else if (op2.type == GVT_FLOAT)                                             \
            {                                                                           \
                out.floating_number = op1.floating_number + op2.floating_number;        \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else EXIT_WITH_ERR(out, lbl);                                               \
            break;                                                                      \
                                                                                        \
        default:                                                                        \
            EXIT_WITH_ERR(out, lbl);                                                    \
            break;                                                                      \
                                                                                        \
    }


#define ARITHMETIC_SUB_CODE(op1, op2, out, lbl)                                         \
    switch (op1.type)                                                                   \
    {                                                                                   \
        case GVT_UNSIGNED_INTEGER:                                                      \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                       \
            {                                                                           \
                if (op1.unsigned_integer < op2.unsigned_integer)                        \
                {                                                                       \
                    out.signed_integer = op1.unsigned_integer - op2.unsigned_integer;   \
                    out.type = GVT_SIGNED_INTEGER;                                      \
                }                                                                       \
                else                                                                    \
                {                                                                       \
                    out.unsigned_integer = op1.unsigned_integer - op2.unsigned_integer; \
                    out.type = GVT_UNSIGNED_INTEGER;                                    \
                }                                                                       \
            }                                                                           \
            else if (op2.type == GVT_SIGNED_INTEGER)                                    \
            {                                                                           \
                out.unsigned_integer = op1.unsigned_integer - op2.signed_integer;       \
                out.type = GVT_UNSIGNED_INTEGER;                                        \
            }                                                                           \
            else if (op2.type == GVT_FLOAT)                                             \
            {                                                                           \
                out.floating_number = op1.unsigned_integer - op2.floating_number;       \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else EXIT_WITH_ERR(out, lbl);                                               \
            break;                                                                      \
                                                                                        \
        case GVT_SIGNED_INTEGER:                                                        \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                       \
            {                                                                           \
                out.signed_integer = op1.signed_integer - op2.unsigned_integer;         \
                out.type = GVT_SIGNED_INTEGER;                                          \
            }                                                                           \
            else if (op2.type == GVT_SIGNED_INTEGER)                                    \
            {                                                                           \
                if (op1.signed_integer < op2.signed_integer)                            \
                {                                                                       \
                    out.signed_integer = op1.signed_integer - op2.signed_integer;       \
                    out.type = GVT_SIGNED_INTEGER;                                      \
                }                                                                       \
                else                                                                    \
                {                                                                       \
                    out.unsigned_integer = op1.signed_integer - op2.signed_integer;     \
                    out.type = GVT_UNSIGNED_INTEGER;                                    \
                }                                                                       \
            }                                                                           \
            else if (op2.type == GVT_FLOAT)                                             \
            {                                                                           \
                out.floating_number = op1.signed_integer - op2.floating_number;         \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else EXIT_WITH_ERR(out, lbl);                                               \
            break;                                                                      \
                                                                                        \
        case GVT_FLOAT:                                                                 \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                       \
            {                                                                           \
                out.floating_number = op1.floating_number - op2.unsigned_integer;       \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else if (op2.type == GVT_SIGNED_INTEGER)                                    \
            {                                                                           \
                out.floating_number = op1.floating_number - op2.signed_integer;         \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else if (op2.type == GVT_FLOAT)                                             \
            {                                                                           \
                out.floating_number = op1.floating_number - op2.floating_number;        \
                out.type = GVT_FLOAT;                                                   \
            }                                                                           \
            else EXIT_WITH_ERR(out, lbl);                                               \
            break;                                                                      \
                                                                                        \
        default:                                                                        \
            EXIT_WITH_ERR(out, lbl);                                                    \
            break;                                                                      \
                                                                                        \
    }


#define ARITHMETIC_GENOP_CODE(op1, op2, _meth_, out, lbl)                                   \
    switch (op1.type)                                                                       \
    {                                                                                       \
        case GVT_UNSIGNED_INTEGER:                                                          \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                           \
            {                                                                               \
                out.unsigned_integer = op1.unsigned_integer _meth_ op2.unsigned_integer;    \
                out.type = GVT_UNSIGNED_INTEGER;                                            \
            }                                                                               \
            else if (op2.type == GVT_SIGNED_INTEGER)                                        \
            {                                                                               \
                out.signed_integer = op1.unsigned_integer _meth_ op2.signed_integer;        \
                out.type = GVT_SIGNED_INTEGER;                                              \
            }                                                                               \
            else if (op2.type == GVT_FLOAT)                                                 \
            {                                                                               \
                out.floating_number = op1.unsigned_integer _meth_ op2.floating_number;      \
                out.type = GVT_FLOAT;                                                       \
            }                                                                               \
            else EXIT_WITH_ERR(out, lbl);                                                   \
            break;                                                                          \
                                                                                            \
        case GVT_SIGNED_INTEGER:                                                            \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                           \
            {                                                                               \
                out.unsigned_integer = op1.signed_integer _meth_ op2.unsigned_integer;      \
                out.type = GVT_SIGNED_INTEGER;                                              \
            }                                                                               \
            else if (op2.type == GVT_SIGNED_INTEGER)                                        \
            {                                                                               \
                out.unsigned_integer = op1.signed_integer _meth_ op2.signed_integer;        \
                out.type = GVT_UNSIGNED_INTEGER;                                            \
            }                                                                               \
            else if (op2.type == GVT_FLOAT)                                                 \
            {                                                                               \
                out.floating_number = op1.signed_integer _meth_ op2.floating_number;        \
                out.type = GVT_FLOAT;                                                       \
            }                                                                               \
            else EXIT_WITH_ERR(out, lbl);                                                   \
            break;                                                                          \
                                                                                            \
        case GVT_FLOAT:                                                                     \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                           \
            {                                                                               \
                out.unsigned_integer = op1.floating_number _meth_ op2.unsigned_integer;     \
                out.type = GVT_FLOAT;                                                       \
            }                                                                               \
            else if (op2.type == GVT_SIGNED_INTEGER)                                        \
            {                                                                               \
                out.signed_integer = op1.floating_number _meth_ op2.signed_integer;         \
                out.type = GVT_FLOAT;                                                       \
            }                                                                               \
            else if (op2.type == GVT_FLOAT)                                                 \
            {                                                                               \
                out.floating_number = op1.floating_number _meth_ op2.floating_number;       \
                out.type = GVT_FLOAT;                                                       \
            }                                                                               \
            else EXIT_WITH_ERR(out, lbl);                                                   \
            break;                                                                          \
                                                                                            \
        default:                                                                            \
            EXIT_WITH_ERR(out, lbl);                                                        \
            break;                                                                          \
                                                                                            \
    }


/**
 * Cf. https://stackoverflow.com/questions/11720656/modulo-operation-with-negative-numbers/52529440#52529440
 */
#define EUCLIDEAN_MODULO(a, b, r)       \
    r = a % (signed long long)b;        \
    if (r < 0)                          \
        r = (b < 0) ? r - b : r + b;    \


#define ARITHMETIC_MOD_CODE(op1, op2, out, lbl)                                                     \
    switch (op1.type)                                                                               \
    {                                                                                               \
        case GVT_UNSIGNED_INTEGER:                                                                  \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                                   \
            {                                                                                       \
                EUCLIDEAN_MODULO(op1.unsigned_integer, op2.unsigned_integer, out.unsigned_integer); \
                out.type = GVT_UNSIGNED_INTEGER;                                                    \
            }                                                                                       \
            else if (op2.type == GVT_SIGNED_INTEGER)                                                \
            {                                                                                       \
                EUCLIDEAN_MODULO(op1.unsigned_integer, op2.signed_integer, out.signed_integer);     \
                out.type = GVT_SIGNED_INTEGER;                                                      \
            }                                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                                           \
            break;                                                                                  \
                                                                                                    \
        case GVT_SIGNED_INTEGER:                                                                    \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                                   \
            {                                                                                       \
                EUCLIDEAN_MODULO(op1.signed_integer, op2.unsigned_integer, out.signed_integer);     \
                out.type = GVT_SIGNED_INTEGER;                                                      \
            }                                                                                       \
            else if (op2.type == GVT_SIGNED_INTEGER)                                                \
            {                                                                                       \
                EUCLIDEAN_MODULO(op1.signed_integer, op2.signed_integer, out.signed_integer);       \
                out.type = GVT_SIGNED_INTEGER;                                                      \
            }                                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                                           \
            break;                                                                                  \
                                                                                                    \
        default:                                                                                    \
            EXIT_WITH_ERR(out, lbl);                                                                \
            break;                                                                                  \
                                                                                                    \
    }


#define RELATIONAL_CODE(op1, op2, _meth_, out, lbl)                                 \
    switch (op1.type)                                                               \
    {                                                                               \
        case GVT_UNSIGNED_INTEGER:                                                  \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                   \
            {                                                                       \
                out.status = (op1.unsigned_integer _meth_ op2.unsigned_integer);    \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else if (op2.type == GVT_SIGNED_INTEGER)                                \
            {                                                                       \
                out.status = (op1.unsigned_integer _meth_ op2.signed_integer);      \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                           \
            break;                                                                  \
                                                                                    \
        case GVT_SIGNED_INTEGER:                                                    \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                   \
            {                                                                       \
                out.status = (op1.signed_integer _meth_ op2.unsigned_integer);      \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else if (op2.type == GVT_SIGNED_INTEGER)                                \
            {                                                                       \
                out.status = (op1.signed_integer _meth_ op2.signed_integer);        \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                           \
            break;                                                                  \
                                                                                    \
        case GVT_BYTES:                                                             \
            if (op2.type == GVT_BYTES)                                              \
            {                                                                       \
                int __ret;                                                          \
                __ret = szmemcmp(&op1.bytes, &op2.bytes);                           \
                out.status = (__ret _meth_ 0);                                      \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else if (op2.type == GVT_ARRAY)                                         \
            {                                                                       \
                sized_string_t __abytes_2;                                          \
                int __ret;                                                          \
                if (!g_kaitai_array_convert_to_bytes(op2.array, &__abytes_2))       \
                    EXIT_WITH_ERR(out, lbl);                                        \
                __ret = szmemcmp(&op1.bytes, &__abytes_2);                          \
                exit_szstr(&__abytes_2);                                            \
                out.status = (__ret _meth_ 0);                                      \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                           \
            break;                                                                  \
                                                                                    \
        case GVT_ARRAY:                                                             \
            if (op2.type == GVT_BYTES)                                              \
            {                                                                       \
                sized_string_t __abytes_1;                                          \
                int __ret;                                                          \
                if (!g_kaitai_array_convert_to_bytes(op1.array, &__abytes_1))       \
                    EXIT_WITH_ERR(out, lbl);                                        \
                __ret = szmemcmp(&__abytes_1, &op2.bytes);                          \
                exit_szstr(&__abytes_1);                                            \
                out.status = (__ret _meth_ 0);                                      \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else if (op2.type == GVT_ARRAY)                                         \
            {                                                                       \
                sized_string_t __abytes_1;                                          \
                sized_string_t __abytes_2;                                          \
                int __ret;                                                          \
                if (!g_kaitai_array_convert_to_bytes(op1.array, &__abytes_1))       \
                    EXIT_WITH_ERR(out, lbl);                                        \
                if (!g_kaitai_array_convert_to_bytes(op2.array, &__abytes_2))       \
                {                                                                   \
                    exit_szstr(&__abytes_1);                                        \
                    EXIT_WITH_ERR(out, lbl);                                        \
                }                                                                   \
                __ret = szmemcmp(&__abytes_1, &__abytes_2);                         \
                exit_szstr(&__abytes_1);                                            \
                exit_szstr(&__abytes_2);                                            \
                out.status = (__ret _meth_ 0);                                      \
                out.type = GVT_BOOLEAN;                                             \
            }                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                           \
            break;                                                                  \
                                                                                    \
        case GVT_STREAM:                                                            \
            if (op2.type == GVT_STREAM)                                             \
            {                                                                       \
                GBinContent *__cnt_1;                                               \
                GBinContent *__cnt_2;                                               \
                __cnt_1 = g_kaitai_stream_get_content(op1.stream);                  \
                __cnt_2 = g_kaitai_stream_get_content(op2.stream);                  \
                out.status = (__cnt_1 _meth_ __cnt_2);                              \
                out.type = GVT_BOOLEAN;                                             \
                g_object_unref(G_OBJECT(__cnt_1));                                  \
                g_object_unref(G_OBJECT(__cnt_2));                                  \
            }                                                                       \
            else EXIT_WITH_ERR(out, lbl);                                           \
            break;                                                                  \
                                                                                    \
        default:                                                                    \
            EXIT_WITH_ERR(out, lbl);                                                \
            break;                                                                  \
                                                                                    \
    }


#define BITWISE_CODE(op1, op2, _meth_, out, lbl)                                            \
    switch (op1.type)                                                                       \
    {                                                                                       \
        case GVT_UNSIGNED_INTEGER:                                                          \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                           \
            {                                                                               \
                out.unsigned_integer = (op1.unsigned_integer _meth_ op2.unsigned_integer);  \
                out.type = GVT_UNSIGNED_INTEGER;                                            \
            }                                                                               \
            else EXIT_WITH_ERR(out, lbl);                                                   \
            break;                                                                          \
                                                                                            \
        case GVT_SIGNED_INTEGER:                                                            \
            if (op2.type == GVT_UNSIGNED_INTEGER)                                           \
            {                                                                               \
                out.signed_integer = (op1.signed_integer _meth_ op2.unsigned_integer);      \
                out.type = GVT_SIGNED_INTEGER;                                              \
            }                                                                               \
            else EXIT_WITH_ERR(out, lbl);                                                   \
            break;                                                                          \
                                                                                            \
        default:                                                                            \
            EXIT_WITH_ERR(out, lbl);                                                        \
            break;                                                                          \
                                                                                            \
    }




}


%token <unsigned_integer> UNSIGNED_INTEGER
%token <signed_integer> SIGNED_INTEGER
%token <floating_number> FLOAT

%token <sized_cstring> IDENTIFIER
%token <sized_cstring> RAW_BYTES
%token <byte> RAW_BYTE
%token <sized_cstring> RAW_BYTES_WITH_ENDING_DOT
%token <sized_cstring> PLAIN_BYTES

%token <sized_cstring> ENCODING_NAME


%token PLUS             "+"
%token MINUS            "-"
%token MUL              "*"
%token DIV              "/"
%token MOD              "%"

%token LT               "<"
%token LE               "<="
%token EQ               "=="
%token NE               "!="
%token GT               ">"
%token GE               ">="

%token SHIFT_LEFT       "<<"
%token SHIFT_RIGHT      ">>"
%token BIT_AND          "&"
%token BIT_OR           "|"
%token BIT_XOR          "^"

%token NOT              "not"
%token AND              "and"
%token OR               "or"

%token PAREN_O          "("
%token PAREN_C          ")"
%token HOOK_O           "["
%token HOOK_C           "]"
%token COMMA            ","
%token DOT              "."

%token QMARK            "?"
%token COLON            ":"
%token DOUBLE_COLON     "::"

%token METH_SIZE        ".size"
%token METH_LENGTH      ".length"
%token METH_REVERSE     ".reverse"
%token METH_SUBSTRING   ".substring"
%token METH_TO_I        ".to_i"
%token METH_TO_I_RAD    ".to_i("
%token METH_TO_S        ".to_s"
%token METH_TO_S_ENC    ".to_s("

%token ROOT             "_root"
%token PARENT           "_parent"
%token LAST             "_"
%token METH_IO          "._io"

%token TRUE_CONST       "true"
%token FALSE_CONST      "false"


                                  //%type <value> operand
%type <value> any_expr
                                  //%type <value> arithm_expr
                                  //%type <value> arithm_op

%type <value> boolean



%type <value> arithmetic_expr
%type <value> relational_expr
%type <value> logical_expr
%type <value> bitwise_expr
%type <value> ternary_expr

%type <value> convert_2_bytes
%type <value> convert_2_integer


%type <value> integer

%type <value> float

%type <value> bytes

%type <value> bytes_concat
%type <value> raw_bytes


%type <value> array
%type <value> array_items


%type <value> field
%type <value> enumeration
%type <value> stream



%destructor { printf("----------------------freeing %p...\n", &$$), fflush(NULL); } <*>


                                  //%type <integer> INTEGER
                                  //

                                  //%type <integer> arithm_expr
                                  //%type <integer> arithm_op

                                  //%type <boolean> bool_expr
                                  //%type <boolean> relational_op logical_op ternary_op


                                  //%type <integer> constant





/**
 * Cf. https://en.wikipedia.org/wiki/Operators_in_C_and_C%2B%2B#Operator_precedence
 */





%left "?" ":"

%left OR
%left "and"

/* 13 */
%left "|"

/* 12 */
%left "^"

/* 11 */
%left "&"

%left LT LE EQ NE GT GE

/* 7 */
%left "<<" ">>"


%right NOT

%left PLUS MINUS
%left "*"
%left DIV MOD


%left "["




%left ".size"
%left ".length"
%left ".reverse"
%left ".substring"
%left ".to_i"
%left ".to_i("
%left ".to_s"
%left ".to_s("

%left "._io"

%left "."

/* 1 */
%right "::"


%%

        expressions : any_expr { *resolved = $1; }
                    ;

           any_expr : boolean           { $$ = $1; }
                    | bytes             { $$ = $1; }
                    | integer           { $$ = $1; }
                    | float             { $$ = $1; }
                    | array             { $$ = $1; }
                    | field             { $$ = $1; }
                    | enumeration       { $$ = $1; }
                    | stream            { $$ = $1; }
                    | arithmetic_expr   { $$ = $1; }
                    | relational_expr   { $$ = $1; }
                    | logical_expr      { $$ = $1; }
                    | bitwise_expr      { $$ = $1; }
                    | ternary_expr      { $$ = $1; }
                    | convert_2_bytes   { $$ = $1; }
                    | convert_2_integer { $$ = $1; }
                    | "(" any_expr ")"  { $$ = $2; }
                    ;


/* Expressions impliquants formules et opérandes */

    arithmetic_expr : any_expr "+" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, arithmetic_expr_plus);
                        REDUCE_NUMERIC_EXPR($3, $$, arithmetic_expr_plus);

                        if ($1.type == GVT_BYTES && $3.type == GVT_BYTES)
                        {
                            $$.bytes.len = $1.bytes.len + $3.bytes.len;
                            $$.bytes.data = malloc($$.bytes.len);

                            memcpy($$.bytes.data, $1.bytes.data, $1.bytes.len);
                            memcpy($$.bytes.data + $1.bytes.len, $3.bytes.data, $3.bytes.len);

                            $$.type = GVT_BYTES;

                        }

                        else if ($1.type == GVT_BYTES && $3.type == GVT_ARRAY)
                        {
                            sized_string_t __abytes_2;

                            if (!g_kaitai_array_convert_to_bytes($3.array, &__abytes_2))
                                EXIT_WITH_ERR($$, arithmetic_expr_plus);

                            $$.bytes.len = $1.bytes.len + __abytes_2.len;
                            $$.bytes.data = malloc($$.bytes.len);

                            memcpy($$.bytes.data, $1.bytes.data, $1.bytes.len);
                            memcpy($$.bytes.data + $1.bytes.len, __abytes_2.data, __abytes_2.len);

                            $$.type = GVT_BYTES;

                            exit_szstr(&__abytes_2);

                        }

                        else
                        {
                            ARITHMETIC_ADD_CODE($1, $3, $$, arithmetic_expr_plus);
                        }

                    exit_arithmetic_expr_plus:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "-" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, arithmetic_expr_minus);
                        REDUCE_NUMERIC_EXPR($3, $$, arithmetic_expr_minus);
                        ARITHMETIC_SUB_CODE($1, $3, $$, arithmetic_expr_minus);
                    exit_arithmetic_expr_minus:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "*" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, arithmetic_expr_mul);
                        REDUCE_NUMERIC_EXPR($3, $$, arithmetic_expr_mul);
                        ARITHMETIC_GENOP_CODE($1, $3, *, $$, arithmetic_expr_mul);
                    exit_arithmetic_expr_mul:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "/" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, arithmetic_expr_div);
                        REDUCE_NUMERIC_EXPR($3, $$, arithmetic_expr_div);
                        ARITHMETIC_GENOP_CODE($1, $3, /, $$, arithmetic_expr_div);
                    exit_arithmetic_expr_div:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "%" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, arithmetic_expr_mod);
                        REDUCE_NUMERIC_EXPR($3, $$, arithmetic_expr_mod);
                        ARITHMETIC_MOD_CODE($1, $3, $$, arithmetic_expr_mod);
                    exit_arithmetic_expr_mod:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    ;


    relational_expr : any_expr "<" any_expr
                    {
                        REDUCE_EXPR($1, $$, relational_expr_lt);
                        REDUCE_EXPR($3, $$, relational_expr_lt);
                        RELATIONAL_CODE($1, $3, <, $$, relational_expr_lt);
                    exit_relational_expr_lt:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "<=" any_expr
                    {
                        REDUCE_EXPR($1, $$, relational_expr_le);
                        REDUCE_EXPR($3, $$, relational_expr_le);
                        RELATIONAL_CODE($1, $3, <=, $$, relational_expr_le);
                    exit_relational_expr_le:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "==" any_expr
                    {
                        REDUCE_EXPR($1, $$, relational_expr_eq);
                        REDUCE_EXPR($3, $$, relational_expr_eq);
                        RELATIONAL_CODE($1, $3, ==, $$, relational_expr_eq);
                    exit_relational_expr_eq:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "!=" any_expr
                    {
                        REDUCE_EXPR($1, $$, relational_expr_ne);
                        REDUCE_EXPR($3, $$, relational_expr_ne);
                        RELATIONAL_CODE($1, $3, !=, $$, relational_expr_ne);
                    exit_relational_expr_ne:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr ">" any_expr
                    {
                        REDUCE_EXPR($1, $$, relational_expr_gt);
                        REDUCE_EXPR($3, $$, relational_expr_gt);
                        RELATIONAL_CODE($1, $3, >, $$, relational_expr_gt);
                    exit_relational_expr_gt:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr ">=" any_expr
                    {
                        REDUCE_EXPR($1, $$, relational_expr_ge);
                        REDUCE_EXPR($3, $$, relational_expr_ge);
                        RELATIONAL_CODE($1, $3, >=, $$, relational_expr_ge);
                    exit_relational_expr_ge:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    ;


       bitwise_expr : any_expr "<<" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, bitwise_expr_shift_left);
                        REDUCE_NUMERIC_EXPR($3, $$, bitwise_expr_shift_left);
                        BITWISE_CODE($1, $3, <<, $$, bitwise_expr_shift_left);
                    exit_bitwise_expr_shift_left:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr ">>" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, bitwise_expr_shift_right);
                        REDUCE_NUMERIC_EXPR($3, $$, bitwise_expr_shift_right);
                        BITWISE_CODE($1, $3, >>, $$, bitwise_expr_shift_right);
                    exit_bitwise_expr_shift_right:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "&" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, bitwise_expr_and);
                        REDUCE_NUMERIC_EXPR($3, $$, bitwise_expr_and);
                        BITWISE_CODE($1, $3, &, $$, bitwise_expr_and);
                    exit_bitwise_expr_and:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "|" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, bitwise_expr_or);
                        REDUCE_NUMERIC_EXPR($3, $$, bitwise_expr_or);
                        BITWISE_CODE($1, $3, |, $$, bitwise_expr_or);
                    exit_bitwise_expr_or:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "^" any_expr
                    {
                        REDUCE_NUMERIC_EXPR($1, $$, bitwise_expr_xor);
                        REDUCE_NUMERIC_EXPR($3, $$, bitwise_expr_xor);
                        BITWISE_CODE($1, $3, ^, $$, bitwise_expr_xor);
                    exit_bitwise_expr_xor:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    ;


       logical_expr : "not" any_expr
                    {
                        REDUCE_EXPR($2, $$, logical_expr_not);
                        CHECK_TYPE($2, GVT_BOOLEAN, $$, logical_expr_not);
                        $$.status = !$2.status;
                        $$.type = GVT_BOOLEAN;
                    exit_logical_expr_not:
                        EXIT_RESOLVED_VALUE($2);
                    }
                    | any_expr "and" any_expr
                    {
                        REDUCE_EXPR($1, $$, logical_expr_and);
                        CHECK_TYPE($1, GVT_BOOLEAN, $$, logical_expr_and);
                        REDUCE_EXPR($3, $$, logical_expr_and);
                        CHECK_TYPE($3, GVT_BOOLEAN, $$, logical_expr_and);
                        $$.status = $1.status && $3.status;
                        $$.type = GVT_BOOLEAN;
                    exit_logical_expr_and:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    | any_expr "or" any_expr
                    {
                        REDUCE_EXPR($1, $$, logical_expr_or);
                        CHECK_TYPE($1, GVT_BOOLEAN, $$, logical_expr_or);
                        REDUCE_EXPR($3, $$, logical_expr_or);
                        CHECK_TYPE($3, GVT_BOOLEAN, $$, logical_expr_or);
                        $$.status = $1.status || $3.status;
                        $$.type = GVT_BOOLEAN;
                    exit_logical_expr_or:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    ;


       ternary_expr : any_expr "?" any_expr ":" any_expr
                    {
                        REDUCE_EXPR($1, $$, ternary_expr);
                        CHECK_TYPE($1, GVT_BOOLEAN, $$, ternary_expr);
                        if ($1.status)
                            COPY_RESOLVED_VALUE($$, $3);
                        else
                            COPY_RESOLVED_VALUE($$, $5);
                    exit_ternary_expr:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                        EXIT_RESOLVED_VALUE($5);
                    }
                    ;


/* Conversions et méthodes particulières de types */

    convert_2_bytes : any_expr ".to_s"
                    {
                        int __ret;

                        if ($1.type == GVT_UNSIGNED_INTEGER)
                        {
                            __ret = asprintf(&$$.bytes.data, "%llu", $1.unsigned_integer);
                            if (__ret == -1) EXIT_WITH_ERR($$, convert_2_bytes_to_s);

                            $$.bytes.len = __ret;
                            $$.type = GVT_BYTES;

                        }
                        else if ($1.type == GVT_SIGNED_INTEGER)
                        {
                            __ret = asprintf(&$$.bytes.data, "%lld", $1.signed_integer);
                            if (__ret == -1) EXIT_WITH_ERR($$, convert_2_bytes_to_s);

                            $$.bytes.len = __ret;
                            $$.type = GVT_BYTES;

                        }
                        else
                            EXIT_WITH_ERR($$, convert_2_bytes_to_s);

                    exit_convert_2_bytes_to_s:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    | any_expr ".to_s(" ENCODING_NAME ")"
                    {
                        /**
                         * Cf. https://fossies.org/linux/libiconv/man/iconv_open.3.html
                         */

                        char *__fromcode;
                        gsize __bytes_read;
                        gsize __bytes_written;

                        if ($1.type != GVT_BYTES)
                            EXIT_WITH_ERR($$, convert_2_bytes_to_s_encoding);

                        __fromcode = strndup($3.data, $3.len);

                        $$.bytes.data = g_convert($1.bytes.data, $1.bytes.len,
                                                  __fromcode, "", &__bytes_read, &__bytes_written, NULL);

                        free(__fromcode);

                        if (__bytes_read != $1.bytes.len)
                            EXIT_WITH_ERR($$, convert_2_bytes_to_s_encoding);

                        $$.bytes.len = __bytes_written;
                        $$.type = GVT_BYTES;

                    exit_convert_2_bytes_to_s_encoding:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    ;


  convert_2_integer : any_expr ".length"
                    {
                        if ($1.type != GVT_BYTES)
                            EXIT_WITH_ERR($$, convert_2_integer_to_s);

                        $$.unsigned_integer = $1.bytes.len;
                        $$.type = GVT_UNSIGNED_INTEGER;

                    exit_convert_2_integer_to_s:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    | any_expr ".to_i"
                    {
                        char *__n;
                        char *__end;

                        if ($1.type == GVT_FLOAT)
                        {
                            if ($1.floating_number < 0)
                            {
                                $$.signed_integer = $1.floating_number;
                                $$.type = GVT_SIGNED_INTEGER;
                            }
                            else
                            {
                                $$.unsigned_integer = $1.floating_number;
                                $$.type = GVT_UNSIGNED_INTEGER;
                            }

                        }

                        else if ($1.type == GVT_BOOLEAN)
                        {
                            $$.unsigned_integer = $1.status ? 1 : 0;
                            $$.type = GVT_UNSIGNED_INTEGER;
                        }

                        else if ($1.type == GVT_BYTES)
                        {
                            if ($1.bytes.len == 0)
                                EXIT_WITH_ERR($$, convert_2_integer_to_i);

                            __n = malloc($1.bytes.len + 1);
                            memcpy(__n, $1.bytes.data, $1.bytes.len);
                            __n[$1.bytes.len] = '\0';

                            if ($1.bytes.data[0] == '-')
                            {
                                if ($1.bytes.len == 1)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i);

                                $$.signed_integer = strtoll(__n, &__end, 10);
                                $$.type = GVT_SIGNED_INTEGER;

                                if (errno == EINVAL || errno == ERANGE)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i);

                                if (__end != &__n[$1.bytes.len])
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i);

                            }
                            else
                            {
                                if ($1.bytes.len == 1)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i);

                                $$.unsigned_integer = strtoull(__n, &__end, 10);
                                $$.type = GVT_UNSIGNED_INTEGER;

                                if (errno == EINVAL || errno == ERANGE)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i);

                                if (__end != &__n[$1.bytes.len])
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i);

                            }

                            free(__n);

                        }

                        else EXIT_WITH_ERR($$, convert_2_integer_to_i);

                    exit_convert_2_integer_to_i:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    | any_expr ".to_i(" any_expr ")"
                    {
                        int __base;
                        char *__n;
                        char *__end;

                        if ($1.type == GVT_BYTES)
                        {
                            if ($1.bytes.len == 0)
                                EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                            if ($3.type == GVT_UNSIGNED_INTEGER)
                            {
                                __base = $3.unsigned_integer;
                                if (__base < 2)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);
                            }
                            else if ($3.type == GVT_SIGNED_INTEGER)
                            {
                                __base = $3.signed_integer;
                                if (__base < 2)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);
                            }
                            else EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                            __n = malloc($1.bytes.len + 1);
                            memcpy(__n, $1.bytes.data, $1.bytes.len);
                            __n[$1.bytes.len] = '\0';

                            if ($1.bytes.data[0] == '-')
                            {
                                if ($1.bytes.len == 1)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                                $$.signed_integer = strtoll(__n, &__end, __base);
                                $$.type = GVT_SIGNED_INTEGER;

                                if (errno == EINVAL || errno == ERANGE)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                                if (__end != &__n[$1.bytes.len])
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                            }
                            else
                            {
                                if ($1.bytes.len == 1)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                                $$.unsigned_integer = strtoull(__n, &__end, __base);
                                $$.type = GVT_UNSIGNED_INTEGER;

                                if (errno == EINVAL || errno == ERANGE)
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                                if (__end != &__n[$1.bytes.len])
                                    EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                            }

                            free(__n);

                        }

                        else EXIT_WITH_ERR($$, convert_2_integer_to_i_base);

                    exit_convert_2_integer_to_i_base:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    | any_expr ".size"
                    {
                        GRecordList *__list;

                        if ($1.type != GVT_RECORD) EXIT_WITH_ERR($$, convert_2_integer_size);
                        if (!G_IS_RECORD_LIST($1.record)) EXIT_WITH_ERR($$, convert_2_integer_size);

                        __list = G_RECORD_LIST($1.record);

                        $$.unsigned_integer = g_record_list_count_records(__list);
                        $$.type = GVT_UNSIGNED_INTEGER;

                    exit_convert_2_integer_size:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    ;


/* Types de base */

            boolean : "true"
                    {
                        $$.status = true;
                        $$.type = GVT_BOOLEAN;
                    }
                    | "false"
                    {
                        $$.status = false;
                        $$.type = GVT_BOOLEAN;
                    }
                    ;


            integer : UNSIGNED_INTEGER
                    {
                        $$.unsigned_integer = $1;
                        $$.type = GVT_UNSIGNED_INTEGER;
                    }
                    | SIGNED_INTEGER
                    {
                        $$.signed_integer = $1;
                        $$.type = GVT_SIGNED_INTEGER;
                    }
                    ;


              float : FLOAT
                    {
                        $$.floating_number = $1;
                        $$.type = GVT_FLOAT;
                    }
                    ;


              bytes : bytes_concat { $$ = $1; }
                    | PLAIN_BYTES
                    {
                        $$.bytes.len = $1.len;
                        $$.bytes.data = malloc($1.len);
                        memcpy($$.bytes.data, $1.data, $1.len);
                        $$.type = GVT_BYTES;
                    }
                    | any_expr ".reverse"
                    {
                        size_t __i;

                        CHECK_TYPE($1, GVT_BYTES, $$, bytes_reverse);

                        $$.bytes.data = malloc($1.bytes.len);
                        $$.bytes.len = $1.bytes.len;

                        for (__i = 0; __i < $1.bytes.len; __i++)
                            $$.bytes.data[__i] = $1.bytes.data[$1.bytes.len - __i - 1];

                        $$.type = GVT_BYTES;

                    exit_bytes_reverse:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    | any_expr ".substring" "(" any_expr "," any_expr ")"
                    {
                        unsigned long long __from;
                        unsigned long long __to;

                        REDUCE_NUMERIC_EXPR($4, $$, bytes_reverse);
                        CHECK_TYPES($4, GVT_UNSIGNED_INTEGER, GVT_SIGNED_INTEGER, $$, bytes_substring);
                        REDUCE_NUMERIC_EXPR($6, $$, bytes_reverse);
                        CHECK_TYPES($6, GVT_UNSIGNED_INTEGER, GVT_SIGNED_INTEGER, $$, bytes_substring);

                        __from = ($4.type == GVT_UNSIGNED_INTEGER ? $4.unsigned_integer : $4.signed_integer);
                        __to = ($6.type == GVT_UNSIGNED_INTEGER ? $6.unsigned_integer : $6.signed_integer);

                        if (__from > __to) EXIT_WITH_ERR($$, bytes_substring);
                        if (__to >= $1.bytes.len) EXIT_WITH_ERR($$, bytes_substring);

                        $$.bytes.len = __to - __from + 1;
                        $$.bytes.data = malloc($$.bytes.len);

                        memcpy($$.bytes.data, &$1.bytes.data[__from], $$.bytes.len);

                        $$.type = GVT_BYTES;

                    exit_bytes_substring:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($4);
                        EXIT_RESOLVED_VALUE($6);
                    }
                    ;

       bytes_concat : raw_bytes { $$ = $1; };
                    | bytes_concat raw_bytes
                    {
                        $$.bytes.len = $1.bytes.len + $2.bytes.len;
                        $$.bytes.data = malloc($$.bytes.len);
                        memcpy($$.bytes.data, $1.bytes.data, $1.bytes.len);
                        memcpy($$.bytes.data + $1.bytes.len, $2.bytes.data, $2.bytes.len);
                        $$.type = GVT_BYTES;
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($2);
                    }
                    ;

          raw_bytes : RAW_BYTES
                    {
                        $$.bytes.len = $1.len;
                        $$.bytes.data = malloc($1.len);
                        memcpy($$.bytes.data, $1.data, $1.len);
                        $$.type = GVT_BYTES;
                    }
                    | RAW_BYTE
                    {
                        $$.bytes.len = 1;
                        $$.bytes.data = malloc(1);
                        $$.bytes.data[0] = $1;
                        $$.type = GVT_BYTES;
                    }
                    | RAW_BYTES_WITH_ENDING_DOT
                    {
                        $$.bytes.len = $1.len;
                        $$.bytes.data = malloc($1.len);
                        memcpy($$.bytes.data, $1.data, $1.len);
                        $$.type = GVT_BYTES;
                    }
                    ;


/* Tableau d'éléments variés */

              array : "[" "]"
                    {
                        $$.array = g_kaitai_array_new();
                        $$.type = GVT_ARRAY;
                    }
                    | "[" array_items "]"
                    {
                        $$ = $2;
                    }
                    ;


        array_items : any_expr
                    {
                        $$.array = g_kaitai_array_new();
                        $$.type = GVT_ARRAY;

                        g_kaitai_array_append_item($$.array, &$1);

                        EXIT_RESOLVED_VALUE($1);

                    }
                    | array_items "," any_expr
                    {
                        $$ = $1;
                        g_kaitai_array_append_item($$.array, &$3);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    ;


/* Accès aux objets Kaitai manipulés */

              field : IDENTIFIER
                    {
                        $$.record = g_match_record_find_by_name(locals->parent,
                                                                $1.data, $1.len,
                                                                DIRECT_SEARCH_DEEP_LEVEL);

                        if ($$.record != NULL)
                            $$.type = GVT_RECORD;

                        /* Si aucune correspondance, le contenu brut est utilisé */
                        else
                        {
                            $$.bytes.len = $1.len;
                            $$.bytes.data = malloc($1.len);
                            memcpy($$.bytes.data, $1.data, $1.len);
                            $$.type = GVT_BYTES;
                        }

                    }
                    | "_root"
                    {
                        $$.record = get_root_record(locals);
                        if ($$.record == NULL) SET_ERR($$);
                        else $$.type = GVT_RECORD;
                    }
                    | "_parent"
                    {
                        $$.record = get_parent_record(locals);
                        if ($$.record == NULL) SET_ERR($$);
                        else $$.type = GVT_RECORD;
                    }
                    | "_"
                    {
                        $$.record = get_last_record(locals);
                        if ($$.record == NULL) SET_ERR($$);
                        else $$.type = GVT_RECORD;
                    }
                    | any_expr "." IDENTIFIER
                    {
                        if ($1.type != GVT_RECORD)
                            EXIT_WITH_ERR($$, field_dot);

                        $$.record = g_match_record_find_by_name($1.record,
                                                                $3.data, $3.len,
                                                                DIRECT_SEARCH_DEEP_LEVEL);

                        if ($$.record == NULL)
                            EXIT_WITH_ERR($$, field_dot);

                        $$.type = GVT_RECORD;

                    exit_field_dot:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    | any_expr "[" any_expr "]"
                    {
                        size_t __index;
                        GRecordList *__list;
                        size_t __count;
                        GKaitaiArray *__array;

                        /* Indice de l'élément auquel accéder */

                        REDUCE_NUMERIC_EXPR($3, $$, field_indexed);

                        if ($3.type == GVT_UNSIGNED_INTEGER)
                            __index = $3.unsigned_integer;
                        else
                            EXIT_WITH_ERR($$, field_indexed);

                        /* Série à consulter */

                        REDUCE_EXPR($1, $$, field_indexed);

                        if ($1.type == GVT_RECORD && G_IS_RECORD_LIST($1.record))
                        {
                            __list = G_RECORD_LIST($1.record);
                            __count = g_record_list_count_records(__list);

                            if (__index >= __count)
                                EXIT_WITH_ERR($$, field_indexed);

                            $$.record = g_record_list_get_record(__list, __index);

                            if ($$.record == NULL)
                                EXIT_WITH_ERR($$, field_indexed);

                            $$.type = GVT_RECORD;

                        }

                        else if ($1.type == GVT_ARRAY)
                        {
                            __array = G_KAITAI_ARRAY($1.array);
                            __count = g_kaitai_array_count_items(__array);

                            if (__index >= __count)
                                EXIT_WITH_ERR($$, field_indexed);

                            if (!g_kaitai_array_get_item(__array, __index, &$$))
                                EXIT_WITH_ERR($$, field_indexed);

                        }

                        else
                            EXIT_WITH_ERR($$, field_indexed);

                    exit_field_indexed:
                        EXIT_RESOLVED_VALUE($1);
                        EXIT_RESOLVED_VALUE($3);
                    }
                    ;


        enumeration : IDENTIFIER "::" IDENTIFIER
                    {
                        if (!g_match_record_resolve_enum(locals->parent, &$1, &$3, &$$))
                            SET_ERR($$);
                    }


             stream : any_expr "._io"
                    {
                        GBinContent *__content;
                        mrange_t __range;

                        if ($1.type != GVT_RECORD)
                            EXIT_WITH_ERR($$, stream_io);

                        __content = g_match_record_get_content($1.record);
                        g_match_record_get_range($1.record, &__range);

                        $$.stream = g_kaitai_stream_new(__content, get_mrange_addr(&__range));
                        $$.type = GVT_STREAM;

                        g_object_unref(G_OBJECT(__content));

                    exit_stream_io:
                        EXIT_RESOLVED_VALUE($1);
                    }
                    ;


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : yyscanner = décodeur impliqué dans le processus.             *
*                locals    = variables locales pour les résolutions de types. *
*                out       = valeur entière résultante. [OUT]                 *
*                msg       = message d'erreur.                                *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(yyscan_t yyscanner, const kaitai_scope_t *locals, resolved_value_t *resolved, const char *msg)
{
	printf("YYERROR line %d: %s\n", yyget_lineno(yyscanner), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                text   = définitions des règles à charger.                   *
*                length = longueur de ces définitions.                        *
*                out    = valeur générique résultante. [OUT]                  *
*                                                                             *
*  Description : Interprète une expression en une valeur quelconque.          *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _resolve_kaitai_expression_as_any(const kaitai_scope_t *locals, const char *text, size_t length, resolved_value_t *out)
{
    bool result;                            /* Bilan à renvoyer            */
    yyscan_t lexstate;                      /* Gestion d'analyse lexicale  */
    char *real_text;                        /* Zone de travail effective   */
    size_t real_length;                     /* Taille associée             */
    YY_BUFFER_STATE state;                  /* Contexte d'analyse          */
    int status;                             /* Bilan d'une analyse         */

    result = false;

    kaitai_lex_init(&lexstate);

    assert(length > 0);

    if (text[length - 1] == '.')
    {
        /**
         * Si le contenu à analyser se termine par un point, la position finale
         * de ce point est prise en compte. Pour ce faire, le marqueur "$" des
         * expressions régulières est sollicité. Hors, ce dernier n'est reconnu
         * que pour le caractère "\n" terminant une ligne.
         *
         * On l'ajoute donc artificiellement.
         */

        real_length = length + 1;

        real_text = malloc(real_length);
        memcpy(real_text, text, length);
        real_text[length] = '\n';

    }
    else
    {
        real_text = (char *)text;
        real_length = length;
    }

    state = kaitai__scan_bytes(real_text, real_length, lexstate);

    if (text[length - 1] == '.')
        free(real_text);

    status = yyparse(lexstate, locals, out);

    result = (status == EXIT_SUCCESS);

    yy_delete_buffer(state, lexstate);

    kaitai_lex_destroy(lexstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                text   = définitions des règles à charger.                   *
*                length = longueur de ces définitions.                        *
*                out    = valeur générique résultante. [OUT]                  *
*                                                                             *
*  Description : Interprète une expression en une valeur quelconque.          *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool resolve_kaitai_expression_as_any(const kaitai_scope_t *locals, const char *text, size_t length, resolved_value_t *out)
{
    bool result;                            /* Bilan à renvoyer            */

    result = _resolve_kaitai_expression_as_any(locals, text, length, out);

    return result;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : in_out = expression résolue traitée. [OUT]                   *
*                                                                             *
*  Description : Traduit les éventuels champs impliqués dans une expression.  *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool reduce_resolved_kaitai_expression(resolved_value_t *in_out)
{
    bool result;                            /* Bilan à renvoyer            */
    resolved_value_t deeper;                /* Précision supplémentaire    */

    result = true;

    while (result && in_out->type == GVT_RECORD)
    {
        if (G_IS_RECORD_VALUE(in_out->record))
            result = g_record_value_compute_value(G_RECORD_VALUE(in_out->record), &deeper);

        else if (G_IS_RECORD_ITEM(in_out->record))
            result = g_record_item_get_value(G_RECORD_ITEM(in_out->record), &deeper);

        else
            break;

        if (result)
        {
            EXIT_RESOLVED_VALUE(*in_out);
            *in_out = deeper;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                text   = définitions des règles à charger.                   *
*                length = longueur de ces définitions.                        *
*                out    = valeur entière résultante. [OUT]                    *
*                                                                             *
*  Description : Interprète une expression en valeur ciblée entière.          *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool resolve_kaitai_expression_as_integer(const kaitai_scope_t *locals, const char *text, size_t length, resolved_value_t *out)
{
    bool result;                            /* Bilan à renvoyer            */

    result = _resolve_kaitai_expression_as_any(locals, text, length, out);

    if (result)
        result = reduce_resolved_kaitai_expression(out);

    if (result)
        result = (out->type == GVT_UNSIGNED_INTEGER || out->type == GVT_SIGNED_INTEGER);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                text   = définitions des règles à charger.                   *
*                length = longueur de ces définitions.                        *
*                out    = valeur booléenne résultante. [OUT]                  *
*                                                                             *
*  Description : Interprète une expression en valeur ciblée booléenne.        *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool resolve_kaitai_expression_as_boolean(const kaitai_scope_t *locals, const char *text, size_t length, resolved_value_t *out)
{
    bool result;                            /* Bilan à renvoyer            */

    result = _resolve_kaitai_expression_as_any(locals, text, length, out);

    if (result)
        result = reduce_resolved_kaitai_expression(out);

    if (result && out->type != GVT_BOOLEAN)
    {
        EXIT_RESOLVED_VALUE(*out);
        result = false;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                text   = définitions des règles à charger.                   *
*                length = longueur de ces définitions.                        *
*                out    = valeur booléenne résultante. [OUT]                  *
*                                                                             *
*  Description : Interprète une expression en série d'octets.                 *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool resolve_kaitai_expression_as_bytes(const kaitai_scope_t *locals, const char *text, size_t length, resolved_value_t *out)
{
    bool result;                            /* Bilan à renvoyer            */
    char ch;                                /* Caractère unique spécifié   */
    sized_string_t converted;               /* Conversion finale ?         */

    result = _resolve_kaitai_expression_as_any(locals, text, length, out);

    if (result)
        result = reduce_resolved_kaitai_expression(out);

    if (result)
    {
        if (out->type == GVT_UNSIGNED_INTEGER)
        {
            ch = out->unsigned_integer;
            result = (ch <= 0xff);

            if (result)
            {
                EXIT_RESOLVED_VALUE(*out);

                out->bytes.data = malloc(sizeof(char));
                out->bytes.data[0] = ch;
                out->bytes.len = 1;
                out->type = GVT_BYTES;

            }

        }

        else if (out->type == GVT_ARRAY)
        {
            result = g_kaitai_array_convert_to_bytes(out->array, &converted);

            if (result)
            {
                EXIT_RESOLVED_VALUE(*out);

                out->bytes = converted;
                out->type = GVT_BYTES;

            }

        }

    }

    if (result && out->type != GVT_BYTES)
    {
        EXIT_RESOLVED_VALUE(*out);
        result = false;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                text   = définitions des règles à charger.                   *
*                length = longueur de ces définitions.                        *
*                stream = flux de données pour Kaitai résultant. [OUT]        *
*                                                                             *
*  Description : Interprète une expression en flux de données pour Kaitai.    *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool resolve_kaitai_expression_as_stream(const kaitai_scope_t *locals, const char *text, size_t length, GKaitaiStream **stream)
{
    bool result;                            /* Bilan à renvoyer            */
    resolved_value_t out;                   /* Elément générique obtenu    */

    result = _resolve_kaitai_expression_as_any(locals, text, length, &out);

    if (result) 
    {
        assert(out.type == GVT_STREAM);
        *stream = out.stream;
    }
    else
        *stream = NULL;

    return result;

}
