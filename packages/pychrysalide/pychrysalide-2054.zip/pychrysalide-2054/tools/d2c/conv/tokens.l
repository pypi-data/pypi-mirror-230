
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option stack
%option noyy_top_state

%x raw_line


%%


[ \t\n]+                { }

[A-Za-z_][A-Za-z0-9_]*  { yylvalp->string = strdup(yytext); return NAME; }

"="                     { yy_push_state(raw_line); return EQ; }

<raw_line>[^\n]+        { yylvalp->cstring = yytext; return RAW_LINE; }
<raw_line>"\n"          { yy_pop_state(); }

.                       {
                            char *msg;
                            int ret;
                            ret = asprintf(&msg, "Unhandled token in d2c conv block: '%s'", yytext);
                            if (ret == -1)
                                YY_FATAL_ERROR("Unhandled token in undisclosed d2c conv block");
                            else
                            {
                                YY_FATAL_ERROR(msg);
                                free(msg);
                            }
                        }


%%
