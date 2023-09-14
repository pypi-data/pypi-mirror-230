
%{

#include "decl.h"
#include "tokens.h"


/* Affiche un message d'erreur suite à l'analyse en échec. */
static int yyerror(GContentScanner *, yyscan_t, GScanRule **, sized_string_t *, sized_string_t *, void/*GBytesPattern*/ **, char **, size_t *, size_t *, char *);

#define raise_error(msg) \
    yyerror(scanner, yyscanner, built_rule, tmp_0, tmp_1, NULL, buf, allocated, used, msg)

%}


%code requires {

#define YY_TYPEDEF_YY_SCANNER_T
typedef void *yyscan_t;

#include <assert.h>
#include <malloc.h>
#include <stdio.h>

#include <i18n.h>

#include "core.h"
#include "scanner.h"
#include "exprs/access.h"
#include "exprs/arithmetic.h"
#include "exprs/call.h"
#include "exprs/counter.h"
#include "exprs/handler.h"
#include "exprs/intersect.h"
#include "exprs/item.h"
#include "exprs/literal.h"
#include "exprs/logical.h"
#include "exprs/set.h"
#include "exprs/setcounter.h"
#include "exprs/relational.h"
#include "exprs/strop.h"
#include "patterns/modifier.h"
#include "patterns/modifiers/list.h"
#include "patterns/tokens/hex.h"
#include "patterns/tokens/plain.h"
#include "patterns/tokens/nodes/any.h"
#include "patterns/tokens/nodes/choice.h"
#include "patterns/tokens/nodes/masked.h"
#include "patterns/tokens/nodes/not.h"
#include "patterns/tokens/nodes/plain.h"
#include "patterns/tokens/nodes/sequence.h"
#include "../../core/logs.h"

}

%union {

    unsigned long long unsigned_integer;    /* Valeur entière #1           */
    signed long long signed_integer;        /* Valeur entière #2           */
    //double floating_number;                 /* Valeur à virgule flottante  */
    sized_string_t sized_cstring;           /* Chaîne de caractères        */
    //char byte;                              /* Octet unique                */




    sized_string_t *tmp_cstring;            /* Série d'octets reconstituée */

    struct
    {
        sized_string_t *tmp_values;         /* Série d'octets partiels     */
        sized_string_t *tmp_masks;          /* Masques associés            */
    } masked;


    GScanRule *rule;                        /* Nouvelle règle à intégrer   */



    GScanTokenNode *node;                   /* Bribe de motif à intégrer   */
    GSearchPattern *pattern;                /* Nouveau motif à considérer  */

    GScanTokenModifier *modifier;           /* Modificateur pour texte     */
    ScanPlainNodeFlags str_flags;           /* Fanions pour texte          */


    GScanExpression *expr;                  /* Expression de condition     */

    struct {
        GScanExpression **args;             /* Liste d'arguments à fournir */
        size_t count;                       /* Quantité de ces arguments   */
    } args_list;

}


/**
 * Cf.
 * http://stackoverflow.com/questions/34418381/how-to-reference-lex-or-parse-parameters-in-flex-rules/34420950
 */

%define api.pure full

%parse-param { GContentScanner *scanner } { yyscan_t yyscanner } { GScanRule **built_rule } { sized_string_t *tmp_0} { sized_string_t *tmp_1} { void /*GBytesPattern*/ **built_pattern } { char **buf } { size_t *allocated } { size_t *used }
%lex-param { yyscan_t yyscanner } { sized_string_t *tmp_0} { sized_string_t *tmp_1} { void/*GBytesPattern*/ **built_pattern } { char **buf } { size_t *allocated } { size_t *used }

%code provides {

#define YY_DECL \
    int rost_lex(YYSTYPE *yylval_param, yyscan_t yyscanner, sized_string_t *tmp_0, sized_string_t *tmp_1, void/*GBytesPattern*/ **built_pattern, char **buf, size_t *allocated, size_t *used)

YY_DECL;

}


%token INCLUDE          "include"

%token RAW_RULE
%token RULE_NAME

%token META "meta"
%token BYTES "bytes"
%token CONDITION "condition"

%token INFO_KEY



%token BYTES_ID
%token BYTES_FUZZY_ID
%token BYTES_ID_COUNTER
%token BYTES_ID_START
%token BYTES_ID_LENGTH
%token BYTES_ID_END
%token NAME


%token NOCASE "nocase"
%token FULLWORD "fullword"
%token PRIVATE "private"


%token HEX_BYTES
%token FULL_MASK
%token SEMI_MASK


%token REGEX_BYTES
%token REGEX_CLASSES
%token REGEX_RANGE



%token BRACE_IN BRACE_OUT
%token ASSIGN "="
%token COLON ":"


%token PLAIN_TEXT
%token ESCAPED_TEXT

