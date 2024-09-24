# AC

## csa_2024

### Автор

> Камянецький Никита Владимирович, P3208

### Вариант

> asm | risc | harv | hw | instr | struct | stram | port | pstr | prob2
>
> Без усложнения

### Описание варианта

- **asm** -- синтаксис ассемблера. Необходима поддержка label-ов.
- **risc** -- система команд должна быть упрощенной, в духе RISC архитектур:
  - стандартизированная длина команд.
  - операции над данными осуществляются только в рамках регистров.
  - доступ к памяти и ввод-вывод -- отдельные операции.
- **harv** -- Гарвардская архитектура:
  - в тестах необходимо привести/проверить как память команд, так и память данных.
- **hw (hardwired)** -- ContolUnit реализуется как часть модели.
- **instr** -- процессор необходимо моделировать с точностью до каждой инструкции (наблюдается состояние после каждой инструкции).
- **struct** -- машинный код в виде высокоуровневой структуры данных. Считается, что одна инструкция укладывается в одно машинное слово.
- **stream** -- вод-вывод осуществляется как поток токенов.
- **port (port-mapped)** -- (специальные инструкции для ввода-вывода).
  - адресация портов ввода-вывода должна присутствовать.
- **pstr (Length-prefixed / Pascal string)** -- перед строкой указывается её длина
- **prob2** -- Even Fibonacci numbers (сумма четных чисел Фибонначи, не превышающих 4 млн).

### Язык программирования

```ebnf
<program> ::= <section_data> <section_program> | <section_program> <section_data> | <section_program>

<section_data> ::= "section_data\n" <declaration_line>*

<section_program> ::= "section_program\n" <instruction_line>*

<declaration_line> ::= <data_label_name> "$" <value><comment>* "\n"

<instruction_line> ::= (<program_label> | <instruction>) <comment>* "\n"

<data_label_name> ::= [a-zA-Z]+

<value> ::= (<string> | <number>)

<string> ::= <Any UTF-8 string>

<number> ::=  [-2^31; 2^31 - 1]

<comment> ::= ";" <char>* "\n"

<program_label> ::= <program_label_name> ":"

<program_label_name> ::= [a-zA-Z]+

<instruction> ::=  <3_operand_instruction> | <2_operand_instruction> | <1_operand_instruction> | <0_operand_instruction>

<3_operand_instruction> ::= ("ADD" | "SUB" | "MOD") " " <reg_reg_reg_op_set>

<reg_reg_reg_op_set> ::= <register> " " <register> " " <register>

<2_operand_instruction> ::= "LOADMEMORY" " " <mem_key_reg_op_set>

<reg_mem_key_op_set> ::= <data_label_name> " " <register>

<1_operand_instruction> ::= ("JZ" | "JUMP" | "WRITE_PORT") " " <label_op_set>

<label_op_set> ::= <program_label_name>

<0_operand_instruction> ::= ("READ_PORT" | "NOP")

<register> ::= ("R0" | "R1" | "R2" | "R3" | "R4" | ... | "R15")

```

Декларации из **section_data** выполняются последовательно. Операции:

- `<data_label_name> $ <value>` -- записать _value_ в ячейку памяти _data_label_name_;

Поддерживаемые аргументы:

- для аргументов **number** число в диапазоне [-2^31; 2^31 - 1]
- для аргументов **string** строка, длина которой в диапозоне [-2^31; 2^31 - 1]

Код из **section_text** выполняется последовательно. Операции:

