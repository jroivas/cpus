.base 0x1000
.code
	# Load mmu mapping table
	LOADADDRi table
	# Table size
	mov r1, 0, 2
	# Load it and enable mapping
	MAP r0, r1, 1

	# Load item in virtual mem mode
	# Data is starting from virtual 0x8000 so need to adapt
	LOADADDRi 0x8008
	LOAD32 r2, r0

	# Same, but adapt on run time
	LOADADDRi item
	mov r3, r0
	LOADADDRi 0x1000
	sub r3, r0
	LOADADDRi 0x8000
	add r3, r0
	LOAD32 r4, r3
	STOP

.data
table:
	dd 0x00000102 # first 0x1000 indentity mapped, executable
	dd 0x00008100 # From 0x8000 virt, 0x1000 phys data
item: dd 0x123456
