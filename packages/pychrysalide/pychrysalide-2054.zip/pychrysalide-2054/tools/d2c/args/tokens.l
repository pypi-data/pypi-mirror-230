
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option stack
%option noyy_top_state

%x binval
%x hexval


%%


%{

    /* Choix d'un des démarrages multiples */
    if (*init_token != ALLOW_ALL)
    {
        unsigned int first;
        first = *init_token;
        *init_token = ALLOW_ALL;
        return first;
    }

%}


[A-Za-z_][A-Za-z0-9_]*      {
                                if (strcmp(yytext, "NOT") == 0) return NOT;
                                else if (strcmp(yytext, "AND") == 0) return AND_LOG;
                                else if (strcmp(yytext, "EOR") == 0) return EOR;
                                else
                                {
                                    yylvalp->string = strdup(yytext);
                                    return NAME;
                                }
                            }

[0-9][0-9]*                 { yylvalp->integer = atoi(yytext); return NUMBER; }

"'"                         { yy_push_state(binval); }
<binval>[01][01]*           { yylvalp->string = strdup(yytext); return BINVAL; }
<binval>"'"                 { yy_pop_state(); }

\"[^\"]*\"                  { yylvalp->string = strndup(yytext + 1, strlen(yytext) - 2); return STRING; }

"0x"                        { yy_push_state(hexval); }
<hexval>[0-9a-f][0-9a-f]*   { yylvalp->string = strdup(yytext); yy_pop_state(); return HEXVAL; }

","                         { return COMMA; }
":"                         { return COLON; }
"&"                         { return AND_LOG; }
"<<"                        { return LSHIFT; }
"=="                        { return EQ; }
"!="                        { return NE; }

"&&"                        { return AND_BOOL; }
"||"                        { return OR_BOOL; }

"("                         { yy_push_state(INITIAL); return OP; }
")"                         { yy_pop_state(); return CP; }

[ ]+                        { }

.                           {
                                char *msg;
                                int ret;
                                ret = asprintf(&msg, "Unhandled token in d2c args block: '%s'", yytext);
                                if (ret == -1)
                                    YY_FATAL_ERROR("Unhandled token in undisclosed d2c args block");
                                else
                                {
                                    YY_FATAL_ERROR(msg);
                                    free(msg);
                                }
                            }


%%
