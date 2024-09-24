import logging
from isa import Opcode, Instruction

class ALU:
    def __init__(self):
        self.result = 0
        self.ZN = 0

    def set_result(self, result: int):
        self.result = result

    def set_flag(self, res):
        if (res <= 0):
            self.ZN = 1 
        else:
            self.ZN = 0

    """Арифметико-логическое устройство (ALU) для выполнения операций."""
    def exec_operation(self, op1: int, op2: int, opcode):
        try:
            num1 = int(op1)  # Преобразуем строку в число
            num2 = int(op2)  # Преобразуем строку в число
        except ValueError:
            raise ValueError(f"Ошибка: операнды '{op1}' или '{op2}' не являются числами.")
        if opcode == Opcode.ADD:
            self.set_flag(num1 + num2)
            return str(num1 + num2) 
        elif opcode == Opcode.SUB:
            self.set_flag(num1 - num2)
            return str(num1 - num2)  
        elif opcode == Opcode.MOD:
            self.set_flag(num1 % num2)
            return str(num1 % num2)  
        else:
            raise NotImplementedError(f"Операция {opcode} не поддерживается ALU.")

class DataMemory:
    def __init__(self):
        self.memory = dict()


class RegFile:
    """Класс для управления регистрами."""
    def __init__(self):
        self.op1: str = ""  
        self.op2: str = ""  
        self._valued_regs: dict[int, str] = {i: "" for i in range(16)} 
        self._valued_regs[0] = "0"

    def choice_ops(self, op1_reg_num: int, op2_reg_num: int):
        self.op1 = self._valued_regs.get(op1_reg_num, "")
        self.op2 = self._valued_regs.get(op2_reg_num, "")

    def set_reg_value(self, reg_num: int, value: str):
        if reg_num in self._valued_regs:
            self._valued_regs[reg_num] = value

    def get_all_regs(self) -> dict[int, str]:
        return self._valued_regs 

    def put_on_output(self, reg_num: int):
        reg = self.get_all_regs().get(reg_num)
        return reg

    def write_reg(self, reg_num: int, value: str):
        if reg_num in self._valued_regs:
            self._valued_regs[reg_num] += str(value) 

class DataPath:
    """Модуль данных, связывающий ALU и регистры."""
    def __init__(self):
        self.reg_file = RegFile()
        self.alu = ALU()
        self.data_mem = DataMemory()
        self.input_stream = []  
        self.output_stream = []  

    def latch_res(self, reg_num: int, result: str):
        self.reg_file.set_reg_value(reg_num, result)

    def read_in_reg(self, st: str):
        self.reg_file.write_reg(4, st)

    def latch_alu(self, res: int):
        self.alu.set_result(str(res))

    def store_in_memory(self, mem_key: str, value: str):
        self.data_mem[mem_key] = value

    def load_from_memory(self, mem_key: str):
        return self.data_mem.get(mem_key, "")

    def output_write(self, reg: int):
        out = self.reg_file.put_on_output(reg)
        for i in out:
            self.output_stream.append(i)

    def read_input(self):
        for i in self.input_stream:
            self.read_in_reg(i)


