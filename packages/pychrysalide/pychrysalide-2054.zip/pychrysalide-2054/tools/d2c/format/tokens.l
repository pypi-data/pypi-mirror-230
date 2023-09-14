
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option noyy_top_state


%%


" "             { }

[A-Za-z0-9_]*   { yylvalp->string = strdup(yytext); return OPS_TYPE; }
"|"             { return OR; }

.               {
                    char *msg;
                    int ret;
                    ret = asprintf(&msg, "Unhandled token in d2c format block: '%s'", yytext);
                    if (ret == -1)
                        YY_FATAL_ERROR("Unhandled token in undisclosed d2c format block");
                    else
                    {
                        YY_FATAL_ERROR(msg);
                        free(msg);
                    }
                }


%%
