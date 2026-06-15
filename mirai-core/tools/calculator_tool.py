import ast
import operator
from tools.registry import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform mathematical calculations. Supports +, -, *, /, **, %, //"
    parameters = {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression to evaluate (e.g., '2 + 2 * 3')"}
        },
        "required": ["expression"]
    }

    SAFE_OPERATORS = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv, ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def execute(self, expression: str = "", **kwargs) -> ToolResult:
        try:
            tree = ast.parse(expression.strip(), mode="eval")
            result = self._eval(tree.body)
            return ToolResult(tool_name=self.name, content=str(result))
        except Exception as e:
            return ToolResult(tool_name=self.name, content=f"Error: {e}", success=False, error=str(e))

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(self._eval(node.operand))
        else:
            raise ValueError(f"Unsupported expression: {type(node).__name__}")
