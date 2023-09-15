import ast
import astor
import subprocess
import os
import json

from . import visitors


class Inspector:
    def __init__(self):
        self.transformed_ast = None
        self.storage_dict_name = (
            None  # Variable name of the dictionary where the variables will be stored.
        )
        self.debug_function_name = (
            None  # Name of the function that has to be called to store variables.
        )

    def modify_code(self, code):
        """
        Modify the code by injecting the print statements in every def and at the end of the code.

        Args:
            code (str): The code that needs to be modified.
        """

        self.transformed_ast = ast.parse(code)

        # Inject all the needed code.
        (
            main_node,
            self.debug_function_name,
            self.storage_dict_name,
        ) = visitors.AstGenerator.get_main_node()

        self.transformed_ast.body.insert(0, main_node)
        self.transformed_ast = visitors.FunctionVisitor(self.debug_function_name).visit(
            self.transformed_ast
        )
        self.transformed_ast.body.append(
            visitors.AstGenerator.get_inject_node(
                self.debug_function_name, node_name="Program"
            )
        )
        self.transformed_ast.body.append(
            visitors.AstGenerator.get_print_storage_node(self.storage_dict_name)
        )

    def get_modified_ast(self):
        """
        Returns the modified ast.

        Returns:
            ast: The modified ast, cannot be run.
        """

        return self.transformed_ast

    def get_modified_code(self):
        """
        Get the readable modified code.

        Returns:
            str: The runnable modified code.
        """

        return astor.to_source(self.get_modified_ast())

    def run_modified_code(self):
        """
        Run the modified code in temp file (in working dir) and returns the output (Variables per scope).

        Returns:
            dict: All the variables per scope.
        """

        script_directory = os.getcwd()
        script_path = os.path.join(script_directory, "modified_code.temp.py")

        file = open(script_path, "w", encoding="utf-8")
        file.write(self.get_modified_code())
        file.close()

        all_output = subprocess.check_output(
            ["py", script_path], stderr=subprocess.STDOUT, universal_newlines=True
        )
        os.remove(script_path)
        storage_result = all_output.split('\n')[-2]

        return json.loads(storage_result)
