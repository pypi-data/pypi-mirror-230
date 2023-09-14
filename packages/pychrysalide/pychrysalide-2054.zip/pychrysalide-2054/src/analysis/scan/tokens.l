
%top {

#include "grammar.h"

}


%{

//#include "manual.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>





/******************************************************************************
*                                                                             *
*  Paramètres  : src = liste d'octets à traiter.                              *
*                len = taille de cette liste.                                 *
*                out = série d'octets bruts obtenue. [OUT]                    *
*                                                                             *
*  Description : Transcrit une série d'octets en en remplaçant certains.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void rost_unescape_string_bytes(const char *src, size_t len, sized_string_t *out)
{
    size_t i;                               /* Boucle de parcours          */
    bin_t byte;                             /* Octet à analyser            */
    bin_t next;                             /* Octet suivant               */

    out->len = 0;

    for (i = 0; i < len; i++)
    {
        byte = src[i];

        switch (byte)
        {
            case '\\':

                next = src[i + 1];

                switch (next)
                {
                    case 'a':
                        out->data[out->len++] = '\a';
                        break;

                    case 'b':
                        out->data[out->len++] = '\b';
                        break;

                    case 't':
                        out->data[out->len++] = '\t';
                        break;

                    case 'n':
                        out->data[out->len++] = '\n';
                        break;

                    case 'v':
                        out->data[out->len++] = '\v';
                        break;

                    case 'f':
                        out->data[out->len++] = '\f';
                        break;

                    case 'r':
                        out->data[out->len++] = '\r';
                        break;

                    case 'e':
                        out->data[out->len++] = '\e';
                        break;

                    case '"':
                        out->data[out->len++] = '\"';
                        break;

                    case '\\':
                        out->data[out->len++] = '\\';
                        break;

                    case 'x':

                        next = src[i + 2];

                        switch (next)
                        {
                            case '0' ... '9':
                                out->data[out->len] = (next - '0');
                                break;

                            case 'A' ... 'F':
                                out->data[out->len] = 0xa + (next - 'A');
                                break;

                            case 'a' ... 'f':
                                out->data[out->len] = 0xa + (next - 'a');
                                break;

                        }

                        out->data[out->len] <<= 4;

                        next = src[i + 3];

                        switch (next)
                        {
                            case '0' ... '9':
                                out->data[out->len] |= (next - '0');
                                break;

                            case 'A' ... 'F':
                                out->data[out->len] |= 0xa + (next - 'A');
                                break;

                            case 'a' ... 'f':
                                out->data[out->len] |= 0xa + (next - 'a');
                                break;

                        }

                        out->len++;

                        i += 2;
                        break;

                }

                i++;
                break;

            default:
                out->data[out->len++] = byte;
                break;

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : src = liste d'octets à traiter.                              *
*                len = taille de cette liste.                                 *
*                out = série d'octets bruts obtenue. [OUT]                    *
*                                                                             *
*  Description : Transcrit une série d'octets en en remplaçant certains.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void rost_unescape_bytes(const char *src, size_t len, sized_string_t *out)
{
    size_t i;                               /* Boucle de parcours          */
    bin_t byte;                             /* Octet à analyser            */
    bin_t next;                             /* Octet suivant               */

    out->len = 0;

    for (i = 0; i < len; i++)
    {
        byte = src[i];

        switch (byte)
        {
            case '\\':

                next = src[i + 1];

                switch (next)
                {
                    case 'a':
                        out->data[out->len++] = '\a';
                        break;

                    case 'b':
                        out->data[out->len++] = '\b';
                        break;

                    case 't':
                        out->data[out->len++] = '\t';
                        break;

                    case 'n':
                        out->data[out->len++] = '\n';
                        break;

                    case 'v':
                        out->data[out->len++] = '\v';
                        break;

                    case 'f':
                        out->data[out->len++] = '\f';
                        break;

                    case 'r':
                        out->data[out->len++] = '\r';
                        break;

                    case 'e':
                        out->data[out->len++] = '\e';
                        break;

                    case '"':
                        out->data[out->len++] = '\"';
                        break;

                    case '\\':
                        out->data[out->len++] = '\\';
                        break;

                    case 'x':

                        next = src[i + 2];

                        switch (next)
                        {
                            case '0' ... '9':
                                out->data[out->len] = (next - '0');
                                break;

                            case 'A' ... 'F':
                                out->data[out->len] = 0xa + (next - 'A');
                                break;

                            case 'a' ... 'f':
                                out->data[out->len] = 0xa + (next - 'a');
                                break;

                        }

                        out->data[out->len] <<= 4;

                        next = src[i + 3];

                        switch (next)
                        {
                            case '0' ... '9':
                                out->data[out->len] |= (next - '0');
                                break;

                            case 'A' ... 'F':
                                out->data[out->len] |= 0xa + (next - 'A');
                                break;

                            case 'a' ... 'f':
                                out->data[out->len] |= 0xa + (next - 'a');
                                break;

                        }

                        out->len++;

                        i += 2;
                        break;

                    case '{':
                        out->data[out->len++] = '{';
                        break;

                    case '}':
                        out->data[out->len++] = '}';
                        break;

                }

                i++;
                break;

            default:
                out->data[out->len++] = byte;
                break;

        }

    }

}



#define PUSH_STATE(s) yy_push_state(s, yyscanner)
#define POP_STATE     yy_pop_state(yyscanner)



#define EXTEND_BUFFER_IF_NEEDED(extra)      \
    if ((*used + extra) > *allocated)       \
    {                                       \
        *allocated *= 2;                    \
        *buf = realloc(*buf, *allocated);   \
    }


%}


%option bison-bridge reentrant
%option stack
%option nounput
%option noinput
%option noyywrap
%option noyy_top_state
%option yylineno
%option never-interactive

%x inc_path

%x rule_intro
%x raw_block

%x meta
%x meta_value

%x bytes
%x bytes_value
%x bytes_value_raw

%x bytes_hex
%x bytes_hex_range

%x bytes_regex
%x bytes_regex_quantifier
%x bytes_regex_range

%x condition
%x strlit

%x wait_for_colon


%x comment


str_not_escaped [^\"\\]
str_escaped \\a|\\b|\\t|\\n|\\v|\\f|\\r|\\e|\\\"|\\\\|\\x{hbyte}
str_mixed ({str_not_escaped}|{str_escaped})

hbyte [0-9a-fA-F]{2}
mbyte (\?[0-9a-fA-F]|[0-9a-fA-F]\?)

reg_allowed [^^$.|/{}()\[\]*+?\\]
reg_allowed_escaped \\^|\\$|\\\.|\\\||\\\/|\\\{|\\\}|\\\(|\\\)|\\\[|\\\]|\\\*|\\\+|\\\?|\\\\
reg_escaped \\a|\\t|\\n|\\v|\\f|\\r
reg_byte \\x[0-9a-fA-F]{2}

regular_chars {reg_allowed}|{reg_allowed_escaped}|{reg_escaped}|{reg_byte}

reg_classes \\w|\\W|\\s|\\S|\\d|\\D|\\b|\\B


bytes_id [A-Za-z_][A-Za-z0-9_]*
bytes_fuzzy_id [\*A-Za-z_][\*A-Za-z0-9_]*


%%


"include"                           { PUSH_STATE(inc_path); return INCLUDE; }

<inc_path>\"{str_not_escaped}+\"    {
                                        POP_STATE;

                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 2;

                                        return PLAIN_TEXT;
                                    }

<inc_path>\"{str_mixed}+\"          {
                                        POP_STATE;

                                        rost_unescape_string_bytes(yytext + 1, yyleng - 2, tmp_0);

#ifndef NDEBUG
                                        /* Pour rendre plus lisibles les impressions de débogage */
                                        tmp_0->data[tmp_0->len] = '\0';
#endif

                                        yylval->tmp_cstring = tmp_0;

                                        return ESCAPED_TEXT;
                                    }


%{ /* Définition locale d'une règle */ %}

                             "rule" {
                                        PUSH_STATE(rule_intro);
                                        return RAW_RULE;
                                    }

          <rule_intro>[A-Za-z0-9_]+ {
                                        yylval->sized_cstring.data = yytext;
                                        yylval->sized_cstring.len = yyleng;
                                        return RULE_NAME;
                                    }

                 <rule_intro>[ \t]* { }

                    <rule_intro>"{" {
                                        POP_STATE;
                                        PUSH_STATE(raw_block);
                                        return BRACE_IN;
                                    }

                  <raw_block>"meta" {
                                        POP_STATE;
                                        PUSH_STATE(meta);
                                        PUSH_STATE(wait_for_colon);
                                        return META;
                                    }

            <raw_block,meta>"bytes" {
                                        POP_STATE;
                                        PUSH_STATE(bytes);
                                        PUSH_STATE(wait_for_colon);
                                        return BYTES;
                                    }

  <raw_block,meta,bytes>"condition" {
                                        POP_STATE;
                                        PUSH_STATE(condition);
                                        PUSH_STATE(wait_for_colon);
                                        return CONDITION;
                                    }

                <wait_for_colon>":" {
                                        POP_STATE;
                                        return COLON;
                                    }

<raw_block,meta,bytes,condition>"}" {
                                        POP_STATE;
                                        return BRACE_OUT;
                                    }


%{ /* Définitions communes pour la section "meta:" */ %}

                   <meta>{bytes_id} {
                                        yylval->sized_cstring.data = yytext;
                                        yylval->sized_cstring.len = yyleng;
                                        return INFO_KEY;
                                    }

                          <meta>"=" { PUSH_STATE(meta_value); return ASSIGN; }

                 <meta_value>"true" { POP_STATE; return TRUE_; }
                <meta_value>"false" { POP_STATE; return FALSE_; }

       <meta_value>-(0|[1-9][0-9]*) {
                                        POP_STATE;
                                        yylval->signed_integer = strtoll(yytext, NULL, 10);
                                        return SIGNED_INTEGER;
                                    }

           <meta_value>-0x[0-9a-f]+ {
                                        POP_STATE;
                                        yylval->signed_integer = strtoll(yytext, NULL, 16);
                                        return SIGNED_INTEGER;
                                    }

        <meta_value>(0|[1-9][0-9]*) {
                                        POP_STATE;
                                        yylval->unsigned_integer = strtoull(yytext, NULL, 10);
                                        return UNSIGNED_INTEGER;
                                    }

            <meta_value>0x[0-9a-f]+ {
                                        POP_STATE;
                                        yylval->unsigned_integer = strtoull(yytext, NULL, 16);
                                        return UNSIGNED_INTEGER;
                                    }

 <meta_value>\"{str_not_escaped}+\" {
                                        POP_STATE;

                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 2;

                                        return PLAIN_TEXT;
                                    }

       <meta_value>\"{str_mixed}+\" {
                                        POP_STATE;

                                        rost_unescape_string_bytes(yytext + 1, yyleng - 2, tmp_0);