%token TRUE_            "true"
%token FALSE_           "false"
%token SIGNED_INTEGER
%token UNSIGNED_INTEGER
%token STRING

%token KB MB GB

%token AND              "and"
%token OR               "or"
%token NOT              "not"

%token LT               "<"
%token LE               "<="
%token EQ               "=="
%token NE               "!="
%token GT               ">"
%token GE               ">="

%token CONTAINS     "contains"
%token STARTSWITH   "startswith"
%token ENDSWITH     "endswith"
%token MATCHES      "matches"
%token ICONTAINS    "icontains"
%token ISTARTSWITH  "istartswith"
%token IENDSWITH    "iendswith"
%token IEQUALS      "iequals"

%token PLUS             "+"
%token MINUS            "-"
%token MUL              "*"
%token DIV              "/"
%token MOD              "%"
%token TILDE            "~"

%token HOOK_O           "["
%token HOOK_C           "]"

%token BRACKET_O        "{"
%token BRACKET_C        "}"
%token QUESTION         "?"

%token PAREN_O          "("
%token PAREN_C          ")"
%token COMMA            ","
%token DOT              "."
%token PIPE             "|"

%token NONE             "none"
%token ANY              "any"
%token ALL              "all"
%token OF               "of"
%token THEM             "them"
%token IN               "in"


%type <sized_cstring> RULE_NAME

%type <sized_cstring> INFO_KEY

%type <sized_cstring> BYTES_ID
%type <sized_cstring> BYTES_FUZZY_ID
%type <sized_cstring> BYTES_ID_COUNTER
%type <sized_cstring> BYTES_ID_START
%type <sized_cstring> BYTES_ID_LENGTH
%type <sized_cstring> BYTES_ID_END
%type <sized_cstring> NAME


%type <signed_integer> SIGNED_INTEGER
%type <unsigned_integer> UNSIGNED_INTEGER
%type <sized_cstring> STRING

%type <rule> rule

%type <sized_cstring> PLAIN_TEXT
%type <tmp_cstring> ESCAPED_TEXT

%type <tmp_cstring> HEX_BYTES
%type <unsigned_integer> FULL_MASK
%type <masked> SEMI_MASK

%type <tmp_cstring> REGEX_BYTES



%type <pattern> str_pattern

%type <modifier> modifiers
%type <modifier> _modifiers
%type <modifier> chained_modifiers
%type <modifier> mod_stage
%type <modifier> modifier

%type <str_flags> str_flags


%type <pattern> hex_pattern
%type <node> hex_tokens
%type <node> hex_token
%type <node> hex_range
%type <node> hex_choices



%type <expr> cexpression _cexpression

%type <expr> literal
%type <expr> item_chain
%type <args_list> call_args
%type <expr> logical_expr
%type <expr> relational_expr
%type <expr> string_op
%type <expr> arithm_expr
%type <expr> set_match_counter
%type <expr> pattern_set
%type <expr> pattern_set_items
%type <expr> set
%type <expr> set_items
%type <expr> set_access
%type <expr> intersection
%type <expr> pattern_handler





%left PIPE



%left OR
%left AND
%left EQ NE
%left CONTAINS STARTSWITH ENDSWITH MATCHES ICONTAINS ISTARTSWITH IENDSWITH IEQUALS
%left LT LE GT GE
%left PLUS MINUS
%left MUL DIV MOD
%left IN
%right NOT



%left HOOK_O HOOK_C




%destructor { printf("-------- Discarding symbol %p.\n", $$); } <rule>


%%

             rules : /* empty */
                   | external rules
                   | rule rules { g_content_scanner_add_rule(scanner, $1); }
                   ;


/**
 * Inclusion d'une règle externe.
 */

          external : "include" PLAIN_TEXT
                   {
                       bool __status;
                       __status = g_content_scanner_include_resource(scanner, $2.data);
                       if (!__status)
                           YYERROR;
                   }
                   | "include" ESCAPED_TEXT
                   {
                       bool __status;
                       __status = g_content_scanner_include_resource(scanner, $2->data);
                       if (!__status)
                           YYERROR;
                   }
                   ;


/**
 * Définition de règle.
 */

              rule : RAW_RULE RULE_NAME
                   {
                       *built_rule = g_scan_rule_new($2.data);
                       $<rule>$ = *built_rule;
                   }
                   BRACE_IN meta bytes condition BRACE_OUT
                   {
                       $$ = $<rule>3;
                   }
                   ;


/**
 * Section "meta:" d'une définition de règle.
 */

              meta : /* empty */
                   | "meta" ":"
                   | "meta" ":" meta_list
                   ;

         meta_list : meta_info
                   | meta_list meta_info
                   ;

         meta_info : INFO_KEY "=" "true"
                   | INFO_KEY "=" "false"
                   | INFO_KEY "=" SIGNED_INTEGER
                   | INFO_KEY "=" UNSIGNED_INTEGER
                   | INFO_KEY "=" PLAIN_TEXT
                   | INFO_KEY "=" ESCAPED_TEXT
                   ;


