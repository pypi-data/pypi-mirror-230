%{

#include "gram.h"

%}

%option noinput
%option nounput
%option noyywrap
%option yylineno

%%

;[^$]*  return COMMENT;

add     return ADD;
and     return AND;
call    return CALL;
div     return DIV;
dup     return DUP;
equ     return EQU;
goe     return GOE;
gt      return GT;
jmp     return JMP;
jz      return JZ;
lb      return LB;
li      return LI;
loe     return LOE;
lt      return LT;
lws     return LWS;
lw      return LW;
mul     return MUL;
nop     return NOP;
nor     return NOR;
not     return NOT;
or      return OR;
pop     return POP;
push    return PUSH;
rot3    return ROT3;
rot     return ROT;
salloc  return SALLOC;
sb      return SB;
shl     return SHL; 
shr     return SHR;
sub     return SUB;
sws     return SWS;
sw      return SW;
syscall return SYSCALL;
xor     return XOR;

0x[0-9a-f]{1,4} { yylval.number = strtol(yytext + 2, NULL, 16); return NUMBER; }
[A-Za-z0-9]+:   { yylval.text = yytext; return LABEL; }

a       return REG_A;
b       return REG_B;
c       return REG_C;
d       return REG_D;
e       return REG_E;
f       return REG_F;

[A-Za-z0-9]+    { yylval.text = yytext; return TEXT; }

[ \t]+
