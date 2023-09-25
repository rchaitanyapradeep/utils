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
