B start
B timer
B .
B .

# Make some initializations
start:
	MOV r1, 0, 0
	MOV r2, 0, 0
	# Start interrupts
	SETI

# Loop
loop:
	ADD r1, 0, 1
	B loop

# Timer handler
timer:
	ADD r2, 0, 1
	mov r3, 10
	BE r2, r3, 4
	IRET
	STOP