- `ADD <reg1> <reg2> <reg_res>` -- прибавить `reg2` к регистру `reg1` и записать в регистр `reg_res`
- `SUB <reg1> <reg2> <reg_res>` -- вычесть `reg2` из регистра `reg1` и записать в регистр `reg_res`
- `MOD <reg1> <reg2> <reg_const>` -- записать остаток от деления регистра `reg1` на `reg2` в регистр `reg_const`
- `JUMP <program_label>` -- безусловный переход на метку `program_label`
- `JZ <program_label>` -- переход на метку `program_label`, если флаг ZN = 1
- `WRITE_PORT <reg1>` -- распечатать в поток вывода значение из `<reg1>`
- `READ_PORT` -- прочитать в `R4` значение из потока ввода
- `LOADMEMORY <mem_key> <reg1>` -- прочитать в `reg1` значение из памяти данных по адресу `mem_key`
- `NOP` -- завершить выполнение программы

Поддерживаемые аргументы:

- для аргументов **reg[1-2]** регистры `reg[0-3;5-15]`
- для аргeментов **reg_res** регистр из `reg[1-3;5-15]`
- для аргументов **program_label** имя метки, определённой в блоке кода
- для аргументов **mem_key** имя метки, определённой в блоке данных

Дополнительные конструкции:

- `; <any sequence>` - комментарий
- `section_program` - объявление секции кода
- `section_data` - объявление секции данных
- `<label>:` - метки для переходов / названия переменных
- `<mem_key> $ <value>` - обьявление области памяти и значения

Примечания:

- Исполнение кода начинается с первой инструкции в section_program
- При введение других инструкций поведение не специфицируется и вызывает ошибку трансляции.
- Запсь данных начинается с section_data

### Организация памяти

Модель памяти процессора:

1. Память команд. Машинное слово -- длина не определена.
2. Память данных. Машинное слово -- целое числовое неотрицательное значение.

Типы адресации:

1. Абсолютная - используется для адресации в памяти данных

## Система команд

Особенности процессора:

- Машинное слово -- длина машинного слова не определена
- Регистры:
  - управляются с помощью устройства RegFile (регистровый файл)
  - RegFile может принимать сигналы op1, op2, res, out
  - сигнал op1 - значение какого регистра будет передано на шину op1
  - сигнал op2 - значение какого регистра будет передано на шину op2
  - сигнал res - в какой регистр запишется значение с шины res_data
  - сигнал out - с какого регистра будут считаны данные в out_port
  - обработка сигналов op1 и op2 и передача занчений на шину происходит в рамках одного такта
  - обработка сигнала res и сохранение значение с шины res_data требует защёлкивания регистра
  - всего 16 регистров: R0, R1, R2, R3, ... R15
  - R0 - hardware_zero (всегда содержит значение 0)
  - R4 - hardwire_input (в него всегда считываются данные)
- Память данных:
  - адресуется через разультат выполнения выражения на алу;
  - может быть прочитана в регистр, обозначенный как res в регистровом файле;
- АЛУ:
  - на **_левый_** вход алу подаётся регистр op1 из регистрового файла
  - на **_правый_** вход алу подаётся регистр op1 из регистрового файла
  - АЛУ поддерживает операции: ADD, SUB, MOD
  - любая операция на АЛУ выставляет флаг ZN в 1 или 0
- Ввод-вывод -- порты ввода/вывода, токенизирован, символьный
- `program_counter` -- счётчик команд:
  - инкрементируется после каждой инструкции или перезаписывается инструкцией перехода.

### Набор инструкций

Более подробное описание команд в пункте **Язык программирования**
Набор инструкций соответствует основным принципам RISC-архитектуры

- `ADD <reg1> <reg2> <reg_res>` -- 1 такт
- `SUB <reg1> <reg2> <reg_res>` -- 1 такт
- `MOD <reg1> <reg2> <reg_res>` -- 1 такт
- `JUMP <program_label>` -- 1 такт
- `JZ <program_label>` -- 1 такт
- `WRITE_PORT <reg>` -- 1 такт
- `READ_PORT` -- 1 такт
- `LOADMEMORY <mem_key> <reg1>` -- 1 такт
- `NOP` -- 1 такт

### Кодирование инструкций

- Машинный код сериализуется в обьект типа Insruction.
- Один обьект - одна инструкция

Пример инструкции:

