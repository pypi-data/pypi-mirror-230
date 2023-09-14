
%top {

#include "grammar.h"

}


%{

#include "manual.h"

%}


%option noyywrap
%option yylineno
%option stack
%option noyy_top_state


%x comments

%x ins_name try_details ins_details
%x encoding encoding_type encoding_content syntax_content

%x encoding_bits encoding_bits_size

%x top_brace
%x raw_line raw_block


%%


[ \t\n]+                        { }

"/*"                            { BEGIN(comments); }
<comments>"*/"                  { BEGIN(INITIAL); }
<comments>[^*\n]                { }
<comments>"Copyright"[^\n]*     { yylvalp->string = strdup(yytext); return COPYRIGHT; }
<comments>"*"                   { }
<comments>"\n"                  { }


"@title"                        { BEGIN(ins_name); return TITLE; }

<ins_name>[ ][A-Za-z0-9-]+      { yylvalp->string = strdup(yytext + 1); BEGIN(try_details); return INS_NAME; }
<try_details>[ ,/-]             { BEGIN(ins_details); yylvalp->character = yytext[0]; return INS_SEP; }
<try_details>[\n]               { BEGIN(INITIAL); }

<ins_details>[^\n]*             { yylvalp->cstring = yytext; return INS_DETAILS; }
<ins_details>[\n]               { BEGIN(INITIAL); }

"@id"                           { yy_push_state(raw_line); return ID; }

"@desc"                         { yy_push_state(raw_block); return DESC; }


"@encoding"                     { yy_push_state(encoding); return ENCODING; }

<encoding>[ ]                   { }
<encoding>"("                   { yy_push_state(encoding_type); }

<encoding_type>[A-Za-z]         { yylvalp->string = strdup(yytext); return TYPE; }
<encoding_type>[0-9]+           { yylvalp->integer = atoi(yytext); return NUMBER; }
<encoding_type>")"              { yy_pop_state(); }

<encoding>"{"                   { yy_push_state(encoding_content); }

<encoding_content>[ \t\n]+      { }
<encoding_content>"}"           { yy_pop_state(); yy_pop_state(); }


<encoding_content>"@format"     { yy_push_state(raw_line); return FORMAT; }
<encoding_content>"@unused"     { yy_push_state(raw_line); return UNUSED; }

<encoding_content>"@half"       { yy_push_state(raw_line); return HALF; }
<encoding_content>"@word"       { yy_push_state(raw_line); return WORD; }

<encoding_content>"@syntax"     { yy_push_state(syntax_content); yy_push_state(top_brace); return SYNTAX; }

<encoding_content>"@hooks"      { yy_push_state(raw_block); return HOOKS; }


<syntax_content>[ \t\n]+        { }

<syntax_content>"@subid"        { yy_push_state(raw_line); return SUBID; }

<syntax_content>"@assert"       { yy_push_state(raw_block); return ASSERT; }

<syntax_content>"@conv"         { yy_push_state(raw_block); return CONV; }

<syntax_content>"@asm"          { yy_push_state(raw_line); return ASM; }

<syntax_content>"@rules"        { yy_push_state(raw_block); return RULES; }

<syntax_content>"}"             { yy_pop_state(); }


<top_brace>[ \t\n]+             { }
<top_brace>"{"                  { yy_pop_state(); }

<raw_line>[^\n]+                { yylvalp->cstring = yytext; return RAW_LINE; }
<raw_line>"\n"                  { yy_pop_state(); }

<raw_block>[ \t\n]+             { }
<raw_block>"{"                  {
                                    read_block(temp);
                                    yylvalp->cstring = temp; return RAW_BLOCK;
                                }
<raw_block>"}"                  { yy_pop_state(); }


<encoding_content>"{"           {
                                    read_block(temp);
                                    yylvalp->cstring = temp; return RAW_BLOCK;
                                }

<*>.                            {
                                    char *msg;
                                    int ret;
                                    ret = asprintf(&msg, "Unhandled token in d2c definition: '%s'", yytext);
                                    if (ret == -1)
                                        YY_FATAL_ERROR("Unhandled token in undisclosed d2c definition");
                                    else
                                    {
                                        YY_FATAL_ERROR(msg);
                                        free(msg);
                                    }
 }


%%
