"""
PEP-8 Conforming program to capture calls' IO across functions/class methods/inner classes in all
    the files in the 'example_projects' DIR.
"""

import inspect
import json
from typing import Any
from py_io_capture.report_table import ReportTable, IOVector, ReportTableJSONEncoder
from py_io_capture.common import MAX_REPORT_SIZE

calls = ReportTable(max_output_len=MAX_REPORT_SIZE)


def dump_records(file_path):
    json.dump(calls, open(file_path, "w"), indent=4, cls=ReportTableJSONEncoder)
    calls.clear()


def decorate_module(module):
    """
    Decorate a imported module

    Args:
        module: the module to be decorated
    """

    instrumented = set()
    for name, value in inspect.getmembers(
        module,
        predicate=lambda e: inspect.isfunction(e) or inspect.isclass(e),
    ):
        module.__setattr__(name, decorate_object(value))  # pylint: disable=C2801
        instrumented.add(name)

    # instrumented functions that are not covered by inspect.getmembers
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if callable(attr) and attr_name not in instrumented:
            setattr(module, attr_name, record_calls(attr))
    return module


def decorate_object(obj):
    """
    Apply the decorator to the given objects.

    Args:
        objects: A list of objects to decorate.
    """

    if inspect.isfunction(obj):
        return record_calls(obj)
    if inspect.isclass(obj):
        for name, attr in inspect.getmembers(obj):
            if is_property(name):
                continue

            # Instance vs. Class Method
            if inspect.isfunction(attr) or inspect.ismethod(attr):
                setattr(obj, name, record_calls(attr))

            elif inspect.isclass(attr) and not name.startswith("__"):
                decorate_object(attr)

    return obj


def record_calls(func):
    """
    Decorator function to record IO of a function call.

    Args:
        func: The function to be decorated.

    Returns:
        The wrapper function.
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper function that records the inputs and outputs of a function call.

        Args:
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The output of the wrapped function.
        """
        rnt = func(*args, **kwargs)

        try:
            rnt_str = str(rnt)
        except:
            rnt_str = "result not printable"

        # some function may not have attribute __qualname__
        # for example, numpy.random.rand
        func_name = (
            func.__qualname__ if hasattr(func, "__qualname__") else func.__name__
        )
        if is_property(func_name):
            return rnt

        # store inputs and outputs
        inputs = [str(value) for value in process_args(func, *args, **kwargs).values()]
        outputs = [rnt_str]

        # Store the call data
        try:
            file_name = inspect.getfile(func)
        except TypeError:
            file_name = "unknown_file"

        calls.report(f"{file_name}?{func_name}", (IOVector(inputs), IOVector(outputs)))

        return rnt

    return wrapper


def process_args(orig_func, *args, **kwargs):
    """
    Flattens composite args (if applicable)
    """

    processed = {}

    # Get the function arguments and their names
    try:
        args_names = inspect.getfullargspec(orig_func).args
    except TypeError:
        args_names = ["arg" + str(i) for i in range(len(args))]

    # Handle *args and **kwargs
    if not args_names:
        if len(args) > 1:
            processed["*args"] = args
            processed.update(kwargs)
        return processed

    processed: dict = {name: "[OPTIONAL ARG ABSENT]" for name in args_names}

    for i, arg in enumerate(args):
        record_arg = None
        # use match-case if wanted
        if isinstance(arg, (list, set)):
            record_arg = str(list(arg))
        elif isinstance(arg, dict):
            record_arg = str(list(zip(arg.keys(), arg.values())))
        else:
            record_arg = str(arg)
        processed[args_names[i]] = str(record_arg)

    return processed


def is_property(name):
    return name.startswith("__") and name.endswith("__")
