import sys
import logging
from isa import Opcode, OpcodeOperandsType, Instruction

class ALU:
    """Арифметико-логическое устройство (ALU) для выполнения операций."""
    def exec_operation(self, op1: int, op2: int, opcode):
        try:
            num1 = int(op1)  # Преобразуем строку в число
            num2 = int(op2)  # Преобразуем строку в число
        except ValueError:
            raise ValueError(f"Ошибка: операнды '{op1}' или '{op2}' не являются числами.")
        if opcode == Opcode.ADD:
            return str(num1 + num2)  # Возвращаем результат как строку
        elif opcode == Opcode.SUB:
            return str(num1 - num2)  # Возвращаем результат как строку
        elif opcode == Opcode.MOD:
            return str(num1 % num2)  # Возвращаем результат как строку
        else:
            raise NotImplementedError(f"Операция {opcode} не поддерживается ALU.")

class RegFile:
    """Класс для управления регистрами."""
    def __init__(self):
        self.op1: str = ""  # Храним строки вместо целых чисел
        self.op2: str = ""  # Храним строки вместо целых чисел
        self._valued_regs: dict[int, str] = {i: "" for i in range(16)}  # Регистры хранят строки

    def choice_ops(self, op1_reg_num: int, op2_reg_num: int):
        self.op1 = self._valued_regs.get(op1_reg_num, "")
        self.op2 = self._valued_regs.get(op2_reg_num, "")

    def set_reg_value(self, reg_num: int, value: str):
        if reg_num in self._valued_regs:
            self._valued_regs[reg_num] = value

    def get_all_regs(self) -> dict[int, str]:
        return self._valued_regs

    def write_reg(self, reg_num: int, value: str):
        """Метод для записи строки в регистр."""
        if reg_num in self._valued_regs:
            self._valued_regs[reg_num] += str(value)  # Добавляем символ к существующему значению регистра

class DataPath:
    """Модуль данных, связывающий ALU и регистры."""
    def __init__(self):
        self.reg_file = RegFile()
        self.alu = ALU()
        self.output_port = ""  # Теперь строковый вывод
        self.input_stream = []  # Буфер для потока ввода
        self.output_stream = []  # Буфер для потока вывода
        self.memory = {}  # Память для хранения констант

    def latch_res(self, reg_num: int, result: str):
        self.reg_file.set_reg_value(reg_num, result)

    def store_in_memory(self, mem_key: str, value: str):
        self.memory[mem_key] = value

    def load_from_memory(self, mem_key: str):
        return self.memory.get(mem_key, "")

    def output_write(self, sig_output: bool):
        if sig_output:
            self.output_port = self.reg_file.op2  # Работаем со строками
            self.output_stream.append(self.output_port)  # Добавляем строку в поток вывода

    def read_input(self):
        if self.input_stream:
            return self.input_stream.pop(0)  # Чтение символа как строки
        return ""


