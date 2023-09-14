
%top {

#include <assert.h>
#include <malloc.h>
#include <string.h>

#include <common/extstr.h>

#include "grammar.h"

}


%{

#define PUSH_STATE(s) yy_push_state(s, yyscanner)
#define POP_STATE     yy_pop_state(yyscanner)

%}


%option bison-bridge reentrant
%option stack
%option nounput
 //%option noinput
%option noyywrap
%option noyy_top_state
%option yylineno
%option never-interactive


%x encoding
%x escaped_str
%x plain_str


%%


%{

    /* no init C code */

%}


"+"                                     { return PLUS; }
"-"                                     { return MINUS; }
"*"                                     { return MUL; }
"/"                                     { return DIV; }
"%"                                     { return MOD; }

"<"                                     { return LT; }
"<="                                    { return LE; }
"=="                                    { return EQ; }
"!="                                    { return NE; }
">"                                     { return GT; }
">="                                    { return GE; }

"<<"                                    { return SHIFT_LEFT; }
">>"                                    { return SHIFT_RIGHT; }
"&"                                     { return BIT_AND; }
"|"                                     { return BIT_OR; }
"^"                                     { return BIT_XOR; }

"not"                                   { return NOT; }
"and"                                   { return AND; }
"or"                                    { return OR; }

"("                                     { return PAREN_O; }
")"                                     { return PAREN_C; }
"["                                     { return HOOK_O; }
"]"                                     { return HOOK_C; }
","                                     { return COMMA; }
"."                                     { return DOT; }

"?"                                     { return QMARK; }
":"                                     { return COLON; }
"::"                                    { return DOUBLE_COLON; }

".size"                                 { return METH_SIZE; }
".length"                               { return METH_LENGTH; }
".reverse"                              { return METH_REVERSE; }
".substring"                            { return METH_SUBSTRING; }
".to_i"                                 { return METH_TO_I; }
".to_i("                                { return METH_TO_I_RAD; }
".to_s"                                 { return METH_TO_S; }
".to_s("                                { PUSH_STATE(encoding); return METH_TO_S_ENC; }

"_root"                                 { return ROOT; }
"_parent"                               { return PARENT; }
"_"                                     { return LAST; }
"._io"                                  { return METH_IO; }

"true"                                  { return TRUE_CONST; }
"false"                                 { return FALSE_CONST; }


%{ /* Lecteurs de valeurs entières */ %}

0[bB][01]+                              {
                                            char *__end;
                                            yylval->unsigned_integer = strtoull(yytext + 2, &__end, 2);
                                            if (__end != (yytext + yyleng))
                                                YY_FATAL_ERROR("failed to parse integer");
                                            return UNSIGNED_INTEGER;
                                        }

0[bB][01]{1,4}(_[01]{4})+               {
                                            char *__tmp;
                                            char *__end;
                                            __tmp = strdup(yytext);
                                            __tmp = strrpl(__tmp, "_", "");
                                            yylval->unsigned_integer = strtoull(__tmp + 2, &__end, 2);
                                            if (__end != (__tmp + strlen(__tmp)))
                                            {
                                                free(__tmp);
                                                YY_FATAL_ERROR("failed to parse integer");
                                            }
                                            else free(__tmp);
                                            return UNSIGNED_INTEGER;
                                        }

(0|[1-9][0-9]*)                         {
                                            char *__end;
                                            yylval->unsigned_integer = strtoull(yytext, &__end, 10);
                                            if (__end != (yytext + yyleng))
                                                YY_FATAL_ERROR("failed to parse integer");
                                            return UNSIGNED_INTEGER;
                                        }

[1-9][0-9]{0,2}(_[1-9][0-9]{2})+        {
                                            char *__tmp;
                                            char *__end;
                                            __tmp = strdup(yytext);
                                            __tmp = strrpl(__tmp, "_", "");
                                            yylval->unsigned_integer = strtoull(__tmp, &__end, 10);
                                            if (__end != (__tmp + strlen(__tmp)))
                                            {
                                                free(__tmp);
                                                YY_FATAL_ERROR("failed to parse integer");
                                            }
                                            else free(__tmp);
                                            return UNSIGNED_INTEGER;
                                        }

-(0|[1-9][0-9]*)                        {
                                            char *__end;
                                            yylval->signed_integer = strtoll(yytext, &__end, 10);
                                            if (__end != (yytext + yyleng))
                                                YY_FATAL_ERROR("failed to parse integer");
                                            return SIGNED_INTEGER;
                                        }

-[1-9][0-9]{0,2}(_[1-9][0-9]{2})+       {
                                            char *__tmp;
                                            char *__end;
                                            __tmp = strdup(yytext);
                                            __tmp = strrpl(__tmp, "_", "");
                                            yylval->signed_integer = strtoll(__tmp, &__end, 10);
                                            if (__end != (__tmp + strlen(__tmp)))
                                            {
                                                free(__tmp);
                                                YY_FATAL_ERROR("failed to parse integer");
                                            }
                                            else free(__tmp);
                                            return SIGNED_INTEGER;
                                        }

0[xX][0-9a-fA-F]+                       {
                                            char *__end;
                                            yylval->unsigned_integer = strtoull(yytext, &__end, 16);
                                            if (__end != (yytext + yyleng))
                                                YY_FATAL_ERROR("failed to parse integer");
                                            return UNSIGNED_INTEGER;
                                        }