#ifndef NDEBUG
                                        /* Pour rendre plus lisibles les impressions de débogage */
                                        tmp_0->data[tmp_0->len] = '\0';
#endif

                                        yylval->tmp_cstring = tmp_0;

                                        return ESCAPED_TEXT;
                                    }


%{ /* A déplacer... */ %}


<condition>"true"               { return TRUE_; }
<condition>"false"              { return FALSE_; }

<condition>-(0|[1-9][0-9]*)     { yylval->signed_integer = strtoll(yytext, NULL, 10); return SIGNED_INTEGER; }
<condition>-0x[0-9a-f]+         { yylval->signed_integer = strtoll(yytext, NULL, 16); return SIGNED_INTEGER; }

<bytes_hex_range,bytes_regex_quantifier,condition>(0|[1-9][0-9]*)      { yylval->unsigned_integer = strtoull(yytext, NULL, 10); return UNSIGNED_INTEGER; }
<bytes_hex_range,bytes_regex_quantifier,condition>0x[0-9a-f]+          { yylval->unsigned_integer = strtoull(yytext, NULL, 16); return UNSIGNED_INTEGER; }

<condition>[kK][bB]             { return KB; }
<condition>[mM][bB]             { return MB; }
<condition>[gG][bB]             { return GB; }

<condition>"\""                 {
                                    *used = 0;
                                    PUSH_STATE(strlit);
                                }

