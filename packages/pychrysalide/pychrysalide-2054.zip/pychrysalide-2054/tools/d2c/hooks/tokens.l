
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option noyy_top_state


%%


[ \t\n]                 { }

[a-z_][a-z0-9_]*        { yylvalp->string = strdup(yytext); return NAME; }
"="                     { return EQ; }

.                       {
                            char *msg;
                            int ret;
                            ret = asprintf(&msg, "Unhandled token in d2c hooks block: '%s'", yytext);
                            if (ret == -1)
                                YY_FATAL_ERROR("Unhandled token in undisclosed d2c hooks block");
                            else
                            {
                                YY_FATAL_ERROR(msg);
                                free(msg);
                            }
                        }


%%
