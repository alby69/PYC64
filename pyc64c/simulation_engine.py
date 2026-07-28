from .sim.sim6502 import sim6502, Flags
from .sim.dis6502 import dis6502

def get_opcode_cycles(opcode):
    cycles_map = {
        0x00: 7, 0x08: 3, 0x09: 2, 0x0A: 2, 0x0D: 4, 0x10: 2, 0x18: 2,
        0x20: 6, 0x24: 3, 0x25: 3, 0x28: 4, 0x29: 2, 0x2A: 2, 0x2C: 4, 0x2D: 4,
        0x30: 2, 0x38: 2, 0x40: 6, 0x45: 3, 0x48: 3, 0x49: 2, 0x4A: 2, 0x4C: 3, 0x4D: 4,
        0x50: 2, 0x58: 2, 0x60: 6, 0x65: 3, 0x68: 4, 0x69: 2, 0x6A: 2, 0x6C: 5, 0x6D: 4,
        0x70: 2, 0x78: 2, 0x84: 3, 0x85: 3, 0x86: 3, 0x88: 2, 0x8A: 2, 0x8C: 4, 0x8D: 4,
        0x8E: 4, 0x90: 2, 0x91: 6, 0x94: 4, 0x95: 4, 0x98: 2, 0x99: 5, 0x9D: 5,
        0xA0: 2, 0xA2: 2, 0xA4: 3, 0xA5: 3, 0xA6: 3, 0xA8: 2, 0xA9: 2, 0xAA: 2,
        0xAC: 4, 0xAD: 4, 0xAE: 4, 0xB0: 2, 0xB1: 5, 0xB4: 4, 0xB5: 4, 0xB6: 4,
        0xB8: 2, 0xB9: 4, 0xBA: 2, 0xBC: 4, 0xBD: 4, 0xBE: 4, 0xC0: 2, 0xC4: 3,
        0xC5: 3, 0xC6: 5, 0xC8: 2, 0xC9: 2, 0xCA: 2, 0xCC: 4, 0xCD: 4, 0xCE: 6,
        0xD0: 2, 0xD8: 2, 0xE0: 2, 0xE4: 3, 0xE5: 3, 0xE6: 5, 0xE8: 2, 0xE9: 2,
        0xEA: 2, 0xEC: 4, 0xED: 4, 0xEE: 6, 0xF0: 2, 0xF8: 2,
    }
    return cycles_map.get(opcode, 3)


class C64Simulator:
    def __init__(self, prg: bytes = None, symbols=None):
        self.output_buffer = ""
        # C64 uses NMOS 6502
        self.sim = sim6502(variant="NMOS", symbols=symbols)
        self.dis = dis6502(self.sim.memory_map._memory_map, symbols=symbols)
        self.history = []
        self.max_history = 100
        self.total_cycles = 0

        if prg:
            self.load_prg(prg)

    def load_prg(self, prg: bytes):
        if len(prg) < 2:
            return
        load_addr = prg[0] + (prg[1] << 8)
        data = prg[2:]
        self.sim.memory_map.InitializeMemory(load_addr, data)
        if load_addr == 0x0801:
            self.sim.pc = 0x080D
        else:
            self.sim.pc = load_addr

    def step(self):
        pc = self.sim.pc

        # Increment total cycles based on opcode
        opcode = self.sim.memory_map.Execute(pc % 65536)
        self.total_cycles += get_opcode_cycles(opcode)

        # Disassemble for history
        line, length = self.dis.disassemble_line(pc)
        self.history.append({
            "pc": pc,
            "line": line,
            "registers": {
                "a": self.sim.a,
                "x": self.sim.x,
                "y": self.sim.y,
                "sp": self.sim.sp,
                "flags": self.sim.cc
            }
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Kernal Traps
        if pc == 0xFFD2: # CHROUT
            # Skip disassembly entry for Kernal trap to avoid "brk" showing up
            if self.history:
                self.history.pop()
            char = self.sim.a
            # Convert PETSCII to ASCII roughly for now
            if char == 0x0D:
                self.output_buffer += "\n"
            elif 32 <= char <= 126:
                self.output_buffer += chr(char)

            # RTS
            self.sim.pc = (self.sim.pulladdr() + 1) % 0x10000
            return True

        if pc == 0xFFE4: # GETIN
            # Simulate no key pressed
            self.sim.a = 0
            self.sim.set_z(True)
            self.sim.pc = (self.sim.pulladdr() + 1) % 0x10000
            return True

        try:
            self.sim.execute()
        except Exception as e:
            self.output_buffer += f"\n[Simulation Error: {e}]\n"
            return False

        return True

    def run(self, max_steps=10000):
        steps = 0
        while steps < max_steps:
            pc = self.sim.pc
            # Basic check for end of program (RTS at top level or BRK)
            # Use % 65536 to be safe
            opcode = self.sim.memory_map._memory_map[pc % 65536]

            # Kernal Traps are not real opcodes in our memory map usually
            if pc >= 0xFF00:
                 if not self.step():
                     break
                 steps += 1
                 continue

            if opcode == 0x60 and self.sim.sp == 0xFF: # RTS at start
                break
            if opcode == 0x00: # BRK
                break

            if not self.step():
                break
            steps += 1
        return steps