class ControlUnit:
    """Управляющее устройство."""
    def __init__(self, data_path: DataPath, input_stream):
        self.data_path = data_path
        self.program_counter = 0
        self.instructions = []
        self.input_stream = input_stream  # Сохраняем входной поток

    def exec_loadi(self, value, reg):
        reg_num = int(reg[1:])  # Преобразуем R1 в 1 и так далее
        self.data_path.reg_file.write_reg(reg_num, value)
        print(f"LOADI: загружено значение {value} в регистр R{reg_num}")
        self.program_counter += 1

    def exec_add(self, reg1: int, reg2: int, reg_res: int):
        reg_num_1 = int(reg1[1:])
        reg_num_2 = int(reg2[1:])
        reg_res = int(reg_res[1:])
        self.data_path.reg_file.choice_ops(reg_num_1, reg_num_2)
        logging.debug("%s", str(self.data_path.reg_file.op1))
        logging.debug('%s', str(self.data_path.reg_file.op2))
        logging.debug('%s', str(self.data_path.reg_file._valued_regs[4]))
        result = str(self.data_path.alu.exec_operation(int(self.data_path.reg_file.op1), int(self.data_path.reg_file.op2), Opcode.ADD))
        self.data_path.latch_res(reg_res, result)
        self.program_counter += 1

    def exec_sub(self, reg1: int, reg2: int, reg_res: int):
        reg_num_1 = int(reg1[1:])
        reg_num_2 = int(reg2[1:])
        reg_res = int(reg_res[1:])
        self.data_path.reg_file.choice_ops(reg_num_1, reg_num_2)
        logging.debug("%s", str(self.data_path.reg_file.op1))
        logging.debug('%s', str(self.data_path.reg_file.op2))
        logging.debug('%s', str(self.data_path.reg_file._valued_regs[4]))
        result = str(self.data_path.alu.exec_operation(int(self.data_path.reg_file.op1), int(self.data_path.reg_file.op2), Opcode.SUB))
        self.data_path.latch_res(reg_res, result)
        self.program_counter += 1

    def exec_mov(self, src_reg: int, dest_reg: int):
        src_reg = int(src_reg[1:])
        dest_reg = int(dest_reg[1:])
        value = self.data_path.reg_file.get_all_regs().get(src_reg, "")
        self.data_path.reg_file.set_reg_value(dest_reg, value)
        self.program_counter += 1

    def exec_mod(self, reg: int, mod_val: int, reg_res: int):
        reg = int(reg[1:])
        reg_res = int(reg_res[1:])
        self.data_path.reg_file.choice_ops(reg, 0)
        result = str(self.data_path.alu.exec_operation(int(self.data_path.reg_file.op1), mod_val, Opcode.MOD))
        self.data_path.latch_res(reg_res, result)
        self.program_counter += 1

    def exec_jz(self, reg: int, label: int):
        reg = int(reg[1:])
        if int(self.data_path.reg_file.get_all_regs().get(reg, "0")) <= 0:
            self.program_counter = label
        else:
            self.program_counter += 1

    def exec_jump(self, label: int):
        self.program_counter = label

    def exec_write_port(self, reg, count=1):
        reg_num = int(reg[1:])
        for i in range(count):
            # Читаем символ из регистра и записываем в выходной поток
            value = self.data_path.reg_file.get_all_regs().get(reg_num + i, "")
            if value:  # Если регистр содержит символ
                self.data_path.output_stream.append(value)  # Добавляем символ в поток вывода
                print(f"Запись в порт: '{value}'")
            else:
                print(f"Ошибка: регистр R{reg_num + i} пуст.")
        self.program_counter += 1
    '''
    def exec_read_port(self, reg):
        reg_num = int(reg[1:])  # Получаем номер регистра

        if self.input_stream:  # Проверяем, есть ли данные во входном потоке
            token = self.input_stream.pop(0)  # Извлекаем символ из потока
            self.data_path.reg_file.write_reg(reg_num, token)  # Записываем символ в регистр
            print(f"Чтение из порта: '{token}' записано в регистр R{reg_num}")
        else:
            print(f"Ошибка: входной поток пуст при попытке записи в регистр R{reg_num}. Остановка.")
            raise StopIteration  # Останавливаем моделирование, если входной поток пуст

        self.program_counter += 1
    '''

    def exec_const(self, arg, value):
        self.data_path.store_in_memory(arg, value)
        self.program_counter += 1

    def exec_read_port(self, reg):
        reg_num = int(reg[1:])  # Получаем номер регистра

        # Читаем весь поток по одному символу и объединяем в строку
        collected_data = []
        while self.input_stream:  # Пока поток не пуст
            token = self.input_stream.pop(0)  # Извлекаем символ из потока
            collected_data.append(token)

        if collected_data:  # Если удалось собрать данные
            combined_data = ''.join(collected_data)  # Объединяем в строку
            self.data_path.reg_file.write_reg(reg_num, combined_data)  # Записываем строку в регистр
            print(f"Чтение из порта: '{combined_data}' записано в регистр R{reg_num}")
        else:
            print(f"Ошибка: входной поток пуст при попытке записи в регистр R{reg_num}. Остановка.")
            raise StopIteration  # Останавливаем моделирование, если входной поток пуст

        self.program_counter += 1

    def exec_load_memory(self, mem_key: str, reg: int):
        reg_num = int(reg[1:])
        value = self.data_path.load_from_memory(mem_key)
        logging.debug('%s', str(value))
        self.data_path.reg_file.write_reg(reg_num, value)
        self.program_counter += 1

    def exec_write_port(self, reg):
        reg_num = int(reg[1:])
        value = self.data_path.reg_file.get_all_regs().get(reg_num, "")
        self.data_path.output_stream.append(value)
        self.program_counter += 1


    def execute_instruction(self):
        instruction = self.instructions[self.program_counter]
        opcode = instruction.opcode

        if opcode == Opcode.LOADI:
            value, reg_num = instruction.operands
            self.exec_loadi(value, reg_num)

        elif opcode == Opcode.ADD:
            reg1, reg2, reg_res = instruction.operands
            self.exec_add(reg1, reg2, reg_res)

        elif opcode == Opcode.SUB:
            reg1, reg2, reg_res = instruction.operands
            self.exec_sub(reg1, reg2, reg_res)

        elif opcode == Opcode.MOV:
            src_reg, dest_reg = instruction.operands
            self.exec_mov(src_reg, dest_reg)

        elif opcode == Opcode.MOD:
            reg, mod_val, reg_res = instruction.operands
            self.exec_mod(reg, mod_val, reg_res)

        elif opcode == Opcode.JZ:
            reg, label = instruction.operands
            self.exec_jz(reg, label)

        elif opcode == Opcode.JUMP:
            label = instruction.operands[0]
            self.exec_jump(label)

        elif opcode == Opcode.WRITE_PORT:
            reg = instruction.operands[0]
            self.exec_write_port(reg)

        elif opcode == Opcode.READ_PORT:
            reg = instruction.operands[0]
            self.exec_read_port(reg)

        elif opcode == Opcode.NOP:
            raise StopIteration()

        elif opcode == Opcode.CONST:
            arg, value = instruction.operands
            self.exec_const(arg, value)

        elif opcode == Opcode.LOADMEMORY:
            mem_key, reg = instruction.operands
            self.exec_load_memory(mem_key, reg)
        else:
            raise NotImplementedError(f"Неизвестная команда: {opcode}")

    def __repr__(self):
        reg_values = [self.data_path.reg_file.get_all_regs().get(i, "") for i in range(16)]
        reg_str = ", ".join(f"REG{i}: {val}" for i, val in enumerate(reg_values))
        state = f"{{PC: {self.program_counter}, {reg_str}, OUTPUT_PORT: {self.data_path.output_port}}}"

        instr = self.instructions[self.program_counter]
        opcode = instr.opcode
        args = instr.operands
        action = f"{opcode.name} {args}"

        return f"{action} {state}"

