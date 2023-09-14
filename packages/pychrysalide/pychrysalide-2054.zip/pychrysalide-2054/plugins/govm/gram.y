%{

#include <stdio.h>
#include <stdlib.h>


#include "build.h"


/* De tok.c... */
extern int yylex(void);
typedef struct yy_buffer_state *YY_BUFFER_STATE;
extern YY_BUFFER_STATE yy_scan_string(const char *);
extern void yy_delete_buffer(YY_BUFFER_STATE);


/* Affiche un message d'erreur concernant l'analyse. */
int yyerror(govm_info *, char *);

/* Procède à l'assemblage d'une ligne de code. */
bool process_govm_code(govm_info *, const char *);

%}

%union {

    char *text;
    short/*uint16_t*/ number;

}


%parse-param { govm_info *info }

%token COMMENT

%token ADD AND CALL DIV DUP EQU GOE GT JMP JZ LB LI LOE LT LW LWS MUL NOP NOR NOT OR POP PUSH ROT ROT3 SALLOC SB SHL SHR SUB SW SWS SYSCALL XOR

%token NUMBER LABEL TEXT
%token REG_A REG_B REG_C REG_D REG_E REG_F

%type <text> LABEL TEXT
%type <number> NUMBER


%%

input:
    /* Vide */
    | input line
    ;

line:
    COMMENT
    | LABEL         { register_govm_label(info, $1); }
    | expression
    ;

expression:
    ADD             { encode_govm_instruction(info, GOP_ADD); }
    | AND           { encode_govm_instruction(info, GOP_AND); }
    | data
    | DIV           { encode_govm_instruction(info, GOP_DIV); }
    | DUP           { encode_govm_instruction(info, GOP_DUP); }
    | EQU           { encode_govm_instruction(info, GOP_EQU); }
    | flow_mod
    | GOE           { encode_govm_instruction(info, GOP_GOE); }
    | GT            { encode_govm_instruction(info, GOP_GT); }
    | LI NUMBER     { encode_govm_instruction(info, GOP_LI); encode_govm_number(info, $2); }
    | LOE           { encode_govm_instruction(info, GOP_LOE); }
    | LT            { encode_govm_instruction(info, GOP_LT); }
    | LWS           { encode_govm_instruction(info, GOP_LWS); }
    | MUL           { encode_govm_instruction(info, GOP_MUL); }
    | NOP           { encode_govm_instruction(info, GOP_NOP); }
    | NOR           { encode_govm_instruction(info, GOP_NOR); }
    | NOT           { encode_govm_instruction(info, GOP_NOT); }
    | OR            { encode_govm_instruction(info, GOP_OR); }
    | POP           { encode_govm_instruction(info, GOP_POP); }
    | pop_reg
    | push_reg
    | ROT           { encode_govm_instruction(info, GOP_ROT); }
    | ROT3          { encode_govm_instruction(info, GOP_ROT3); }
    | SALLOC        { encode_govm_instruction(info, GOP_SALLOC); }
    | SHL           { encode_govm_instruction(info, GOP_SHL); }
    | SHR           { encode_govm_instruction(info, GOP_SHR); }
    | SUB           { encode_govm_instruction(info, GOP_SUB); }
    | SWS           { encode_govm_instruction(info, GOP_SWS); }
    | SYSCALL       { encode_govm_instruction(info, GOP_SYSCALL); }
    | XOR           { encode_govm_instruction(info, GOP_XOR); }
    ;

data:
    LB              { encode_govm_instruction(info, GOP_LB); }
    | LW            { encode_govm_instruction(info, GOP_LW); }
    | SB            { encode_govm_instruction(info, GOP_SB); }
    | SW            { encode_govm_instruction(info, GOP_SW); }
    ;

flow_mod:
    CALL            { encode_govm_instruction(info, GOP_CALL); }
    | JMP           { encode_govm_instruction(info, GOP_JMP); }
    | JZ            { encode_govm_instruction(info, GOP_JZ); }
    | CALL TEXT     { encode_reference_to_govm_label(info, GOP_CALL, $2); }
    | JMP TEXT      { encode_reference_to_govm_label(info, GOP_JMP, $2); }
    | JZ TEXT       { encode_reference_to_govm_label(info, GOP_JZ, $2); }
    ;

pop_reg:
    POP REG_A       { encode_govm_instruction(info, GOP_MOV_A); }
    | POP REG_B     { encode_govm_instruction(info, GOP_MOV_B); }
    | POP REG_C     { encode_govm_instruction(info, GOP_MOV_C); }
    | POP REG_D     { encode_govm_instruction(info, GOP_MOV_D); }
    | POP REG_E     { encode_govm_instruction(info, GOP_MOV_E); }
    | POP REG_F     { encode_govm_instruction(info, GOP_MOV_F); }

push_reg:
    PUSH REG_A      { encode_govm_instruction(info, GOP_A_MOV); }
    | PUSH REG_B    { encode_govm_instruction(info, GOP_B_MOV); }
    | PUSH REG_C    { encode_govm_instruction(info, GOP_C_MOV); }
    | PUSH REG_D    { encode_govm_instruction(info, GOP_D_MOV); }
    | PUSH REG_E    { encode_govm_instruction(info, GOP_E_MOV); }
    | PUSH REG_F    { encode_govm_instruction(info, GOP_F_MOV); }


%%


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations en place.                     *
*                msg  = texte à afficher.                                     *
*                                                                             *
*  Description : Affiche un message d'erreur concernant l'analyse.            *
*                                                                             *
*  Retour      : Statut de sortie à fournir.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int yyerror(govm_info *info, char *msg)
{
    printf("PARSING ERROR :: %s\n", msg);

    return -1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble d'informations à venir compléter.            *
*                code = ligne de code à traiter.                              *
*                                                                             *
*  Description : Procède à l'assemblage d'une ligne de code.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool process_govm_code(govm_info *info, const char *code)
{
	YY_BUFFER_STATE buffer;                 /* Tampon pour bison           */
	int ret;                                /* Bilan de l'appel            */

	buffer = yy_scan_string(code);
	ret = yyparse(info);
	yy_delete_buffer(buffer);

    return (ret == 0);

}
