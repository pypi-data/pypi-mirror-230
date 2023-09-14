
#include <stdio.h>


/**
 * On reproduit un code similaire à celui d'un fichier de Busybox (busybox-1.30.0/libbb/appletlib.c).
 *
 * La commande de compilation est :
 *
 * arm-linux-gnueabi-gcc -Wp,-MD,libbb/.appletlib.o.d   -std=gnu99 -Iinclude -Ilibbb  -include include/autoconf.h -D_GNU_SOURCE -DNDEBUG  -D"BB_VER=KBUILD_STR(1.30.0)"  -Wall -Wshadow -Wwrite-strings -Wundef -Wstrict-prototypes -Wunused -Wunused-parameter -Wunused-function -Wunused-value -Wmissing-prototypes -Wmissing-declarations -Wno-format-security -Wdeclaration-after-statement -Wold-style-definition -fno-builtin-strlen -finline-limit=0 -fomit-frame-pointer -ffunction-sections -fdata-sections -fno-guess-branch-probability -funsigned-char -static-libgcc -falign-functions=1 -falign-jumps=1 -falign-labels=1 -falign-loops=1 -fno-unwind-tables -fno-asynchronous-unwind-tables -fno-builtin-printf -Os     -D"KBUILD_STR(s)=#s" -D"KBUILD_BASENAME=KBUILD_STR(appletlib)"  -D"KBUILD_MODNAME=KBUILD_STR(appletlib)" -c -o libbb/appletlib.o libbb/appletlib.c
 *
 */


/*
unsigned FAST_FUNC string_array_len(char **argv)
{
	char **start = argv;

	while (*argv)
		argv++;

	return argv - start;
}
*/

unsigned __attribute__ ((naked)) string_array_len(char **argv)
{
    /*
   0x00009a0c <+0>:	mov	r2, r0
   0x00009a10 <+4>:	mov	r3, r2
   0x00009a14 <+8>:	ldr	r1, [r3]
   0x00009a18 <+12>:	add	r2, r2, #4
   0x00009a1c <+16>:	cmp	r1, #0
   0x00009a20 <+20>:	bne	0x9a10 <string_array_len+4>
   0x00009a24 <+24>:	rsb	r0, r0, r3
   0x00009a28 <+28>:	asr	r0, r0, #2
   0x00009a2c <+32>:	bx	lr
    */

asm (

     "mov	r2, r0"             "\n"

     ".Lbl_9a10%=:"             "\n"

     "mov	r3, r2"             "\n"
     "ldr	r1, [r3]"           "\n"
     "add	r2, r2, #4"         "\n"
     "cmp	r1, #0"             "\n"
     "bne   .Lbl_9a10%="        "\n"
     "rsb	r0, r0, r3"         "\n"
     "asr	r0, r0, #2"         "\n"
     "bx	lr"                 "\n"

     ::"r" (argv));

}

int main(int argc, char **argv)
{
    return string_array_len(argv);

}