/**
 * Section "bytes:" d'une définition de règle.
 */

           bytes : /* empty */
                   | "bytes" ":"
                   | "bytes" ":" bytes_decls
                   ;

       bytes_decls : str_pattern
                   {
                       if ($1 == NULL) YYERROR;
                       g_scan_rule_add_local_variable(*built_rule, $1);
                       g_object_unref(G_OBJECT($1));
                   }
                   | hex_pattern
                   {
                       if ($1 == NULL) YYERROR;
                       g_scan_rule_add_local_variable(*built_rule, $1);
                       g_object_unref(G_OBJECT($1));
                   }
                   | regex_pattern
                   {
                       // TODO
                   }
                   | bytes_decls str_pattern
                   {
                       if ($2 == NULL) YYERROR;
                       g_scan_rule_add_local_variable(*built_rule, $2);
                       g_object_unref(G_OBJECT($2));
                   }
                   | bytes_decls hex_pattern
                   {
                       if ($2 == NULL) YYERROR;
                       g_scan_rule_add_local_variable(*built_rule, $2);
                       g_object_unref(G_OBJECT($2));
                   }
                   | bytes_decls regex_pattern
                   {
                       // TODO
                   }
                   ;


/**
 * Définition de motif en texte brut.
 */

       str_pattern : BYTES_ID ASSIGN PLAIN_TEXT modifiers str_flags
                   {
                       GScanTokenNode *node;

                       node = g_scan_token_node_plain_new(&$3, $4, $5);

                       $$ = g_scan_plain_bytes_new(node);
                       g_search_pattern_set_name($$, $1.data, $1.len);

                       g_object_unref(G_OBJECT(node));

                   }
                   | BYTES_ID ASSIGN ESCAPED_TEXT modifiers str_flags
                   {
                       GScanTokenNode *node;

                       node = g_scan_token_node_plain_new($3, $4, $5);

                       $$ = g_scan_plain_bytes_new(node);
                       g_search_pattern_set_name($$, $1.data, $1.len);

                       g_object_unref(G_OBJECT(node));

                   }
                   ;


/**
 * Prise en charge des modificateurs.
 */

         modifiers : /* empty */
                   {
                       $$ = NULL;
                   }
                   | _modifiers
                   {
                       $$ = $1;

                       // if (...) useless

                   }
                   ;

        _modifiers : mod_stage
                   {
                       $$ = $1;
                   }
                   | chained_modifiers
                   {
                       $$ = $1;
                   }
                   ;

 chained_modifiers : _modifiers "|" _modifiers
                   ;

         mod_stage : modifier
                   {
                       $$ = $1;
                   }
                   | mod_stage modifier
                   {
                       bool status;

                       if (G_IS_SCAN_MODIFIER_LIST($1))
                           $$ = $1;
                       else
                       {
                           $$ = g_scan_modifier_list_new();
                           g_scan_modifier_list_add(G_SCAN_MODIFIER_LIST($$), $1);
                       }

                       status = g_scan_modifier_list_add(G_SCAN_MODIFIER_LIST($$), $2);
                       if (!status)
                       {
                           if (1)
                               log_simple_message(LMT_WARNING, "modifier already taken into account!");
                           g_object_unref(G_OBJECT($2));
                       }

                   }
                   ;

          modifier : NAME
                   {
                       $$ = find_scan_token_modifiers_for_name($1.data);
                       if ($$ == NULL)
                       {
                           char *_msg;
                           int _ret;

                           _ret = asprintf(&_msg, _("Unknown modifier: \"%s\""), $1.data);

                           if (_ret != -1)
                           {
                               raise_error(_msg);
                               free(_msg);
                           }

                           YYERROR;
                       }
                   }
                   | "(" chained_modifiers ")"
                   {
                       $$ = $2;
                   }
                   ;


/**
 * Prise en charge des fanions pour texte.
 */

         str_flags : /* empty */
                   {
                       $$ = SPNF_NONE;
                   }
                   | str_flags "nocase"
                   {
                       $$ = $1 | SPNF_CASE_INSENSITIVE;
                   }
                   | str_flags "fullword"
                   {
                       $$ = $1 | SPNF_FULLWORD;
                   }
                   | str_flags "private"
                   {
                       $$ = $1 | SPNF_PRIVATE;
                   }
                   ;