<strlit>"\""                    {
                                    POP_STATE; 
                                    yylval->sized_cstring.data = *buf;
                                    yylval->sized_cstring.len = *used;
                                    return STRING;
                                }

<strlit>"\\\""                  { EXTEND_BUFFER_IF_NEEDED(1); (*buf)[(*used)++] = '"'; }
<strlit>"\\t"                   { EXTEND_BUFFER_IF_NEEDED(1); (*buf)[(*used)++] = '\t'; }
<strlit>"\\r"                   { EXTEND_BUFFER_IF_NEEDED(1); (*buf)[(*used)++] = '\r'; }
<strlit>"\\n"                   { EXTEND_BUFFER_IF_NEEDED(1); (*buf)[(*used)++] = '\n'; }
<strlit>"\\\\"                  { EXTEND_BUFFER_IF_NEEDED(1); (*buf)[(*used)++] = '\\'; }

<strlit>\\x[0-9a-fA-F]{2}       {
                                    char __ch;
                                    __ch = strtol(yytext + 2, NULL, 16);
                                    EXTEND_BUFFER_IF_NEEDED(1);
                                    (*buf)[(*used)++] = __ch;
                                }

<strlit>[^\\\"]+                {
                                    size_t __len;
                                    __len = strlen(yytext);
                                    EXTEND_BUFFER_IF_NEEDED(__len);
                                    strcpy(&(*buf)[*used], yytext);
                                    *used += __len;
                                }


