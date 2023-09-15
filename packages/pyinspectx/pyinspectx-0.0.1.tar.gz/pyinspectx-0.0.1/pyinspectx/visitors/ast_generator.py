import ast
import random

# TODO: Add regex support for blacklist
# TODO: Blacklist all __ variables
# Variables need to be in global scope so they can be accessed inside static methods
BLACKLIST = [
    "__builtins__",
    "__doc__",
    "__file__",
    "__name__",
    "__package__",
    "__loader__",
    "__spec__",
    "__annotations__",
    "__cached__",
]


class AstGenerator:
    def __init__(self):
        pass

    @staticmethod
    def get_main_node():
        """
        Creates the main AST node with the blacklist, storage and function where the variables will be saved.

        Returns:
            ast.Module: The AST node that includes the blacklist, storage and helper function.
            str: Debug function name.
            str: Storage dict name.
        """

        storage_dict_name = "inspect_storage_%s" % random.randint(1000, 10000000)
        debug_function_name = "inspect_debug_%s" % random.randint(1000, 10000000)
        blacklist_name = "inspect_blacklist_%s" % random.randint(1000, 10000000)
        BLACKLIST.append(storage_dict_name)
        BLACKLIST.append(debug_function_name)
        BLACKLIST.append(blacklist_name)

        blacklist_node = ast.Assign(
            targets=[ast.Name(id=blacklist_name, ctx=ast.Store())],
            value=ast.List(elts=[ast.Str(s=item) for item in BLACKLIST]),
        )
        import_node = ast.Expr(
            value=ast.Import(names=[ast.alias(name="json", asname=None)])
        )

        storage_node = ast.Assign(
            targets=[ast.Name(id=storage_dict_name, ctx=ast.Store())],
            value=ast.Dict(keys=[], values=[]),
        )

        debug_function_node = ast.FunctionDef(
            name=debug_function_name,
            args=ast.arguments(
                args=[
                    ast.arg(arg="node_name", annotation=None),
                    ast.arg(arg="local_variables_copy", annotation=None),
                ],
                defaults=[],
                kw_defaults=[],
                kwarg=None,
                kwonlyargs=[],
                kwonlydefaults=[],
                posonlyargs=[],
                vararg=None,
            ),
            body=[
                ast.For(
                    target=ast.Tuple(
                        elts=[
                            ast.Name(id="var_name", ctx=ast.Store()),
                            ast.Name(id="var_value", ctx=ast.Store()),
                        ],
                        ctx=ast.Store(),
                    ),
                    iter=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="local_variables_copy", ctx=ast.Load()),
                            attr="items",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                    body=[
                        ast.If(
                            test=ast.Compare(
                                left=ast.Call(
                                    func=ast.Name(id="str", ctx=ast.Load()),
                                    args=[
                                        ast.Call(
                                            func=ast.Name(id="type", ctx=ast.Load()),
                                            args=[
                                                ast.Name(
                                                    id="var_value", ctx=ast.Store()
                                                )
                                            ],
                                            keywords=[],
                                        )
                                    ],
                                    keywords=[],
                                ),
                                ops=[
                                    ast.In()
                                ],  # <class 'module'> ast.Str(s="<class 'function'>")
                                comparators=[
                                    ast.Tuple( # Possible to add more or reverse this statement and check with regex or <class in ..
                                        elts=[
                                            ast.Str(s="<class 'function'>"),
                                            ast.Str(s="<class 'module'>"),
                                            ast.Str(s="<class 'type'>"),
                                        ],
                                        ctx=ast.Store(),
                                    )
                                ],
                            ),
                            body=[
                                ast.Assign(
                                    targets=[ast.Name(id="var_value", ctx=ast.Store())],
                                    value=ast.Call(
                                        func=ast.Name(id="str", ctx=ast.Load()),
                                        args=[
                                            ast.Call(
                                                func=ast.Name(
                                                    id="type", ctx=ast.Load()
                                                ),
                                                args=[
                                                    ast.Name(
                                                        id="var_value", ctx=ast.Store()
                                                    )
                                                ],
                                                keywords=[],
                                            )
                                        ],
                                        keywords=[],
                                    ),
                                )
                            ],
                            orelse=[],
                        ),
                        ast.If(
                            test=ast.Compare(
                                left=ast.Name(id="var_name", ctx=ast.Load()),
                                ops=[ast.In()],
                                comparators=[
                                    ast.Name(id=blacklist_name, ctx=ast.Load())
                                ],
                            ),
                            body=[ast.Continue()],
                            orelse=[
                                ast.If(
                                    test=ast.Compare(
                                        left=ast.Name(id="node_name", ctx=ast.Load()),
                                        ops=[ast.NotIn()],
                                        comparators=[
                                            ast.Name(
                                                id=storage_dict_name, ctx=ast.Load()
                                            )
                                        ],
                                    ),
                                    body=[
                                        ast.Assign(
                                            targets=[
                                                ast.Subscript(
                                                    value=ast.Name(
                                                        id=storage_dict_name,
                                                        ctx=ast.Load(),
                                                    ),
                                                    slice=ast.Index(
                                                        value=ast.Name(
                                                            id="node_name",
                                                            ctx=ast.Load(),
                                                        )
                                                    ),
                                                    ctx=ast.Store(),
                                                )
                                            ],
                                            value=ast.Dict(
                                                keys=[
                                                    ast.Name(
                                                        id="var_name", ctx=ast.Load()
                                                    )
                                                ],
                                                values=[
                                                    ast.Name(
                                                        id="var_value", ctx=ast.Load()
                                                    )
                                                ],
                                            ),
                                        )
                                    ],
                                    orelse=[
                                        ast.Assign(
                                            targets=[
                                                ast.Expr(
                                                    value=ast.Subscript(
                                                        value=ast.Subscript(
                                                            value=ast.Name(
                                                                id=storage_dict_name,
                                                                ctx=ast.Load(),
                                                            ),
                                                            slice=ast.Index(
                                                                value=ast.Name(
                                                                    id="node_name",
                                                                    ctx=ast.Load(),
                                                                )
                                                            ),
                                                            ctx=ast.Load(),
                                                        ),
                                                        slice=ast.Index(
                                                            value=ast.Name(
                                                                id="var_name",
                                                                ctx=ast.Load(),
                                                            )
                                                        ),
                                                        ctx=ast.Store(),
                                                    )
                                                )
                                            ],
                                            value=ast.Name(
                                                id="var_value", ctx=ast.Load()
                                            ),
                                        )
                                    ],
                                )
                            ],
                        ),
                    ],
                    orelse=[],
                )
            ],
            decorator_list=[],
        )

        injection_node = ast.Module(
            [import_node, blacklist_node, storage_node, debug_function_node]
        )

        return injection_node, debug_function_name, storage_dict_name

    @staticmethod
    def get_print_storage_node(storage_dict_name):
        """
        Creates the AST node that logs the storage in JSON format.

        Returns:
            ast.Module: The print storage node
        """

        print_node = ast.Module(
            [
                ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="print", ctx=ast.Load()),
                        args=[
                            ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="json", ctx=ast.Load()),
                                    attr="dumps",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Name(id=storage_dict_name, ctx=ast.Load())],
                                keywords=[],
                            )
                        ],
                        keywords=[],
                    )
                ),
            ]
        )

        return print_node

    @staticmethod
    def get_inject_node(debug_function_name, node_name="Program"):
        """
        Creates the AST node of the calls the debug function where the items can be saved..

        Args:
            debug_function_name (str): The name of the debugger function that has been injected earlier.
            node_name (str): The name of the node that is being injected.

        Returns:
            ast.Module: The AST node of the print statement that needs to be injected.
        """

        # Generate the inject AST node
        inject_node = ast.Module(
            [
                ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id=debug_function_name, ctx=ast.Load()),
                        args=[
                            ast.Str(s=node_name),
                            ast.Call(
                                func=ast.Attribute(
                                    value=ast.Call(
                                        func=ast.Name(id="locals", ctx=ast.Load()),
                                        args=[],
                                        keywords=[],
                                    ),
                                    attr="copy",
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                        ],
                        keywords=[],
                    )
                )
            ]
        )

        return inject_node
