import logging
import os
import tempfile

import pytest

# Добавляем импорт вашего модуля translator и machine
import translator  # убедитесь, что путь к модулю правильный
import machine

@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.src")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.o")
        target_code = os.path.join(tmpdirname, "target_code.mnemonics")
        print(source, input_stream, target)

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        # Чтение и перевод исходного кода
        with open(source, "r", encoding="utf-8") as asm_file:
            asm_code = asm_file.readlines()

        # Запускаем переводчик
        translator_instance = translator.Translator(asm_code)
        data, instructions = translator_instance.translate()

        # Симуляция машины с инструкциями
        with open(input_stream, "r", encoding="utf-8") as input_file:
            file_contents = input_file.read()
            input_data = translator_instance.parse_input_stream(file_contents)               
        output, instr_counter, mnemonic = machine.simulation(data, instructions, input_data, 100000)

        # Записываем результат в выходной файл
        with open(target, "w", encoding="utf-8") as file:
            file.write(output)

        with open(target_code, "w", encoding="utf-8") as file:
            file.write(mnemonic)     
            
        # Проверяем результат работы
        with open(target, encoding="utf-8") as file:
            code = file.read()

        with open(target_code, encoding="utf-8") as file:
            outcode = file.read()

        # Проверка соответствия данных
        assert code == golden["out_stdout"]
        assert caplog.text == golden["out_log"]
        assert outcode == golden["out_code"]