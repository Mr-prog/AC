from isa import Opcode, OpcodeOperandsType, Instruction
import re

class Translator:
    def __init__(self):
        self.label_map = {}
        self.instructions = []
        self.current_instruction_index = 0  # Для правильного индекса команд

    def remove_comments(self, line: str) -> str:
        return line.split(';', 1)[0].strip()

    def remove_empty_lines(self, lines: list[str]) -> list[str]:
        return [line for line in lines if line.strip()]

    def find_labels(self, lines: list[str]):
        """Сбор меток и привязка их к индексам команд"""
        for line in lines:
            if ':' in line:
                label, instruction = line.split(':', 1)
                self.label_map[label.strip()] = self.current_instruction_index
                if instruction.strip():  # Если после метки есть команда, увеличиваем индекс
                    self.current_instruction_index += 1
            else:
                self.current_instruction_index += 1  # Увеличиваем индекс для команды

    def process_labels(self, lines: list[str]):
        """Обработка инструкций и замена меток на их индексы"""
        for line in lines:
            if ':' in line:
                _, line = line.split(':', 1)  # Пропускаем метку, если она есть

            if not line.strip():  # Пропускаем пустые строки
                continue

            parts = re.findall(r'"[^"]*"|\w+', line)
            opcode = Opcode[parts[0]]
            operands = parts[1:]

            # Проверка количества операндов
            if len(operands) != opcode.operand_count:
                raise ValueError(f"Ошибка: Операция {opcode.name} требует {opcode.operand_count} операндов, "
                                 f"но было передано {len(operands)}.")

            # Замена меток на номера строк
            new_operands = []
            for op in operands:
                if op.startswith('"') and op.endswith('"'):
                    # Это строка, оставляем её как есть
                    new_operands.append(op.strip('"'))
                elif op.isdigit():
                    # Это число, преобразуем его
                    new_operands.append(int(op))
                else:
                    # Это метка или регистр, заменяем метку на её индекс
                    new_operands.append(self.label_map.get(op, op))

            # Определение типа операндов
            if opcode.operand_count == 3:
                operands_type = OpcodeOperandsType.THREE
            elif opcode.operand_count == 2:
                operands_type = OpcodeOperandsType.TWO
            elif opcode.operand_count == 1:
                operands_type = OpcodeOperandsType.ONE
            else:
                operands_type = OpcodeOperandsType.NONE

            self.instructions.append(Instruction(opcode, operands_type, new_operands))

    def translate(self, asm_code: list[str]) -> list[Instruction]:
        """Основной метод перевода: удаление комментариев, сбор меток и перевод команд"""
        # Удаление комментариев и пустых строк
        cleaned_code = self.remove_empty_lines([self.remove_comments(line) for line in asm_code])

        # Первый проход: сбор меток
        self.find_labels(cleaned_code)

        # Второй проход: обработка инструкций и замена меток на адреса
        self.process_labels(cleaned_code)

        return self.instructions
