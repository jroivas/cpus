
class Opcodes:
    opcodes = {
        0x00: 'NOP',
        0x01: 'LOADi',
        0x02: 'STOREi',
        0x03: 'LOAD',
        0x04: 'STORE',
        0x05: 'MOV',
        0x06: 'MOVi',
        0x07: 'SWP',
        0x10: 'ADD',
        0x11: 'SUB',
        0x12: 'MUL',
        0x13: 'DIV',
        0x14: 'MOD',
        0x15: 'SHL',
        0x16: 'SHR',
        0x17: 'AND',
        0x18: 'OR',
        0x19: 'XOR',
        0x20: 'NOT',
        0x30: 'B',
        0x31: 'BZ',
        0x32: 'BNZ',
        0x33: 'BE',
        0x34: 'BNE',
        0x35: 'BLE',
        0xFF: 'STOP'
        }

    def __init__(self):
        self.rev_opcodes = {v:k for k, v in self.opcodes.iteritems()}
