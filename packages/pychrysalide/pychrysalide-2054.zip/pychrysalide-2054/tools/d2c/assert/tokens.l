
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option stack
%option noyy_top_state
%option noyy_push_state
%option noyy_pop_state


%%


[ \t\n]                 { }

"=="                    { return EQ; }
"!="                    { return NE; }

"&&"                    { return AND; }
"||"                    { return OR; }

[A-Za-z_][A-Za-z0-9_]*  { yylvalp->string = strdup(yytext); return FIELD; }

[01x]+                  { yylvalp->string = strdup(yytext); return VALUE; }

.                       {
                            char *msg;
                            int ret;
                            ret = asprintf(&msg, "Unhandled token in d2c assert block: '%s'", yytext);
                            if (ret == -1)
                                YY_FATAL_ERROR("Unhandled token in undisclosed d2c assert block");
                            else
                            {
                                YY_FATAL_ERROR(msg);
                                free(msg);
                            }
                        }

%%
