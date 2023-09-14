
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option stack
%option noyy_top_state

%x bsize


%%


" "                     { }

[A-Za-z_][A-Za-z0-9_]*  { yylvalp->string = strdup(yytext); return NAME; }

"("                     { yy_push_state(bsize); }
<bsize>[0-9]+           { yylvalp->integer = atoi(yytext); return SIZE; }
<bsize>")"              { yy_pop_state(); }

[01]                    { yylvalp->integer = atoi(yytext); return BIT; }

.                       {
                            char *msg;
                            int ret;
                            ret = asprintf(&msg, "Unhandled token in d2c bits block: '%s'", yytext);
                            if (ret == -1)
                                YY_FATAL_ERROR("Unhandled token in undisclosed d2c bits block");
                            else
                            {
                                YY_FATAL_ERROR(msg);
                                free(msg);
                            }
                        }

%%
