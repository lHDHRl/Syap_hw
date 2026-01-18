from lexer.tokenizer import GoLexer
from parser.go_parser import GoParser
from translator.python_emitter import PythonEmitter

def process_file(filename):
    with open(filename, 'r') as f:
        source_code = f.read()

    print("=" * 80)
    print(f"ОБРАБОТКА ФАЙЛА: {filename}")
    print("=" * 80)
    print("ИСХОДНЫЙ GO КОД:")
    print("-" * 80)
    print(source_code)
    print()

    print("=" * 80)
    print("ЭТАП 1: ТОКЕНИЗАЦИЯ")
    print("=" * 80)
    lexer = GoLexer(source_code)
    tokens = lexer.tokenize()

    for i, token in enumerate(tokens[:20]):
        print(token)
    if len(tokens) > 20:
        print(f"... и еще {len(tokens) - 20} токенов")
    print()

    print("=" * 80)
    print("ЭТАП 2: ПАРСИНГ (AST)")
    print("=" * 80)
    parser = GoParser(tokens)
    try:
        ast = parser.parse()
        print(f"Успешно спарсено {len(ast)} узлов AST:")
        for i, node in enumerate(ast):
            print(f"{i+1}. {node.__class__.__name__}")
        print()
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()
        return

    print("=" * 80)
    print("ЭТАП 3: ТРАНСЛЯЦИЯ В PYTHON")
    print("=" * 80)
    try:
        emitter = PythonEmitter()
        python_code = emitter.translate(ast)

        print(python_code)
        print()

        suffix = filename.replace('tests/test', '').replace('.go', '')
        output_filename = f'output{suffix}.py'
        with open(output_filename, 'w') as f:
            f.write(python_code)
        print(f"✓ Результат сохранен в {output_filename}")

    except Exception as e:
        print(f"Ошибка трансляции: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("=" * 80)
    print(f"ТРАНСЛЯЦИЯ ФАЙЛА {filename} ЗАВЕРШЕНА")
    print("=" * 80)
    print()

process_file('tests/test.go')
process_file('tests/test2.go')
process_file('tests/test3.go')