/**
 * Définition de motif en hexadécimal.
 */

       hex_pattern : BYTES_ID ASSIGN hex_tokens
                   {
                       $$ = g_scan_hex_bytes_new($3, false);
                       g_search_pattern_set_name($$, $1.data, $1.len);
                   }
                   | BYTES_ID ASSIGN hex_tokens "private"
                   {
                       $$ = g_scan_hex_bytes_new($3, true);
                       g_search_pattern_set_name($$, $1.data, $1.len);
                   }
                   ;

        hex_tokens : hex_token
                   {
                       if ($1 == NULL) YYERROR;

                       $$ = $1;

                   }
                   | hex_tokens hex_token
                   {
                       if ($2 == NULL) YYERROR;

                       if (!G_IS_SCAN_TOKEN_NODE_SEQUENCE($1))
                       {
                           $$ = g_scan_token_node_sequence_new($1);
                           g_object_unref(G_OBJECT($1));
                           g_scan_token_node_sequence_add(G_SCAN_TOKEN_NODE_SEQUENCE($$), $2);
                           g_object_unref(G_OBJECT($2));
                       }
                       else
                       {
                           $$ = $1;
                           g_scan_token_node_sequence_add(G_SCAN_TOKEN_NODE_SEQUENCE($$), $2);
                           g_object_unref(G_OBJECT($2));
                       }

                   }
                   ;

         hex_token : HEX_BYTES
                   {
                       $$ = g_scan_token_node_plain_new($1, NULL, SPNF_NONE);
                   }
                   | FULL_MASK
                   {
                       phys_t min;
                       phys_t max;

                       min = $1;
                       max = $1;

                       $$ = g_scan_token_node_any_new(&min, &max);

                   }
                   | SEMI_MASK
                   {
                       size_t i;
                       masked_byte_t byte;

                       assert($1.tmp_values->len == $1.tmp_masks->len);

                       byte.value = $1.tmp_values->data[0];
                       byte.mask = $1.tmp_masks->data[0];

                       $$ = g_scan_token_node_masked_new(&byte);

                       for (i = 1; i < $1.tmp_values->len; i++)
                       {
                           byte.value = $1.tmp_values->data[i];
                           byte.mask = $1.tmp_masks->data[i];

                           g_scan_token_node_masked_add(G_SCAN_TOKEN_NODE_MASKED($$), &byte);

                       }

                   }
                   | hex_range
                   {
                       $$ = $1;
                   }
                   | "~" hex_token
                   {
                       $$ = g_scan_token_node_not_new($2);

                   }
                   | "(" hex_choices ")"
                   {
                       $$ = $2;
                   }
                   ;

         hex_range : "[" "-" "]"
                   {
                       $$ = g_scan_token_node_any_new(NULL, NULL);
                   }
                   | "[" UNSIGNED_INTEGER "]"
                   {
                       phys_t min;
                       phys_t max;

                       min = $2;
                       max = $2;

                       $$ = g_scan_token_node_any_new(&min, &max);

                   }
                   | "[" UNSIGNED_INTEGER "-" "]"
                   {
                       phys_t min;

                       min = $2;

                       $$ = g_scan_token_node_any_new(&min, NULL);

                   }
                   | "[" "-" UNSIGNED_INTEGER "]"
                   {
                       phys_t max;

                       max = $3;

                       $$ = g_scan_token_node_any_new(NULL, &max);

                   }
                   | "[" UNSIGNED_INTEGER "-" UNSIGNED_INTEGER "]"
                   {
                       phys_t min;
                       phys_t max;

                       min = $2;
                       max = $4;

                       $$ = g_scan_token_node_any_new(&min, &max);

                   }
                   ;

       hex_choices : hex_token "|" hex_token
                   {
                       $$ = g_scan_token_node_choice_new();
                       g_scan_token_node_choice_add(G_SCAN_TOKEN_NODE_CHOICE($$), $1);
                       g_object_unref(G_OBJECT($1));
                       g_scan_token_node_choice_add(G_SCAN_TOKEN_NODE_CHOICE($$), $3);
                       g_object_unref(G_OBJECT($3));
                   }
                   | hex_choices "|" hex_token
                   {
                       $$ = $1;
                       g_scan_token_node_choice_add(G_SCAN_TOKEN_NODE_CHOICE($$), $3);
                       g_object_unref(G_OBJECT($3));
                   }
                   ;


