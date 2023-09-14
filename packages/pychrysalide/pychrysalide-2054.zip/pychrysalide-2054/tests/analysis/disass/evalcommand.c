

/**
 * On reproduit un code similaire à celui d'un fichier de Busybox (busybox-1.30.0/shell/ash.c).
 *
 * La commande de compilation est :
 *
 * arm-linux-gnueabi-gcc -Wp,-MD,shell/.ash.o.d   -std=gnu99 -Iinclude -Ilibbb  -include include/autoconf.h -D_GNU_SOURCE -DNDEBUG  -D"BB_VER=KBUILD_STR(1.30.0)"  -Wall -Wshadow -Wwrite-strings -Wundef -Wstrict-prototypes -Wunused -Wunused-parameter -Wunused-function -Wunused-value -Wmissing-prototypes -Wmissing-declarations -Wno-format-security -Wdeclaration-after-statement -Wold-style-definition -fno-builtin-strlen -finline-limit=0 -fomit-frame-pointer -ffunction-sections -fdata-sections -fno-guess-branch-probability -funsigned-char -static-libgcc -falign-functions=1 -falign-jumps=1 -falign-labels=1 -falign-loops=1 -fno-unwind-tables -fno-asynchronous-unwind-tables -fno-builtin-printf -Os     -D"KBUILD_STR(s)=#s" -D"KBUILD_BASENAME=KBUILD_STR(ash)"  -D"KBUILD_MODNAME=KBUILD_STR(ash)" -c -o shell/ash.o shell/ash.c
 *
 */

#if 0

static int
evalcommand(union node *cmd, int flags)
{
	static const struct builtincmd null_bltin = {
		"\0\0", bltincmd /* why three NULs? */
	};

	union node *argp;
	struct arglist arglist;
	char **argv;
	int argc;
	const struct strlist *sp;
	struct cmdentry cmdentry;
	const char *path;
	char **nargv;


	/* First expand the arguments. */

	cmdentry.cmdtype = CMDBUILTIN;
	cmdentry.u.cmd = &null_bltin;
	arglist.lastp = &arglist.list;
	*arglist.lastp = NULL;

	argc = 0;
	if (cmd->ncmd.args) {
		smallint pseudovarflag;

		for (argp = cmd->ncmd.args; argp; argp = argp->narg.next) {
			struct strlist **spp;

			spp = arglist.lastp;
			if (pseudovarflag)
				expandarg(argp, &arglist, EXP_VARTILDE);

			for (sp = *spp; sp; sp = sp->next)
				argc++;
		}
	}

	/* Reserve one extra spot at the front for shellexec. */
	nargv = NULL;//stalloc(sizeof(char *) * (argc + 2));
	argv = ++nargv;
	*nargv = NULL;




	path = vpath.var_text;

	/* Now locate the command. */

		for (;;) {
			find_command(argv[0], &cmdentry, DO_ERR, path);

#if ENABLE_ASH_CMDCMD
			if (cmdentry.u.cmd == COMMANDCMD) {
				nargv = parse_command_args(argv, &path);
                break;

			} else
#endif
				break;
		}



	return 0;

}

#endif


