from enum import Enum

from enum import Enum

class Opcode(Enum):
    LOADI = (1, 2)
    ADD = (2, 3)
    MOV = (3, 2)
    MOD = (4, 3)
    JZ = (5, 2)
    SUB = (6, 3)
    JUMP = (7, 1)
    WRITE_PORT = (8, 1)
    READ_PORT = (9, 1)
    NOP = (10, 0)
    CONST = (11, 2)  # Новая команда CONST для работы с памятью
    LOADMEMORY = (12, 2)  # Новая команда для загрузки из памяти в регистр

    def __init__(self, code, num_operands):
        self.code = code
        self.num_operands = num_operands

    @property
    def operand_count(self):
        return self.num_operands


class OpcodeOperandsType(Enum):
    """Перечисление для типов операндов."""
    NONE = 1
    ONE = 2
    TWO = 3
    THREE = 4


class Instruction:
    """Структурное представление инструкции."""

    def __init__(self, opcode: Opcode, operands_type: OpcodeOperandsType, operands: list[int]):
        self.opcode: Opcode = opcode
        self.operands_type: OpcodeOperandsType = operands_type
        self.operands: list[int] = operands

    def __repr__(self):
        operands: list[str] = list(map(lambda it: str(it), self.operands))
        return "opcode={} operands_type={} operands={}".format(self.opcode.name, self.operands_type.name, operands)