/**
 * Définition de motif sous forme d'expression régulière
 */

     regex_pattern : BYTES_ID ASSIGN regex_tokens
                   {

                   }
                   ;

      regex_tokens : regex_token
                   {

                   }
                   | regex_tokens regex_token
                   {

                   }
                   | "(" regex_tokens_list ")"
                   {

                       printf("regex -- OR --\n");

                   }
                   | regex_tokens "(" regex_tokens_list ")"
                   {

                       printf("regex -- OR --\n");

                   }
                   ;


 regex_tokens_list : regex_tokens
                   | regex_tokens_list "|" regex_tokens
                   ;


       regex_token : _regex_token
                   {

                   }
                   | _regex_token regex_repeat
                   {

                   }
                   ;

      _regex_token : DOT
                   {
                       printf("reg dot!\n");
                   }
                   | REGEX_BYTES
                   {
                       printf("reg bytes: '%s' (l=%zu)\n", $1->data, $1->len);
                   }
                   | REGEX_CLASSES
                   {
                       printf("reg class!\n");
                   }
                   | "[" REGEX_RANGE "]"
                   {
                       printf("reg range!\n");
                   }
                   ;

      regex_repeat : "*"
                   {
                       printf("  .. repeat: *\n");
                   }
                   | "+"
                   {
                       printf("  .. repeat: +\n");
                   }
                   | "?"
                   {
                       printf("  .. repeat: ?\n");
                   }
                   | "{" UNSIGNED_INTEGER "}"
                   {

                       printf("  .. repeat {%llu}\n", $2);

                   }
                   | "{" UNSIGNED_INTEGER "," "}"
                   {

                       printf("  .. repeat {%llu,}\n", $2);

                   }
                   | "{" "," UNSIGNED_INTEGER "}"
                   {

                       printf("  .. repeat {,%llu}\n", $3);

                   }
                   | "{" UNSIGNED_INTEGER "," UNSIGNED_INTEGER "}"
                   {

                       printf("  .. repeat {%llu,%llu}\n", $2, $4);

                   }
                   ;



/**
 * Définition des conditions.
 */

      condition : CONDITION COLON cexpression
                {
                    g_scan_rule_set_match_condition(*built_rule, $3);
                    g_object_unref(G_OBJECT($3));
                }
                ;

    cexpression : _cexpression { $$ = $1; if ($$ == NULL) { printf("ERROR !!!\n"); YYERROR; } }

      _cexpression : literal { $$ = $1; }
                   | item_chain { $$ = $1; }
                   | logical_expr { $$ = $1; }
                   | relational_expr { $$ = $1; }
                   | string_op { $$ = $1; }
                   | arithm_expr { $$ = $1; }
                   | set_match_counter { $$ = $1; }
                   | set { $$ = $1; }
                   | set_access { $$ = $1; }
                   | intersection { $$ = $1; }
                   | pattern_handler { $$ = $1; }
                   | "(" cexpression ")" { $$ = $2; }
                   ;

        literal : "true"
                {
                    $$ = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ true });
                }
                | "false"
                {
                    $$ = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ false });
                }
                | SIGNED_INTEGER
                {
                    $$ = g_scan_literal_expression_new(LVT_SIGNED_INTEGER, &$1);
                }
                | UNSIGNED_INTEGER
                {
                    $$ = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, &$1);
                }
                | UNSIGNED_INTEGER KB
                {
                    unsigned long long __converted;
                    __converted = $1 * 1024;
                    $$ = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, &__converted);
                }
                | UNSIGNED_INTEGER MB
                {
                    unsigned long long __converted;
                    __converted = $1 * 1048576;
                    $$ = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, &__converted);
                }
                | UNSIGNED_INTEGER GB
                {
                    unsigned long long __converted;
                    __converted = $1 * 1073741824;
                    $$ = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, &__converted);
                }
                | STRING
                {
                    $$ = g_scan_literal_expression_new(LVT_STRING, &$1);
                }
                ;

     item_chain : NAME { $$ = g_scan_named_access_new(&$1); }
                | NAME "(" ")" { $$ = g_scan_pending_call_new(&$1, NULL, 0); }
                | NAME "(" call_args ")"
                {
                    size_t __i;
                    $$ = g_scan_pending_call_new(&$1, $3.args, $3.count);
                    for (__i = 0; __i < $3.count; __i++)
                        g_object_unref(G_OBJECT($3.args[__i]));
                    free($3.args);
                }
                | item_chain "." NAME
                {
                    GScanExpression *__next;
                    __next = g_scan_named_access_new(&$3);
                    g_scan_named_access_attach_next(G_SCAN_NAMED_ACCESS($1), G_SCAN_NAMED_ACCESS(__next));
                    $$ = $1;
                }
                | item_chain "." NAME "(" ")"
                {
                    GScanExpression *__next;
                    __next = g_scan_pending_call_new(&$3, NULL, 0);
                    g_scan_named_access_attach_next(G_SCAN_NAMED_ACCESS($1), G_SCAN_NAMED_ACCESS(__next));
                    $$ = $1;
                }
                | item_chain "." NAME "(" call_args ")"
                {
                    GScanExpression *__next;
                    size_t __i;
                    __next = g_scan_pending_call_new(&$3, $5.args, $5.count);
                    for (__i = 0; __i < $5.count; __i++)
                        g_object_unref(G_OBJECT($5.args[__i]));
                    free($5.args);
                    g_scan_named_access_attach_next(G_SCAN_NAMED_ACCESS($1), G_SCAN_NAMED_ACCESS(__next));
                    $$ = $1;
                }
                ;

      call_args : cexpression
                {
                    $$.count = 1;
                    $$.args = malloc(sizeof(GScanExpression *));
                    $$.args[0] = $1;
                }
                | call_args "," cexpression
                {
                    $1.count++;
                    $1.args = realloc($1.args, $1.count * sizeof(GScanExpression *));
                    $1.args[$1.count - 1] = $3;
                    $$ = $1;
                }
                ;

   logical_expr : cexpression "and" cexpression { $$ = g_scan_logical_operation_new(BOT_AND, $1, $3); }
                | cexpression "or" cexpression  { $$ = g_scan_logical_operation_new(BOT_OR, $1, $3); }
                | "not" "(" cexpression ")"     { $$ = g_scan_logical_operation_new(BOT_NOT, $3, NULL); }
                ;

