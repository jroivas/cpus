
class Opcodes:
    opcodes = {
        0x00: 'NOP',
        0x01: 'LOAD8i',
        0x02: 'LOAD16i',
        0x03: 'LOAD32i',
        0x04: 'STORE8i',
        0x05: 'STORE16i',
        0x06: 'STORE32i',
        0x07: 'LOAD8',
        0x08: 'LOAD16',
        0x09: 'LOAD32',
        #0x0A: 'LOAD64',
        0x0B: 'STORE8',
        0x0C: 'STORE16',
        0x0D: 'STORE32',
        #0x0E: 'STORE64',
        0x0F: 'LOADADDRi',

        0x23: 'MOV',
        0x24: 'MOVi',
        0x25: 'SWP',

        0x2D: 'MAP',
        0x2E: 'START',
        0x2F: 'INTVEC',

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
        0x21: 'PUSH',
        0x22: 'POP',
        0x30: 'Bi',
        0x31: 'B',
        0x32: 'BZi',
        0x33: 'BZ',
        0x34: 'BNZi',
        0x35: 'BNZ',
        0x36: 'BE',
        0x37: 'BNE',
        0x38: 'BLE',
        0x3A: 'BSUBi',
        0x3B: 'BSUB',
        0x3C: 'BRET',
        0x3D: 'IRET',
        0x3E: 'SETI',
        0x3F: 'CLRI',
        0x40: 'CO',
        0x41: 'COS',
        0x42: 'COQ',
        0x43: 'COH',
        0xFF: 'STOP'
        }

    aliases = {
        'LOADi': 'LOAD32i',
        'STOREi': 'STORE32i',
        'LOAD': 'LOAD32',
        'STORE': 'STORE32',
        }

    def __init__(self):
        self.rev_opcodes = {v:k for k, v in self.opcodes.items()}
        self.rev_upper_opcodes = {v.upper():k for k, v in self.opcodes.items()}