static int __attribute__ ((naked)) evalcommand(void /*union node*/ *cmd, int flags)
{

    /*
   138ac:       e92d401f        push    {r0, r1, r2, r3, r4, lr}
   138b0:       e3a03002        mov     r3, #2
   138b4:       e58d3008        str     r3, [sp, #8]
   138b8:       e59f30b8        ldr     r3, [pc, #184]  ; 13978 <evalcommand+0xcc>
   138bc:       e58dd004        str     sp, [sp, #4]
   138c0:       e58d300c        str     r3, [sp, #12]
   138c4:       e3a03000        mov     r3, #0
   138c8:       e58d3000        str     r3, [sp]
   138cc:       e590300c        ldr     r3, [r0, #12]
   138d0:       e3530000        cmp     r3, #0
   138d4:       1a00000d        bne     13910 <evalcommand+0x64>
   138d8:       e3a00000        mov     r0, #0
   138dc:       e59f3098        ldr     r3, [pc, #152]  ; 1397c <evalcommand+0xd0>
   138e0:       e5800004        str     r0, [r0, #4]
   138e4:       e5933000        ldr     r3, [r3]
   138e8:       e3a02001        mov     r2, #1
   138ec:       e59330f0        ldr     r3, [r3, #240]  ; 0xf0
   138f0:       e28d1008        add     r1, sp, #8
   138f4:       ebfffe71        bl      132c0 <find_command>
   138f8:       e59d200c        ldr     r2, [sp, #12]
   138fc:       e59f307c        ldr     r3, [pc, #124]  ; 13980 <evalcommand+0xd4>
   13900:       e1520003        cmp     r2, r3
   13904:       1a000018        bne     1396c <evalcommand+0xc0>
   13908:       e3a01004        mov     r1, #4
   1390c:       ea00000f        b       13950 <evalcommand+0xa4>
   13910:       e5933004        ldr     r3, [r3, #4]
   13914:       eaffffed        b       138d0 <evalcommand+0x24>
   13918:       e5d23000        ldrb    r3, [r2]
   1391c:       e353002d        cmp     r3, #45 ; 0x2d
   13920:       1a000011        bne     1396c <evalcommand+0xc0>
   13924:       e5d23001        ldrb    r3, [r2, #1]
   13928:       e2820002        add     r0, r2, #2
   1392c:       e3530000        cmp     r3, #0
   13930:       0a00000d        beq     1396c <evalcommand+0xc0>
   13934:       e353002d        cmp     r3, #45 ; 0x2d
   13938:       0a000008        beq     13960 <evalcommand+0xb4>
   1393c:       e3530070        cmp     r3, #112        ; 0x70
   13940:       1a000009        bne     1396c <evalcommand+0xc0>
   13944:       e4d03001        ldrb    r3, [r0], #1
   13948:       e3530000        cmp     r3, #0
   1394c:       1afffffa        bne     1393c <evalcommand+0x90>
   13950:       e5b12004        ldr     r2, [r1, #4]!
   13954:       e3520000        cmp     r2, #0
   13958:       0a000003        beq     1396c <evalcommand+0xc0>
   1395c:       eaffffed        b       13918 <evalcommand+0x6c>
   13960:       e5d22002        ldrb    r2, [r2, #2]
   13964:       e3520000        cmp     r2, #0
   13968:       1afffff3        bne     1393c <evalcommand+0x90>
   1396c:       e3a00000        mov     r0, #0
   13970:       e28dd014        add     sp, sp, #20
   13974:       e49df004        pop     {pc}            ; (ldr pc, [sp], #4)
   13978:       00017fa4        .word   0x00017fa4
   1397c:       000213f4        .word   0x000213f4
   13980:       00017e60        .word   0x00017e60
    */


asm (

     "push    {r0, r1, r2, r3, r4, lr}" "\n"
     "mov     r3, #2"                   "\n"
     "str     r3, [sp, #8]"             "\n"
     "ldr     r3, [pc, #184]"           "\n"
     "str     sp, [sp, #4]"             "\n"
     "str     r3, [sp, #12]"            "\n"
     "mov     r3, #0"                   "\n"
     "str     r3, [sp]"                 "\n"
     "ldr     r3, [r0, #12]"            "\n"

     ".Lbl_138d0%=:"                    "\n"

     "cmp     r3, #0"                   "\n"
     "bne     .Lbl_13910%="             "\n"

     "mov     r0, #0"                   "\n"
     "ldr     r3, [pc, #152]"           "\n"
     "str     r0, [r0, #4]"             "\n"
     "ldr     r3, [r3]"                 "\n"
     "mov     r2, #1"                   "\n"
     "ldr     r3, [r3, #240]"           "\n"
     "add     r1, sp, #8"               "\n"
     "bl      .Lbl_find%="              "\n" /* <find_command> */
     "ldr     r2, [sp, #12]"            "\n"
     "ldr     r3, [pc, #124]"           "\n"
     "cmp     r2, r3"                   "\n"
     "bne     .Lbl_1396c%="             "\n"

     "mov     r1, #4"                   "\n"
     "b       .Lbl_13950%="             "\n"

     ".Lbl_13910%=:"                    "\n"

     "ldr     r3, [r3, #4]"             "\n"
     "b       .Lbl_138d0%="             "\n"

     ".Lbl_13918%=:"                    "\n"

     "ldrb    r3, [r2]"                 "\n"
     "cmp     r3, #45"                  "\n"
     "bne     .Lbl_1396c%="             "\n"

     "ldrb    r3, [r2, #1]"             "\n"
     "add     r0, r2, #2"               "\n"
     "cmp     r3, #0"                   "\n"
     "beq     .Lbl_1396c%="             "\n"

     "cmp     r3, #45"                  "\n"
     "beq     .Lbl_13960%="             "\n"

     ".Lbl_1393c%=:"                    "\n"

     "cmp     r3, #112"                 "\n"
     "bne     .Lbl_1396c%="             "\n"

     "ldrb    r3, [r0], #1"             "\n"
     "cmp     r3, #0"                   "\n"
     "bne     .Lbl_1393c%="             "\n"

     ".Lbl_13950%=:"                    "\n"

     "ldr     r2, [r1, #4]!"            "\n"
     "cmp     r2, #0"                   "\n"
     "beq     .Lbl_1396c%="             "\n"
     "b       .Lbl_13918%="             "\n"

     ".Lbl_13960%=:"                    "\n"

     "ldrb    r2, [r2, #2]"             "\n"
     "cmp     r2, #0"                   "\n"
     "bne     .Lbl_1393c%="             "\n"

     ".Lbl_1396c%=:"                    "\n"

     "mov     r0, #0"                   "\n"
     "add     sp, sp, #20"              "\n"
     "pop     {pc}"                     "\n"

     ".word   0x00017fa4"               "\n"
     ".word   0x000213f4"               "\n"
     ".word   0x00017e60"               "\n"

     ".Lbl_find%=:"                     "\n"

     ::"r" (cmd, flags));

}

int main(int argc, char **argv)
{
    return evalcommand((void *)0, 0);

}