%{ /* Définitions communes pour la section "bytes:" */ %}

  <bytes>"fullword"                 { return FULLWORD; }
  <bytes>"nocase"                   { return NOCASE; }
  <bytes>"private"                  { return PRIVATE; }

  <bytes>"="                        { PUSH_STATE(bytes_value); return ASSIGN; }


%{ /* Définition de motif en texte brut */ %}

<bytes_value>\"{str_not_escaped}+\" {
                                        POP_STATE;

                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 2;

                                        return PLAIN_TEXT;
                                    }

<bytes_value>\"{str_mixed}+\"       {
                                        POP_STATE;

                                        rost_unescape_string_bytes(yytext + 1, yyleng - 2, tmp_0);

#ifndef NDEBUG
                                        /* Pour rendre plus lisibles les impressions de débogage */
                                        tmp_0->data[tmp_0->len] = '\0';
#endif

                                        yylval->tmp_cstring = tmp_0;

                                        return ESCAPED_TEXT;
                                    }


%{ /* Définition de motif en hexadécimal */ %}

                   <bytes_value>"{" {
                                        POP_STATE;
                                        PUSH_STATE(bytes_hex);
                                    }

                     <bytes_hex>"}" { POP_STATE; }

                     <bytes_hex>"[" {
                                        PUSH_STATE(bytes_hex_range);
                                        return HOOK_O;
                                    }

               <bytes_hex_range>"-" { return MINUS; }

               <bytes_hex_range>"]" {
                                        POP_STATE;
                                        return HOOK_C;
                                    }

                     <bytes_hex>"(" { return PAREN_O; }

                     <bytes_hex>")" { return PAREN_C; }

                     <bytes_hex>"|" { return PIPE; }

                     <bytes_hex>"~" { return TILDE; }

   <bytes_hex>{hbyte}([ ]*{hbyte})* {
                                        bool even;
                                        size_t i;
                                        bin_t byte;
                                        bin_t value;

                                        tmp_0->len = 0;

                                        even = true;

                                        for (i = 0; i < yyleng; i++)
                                        {
                                            byte = yytext[i];

                                            switch (byte)
                                            {
                                                case ' ':
                                                    continue;
                                                    break;

                                                case '0' ... '9':
                                                    value = (byte - '0');
                                                    break;

                                                case 'A' ... 'F':
                                                    value = 0xa + (byte - 'A');
                                                    break;

                                                case 'a' ... 'f':
                                                    value = 0xa + (byte - 'a');
                                                    break;

                                            }

                                            if (even)
                                                tmp_0->data[tmp_0->len] = (value << 4);
                                            else
                                                tmp_0->data[tmp_0->len++] |= value;

                                            even = !even;

                                        }

                                        assert(even);

#ifndef NDEBUG
                                        /* Pour rendre plus lisibles les impressions de débogage */
                                        tmp_0->data[tmp_0->len] = '\0';
#endif

                                        yylval->tmp_cstring = tmp_0;
                                        return HEX_BYTES;

                                    }

   <bytes_hex>[\?]{2}([ ]*[\?]{2})* {
                                        unsigned long long counter;
                                        size_t i;

                                        counter = 0;

                                        for (i = 0; i < yyleng; i++)
                                            if (yytext[i] == '?')
                                                counter++;

                                        assert(counter % 2 == 0);

                                        yylval->unsigned_integer = counter / 2;
                                        return FULL_MASK;

                                    }

   <bytes_hex>{mbyte}([ ]*{mbyte})* {
                                        bool even;
                                        size_t i;
                                        bin_t byte;
                                        bin_t value;

                                        tmp_0->len = 0;
                                        tmp_1->len = 0;

                                        even = true;

                                        for (i = 0; i < yyleng; i++)
                                        {
                                            byte = yytext[i];

                                            switch (byte)
                                            {
                                                case ' ':
                                                    continue;
                                                    break;

                                                case '?':
                                                    even = !even;
                                                    continue;
                                                    break;

                                                case '0' ... '9':
                                                    value = (byte - '0');
                                                    break;

                                                case 'A' ... 'F':
                                                    value = 0xa + (byte - 'A');
                                                    break;

                                                case 'a' ... 'f':
                                                    value = 0xa + (byte - 'a');
                                                    break;

                                            }

                                            if (even)
                                            {
                                                tmp_0->data[tmp_0->len++] = (value << 4);
                                                tmp_1->data[tmp_1->len++] = 0xf0;
                                            }
                                            else
                                            {
                                                tmp_0->data[tmp_0->len++] = value;
                                                tmp_1->data[tmp_1->len++] = 0x0f;
                                            }

                                            even = !even;

                                        }

#ifndef NDEBUG
                                        /* Pour rendre plus lisibles les impressions de débogage */
                                        tmp_0->data[tmp_0->len] = '\0';
                                        tmp_1->data[tmp_1->len] = '\0';
#endif

                                        yylval->masked.tmp_values = tmp_0;
                                        yylval->masked.tmp_masks = tmp_1;
                                        return SEMI_MASK;

                                    }