relational_expr : cexpression "<" cexpression  { $$ = g_scan_relational_operation_new(RCO_LT, $1, $3); }
                | cexpression "<=" cexpression { $$ = g_scan_relational_operation_new(RCO_LE, $1, $3); }
                | cexpression "==" cexpression { $$ = g_scan_relational_operation_new(RCO_EQ, $1, $3); }
                | cexpression "!=" cexpression { $$ = g_scan_relational_operation_new(RCO_NE, $1, $3); }
                | cexpression ">" cexpression  { $$ = g_scan_relational_operation_new(RCO_GT, $1, $3); }
                | cexpression ">=" cexpression { $$ = g_scan_relational_operation_new(RCO_GE, $1, $3); }
                ;

      string_op : cexpression "contains" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_CONTAINS, $1, $3, true);
                }
                | cexpression "startswith" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_STARTSWITH, $1, $3, true);
                }
                | cexpression "endswith" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_ENDSWITH, $1, $3, true);
                }
                | cexpression "matches" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_MATCHES, $1, $3, true);
                }
                | cexpression "icontains" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_CONTAINS, $1, $3, false);
                }
                | cexpression "istartswith" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_STARTSWITH, $1, $3, false);
                }
                | cexpression "iendswith" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_ENDSWITH, $1, $3, false);
                }
                | cexpression "iequals" cexpression
                {
                    $$ = g_scan_string_operation_new(SOT_IEQUALS, $1, $3, false);
                }
                ;

    arithm_expr : cexpression "+" cexpression { $$ = g_scan_arithmetic_operation_new(AEO_PLUS, $1, $3); }
                | cexpression "-" cexpression { $$ = g_scan_arithmetic_operation_new(AEO_MINUS, $1, $3); }
                | cexpression "*" cexpression { $$ = g_scan_arithmetic_operation_new(AEO_MUL, $1, $3); }
                | cexpression "/" cexpression { $$ = g_scan_arithmetic_operation_new(AEO_DIV, $1, $3); }
                | cexpression "%" cexpression { $$ = g_scan_arithmetic_operation_new(AEO_MOD, $1, $3); }
                ;


 set_match_counter : "none" "of" pattern_set
                   {
                       GScanSetMatchCounter *__counter;
                       __counter = G_SCAN_SET_MATCH_COUNTER($3);
                       g_scan_set_match_counter_define_expected_matches(__counter, SSCT_NONE, NULL);
                       $$ = $3;
                   }
                   | "any" "of" pattern_set
                   {
                       GScanSetMatchCounter *__counter;
                       __counter = G_SCAN_SET_MATCH_COUNTER($3);
                       g_scan_set_match_counter_define_expected_matches(__counter, SSCT_ANY, NULL);
                       $$ = $3;
                   }
                   | "all" "of" pattern_set
                   {
                       GScanSetMatchCounter *__counter;
                       __counter = G_SCAN_SET_MATCH_COUNTER($3);
                       g_scan_set_match_counter_define_expected_matches(__counter, SSCT_ALL, NULL);
                       $$ = $3;
                   }
                   | UNSIGNED_INTEGER "of" pattern_set
                   {
                       GScanSetMatchCounter *__counter;
                       size_t __number;
                       bool __status;

                       __counter = G_SCAN_SET_MATCH_COUNTER($3);
                       __number = $1;

                       __status = g_scan_set_match_counter_define_expected_matches(__counter,
                                                                                   SSCT_NUMBER, &__number);

                       if (!__status)
                       {
                           char *_msg;
                           int _ret;

                           _ret = asprintf(&_msg, _("Expected matches counter too high: %zu"), __number);

                           if (_ret != -1)
                           {
                               raise_error(_msg);
                               free(_msg);
                           }

                           YYERROR;
                       }

                       $$ = $3;

                   }
                   ;

       pattern_set : "them"
                   {
                       size_t __count;
                       GSearchPattern **__patterns;
                       size_t __i;

                       __patterns = g_scan_rule_get_local_variables(*built_rule, NULL, &__count);

                       $$ = g_scan_set_match_counter_new(__patterns, __count);

                       for (__i = 0; __i < __count; __i++)
                           g_object_unref(G_OBJECT(__patterns[__i]));

                       free(__patterns);

                   }
                   | "(" pattern_set_items ")"
                   {
                       $$ = $2;
                   }
                   ;

 pattern_set_items : BYTES_ID
                   {
                       GSearchPattern *__pat;

                       __pat = g_scan_rule_get_local_variable(*built_rule, $1.data);

                       if (__pat == NULL)
                       {
                           char *_msg;
                           int _ret;

                           _ret = asprintf(&_msg, _("Pattern not found: \"%s\""), $1.data);

                           if (_ret != -1)
                           {
                               raise_error(_msg);
                               free(_msg);
                           }

                           YYERROR;
                       }

                       $$ = g_scan_set_match_counter_new((GSearchPattern *[]) { __pat }, 1);

                       g_object_unref(G_OBJECT(__pat));

                   }
                   | BYTES_FUZZY_ID
                   {
                       size_t __count;
                       GSearchPattern **__patterns;
                       size_t __i;

                       __patterns = g_scan_rule_get_local_variables(*built_rule, $1.data, &__count);

                       if (__count == 0)
                       {
                           char *_msg;
                           int _ret;

                           _ret = asprintf(&_msg, _("Patterns not found: \"%s\""), $1.data);

                           if (_ret != -1)
                           {
                               raise_error(_msg);
                               free(_msg);
                           }

                           YYERROR;
                       }

                       $$ = g_scan_set_match_counter_new(__patterns, __count);

                       for (__i = 0; __i < __count; __i++)
                           g_object_unref(G_OBJECT(__patterns[__i]));

                       free(__patterns);

                   }
                   | pattern_set_items "," BYTES_ID
                   {
                       GSearchPattern *__pat;
                       GScanSetMatchCounter *__counter;

                       __pat = g_scan_rule_get_local_variable(*built_rule, $3.data);

                       if (__pat == NULL)
                       {
                           char *_msg;
                           int _ret;

                           _ret = asprintf(&_msg, _("Pattern not found: \"%s\""), $3.data);

                           if (_ret != -1)
                           {
                               raise_error(_msg);
                               free(_msg);
                           }

                           YYERROR;
                       }

                       __counter = G_SCAN_SET_MATCH_COUNTER($1);
                       g_scan_set_match_counter_add_extra_patterns(__counter, (GSearchPattern *[]) { __pat }, 1);

                       g_object_unref(G_OBJECT(__pat));

                       $$ = $1;

                   }
                   | pattern_set_items "," BYTES_FUZZY_ID
                   {
                       size_t __count;
                       GSearchPattern **__patterns;
                       GScanSetMatchCounter *__counter;
                       size_t __i;

                       __patterns = g_scan_rule_get_local_variables(*built_rule, $3.data, &__count);

                       if (__count == 0)
                       {
                           char *_msg;
                           int _ret;

                           _ret = asprintf(&_msg, _("Patterns not found: \"%s\""), $3.data);

                           if (_ret != -1)
                           {
                               raise_error(_msg);
                               free(_msg);
                           }

                           YYERROR;
                       }

                       __counter = G_SCAN_SET_MATCH_COUNTER($1);
                       g_scan_set_match_counter_add_extra_patterns(__counter, __patterns, __count);

                       for (__i = 0; __i < __count; __i++)
                           g_object_unref(G_OBJECT(__patterns[__i]));

                       free(__patterns);

                       $$ = $1;

                   }
                   ;


            set : "(" ")"
                {
                    $$ = g_scan_generic_set_new();
                }
                | "(" cexpression "," ")"
                {
                    $$ = g_scan_generic_set_new();
                    g_scan_generic_set_add_item(G_SCAN_GENERIC_SET($$), $2);
                    g_object_unref(G_OBJECT($2));
                }
                | "(" set_items ")"
                {
                    $$ = $2;
                }
                ;

      set_items : cexpression "," cexpression
                {
                    $$ = g_scan_generic_set_new();
                    g_scan_generic_set_add_item(G_SCAN_GENERIC_SET($$), $1);
                    g_object_unref(G_OBJECT($1));
                    g_scan_generic_set_add_item(G_SCAN_GENERIC_SET($$), $3);
                    g_object_unref(G_OBJECT($3));
                }
                | set_items "," cexpression
                {
                    $$ = $1;
                    g_scan_generic_set_add_item(G_SCAN_GENERIC_SET($$), $3);
                    g_object_unref(G_OBJECT($3));
                }
                ;

        set_access : cexpression "[" cexpression "]"
                   {
                       $$ = g_scan_set_item_new($1, $3);
                       g_object_unref(G_OBJECT($1));
                       g_object_unref(G_OBJECT($3));
                   }
                   ;

      intersection : cexpression "in" cexpression
                   {
                       $$ = g_scan_sets_intersection_new($1, $3);
                       g_object_unref(G_OBJECT($1));
                       g_object_unref(G_OBJECT($3));
                   }
                   ;

   pattern_handler : BYTES_ID
                   {
                       GSearchPattern *__pat;
                       __pat = g_scan_rule_get_local_variable(*built_rule, $1.data);
                       if (__pat == NULL)
                           $$ = NULL;
                       else
                       {
                           $$ = g_scan_pattern_handler_new(__pat, SHT_RAW);
                           g_object_unref(G_OBJECT(__pat));
                       }
                   }
                   | BYTES_ID_COUNTER
                   {
                       GSearchPattern *__pat;
                       __pat = g_scan_rule_get_local_variable(*built_rule, $1.data);
                       if (__pat == NULL)
                           $$ = NULL;
                       else
                       {
                           $$ = g_scan_match_counter_new(__pat);
                           g_object_unref(G_OBJECT(__pat));
                       }
                   }
                   | BYTES_ID_START
                   {
                       GSearchPattern *__pat;
                       __pat = g_scan_rule_get_local_variable(*built_rule, $1.data);
                       if (__pat == NULL)
                           $$ = NULL;
                       else
                       {
                           $$ = g_scan_pattern_handler_new(__pat, SHT_START);
                           g_object_unref(G_OBJECT(__pat));
                       }
                   }
                   | BYTES_ID_LENGTH
                   {
                       GSearchPattern *__pat;
                       __pat = g_scan_rule_get_local_variable(*built_rule, $1.data);
                       if (__pat == NULL)
                           $$ = NULL;
                       else
                       {
                           $$ = g_scan_pattern_handler_new(__pat, SHT_LENGTH);
                           g_object_unref(G_OBJECT(__pat));
                       }
                   }
                   | BYTES_ID_END
                   {
                       GSearchPattern *__pat;
                       __pat = g_scan_rule_get_local_variable(*built_rule, $1.data);
                       if (__pat == NULL)
                           $$ = NULL;
                       else
                       {
                           $$ = g_scan_pattern_handler_new(__pat, SHT_END);
                           g_object_unref(G_OBJECT(__pat));
                       }
                   }
                   ;

