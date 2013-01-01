.code
	loadaddri 0x8010
	mov r10, r0
	loadaddri 0x8000
	mov r11, r0
	mov r1, 0, 0x48
	store8 r10, r1
	mov r1, 0, 0x69
	add r10, 0, 1
	store8 r10, r1
	mov r1, 0, 1
	store8 r11, r1
	stop
