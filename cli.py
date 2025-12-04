import argparse
from ecoscript import tokenizer
from ecoscript.parser import parse_source
from ecoscript.evaluator import Evaluator

def run_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    ev = Evaluator()
    ev.run_source(src)

def repl():
    ev = Evaluator()
    print('EcoScript REPL (type "exit" to quit)')
    buf = ''
    while True:
        try:
            line = input('> ')
        except EOFError:
            break
        if line.strip() == 'exit':
            break
        buf += line + '\n'
        # try to parse and run
        try:
            tree = parse_source(buf)
            ev.eval(tree)
            buf = ''
        except Exception as e:
            # wait for more input or print error
            if 'Unexpected EOF' in str(e) or 'in block' in str(e):
                continue
            print('Error:', e)
            buf = ''

def main():
    parser = argparse.ArgumentParser(prog='es')
    parser.add_argument('file', nargs='?', help='EcoScript file to run')
    args = parser.parse_args()
    if args.file:
        run_file(args.file)
    else:
        repl()

if __name__ == '__main__':
    main()