```
    def __init__(self, opcode: Opcode, operands_type: OpcodeOperandsType, operands: list[int]):
        self.opcode: Opcode = opcode
        self.operands_type: OpcodeOperandsType = operands_type
        self.operands: list[int] = operands
```

Типы данные в модуле [isa](src/isa.py), где:

- `Opcode` -- перечисление кодов операций и возможных для них наборов аргументов;
- `OpcodeOperandsType` -- перечисление возможных наборов аргументов для операций;
- `Instruction` -- структура для хранения информации о типе операции, её наборе аргументов и их типе

## Транслятор

Реализовано в модуле: [translation](./translation.py)

Этапы трансляции (функция `translate`):

1. удаление все пустых строк и комментариев
2. формирование списка данных из section_data
3. формирование списка команд из section_program
4. замена label на их индексы
5. создание списка инструкций (структура для хранения типа операции, типа набора её операндов, занчений операндов в
   наборе)

Правила генерации машинного кода:

- одна инструкция процессора -- одна инструкция в коде;
- инструкция и все её операнды хранятся в одном машинном слове
- команды из **section_data** используются для заполнения памяти данных;
- запись в память данных происходит начиная с первой команды из **section_data**
- запись в память команд происходит начиная с первой команды из **section_program**;

## Модель процессора

Реализовано в модуле: [machine](src/machine.py).
Процессор разработан с целью соответсвовать RISC-архитектуре исполняемых на нём команд.

### Схема Datapath и Control_unit

