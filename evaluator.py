from ecoscript.parser import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}
    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Name '{name}' is not defined")
    def set(self, name, value):
        self.values[name] = value

class Function:
    def __init__(self, decl: FunctionDecl, env: Environment):
        self.decl = decl
        self.env = env
    def call(self, args, evaluator):
        new_env = Environment(self.env)
        for i, p in enumerate(self.decl.params):
            new_env.set(p, args[i] if i < len(args) else None)
        try:
            evaluator.eval_block(self.decl.body, new_env)
        except ReturnException as r:
            return r.value
        return None

class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        # builtins
        self.global_env.set('print', lambda *a: print(*a))

    def eval(self, node, env=None):
        if env is None:
            env = self.global_env
        method = 'eval_' + node.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(node, env)
        raise NotImplementedError(method)

    def eval_Program(self, node: Program, env: Environment):
        result = None
        for s in node.body:
            result = self.eval(s, env)
        return result

    def eval_LetStmt(self, node: LetStmt, env: Environment):
        val = None
        if node.expr is not None:
            val = self.eval(node.expr, env)
        env.set(node.name, val)
        return None

    def eval_ExprStmt(self, node: ExprStmt, env: Environment):
        return self.eval(node.expr, env)

    def eval_NumberLiteral(self, node: NumberLiteral, env: Environment):
        return node.value

    def eval_StringLiteral(self, node: StringLiteral, env: Environment):
        return node.value

    def eval_Identifier(self, node: Identifier, env: Environment):
        return env.get(node.name)

    def eval_BinaryOp(self, node: BinaryOp, env: Environment):
        l = self.eval(node.left, env)
        r = self.eval(node.right, env)
        op = node.op
        if op == '+':
            return l + r
        if op == '-':
            return l - r
        if op == '*':
            return l * r
        if op == '/':
            return l / r
        if op == '%':
            return l % r
        if op == '==':
            return l == r
        if op == '!=':
            return l != r
        if op == '<':
            return l < r
        if op == '<=':
            return l <= r
        if op == '>':
            return l > r
        if op == '>=':
            return l >= r
        if op == '&&':
            return bool(l) and bool(r)
        if op == '||':
            return bool(l) or bool(r)
        raise NotImplementedError(f'Operator {op}')

    def eval_UnaryOp(self, node: UnaryOp, env: Environment):
        v = self.eval(node.operand, env)
        if node.op == '-':
            return -v
        if node.op == '!':
            return not v
        raise NotImplementedError(node.op)

    def eval_PrintStmt(self, node: PrintStmt, env: Environment):
        v = self.eval(node.expr, env)
        builtin = env.get('print')
        if callable(builtin):
            return builtin(v)
        else:
            print(v)

    def eval_Block(self, node: Block, env: Environment):
        return self.eval_block(node, Environment(env))

    def eval_block(self, block: Block, env: Environment):
        for s in block.statements:
            self.eval(s, env)

    def eval_IfStmt(self, node: IfStmt, env: Environment):
        cond = self.eval(node.condition, env)
        if cond:
            return self.eval_Block(node.then_block, env)
        elif node.else_block is not None:
            return self.eval_Block(node.else_block, env)
        return None

    def eval_WhileStmt(self, node: WhileStmt, env: Environment):
        while self.eval(node.condition, env):
            res = self.eval_Block(node.body, env)
        return None

    def eval_FunctionDecl(self, node: FunctionDecl, env: Environment):
        func = Function(node, env)
        env.set(node.name, func)
        return None

    def eval_ReturnStmt(self, node: ReturnStmt, env: Environment):
        val = None
        if node.expr is not None:
            val = self.eval(node.expr, env)
        raise ReturnException(val)

    def eval_CallExpr(self, node: CallExpr, env: Environment):
        callee = self.eval(node.callee, env) if not isinstance(node.callee, Identifier) else env.get(node.callee.name)
        args = [self.eval(a, env) for a in node.args]
        # builtin function
        if callable(callee):
            return callee(*args)
        # user function
        if isinstance(callee, Function):
            return callee.call(args, self)
        raise TypeError('Not callable')

    # convenience runner
    def run_source(self, source: str):
        tree = parse_source(source)
        return self.eval(tree, self.global_env)