def simulation(init_data: list[int], instructions: list, input_stream: list[str], limit: int) -> tuple[str, int]:
    data_path = DataPath()
    control_unit = ControlUnit(data_path, input_stream)
    control_unit.instructions = instructions
    data_path.input_stream = input_stream

    instr_counter = 0
    try:
        while instr_counter < limit:
            logging.debug('%s', control_unit)  # Отладочная печать состояния машины
            print(control_unit)  # Добавим вывод состояния машины для каждого шага
            control_unit.execute_instruction()
            instr_counter += 1
    except StopIteration:
        pass
    return ''.join(control_unit.data_path.output_stream), instr_counter



def deserialize_bin_lines_list(lines: list[str]) -> tuple[list[int], list[Instruction]]:
    init_data = []
    instructions = []

    for line in lines:
        parts = line.split()
        opcode = Opcode[parts[0]]
        operands_type = OpcodeOperandsType[parts[1]]
        operands = list(map(int, parts[2:]))
        instructions.append(Instruction(opcode, operands_type, operands))

    return init_data, instructions


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    code_file = sys.argv[1]
    bin_lines = open(code_file, 'r').read().splitlines()
    init_data, instructions = deserialize_bin_lines_list(bin_lines)
    input_stream = list("hello")
    output, instr_counter = simulation(init_data, instructions, input_stream, 100000)

    print(f"Output: {output}")
    print(f"Executed instructions: {instr_counter}")