![Схема datapath](https://github.com/Mr-prog/AC/raw/main/img/Datapath.png)
![Схема control_unit](https://github.com/Mr-prog/AC/raw/main/img/Control_unit.png)

### DataPath

Реализован в классе `DataPath`.

- `data_memory` -- однопортовая, read_only.
  - `data_mem.res` -- результат чтения из памяти сохраняется сюда и подаётся на шину res_data
- `input` -- вызовет остановку процесса моделирования, если буфер входных значений закончился.
- `reg_file` -- регистровый файл, устройство с помощью сигналов op1, op2, res, out манипулирующее регистрами reg0-reg15
  - `reg_file.op1` - регистр, данные из которого идут на правый вход алу
  - `reg_file.op2` - регистр, данные из которого идут на левый вход алу
  - `reg_file.res` - регистр, в который будут записаны данные с алу
  - `reg_file.out` - регистр, с которого данные идут на out
- `alu` -- выполняет арифметические операции
  - `alu.left` -- левые вход АЛУ
  - `alu.right` -- правый вход АЛУ
  - `alu.res` -- результат выполнения арифметической операции на АЛУ
  - `alu.zn` -- флаг значения меньшего или равного нулю
- `control_unit` - модуль управления работой процессора
  - `control_unit.const` - константа, которая может быть принята как один из операндов в АЛУ с использованием сигнала sig_const

Сигналы:

- `sig_const` - если пришёл, то на левый вход алу идёт константа из control unit, нет - значение из reg_file.op2
- `sig_read` - сигнал на получение данных из памяти, если не пришёл, то на шину res_data поступает значение alu.res
- `sig_input` - сигнал на чтение из input_buffer (порта ввода), если не приходит, то данные на шине res_data не изменяются

Сигналы RegFile:

- `op1` - указатель значение какого регистра следует передать на reg_file.op1
- `op2` - указатель значение какого регистра следует передать на reg_file.op2
- `res` - указатель в какой регистр нужно записать данные с шины res_data
- `out` - указатель, с какого регистра будут считаны данные

Флаги:

- `zn` -- отражает наличие нулевого или отрицательного значения в алу.

### ControlUnit

Реализован в классе `ControlUnit`.

- Hardwired (реализовано полностью на python).
- Моделирование на уровне инструкций.
- Трансляция инструкции в последовательность сигналов: `decode_and_execute_instruction`.

Сигнал:

- `latch_program_counter` -- сигнал для обновления счётчика команд в ControlUnit.
- `sig_next` - если пришёл, то PC - итерируется, нет - заменяет значение на новое (ветвление)
  Особенности работы модели:

- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования ограничено hardcoded константой.
- Остановка моделирования осуществляется при помощи исключений:
  - `StopIteration` -- если выполнена инструкция `NOP`.
- Управление симуляцией реализовано в функции `simulate`.

## Апробация

В качестве интеграционных тестов реализовано 4 алгоритма:

1. [hello world](files/helloworld.asm).
2. [cat](files/cat.asm) -- программа `cat`, повторяем ввод на выводе.
3. [hello username](files/hello_username.asm) -- запрос имени у пользователя, его считывание и вывод на экран
4. [prob2](files/alg.asm) -- рассчитать сумму всех чётных чисел Фибоначчи до 4000000

Интеграционные тесты реализованы в файле [integration_test](integration_test.py)

CI:

```yaml
name: Python CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff

      - name: Run Ruff
        run: ruff check
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install pytest
        run: |
          pip install pytest-golden
          pip install pytest
      - name: Run tests
        run: pytest
```

где:.

- `pytest` -- утилита для запуска тестов.
- `pytest-golden` -- утилита для запуска golden тестов
- `ruff` -- утилита для проверки качества кода. Некоторые правила отключены в отдельных модулях с целью упрощения
  кода.

Пример использования и журнал работы процессора на примере `cat`:

```
PS B:\ITMO\Course2\AC\files> cat cat.txt
  section_program
  start:
    READ_PORT
    WRITE_PORT R4
    NOP
PS B:\ITMO\Course2\AC> pytest -r P
C:\Users\miste\AppData\Local\Temp\tmpn00j1y0x\source.src C:\Users\miste\AppData\Local\Temp\tmpn00j1y0x\input.txt C:\Users\miste\AppData\Local\Temp\tmpn00j1y0x\target.o
Instruction counter: 0, READ_PORT []
Instruction counter: 1, WRITE_PORT ['R4']
Instruction counter: 2, NOP []
-------------------------------------------------- Captured log call --------------------------------------------------
DEBUG    root:machine.py:233 READ_PORT [] {PC: 0, REG0: 0, REG1: , REG2: , REG3: , REG4: , REG5: , REG6: , REG7: , REG8: , REG9: , REG10: , REG11: , REG12: , REG13: , REG14: , REG15: , OUTPUT_PORT: []}
DEBUG    root:machine.py:233 WRITE_PORT ['R4'] {PC: 1, REG0: 0, REG1: , REG2: , REG3: , REG4: Cat, REG5: , REG6: , REG7: , REG8: , REG9: , REG10: , REG11: , REG12: , REG13: , REG14: , REG15: , OUTPUT_PORT: []}
DEBUG    root:machine.py:233 NOP [] {PC: 2, REG0: 0, REG1: , REG2: , REG3: , REG4: Cat, REG5: , REG6: , REG7: , REG8: , REG9: , REG10: , REG11: , REG12: , REG13: , REG14: , REG15: , OUTPUT_PORT: ['C', 'a', 't']}
```

| ФИО                             | алг.           | LoC | code инстр. | инстр. | вариант                                             |
| ------------------------------- | -------------- | --- | ----------- | ------ | --------------------------------------------------- |
| Камянецький Никита владимирович | hello          | 10  | 5           | 4      | asm risc harv hw instr struct stram port pstr prob2 |
| Камянецький Никита владимирович | cat            | 5   | 3           | 3      | asm risc harv hw instr struct stram port pstr prob2 |
| Камянецький Никита владимирович | prob2          | 29  | 23          | 290    | asm risc harv hw instr struct stram port pstr prob2 |
| Камянецький Никита владимирович | hello_username | 15  | 9           | 8      | asm risc harv hw instr struct stram port pstr prob2 |
