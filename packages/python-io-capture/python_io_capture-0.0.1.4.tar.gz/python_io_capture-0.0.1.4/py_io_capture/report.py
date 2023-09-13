from inspect import isclass, isfunction


def report(func):
    def wrapper(*args, **kwargs):
        try:
            fname = func.__name__
            print(
                f"Function {fname} called with args: {str(args)}, kwargs: {str(kwargs)}"
            )
            result = func(*args, **kwargs)
            print(f"Function {fname} returned: {str(result)}")
            return result
        except:
            return func

    return wrapper


# Instrument all functions in numpy
def instrument_report(module):
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if callable(attr):
            setattr(module, attr_name, report(attr))
    return module
