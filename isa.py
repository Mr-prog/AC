from enum import Enum


class Opcode(Enum):
    ADD = (2, 3)
    MOD = (4, 3)
    JZ = (5, 2)
    SUB = (6, 3)
    JUMP = (7, 2)
    WRITE_PORT = (8, 2)
    READ_PORT = (9, 1)
    NOP = (10, 1)
    LOADMEMORY = (12, 3)  
    
    def __init__(self, code, num_operands):
        self.code = code
        self.num_operands = num_operands

    @property
    def operand_count(self):
        return self.num_operands


class OpcodeOperandsType(Enum):
    """Перечисление для типов операндов."""
    NONE = 0
    ONE = 1
    TWO = 2
    THREE = 3


class Instruction:
    """Структурное представление инструкции."""

    def __init__(self, opcode: Opcode, operands_type: OpcodeOperandsType, operands: list[int]):
        self.opcode: Opcode = opcode
        self.operands_type: OpcodeOperandsType = operands_type
        self.operands: list[int] = operands

    def __repr__(self):
        operands: list[str] = list(map(lambda it: str(it), self.operands))
        return "opcode={} operands_type={} operands={}".format(self.opcode.name, self.operands_type.name, operands)