# First here's the interrupt vector
B start   # Initial/startup handler
B timer   # Timer/IRQ handler
B .       # Empty handler
B .       # Empty handler

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
	mov r3, 0, 10
	BE r2, r3, 4
	IRET
	STOP
