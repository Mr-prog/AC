from isa import Opcode
from isa import OpcodeOperandsType
from isa import Instruction
class Translator:
    def __init__(self, asm_code: list[str]):
        self.asm_code = asm_code
        self.labels = {}
        self.instructions = []
        self.data = {}
        self.input_stream = []
        self.init_data = []
        self.section_data_found = False
        self.section_programm_found = False
    
    def _remove_comments_and_empty_lines(self):
        """Удаляет комментарии и пустые строки."""
        clean_code = []
        for line in self.asm_code:
            clean_line = line.split(';')[0].strip()  
            if clean_line:
                clean_code.append(clean_line)
        self.asm_code = clean_code
    
    def _parse_labels(self):
        """Находит метки в секции программы и заменяет их на индексы."""
        instruction_counter = 0
        for i, line in enumerate(self.asm_code):
            if ":" in line:
                label = line.split(":")[0].strip()
                self.labels[label] = instruction_counter  
                self.asm_code[i] = line.split(":")[1].strip()
            if self.asm_code[i]:
                instruction_counter += 1
    
    def _parse_instructions(self):
        """Парсит инструкции в секции программы, заменяя метки на индексы."""
        for line in self.asm_code:
            if line and not line.startswith("section_"):  
                parts = line.split()
                opcode_str = parts[0]
                operands = parts[1:]
                operands = [self.labels.get(operand, operand) for operand in operands]
                operands = [int(op) if isinstance(op, str) and op.isdigit() else op for op in operands]
                opcode = Opcode[opcode_str.upper()]
                operands_type = OpcodeOperandsType(len(operands))
                instruction = Instruction(opcode, operands_type, operands)
                self.instructions.append(instruction)

    def _parse_data_section(self):
        for line in self.asm_code:
            if line.lower().startswith("section_data"):
                self.section_data_found = True
            elif line.lower().startswith("section_program"):
                break 
            elif self.section_data_found:
                line = line.strip()  
                if " $ " in line:
                    key, value = line.split(" $ ", 1)  
                    self.data[key.strip()] = value.strip()
                else:
                    raise ValueError(f"Неверный формат строки данных: '{line}'")

    
    def _parse_program_section(self):
        """Парсит секцию программ (section_programm)."""
        parsing_programm = False
        clean_program_code = []
        for line in self.asm_code:
            if line.lower().startswith("section_program"):
                parsing_programm = True
                self.section_programm_found = True
                continue
            if parsing_programm:
                clean_program_code.append(line)
        self.asm_code = clean_program_code

    def parse_input_stream(self, input_stream_str: str):
        input_stream = [char.strip().strip('"') for char in input_stream_str.split(",")]
    
        return input_stream

    
    def translate(self):
        """Основной метод, вызываемый для выполнения всех этапов парсинга."""
        self._remove_comments_and_empty_lines()
        self._parse_data_section()  
        self._parse_program_section()  
        self._parse_labels()  
        self._parse_instructions()  

        return self.data, self.instructions
