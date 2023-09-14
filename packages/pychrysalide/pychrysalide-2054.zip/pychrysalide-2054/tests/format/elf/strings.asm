
.data

.global msg
.global no_arg_msg
.global got_arg_msg

msg:
    .ascii      "Hello, ARM!\n"

len = . - msg

no_arg_msg:
    .ascii      "No command line argument...\n"

no_arg_len = . - no_arg_msg

got_arg_msg:
    .ascii      "Got command line argument(s)...\n"

got_arg_len = . - got_arg_msg

.text

.global do_syscalls

do_syscalls:

    /**
     * syscall write(int fd, const void *buf, size_t count)
     */

    mov     %r0, $1     /* fd -> stdout */
    ldr     %r1, =msg   /* buf -> msg */
    ldr     %r2, =len   /* count -> len(msg) */
    mov     %r7, $4     /* write is syscall #4 */
    swi     $0          /* invoke syscall */

    /**
     * syscall write(int fd, const void *buf, size_t count)
     */

    mov     %r0, $2     /* fd -> stderr */
    mov     %r7, $4     /* write is syscall #4 */

    ldr     %r3, [sp]   /* argc */
    cmp     %r3, $1

    beq     no_arg

    ldr     %r1, =got_arg_msg   /* buf -> msg */
    ldr     %r2, =got_arg_len   /* count -> len(msg) */

    b       process_arg

no_arg:

    ldr     %r1, =no_arg_msg   /* buf -> msg */
    ldr     %r2, =no_arg_len   /* count -> len(msg) */

process_arg:

    swi     $0          /* invoke syscall */

    /**
     * syscall exit(int status)
     */

    mov     %r0, $123   /* status -> 0 */
    mov     %r7, $1     /* exit is syscall #1 */
    swi     $0          /* invoke syscall */

.global _start

_start:

    bl      do_syscalls
