from dataclasses import dataclass
from typing import List, Any
from ecoscript import tokenizer

# AST node classes

@dataclass
class Program:
    body: List[Any]

@dataclass
class LetStmt:
    name: str
    expr: Any

@dataclass
class ExprStmt:
    expr: Any

@dataclass
class NumberLiteral:
    value: Any

@dataclass
class StringLiteral:
    value: str

@dataclass
class Identifier:
    name: str

@dataclass
class BinaryOp:
    op: str
    left: Any
    right: Any

@dataclass
class UnaryOp:
    op: str
    operand: Any

@dataclass
class PrintStmt:
    expr: Any

@dataclass
class Block:
    statements: List[Any]

@dataclass
class IfStmt:
    condition: Any
    then_block: Block
    else_block: Any  # Block or None

@dataclass
class WhileStmt:
    condition: Any
    body: Block

@dataclass
class FunctionDecl:
    name: str
    params: List[str]
    body: Block

@dataclass
class ReturnStmt:
    expr: Any

@dataclass
class CallExpr:
    callee: Any
    args: List[Any]

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type_):
        tok = self.peek()
        if tok.type != type_:
            raise SyntaxError(f"Expected {type_} but got {tok.type} at {tok.lineno}:{tok.col}")
        return self.advance()

    def parse(self):
        stmts = []
        while self.peek().type != 'EOF':
            # skip empty statement separators
            if self.peek().type in ('SEMICOL','NEWLINE'):
                self.advance()
                continue
            stmts.append(self.parse_statement())
        return Program(stmts)

    def parse_statement(self):
        tok = self.peek()
        if tok.type == 'LET' or tok.type == 'VAR' or tok.type == 'CONST':
            return self.parse_let()
        if tok.type == 'FUNCTION':
            return self.parse_function()
        if tok.type == 'PRINT':
            return self.parse_print()
        if tok.type == 'IF':
            return self.parse_if()
        if tok.type == 'WHILE':
            return self.parse_while()
        if tok.type == 'RETURN':
            return self.parse_return()
        # otherwise expression statement
        expr = self.parse_expression()
        # optional semicolon
        if self.peek().type == 'SEMICOL':
            self.advance()
        return ExprStmt(expr)

    def parse_let(self):
        self.advance()  # let/var/const
        name_tok = self.expect('IDENT')
        name = name_tok.value
        if self.peek().type == 'OP' and self.peek().value == '=':
            self.advance()
            expr = self.parse_expression()
        else:
            expr = None
        if self.peek().type == 'SEMICOL':
            self.advance()
        return LetStmt(name, expr)

    def parse_function(self):
        self.advance()  # function
        name_tok = self.expect('IDENT')
        name = name_tok.value
        self.expect('LPAREN')
        params = []
        if self.peek().type != 'RPAREN':
            while True:
                p = self.expect('IDENT')
                params.append(p.value)
                if self.peek().type == 'COMMA':
                    self.advance()
                    continue
                break
        self.expect('RPAREN')
        body = self.parse_block()
        return FunctionDecl(name, params, body)

    def parse_print(self):
        self.advance()
        self.expect('LPAREN')
        expr = self.parse_expression()
        self.expect('RPAREN')
        if self.peek().type == 'SEMICOL':
            self.advance()
        return PrintStmt(expr)

    def parse_if(self):
        self.advance()
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        then_block = self.parse_block()
        else_block = None
        if self.peek().type == 'ELSE':
            self.advance()
            else_block = self.parse_block()
        return IfStmt(cond, then_block, else_block)

    def parse_while(self):
        self.advance()
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_return(self):
        self.advance()
        if self.peek().type == 'SEMICOL':
            self.advance()
            return ReturnStmt(None)
        expr = self.parse_expression()
        if self.peek().type == 'SEMICOL':
            self.advance()
        return ReturnStmt(expr)

    def parse_block(self):
        # support both { ... } and indentation blocks
        if self.peek().type == 'LBRACE':
            self.expect('LBRACE')
            stmts = []
            while self.peek().type != 'RBRACE':
                if self.peek().type == 'EOF':
                    raise SyntaxError('Unexpected EOF in block')
                if self.peek().type in ('SEMICOL','NEWLINE'):
                    self.advance()
                    continue
                stmts.append(self.parse_statement())
            self.expect('RBRACE')
            return Block(stmts)

        # indentation block: expect NEWLINE then INDENT ... DEDENT
        if self.peek().type == 'NEWLINE':
            self.advance()
        if self.peek().type != 'INDENT':
            raise SyntaxError('Expected INDENT to start block')
        self.advance()  # consume INDENT
        stmts = []
        while self.peek().type != 'DEDENT':
            if self.peek().type == 'EOF':
                raise SyntaxError('Unexpected EOF in indented block')
            if self.peek().type in ('NEWLINE','SEMICOL'):
                self.advance()
                continue
            stmts.append(self.parse_statement())
        self.expect('DEDENT')
        return Block(stmts)

    # Expression parsing (precedence climbing)
    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.peek().type == 'OP' and self.peek().value == '||':
            op = self.advance().value
            right = self.parse_logical_and()
            node = BinaryOp(op, node, right)
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while self.peek().type == 'OP' and self.peek().value == '&&':
            op = self.advance().value
            right = self.parse_equality()
            node = BinaryOp(op, node, right)
        return node

    def parse_equality(self):
        node = self.parse_comparison()
        while self.peek().type == 'OP' and self.peek().value in ('==','!='):
            op = self.advance().value
            right = self.parse_comparison()
            node = BinaryOp(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.peek().type == 'OP' and self.peek().value in ('<','>','<=','>='):
            op = self.advance().value
            right = self.parse_term()
            node = BinaryOp(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek().type == 'OP' and self.peek().value in ('+','-'):
            op = self.advance().value
            right = self.parse_factor()
            node = BinaryOp(op, node, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.peek().type == 'OP' and self.peek().value in ('*','/','%'):
            op = self.advance().value
            right = self.parse_unary()
            node = BinaryOp(op, node, right)
        return node

    def parse_unary(self):
        if self.peek().type == 'OP' and self.peek().value in ('-','!'):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok.type == 'NUMBER':
            self.advance()
            return NumberLiteral(tok.value)
        if tok.type == 'STRING':
            self.advance()
            return StringLiteral(tok.value)
        if tok.type == 'IDENT':
            self.advance()
            node = Identifier(tok.value)
            # call?
            if self.peek().type == 'LPAREN':
                self.advance()
                args = []
                if self.peek().type != 'RPAREN':
                    while True:
                        args.append(self.parse_expression())
                        if self.peek().type == 'COMMA':
                            self.advance()
                            continue
                        break
                self.expect('RPAREN')
                return CallExpr(node, args)
            return node
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f'Unexpected token {tok.type} ({tok.value}) at {tok.lineno}:{tok.col}')


def parse_source(source: str):
    tokens = tokenizer.tokenize(source)
    p = Parser(tokens)
    return p.parse()
