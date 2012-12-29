.code
	mov r1, 0, text
	mov r9, 0, 0
	LOAD32i vidmem
	mov r10, r0, 0
loop:
	LOAD8 r1, r2, 0
	BNE r2, r9, 4
	B out

	STORE8 r10, r2
	ADD r1, 0, 1
	ADD r10, 0, 1
	B loop

out:
	#LOAD32i vidctrl
	LOADADDRi 0x03BB
	mov r11, r0, 0
	LOADADDRi 0x8000
	STORE16 r0, r11
	MOV r10, 0, 1
	STORE8 r0, r10
	STOP

.data
	dd 0x1234
vidctrl:
	#dd 0x8000
vidmem:
	dd 0x8010
text:
	dt "Hello World!"
num:
	dd 123