%{ /* Définition d'expressions régulières */ %}

                   <bytes_value>"/" {
                                        POP_STATE;
                                        printf(" -- regex\n");
                                        PUSH_STATE(bytes_regex);
                                    }

                   <bytes_regex>"/" { printf("exit regex\n"); POP_STATE; }

                   <bytes_regex>"." { return DOT; }

    <bytes_regex>({regular_chars})+ {
                                        rost_unescape_bytes(yytext, yyleng, tmp_0);

                                        printf(" regular: '%s'\n", yytext);

#ifndef NDEBUG
                                        /* Pour rendre plus lisibles les impressions de débogage */
                                        tmp_0->data[tmp_0->len] = '\0';
#endif

                                        yylval->tmp_cstring = tmp_0;
                                        return REGEX_BYTES;

                                    }

      <bytes_regex>({reg_classes})+ {

                                        return REGEX_CLASSES;

                                    }

%{ /* <bytes_regex>\[({regular_chars}|({regular_chars})-z|{reg_classes})+\] { */ %}


                   <bytes_regex>"[" {
                                        PUSH_STATE(bytes_regex_range);
                                        printf(" !! entering range\n");
                                        return HOOK_O;
                                    }

             <bytes_regex_range>"]" {
                                        POP_STATE;
                                        printf(" !! exiting range\n");
                                        return HOOK_C;
                                    }




<bytes_regex_range>({regular_chars}|({regular_chars}-{regular_chars})|{reg_classes})+ {

       printf("range: '%s'\n", yytext);
                                        return REGEX_RANGE;

                                    }

                   <bytes_regex>"(" { return PAREN_O; }

                   <bytes_regex>")" { return PAREN_C; }

                   <bytes_regex>"|" { return PIPE; }

                   <bytes_regex>"*" { return MUL; }
                   <bytes_regex>"+" { return PLUS; }
                   <bytes_regex>"?" { return QUESTION; }

                   <bytes_regex>"{" {
                                        PUSH_STATE(bytes_regex_quantifier);
                                        return BRACKET_O;
                                    }

        <bytes_regex_quantifier>"," { return COMMA; }

        <bytes_regex_quantifier>"}" {
                                        POP_STATE;
                                        return BRACKET_C;
                                    }


%{ /* Condition de correspondance */ %}

<condition>"and"                { return AND; }
<condition>"or"                 { return OR; }
<condition>"not"                { return NOT; }

<condition>"<"                  { return LT; }
<condition>"<="                 { return LE; }
<condition>"=="                 { return EQ; }
<condition>"!="                 { return NE; }
<condition>">"                  { return GT; }
<condition>">="                 { return GE; }

