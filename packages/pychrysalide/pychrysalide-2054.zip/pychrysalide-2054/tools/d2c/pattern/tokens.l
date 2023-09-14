
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


[ \t]  { }

[^ ]+  { yylvalp->string = strdup(yytext); return OPERAND; }

.      {
           char *msg;
           int ret;
           ret = asprintf(&msg, "Unhandled token in d2c pattern block: '%s'", yytext);
           if (ret == -1)
               YY_FATAL_ERROR("Unhandled token in undisclosed d2c pattern block");
           else
           {
               YY_FATAL_ERROR(msg);
               free(msg);
           }
       }


%%
