.base 0x1000
.code
	# Load mmu mapping table
	LOADADDRi table
	# Table size
	mov r1, 0, 9
	# Load it and enable mapping
	MAP r0, r1, 1

	# We have malicious code in data section
	# Load the address

	LOADADDRi maldata
	mov r3, r0
	LOADADDRi 0x1000
	sub r3, r0
	LOADADDRi 0xA000
	add r3, r0

	# Jump there
	B r3

	STOP

.data
table:
	dd 0x00000102 # first 0x1000 indentity mapped, executable
	dd 0x0000A100 # From 0xA000 virt, 0x1000 phys data
	dd 0x0000B000 # dummy
	dd 0x0000B000 # dummy
	dd 0x0000B000 # dummy
	dd 0x0000B000 # dummy
	dd 0x0000B000 # dummy
	dd 0x0000B000 # dummy
	dd 0x00008110 # Map video memory identity mapped
maldata:
	dd 0x0080100f
	dd 0x00010b23
	dd 0x0080000f
	dd 0x00010c23
	dd 0x48000223
	dd 0x00020b0b
	dd 0x69000223
	dd 0x01000b10
	dd 0x00020b0b
	dd 0x01000223
	dd 0x00020c0b
	dd 0x000000ff