<condition>"contains"           { return CONTAINS; }
<condition>"startswith"         { return STARTSWITH; }
<condition>"endswith"           { return ENDSWITH; }
<condition>"matches"            { return MATCHES; }
<condition>"icontains"          { return ICONTAINS; }
<condition>"istartswith"        { return ISTARTSWITH; }
<condition>"iendswith"          { return IENDSWITH; }
<condition>"iequals"            { return IEQUALS; }

<condition>"+"                  { return PLUS; }
<condition>"-"                  { return MINUS; }
<condition>"*"                  { return MUL; }
<condition>"/"                  { return DIV; }
<condition>"%"                  { return MOD; }

<bytes,condition>"("            { return PAREN_O; }
<bytes,condition>")"            { return PAREN_C; }
<bytes,condition>","            { return COMMA; }


<condition>"["                  { return HOOK_O; }
<condition>"]"                  { return HOOK_C; }


<condition>"."                  { return DOT; }
<bytes>"|"                      { return PIPE; }

<condition>"none"               { return NONE; }
<condition>"any"                { return ANY; }
<condition>"all"                { return ALL; }
<condition>"of"                 { return OF; }
<condition>"them"               { return THEM; }
<condition>"in"                 { return IN; }


       <bytes,condition>${bytes_id} {
                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 1;
                                        return BYTES_ID;
                                    }

      <condition>${bytes_fuzzy_id}  {
                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 1;
                                        return BYTES_FUZZY_ID;
                                    }

             <condition>#{bytes_id} {
                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 1;
                                        return BYTES_ID_COUNTER;
                                    }

             <condition>@{bytes_id} {
                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 1;
                                        return BYTES_ID_START;
                                    }

             <condition>!{bytes_id} {
                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 1;
                                        return BYTES_ID_LENGTH;
                                    }

             <condition>~{bytes_id} {
                                        yylval->sized_cstring.data = yytext + 1;
                                        yylval->sized_cstring.len = yyleng - 1;
                                        return BYTES_ID_END;
                                    }






<bytes,condition>[A-Za-z_][A-Za-z0-9_]* {
                                    yylval->sized_cstring.data = yytext;
                                    yylval->sized_cstring.len = yyleng;
                                    return NAME;
                                }




<bytes_value>"\""                    {
                                    POP_STATE;
                                    // *built_pattern = g_bytes_pattern_new();
                                    PUSH_STATE(bytes_value_raw);
                                }

<bytes_value_raw>"\""                { POP_STATE; /*yylval->pattern = *built_pattern*/; return 11111/*MASKED_STRING*/; }

<bytes_value_raw>"\\\""              { }//g_bytes_pattern_append_data(*built_pattern, '"', 0xff); }
<bytes_value_raw>"\\t"               { }//g_bytes_pattern_append_data(*built_pattern, '\t', 0xff); }
<bytes_value_raw>"\\r"               { }//g_bytes_pattern_append_data(*built_pattern, '\r', 0xff); }
<bytes_value_raw>"\\n"               { }//g_bytes_pattern_append_data(*built_pattern, '\n', 0xff); }
<bytes_value_raw>"\\\\"              { }//g_bytes_pattern_append_data(*built_pattern, '\\', 0xff); }

<bytes_value_raw>\\x[0-9a-fA-F]{2} {
                                    uint8_t __ch;
                                    __ch = strtol(yytext + 2, NULL, 16);
                                    printf("__ch: %hhx\n", __ch);
                                    //g_bytes_pattern_append_data(*built_pattern, __ch, 0xff);
                                }

<bytes_value_raw>.                   { }//g_bytes_pattern_append_data(*built_pattern, *yytext, 0xff); }






%{ /* Commentaires */ %}

<*>"/*"                         { PUSH_STATE(comment); }
<comment>"*/"                   { POP_STATE; }
<comment>(.|\n)                 { }

<*>"//"[^\n]*                   { }


%{ /* Actions par défaut */ %}

<*>[ \t]+                     { }

<*>[\n]                     { static int ln = 1; if (0) printf("----------- %%< -------------- %%< ---- %d\n", ln++); }

<*>.                            {
                                    char *msg;
                                    int ret;
                                    ret = asprintf(&msg, "Unhandled token in rule definition: '%s'", yytext);
                                    if (ret == -1)
                                        YY_FATAL_ERROR("Unhandled token in undisclosed rule definition");
                                    else
                                    {
                                        YY_FATAL_ERROR(msg);
                                        free(msg);
                                    }
 }


%%
