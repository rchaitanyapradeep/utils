def schema(f):
    """
    Generate a schema for the input function based on its signature and annotations.

    This function examines the provided function's signature, including its parameters,
    annotations, and default values. It then creates a model representing this signature
    and returns a schema for the function.

    Parameters:
        f (callable): The function for which the schema needs to be generated.

    Returns:
        dict: A dictionary containing the function's name, its docstring as a description,
              and the generated schema for its parameters.

    Example:
        Given a function:
        def example_function(param1: int, param2: str = "default"):
            pass

        Calling `schema(example_function)` would return:
        {
            'name': 'example_function',
            'description': None,
            'parameters': {
                'param1': (int, ...),
                'param2': (str, 'default')
            }
        }
    """

    kw = {n: (o.annotation, ... if o.default == Parameter.empty else o.default)
          for n, o in inspect.signature(f).parameters.items()}
    s = create_model(f'Input for `{f.__name__}`', **kw).schema()
    return dict(name=f.__name__, description=f.__doc__, parameters=s)

def call_func(c):
    fc = c.choices[0].message.function_call
    if fc.name not in funcs_ok: return print(f'Not allowed: {fc.name}')
    f = globals()[fc.name]
    return f(**json.loads(fc.arguments))

def run(code):
    """
    Execute the provided Python code and return the result of the last expression, if present.

    This function parses the given code into an Abstract Syntax Tree (AST), and if the last 
    statement in the code is an expression, it modifies the AST to capture the result of that 
    expression. The code (with any modifications) is then executed, and the result of the last 
    expression (if any) is returned.

    Parameters:
    -----------
    code : str
        The Python code to be executed.

    Returns:
    --------
    Any or None
        The result of the last expression in the provided code, if it exists. 
        If the last statement is not an expression or there are no statements, 
        it returns None.

    Notes:
    ------
    - The function uses the `ast` module to parse and potentially modify the code.
    - The modified code is executed in a new namespace to avoid side effects.
    - If the last statement is an expression, its result is stored in a temporary
      variable `_result` in the namespace. This value is then retrieved and returned.

    Examples:
    ---------
    >>> run("a = 5\na + 10")
    15

    >>> run("a = 5\na = a + 10")
    None

    >>> run("print('Hello, World!')")
    None

    """
    tree = ast.parse(code)
    last_node = tree.body[-1] if tree.body else None
    
    # If the last node is an expression, modify the AST to capture the result
    if isinstance(last_node, ast.Expr):
        tgts = [ast.Name(id='_result', ctx=ast.Store())]
        assign = ast.Assign(targets=tgts, value=last_node.value)
        tree.body[-1] = ast.fix_missing_locations(assign)

    ns = {}
    exec(compile(tree, filename='<ast>', mode='exec'), ns)
    return ns.get('_result', None)
