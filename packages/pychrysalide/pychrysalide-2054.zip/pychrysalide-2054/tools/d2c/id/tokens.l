
%top {

#include <stdlib.h>

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option noyy_top_state


%%


" "             { }

[0-9_]*         { yylvalp->value = strtoul(yytext, NULL, 10); return VALUE; }

.               {
                    char *msg;
                    int ret;
                    ret = asprintf(&msg, "Unhandled token in d2c id block: '%s'", yytext);
                    if (ret == -1)
                        YY_FATAL_ERROR("Unhandled token in undisclosed d2c id block");
                    else
                    {
                        YY_FATAL_ERROR(msg);
                        free(msg);
                    }
                }


%%