%%


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = décodeur impliqué dans le processus.               *
*                temp    = zone de travail à destination des lectures.        *
*                msg     = message d'erreur.                                  *
*                                                                             *
*  Description : Affiche un message d'erreur suite à l'analyse en échec.      *
*                                                                             *
*  Retour      : 0                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int yyerror(GContentScanner *scanner, yyscan_t yyscanner, GScanRule **built_rule, sized_string_t *tmp_0, sized_string_t *tmp_1, void/*GBytesPattern*/ **built_pattern, char **buf, size_t *allocated, size_t *used, char *msg)
{
	printf("YYERROR line %d: %s\n", yyget_lineno(yyscanner), msg);

	return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = chercheur de motifs à préparer.                    *
*                text    = définitions des règles à charger.                  *
*                length  = longueur de ces définitions.                       *
*                                                                             *
*  Description : Complète une recherche de motifs avec des règles.            *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool process_rules_definitions(GContentScanner *scanner, const char *text, size_t length)
{
    bool result;                            /* Bilan à renvoyer            */
    GScanRule *built_rule;                  /* Règle en construction       */
    sized_string_t tmp_0;                   /* Zone tampon #1              */
    sized_string_t tmp_1;                   /* Zone tampon #2              */
    void /*GBytesPattern*/ *built_pattern;           /* Motif en construction       */
    char *buf;                              /* Zone de travail temporaire  */
    size_t allocated;                       /* Taille de mémoire allouée   */
    size_t used;                            /* Quantité utilisée           */
    yyscan_t lexstate;                      /* Gestion d'analyse lexicale  */
    YY_BUFFER_STATE state;                  /* Contexte d'analyse          */
    int status;                             /* Bilan d'une analyse         */

    result = false;

    built_rule = NULL;

    tmp_0.data = malloc((length + 1) * sizeof(bin_t));
    tmp_0.len = 0;

    tmp_1.data = malloc((length + 1) * sizeof(bin_t));
    tmp_1.len = 0;

    built_pattern = NULL;

    allocated = 256;
    used = 0;

    buf = malloc(allocated * sizeof(char));
    buf[0] = '\0';

    rost_lex_init(&lexstate);

    state = rost__scan_bytes(text, length, lexstate);

    status = yyparse(scanner, lexstate, &built_rule, &tmp_0, &tmp_1, &built_pattern, &buf, &allocated, &used);

    result = (status == EXIT_SUCCESS);

    yy_delete_buffer(state, lexstate);

    rost_lex_destroy(lexstate);

    exit_szstr(&tmp_0);
    exit_szstr(&tmp_1);

    free(buf);

    return result;

}
