import ast
from collections import defaultdict


class CodeAnalysisVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = set()
        self.calls = set()
        self.modules = set()
        self.counts = defaultdict(int)

    def record(self, node):
        self.counts[type(node).__name__] += 1

    # record
    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node):
        self.calls.add(node.func.id)
        self.generic_visit(node)

    def visit_Import(self, node):
        for name in node.names:
            self.modules.add(name.name.split(".")[0])

    def visit_ImportFrom(self, node):
        if node.module is not None and node.level == 0:
            self.modules.add(node.module.split(".")[0])

    # count
    def visit_Expression(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Return(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Delete(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_For(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_While(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_If(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_With(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Raise(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Try(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Global(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Expr(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Pass(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Break(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Continue(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Slice(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_BinOp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Set(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Await(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Yield(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_YieldFrom(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_FormattedValue(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_JoinedStr(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Constant(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Starred(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Name(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_List(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Tuple(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Del(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Load(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Store(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_And(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Or(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Add(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_BitAnd(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_BitOr(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_BitXor(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Div(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_FloorDiv(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_LShift(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Mod(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Mult(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_MatMult(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Pow(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_RShift(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Sub(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Invert(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Not(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_UAdd(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_USub(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Eq(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Gt(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_GtE(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_In(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Is(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_IsNot(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Lt(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_LtE(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_NotEq(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_NotIn(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_arguments(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_arg(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_keyword(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_alias(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_withitem(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Index(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Suite(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_AugLoad(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_AugStore(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Param(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Num(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Str(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Bytes(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_NameConstant(self, node):
        self.record(node)
        self.generic_visit(node)

    def visit_Ellipsis(self, node):
        self.record(node)
        self.generic_visit(node)
