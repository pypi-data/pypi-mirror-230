
#include <stdio.h>


/**
 * On reproduit un code similaire à celui d'un fichier de Busybox (busybox-1.30.0/libbb/libbb/endofname.c).
 *
 * La commande de compilation est :
 *
 * arm-linux-gnueabi-gcc     -I../include -I../libbb  -include ../include/autoconf.h -D_GNU_SOURCE -DNDEBUG   -fno-builtin-strlen -finline-limit=0 -fomit-frame-pointer -ffunction-sections -fdata-sections -fno-guess-branch-probability -funsigned-char -static-libgcc -falign-functions=1 -falign-jumps=1 -falign-labels=1 -falign-loops=1 -fno-unwind-tables -fno-asynchronous-unwind-tables -fno-builtin-printf -Os -E  -c -o a.out endofname.c
 *
 */


/*
static __attribute__ ((always_inline)) __inline__ int bb_ascii_isalnum(unsigned char a)
{
    unsigned char b = a - '0';
    if (b <= 9)
        return (b <= 9);
    b = (a|0x20) - 'a';
    return b <= 'z' - 'a';
}

const char *endofname(const char *name)
{
    if (!((*name) == '_' || ((unsigned char)((((unsigned char)(*name))|0x20) - 'a') <= ('z' - 'a'))))
        return name;
    while (*++name) {
        if (!((*name) == '_' || bb_ascii_isalnum((unsigned char)(*name))))
            break;
    }
    return name;
}
*/


void __attribute__ ((naked)) endofname(const char *name)
{
    /*
      83bc:       e5d03000        ldrb    r3, [r0]
      83c0:       e353005f        cmp     r3, #95 ; 0x5f
      83c4:       0a000003        beq     83d8 <endofname+0x1c>
      83c8:       e3833020        orr     r3, r3, #32
      83cc:       e2433061        sub     r3, r3, #97     ; 0x61
      83d0:       e3530019        cmp     r3, #25
      83d4:       812fff1e        bxhi    lr
      83d8:       e5f03001        ldrb    r3, [r0, #1]!
      83dc:       e3530000        cmp     r3, #0
      83e0:       0a000005        beq     83fc <endofname+0x40>
      83e4:       e353005f        cmp     r3, #95 ; 0x5f
      83e8:       0afffffa        beq     83d8 <endofname+0x1c>
      83ec:       e2432030        sub     r2, r3, #48     ; 0x30
      83f0:       e3520009        cmp     r2, #9
      83f4:       9afffff7        bls     83d8 <endofname+0x1c>
      83f8:       eafffff2        b       83c8 <endofname+0xc>
      83fc:       e12fff1e        bx      lr
    */

asm (

     "ldrb    r3, [r0]"         "\n"
     "cmp     r3, #95"          "\n"
     "beq     .Lbl_83d8%="      "\n"

     ".Lbl_83c8%=:"             "\n"

     "orr     r3, r3, #32"      "\n"
     "sub     r3, r3, #97"      "\n"
     "cmp     r3, #25"          "\n"
     "bxhi    lr"               "\n"

     ".Lbl_83d8%=:"             "\n"

     "ldrb    r3, [r0, #1]!"    "\n"
     "cmp     r3, #0"           "\n"
     "beq     .Lbl_83fc%="      "\n"
     "cmp     r3, #95"          "\n"
     "beq     .Lbl_83d8%="      "\n"
     "sub     r2, r3, #48"      "\n"
     "cmp     r2, #9"           "\n"
     "bls     .Lbl_83d8%="      "\n"
     "b       .Lbl_83c8%="      "\n"

     ".Lbl_83fc%=:"             "\n"

     "bx      lr"               "\n"

     ::"r" (name));

}

int main(int argc, char **argv)
{
    endofname(argv[0]);

    return 0;

}
