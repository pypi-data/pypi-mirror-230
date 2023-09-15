import ast
from .ast_generator import AstGenerator

class Visitor(ast.NodeTransformer):
    def __init__(self, debug_function_name):
        self.debug_function_name = debug_function_name
        
    def visit_FunctionDef(self, node):
        """
        Ast visitor to access the function definitions in the code and modify them.

        Args:
            ast (ast.NodeTransformer): Ast node transformer that is being accessed.
            
        Returns:
            ast.NodeTransformer: Ast node transformer that has been modified.
        """
        
        if node.name == self.debug_function_name:
            return node
    
        inject_node = AstGenerator.get_inject_node(self.debug_function_name, node_name=node.name)
        
        # Loop over all the subnodes: check for Return Statement
        for i, subnode in enumerate(node.body):
            if isinstance(subnode, ast.Return):
                node.body.insert(i, inject_node)
                return node

        # Loop over all the subnodes: check for FunctionDef (nested function)
        for i, subnode in enumerate(node.body):
            if isinstance(subnode, ast.FunctionDef):
                self.visit_FunctionDef(subnode)
                continue
            
        # If no return statement was found, just append the code to the end of the function.
        node.body = node.body + inject_node.body
        return node
