
%top {

#include "grammar.h"

}


%option noyywrap
%option nounput
%option noinput
%option yylineno
%option stack
%option noyy_top_state

%x cond
%x cond_binval
%x cond_hexval
%x action
%x raw_line


%%


\/\/[^\n]+          { }

"if"                            { yy_push_state(cond); return IF; }
<cond>[ ]+                      { }
<cond>"("                       { return EXPR_START; }
<cond>[A-Za-z_][A-Za-z0-9_]*    { yylvalp->string = strdup(yytext); return NAME; }
<cond>"=="                      { return EQUAL; }
<cond>"'"                       { yy_push_state(cond_binval); }
<cond_binval>[01][01]*          { yylvalp->string = strdup(yytext); return BINVAL; }
<cond_binval>"'"                { yy_pop_state(); }
<cond>"0x"                      { yy_push_state(cond_hexval); }
<cond_hexval>[0-9a-f][0-9a-f]*  { yylvalp->string = strdup(yytext); yy_pop_state(); return HEXVAL; }
<cond>")"                       { return EXPR_END; }
<cond>"&&"                      { return AND; }
<cond>"&"                       { return AND_LOG; }

<cond>";"           { yy_pop_state(); return THEN; }

[ \t\n]             { }

"see "              { yy_push_state(raw_line); return SEE; }

"unpredictable"     { return UNPREDICTABLE; }

"call"              { yy_push_state(raw_line); return CALL; }
"check"             { yy_push_state(raw_line); return CHK_CALL; }

<raw_line>[^\n]+    { yylvalp->cstring = yytext; return RAW_LINE; }
<raw_line>"\n"      { yy_pop_state(); }

.                   {
                        char *msg;
                        int ret;
                        ret = asprintf(&msg, "Unhandled token in d2c rules block: '%s'", yytext);
                        if (ret == -1)
                            YY_FATAL_ERROR("Unhandled token in undisclosed d2c rules block");
                        else
                        {
                            YY_FATAL_ERROR(msg);
                            free(msg);
                        }
                    }


%%
