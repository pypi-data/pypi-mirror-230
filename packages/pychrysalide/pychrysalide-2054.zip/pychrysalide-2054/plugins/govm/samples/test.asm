
	; Should be skipped
	jmp	end

start:
	; Let's start !

	nop
	nop
	nop		; Zzz

	li	0x1234

	li	0x01
	li	0x002
	add

	pop	b

end:

	li	0x0
	syscall		; halt

	nop