0[xX][0-9a-fA-F]{1,4}(_[0-9a-fA-F]{4})+ {
                                            char *__tmp;
                                            char *__end;
                                            __tmp = strdup(yytext);
                                            __tmp = strrpl(__tmp, "_", "");
                                            yylval->unsigned_integer = strtoull(__tmp, &__end, 16);
                                            if (__end != (__tmp + strlen(__tmp)))
                                            {
                                                free(__tmp);
                                                YY_FATAL_ERROR("failed to parse integer");
                                            }
                                            else free(__tmp);
                                            return UNSIGNED_INTEGER;
                                        }



-?(0|[1-9][0-9]*\.[0-9]+)               {
                                            char *__end;
                                            yylval->floating_number = strtod(yytext, &__end);
                                            if (__end != (yytext + yyleng))
                                                YY_FATAL_ERROR("failed to parse float");
                                            return FLOAT;
                                        }


%{ /* Paramètre d'encodage */ %}

<encoding>["'][-_A-Za-z0-9 ]+["']       {
                                            yylval->sized_cstring.data = yytext + 1;
                                            yylval->sized_cstring.len = yyleng - 2;
                                            return ENCODING_NAME;
                                        }

<encoding>")"                           { POP_STATE; return PAREN_C; }


[a-z][a-z0-9_]*                         {
                                            yylval->sized_cstring.data = yytext;
                                            yylval->sized_cstring.len = yyleng;
                                            return IDENTIFIER;
                                        }

[^\\\[\],"'()\.: ]+                     {
                                            yylval->sized_cstring.data = yytext;
                                            yylval->sized_cstring.len = yyleng;
                                            return PLAIN_BYTES;
                                        }


%{ /* Lecteurs des tableaux de définition d'octets */ %}

"\""                                    { PUSH_STATE(escaped_str); }


<escaped_str>[^\\"]+                    {
                                            yylval->sized_cstring.data = yytext;
                                            yylval->sized_cstring.len = yyleng;
                                            return RAW_BYTES;
                                        }

<escaped_str>"\\a"                      { yylval->byte = '\a'; return RAW_BYTE; }
<escaped_str>"\\b"                      { yylval->byte = '\b'; return RAW_BYTE; }
<escaped_str>"\\t"                      { yylval->byte = '\t'; return RAW_BYTE; }
<escaped_str>"\\n"                      { yylval->byte = '\n'; return RAW_BYTE; }
<escaped_str>"\\v"                      { yylval->byte = '\v'; return RAW_BYTE; }
<escaped_str>"\\f"                      { yylval->byte = '\f'; return RAW_BYTE; }
<escaped_str>"\\r"                      { yylval->byte = '\r'; return RAW_BYTE; }
<escaped_str>"\\e"                      { yylval->byte = '\e'; return RAW_BYTE; }
<escaped_str>"\\\""                     { yylval->byte = '"';  return RAW_BYTE; }
<escaped_str>"\\'"                      { yylval->byte = '\''; return RAW_BYTE; }
<escaped_str>"\\\\"                     { yylval->byte = '\\'; return RAW_BYTE; }
<escaped_str>"\\0"                      { yylval->byte = '\0'; return RAW_BYTE; }

<escaped_str>\\[0-9]{1,3}               {
                                            char __tmp[4];
                                            memcpy(__tmp, yytext + 1, yyleng - 1);
                                            __tmp[yyleng] = '\0';
                                            yylval->byte = strtoull(__tmp, NULL, 8);
                                            return RAW_BYTE;
                                        }

<escaped_str>"\""                       { POP_STATE; }




"'"                                     { PUSH_STATE(plain_str); }

<plain_str>[^']+                        {
                                            yylval->sized_cstring.data = yytext;
                                            yylval->sized_cstring.len = yyleng;
                                            return PLAIN_BYTES;
                                        }

<plain_str>[']                          { POP_STATE; }

[.]$                                    {
#ifndef NDEBUG
                                            int ch;
#endif
                                            yylval->sized_cstring.data = yytext;
                                            yylval->sized_cstring.len = yyleng;
#ifndef NDEBUG
                                            ch = input(yyscanner);
                                            assert(ch == '\n');
#else
                                            input(yyscanner);
#endif
                                            return RAW_BYTES_WITH_ENDING_DOT;
                                        }

[^\\\[\],"'()\.: ]+[.]$                 {
#ifndef NDEBUG
                                            int ch;
#endif
                                            yylval->sized_cstring.data = yytext;
                                            yylval->sized_cstring.len = yyleng;
#ifndef NDEBUG
                                            ch = input(yyscanner);
                                            assert(ch == '\n');
#else
                                            input(yyscanner);
#endif
                                            return RAW_BYTES_WITH_ENDING_DOT;
                                        }


%{ /* Actions par défaut */ %}

<*>[ \t\n]+                             { }

<*>.                                    {
                                            char *msg;
                                            int ret;
                                            ret = asprintf(&msg,
                                                           "Unhandled token in rule definition: '%s'",
                                                           yytext);
                                            if (ret == -1)
                                                YY_FATAL_ERROR("Unhandled token in undisclosed rule definition");
                                            else
                                            {
                                                YY_FATAL_ERROR(msg);
                                                free(msg);
                                            }
                                        }


%%