class ControlUnit:
    """Управляющее устройство."""
    def __init__(self, data_path: DataPath, instruction: Instruction):
        self.data_path = data_path
        self.program_counter = 0
        self.instructions = instruction

    def exec_add(self, reg1: int, reg2: int, reg_res: int):
        reg_num_1 = int(reg1[1:])
        reg_num_2 = int(reg2[1:])
        reg_res = int(reg_res[1:])
        self.data_path.reg_file.choice_ops(reg_num_1, reg_num_2)
        result = str(self.data_path.alu.exec_operation(int(self.data_path.reg_file.op1), int(self.data_path.reg_file.op2), Opcode.ADD))
        self.data_path.latch_res(reg_res, result)
        self.program_counter += 1

    def exec_sub(self, reg1: int, reg2: int, reg_res: int):
        reg_num_1 = int(reg1[1:])
        reg_num_2 = int(reg2[1:])
        reg_res = int(reg_res[1:])
        self.data_path.reg_file.choice_ops(reg_num_1, reg_num_2)
        result = str(self.data_path.alu.exec_operation(int(self.data_path.reg_file.op1), int(self.data_path.reg_file.op2), Opcode.SUB))
        self.data_path.latch_res(reg_res, result)
        self.program_counter += 1

    def exec_mod(self, reg1: int, reg2: int, reg_res: int):
        reg1 = int(reg1[1:])
        reg2 = int(reg2[1:])
        reg_res = int(reg_res[1:])
        self.data_path.reg_file.choice_ops(reg1, reg2)
        result = str(self.data_path.alu.exec_operation(int(self.data_path.reg_file.op1), int(self.data_path.reg_file.op2), Opcode.MOD))
        self.data_path.latch_res(reg_res, result)
        self.program_counter += 1

    def exec_jz(self, label: int):
        if (self.data_path.alu.ZN):
            self.exec_jump(label)
        else:
            self.program_counter += 1

    def exec_jump(self, label: int):
        self.data_path.reg_file.choice_ops("0", "0")
        self.data_path.latch_alu(self.data_path.alu.exec_operation(0, label, Opcode.ADD))
        self.program_counter = int(self.data_path.alu.result)

    def exec_write_port(self, reg: int):
        reg = int(reg[1:])
        self.data_path.output_write(reg)
        self.program_counter += 1

    def exec_read_port(self):
        self.data_path.read_input()
        self.program_counter += 1

    def exec_load_memory(self, mem_key: str, reg: int):
        reg_num = int(reg[1:])
        value = self.data_path.load_from_memory(mem_key)
        self.data_path.reg_file.write_reg(reg_num, value)
        self.program_counter += 1

    def execute_instruction(self):
        instruction = self.instructions[self.program_counter]
        opcode = instruction.opcode

        if opcode == Opcode.ADD:
            reg1, reg2, reg_res = instruction.operands
            self.exec_add(reg1, reg2, reg_res)

        elif opcode == Opcode.SUB:
            reg1, reg2, reg_res = instruction.operands
            self.exec_sub(reg1, reg2, reg_res)

        elif opcode == Opcode.MOD:
            reg, mod_val, reg_res = instruction.operands
            self.exec_mod(reg, mod_val, reg_res)

        elif opcode == Opcode.JZ:
            label = instruction.operands[0]
            self.exec_jz(label)

        elif opcode == Opcode.JUMP:
            label = instruction.operands[0]
            self.exec_jump(label)

        elif opcode == Opcode.WRITE_PORT:
            reg = instruction.operands[0]
            self.exec_write_port(reg)

        elif opcode == Opcode.READ_PORT:
            self.exec_read_port()

        elif opcode == Opcode.NOP:
            raise StopIteration()

        elif opcode == Opcode.LOADMEMORY:
            mem_key, reg = instruction.operands
            self.exec_load_memory(mem_key, reg)
        else:
            raise NotImplementedError(f"Неизвестная команда: {opcode}")

    def __repr__(self):
        reg_values = [self.data_path.reg_file.get_all_regs().get(i, "") for i in range(16)]
        reg_str = ", ".join(f"REG{i}: {val}" for i, val in enumerate(reg_values))
        state = f"{{PC: {self.program_counter}, {reg_str}, OUTPUT_PORT: {self.data_path.output_stream}}}"
        instr = self.instructions[self.program_counter]
        opcode = instr.opcode
        args = instr.operands
        action = f"{opcode.name} {args}"

        return f"{action} {state}"

    def short_repr(self):
        """Краткий вывод для print()."""
        instr = self.instructions[self.program_counter]
        opcode = instr.opcode
        args = instr.operands
        return f"Instruction counter: {instr_counter}, {opcode.name} {args}"
    
def simulation(data: dict, instructions: list, input_stream: list[str], limit: int) -> tuple[str, int]:
    data_path = DataPath()
    control_unit = ControlUnit(data_path, instructions)
    control_unit.data_path.input_stream = input_stream
    control_unit.data_path.data_mem = data

    global instr_counter
    instr_counter = 0
    mnemonic = []

    try:
        while instr_counter < limit:
            logging.debug('%s', control_unit)  # Отладочная печать состояния машины
            print(control_unit.short_repr())  # Добавим вывод состояния машины для каждого шага
            mnemonic.append(control_unit.short_repr())  # Добавляем инструкцию в список
            control_unit.execute_instruction()
            instr_counter += 1
    except StopIteration:
        pass
    return ''.join(control_unit.data_path.output_stream), instr_counter, '\n'.join(mnemonic) + "\n"

