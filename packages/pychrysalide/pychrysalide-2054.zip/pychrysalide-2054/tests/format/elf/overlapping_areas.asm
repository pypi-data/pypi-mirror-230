
.macro bump addr
    .word \addr + 0x200000
.endm

.macro label_offset lbl
    .word \lbl - str_table
.endm


elf_header:

    .byte 0x7F, 'E', 'L', 'F'   @ e_ident
    .byte 1                     @ EI_CLASS => ELFCLASS32
    .byte 1                     @ EI_DATA => ELFDATA2LSB
    .byte 1                     @ EI_VERSION => EV_CURRENT
    .byte 0                     @ EI_OSABI => ELFOSABI_SYSV
    .byte 0                     @ EI_ABIVERSION

    .word 0
    .short 0
    .byte 0

    .short 2        @ e_type => ET_EXEC
    .short 40       @ e_machine => EM_ARM
    .word 1         @ e_version =>  EV_CURRENT
    bump main       @ e_entry

    .word program_headers   @ e_phoff
    .word section_headers   @ e_shoff

    .word 0x80      @ e_flags => EF_ARM_NEW_ABI

    .short 52       @ e_ehsize
    .short 32       @ e_phentsize
    .short 2        @ e_phnum
    .short 40       @ e_shentsize
    .short 2        @ e_shnum
    .short 1        @ e_shstrndx


program_headers:

    .word 1             @ p_type => PT_LOAD
    .word O             @ p_offset
    .word 0x200000      @ p_vaddr
    .word 0x200000      @ p_paddr
    .word bss_start     @ p_filesz
    .word bss_start     @ p_memsz
    .word 0x5           @ p_flags =>  PF_X | PF_R
    .word 0x1000        @ p_align

    .word 1             @ p_type => PT_LOAD
    .word bss_start     @ p_offset
    .word 0x300000      @ p_vaddr
    .word 0x300000      @ p_paddr
    .word bss_end - bss_start   @ p_filesz
    .word bss_end - bss_start   @ p_memsz
    .word 0x6           @ p_flags =>  PF_W | PF_R
    .word 0x1           @ p_align


section_headers:

    label_offset text_lbl   @ sh_name
    .word 1                 @ sh_type => SHT_PROGBITS
    .word 0x6               @ sh_flags => SHF_ALLOC | SHF_EXECINSTR
    bump main               @ sh_addr
    .word main              @ sh_offset
    .word main_return - main    @ sh_size
    .word 0                 @ sh_link
    .word 0                 @ sh_info
    .word 4                 @ sh_addralign
    .word 0                 @ sh_entsize

    label_offset strtab_lbl @ sh_name
    .word 3                 @ sh_type => SHT_STRTAB
    .word 0x0               @ sh_flags
    .word 0x0               @ sh_addr
    .word str_table         @ sh_offset
    .word str_table_end - str_table @ sh_size
    .word 0                 @ sh_link
    .word 0                 @ sh_info
    .word 1                 @ sh_addralign
    .word 0                 @ sh_entsize


main:
    mov r7, #1   @ __NR_exit
    mov r0, #42  @ $?
    svc 0

main_return:


bss_start:

    .word 0x0
    .word 0x0
    .word 0x0
    .word 0x0

str_table:

    .byte 0, 0
text_lbl:
    .byte '.', 't', 'e', 'x', 't', 0
strtab_lbl:
    .byte '.', 's', 't', 'r', 't', 'a', 'b', 0
blabla:
    .byte 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'
bss_end:
    .byte 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 0

str_table_end:
