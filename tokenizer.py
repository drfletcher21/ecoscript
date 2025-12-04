import re

# We'll tokenize line-by-line and emit INDENT/DEDENT/NEWLINE tokens similar to Python's tokenizer.
TOKEN_SPEC = [
    ('NUMBER',   r"\d+(?:\.\d+)?"),
    # string can be double-quoted or single-quoted, allow escaped chars
    ('STRING',   r'\"(?:\\.|[^"\\])*\"|\'(?:\\.|[^\'\\])*\''),
    ('IDENT',    r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP',       r'==|!=|<=|>=|&&|\|\||[+\-*/%<>!=]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('COMMA',    r','),
    ('SEMICOL',  r';'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.'),
]

MASTER_RE = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))
KEYWORDS = {'let','var','const','function','return','if','else','while','for','print','true','false','else'}


class Token:
    def __init__(self, type_, value, lineno, col):
        self.type = type_
        self.value = value
        self.lineno = lineno
        self.col = col
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.lineno}, {self.col})"


def _tokenize_line(line, lineno, line_offset=0):
    tokens = []
    pos = 0
    while pos < len(line):
        m = MASTER_RE.match(line, pos)
        if not m:
            break
        kind = m.lastgroup
        value = m.group()
        col = pos + 1
        pos = m.end()
        if kind == 'NUMBER':
            if '.' in value:
                val = float(value)
            else:
                val = int(value)
            tokens.append(Token('NUMBER', val, lineno, col))
        elif kind == 'STRING':
            # strip surrounding quotes and decode escapes
            val = value[1:-1]
            val = bytes(val, 'utf-8').decode('unicode_escape')
            tokens.append(Token('STRING', val, lineno, col))
        elif kind == 'IDENT':
            if value in KEYWORDS:
                tokens.append(Token(value.upper(), value, lineno, col))
            else:
                tokens.append(Token('IDENT', value, lineno, col))
        elif kind == 'OP':
            tokens.append(Token('OP', value, lineno, col))
        elif kind in ('LPAREN','RPAREN','LBRACE','RBRACE','COMMA','SEMICOL'):
            tokens.append(Token(kind, value, lineno, col))
        elif kind == 'SKIP':
            # skip whitespace inside line
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character {value!r} on line {lineno}')
    return tokens


def tokenize(code: str):
    tokens = []
    indent_stack = [0]
    lines = code.splitlines()
    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip('\r\n')
        # ignore pure blank lines
        if line.strip() == '':
            continue
        # compute indent (use spaces only; tabs converted to 4 spaces)
        leading = 0
        for ch in line:
            if ch == ' ':
                leading += 1
            elif ch == '\t':
                leading += 4
            else:
                break
        if leading > indent_stack[-1]:
            indent_stack.append(leading)
            tokens.append(Token('INDENT', '', i, 1))
        while leading < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token('DEDENT', '', i, 1))
        # tokenize the rest of the line
        content = line.lstrip('\t ')
        line_tokens = _tokenize_line(content, i, leading)
        tokens.extend(line_tokens)
        # newline separator
        tokens.append(Token('NEWLINE', '', i, len(line)))

    # close any remaining indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token('DEDENT', '', len(lines) or 1, 1))
    tokens.append(Token('EOF', '', len(lines) or 1, 0))
    return tokens
