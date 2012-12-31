.base 0x1000
.code
	# Move location of text to r1
	LOADADDRi text
	mov r1, r0
	mov r9, 0, 0
	# Load video memory location to r0 and...
	LOAD32i vidmem
	# ...move it to r10
	mov r10, r0, 0

loop:
	# Get one byte from r1 location to r2
	LOAD8 r2, r1, 0
	# If value of r2 is not value of r9, skip next
	BNE r2, r9, 4
	# In case r2 == r9, get out (r9 value is zero, means null terminating)
	Bi out

	# Store value of r2 to location of r10
	# Means we're writing it to video memory
	STORE8 r10, r2
	# Increase text address
	ADD r1, 0, 1
	# Increase video mem address
	ADD r10, 0, 1
	# Loop
	Bi loop

out:
	# This sets video memory to be 3 lines height
	LOADADDRi 0x03BB
	# Store it to r11
	mov r11, r0, 0
	# Load video memory control address
	LOADADDRi 0x8000
	# Change height to 3
	STORE16 r0, r11
	# Put 1 to r10, which means update screen
	MOV r10, 0, 1
	# Put contents of r10 to control address
	# Meaning show video buffer contents
	STORE8 r0, r10
	# Stop execution
	STOP

vidctrl:
	dd 0x8000
vidmem:
	dd 0x8010

.data
	dd 0x1234
text:
	dt "Hello World!"
num:
	dd 123
