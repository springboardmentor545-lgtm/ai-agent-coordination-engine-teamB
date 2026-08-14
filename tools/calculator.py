import ast
import operator as op

_ALLOWED = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Mod: op.mod, ast.Pow: op.pow,
    ast.USub: op.neg,
}

def calculate(expression: str):
    expression = expression.strip()
    if not expression:
        raise ValueError("Please provide a mathematical expression.")

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic expressions are supported.")

    try:
        return evaluate(ast.parse(expression, mode="eval").body)
    except ZeroDivisionError:
        raise ValueError("Division by zero is not allowed.")
    except (SyntaxError, ValueError):
        raise ValueError("Invalid arithmetic expression.")
