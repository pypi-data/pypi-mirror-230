"""
deprecated
The driver code for IO capture
"""

import sys
import os
import logging
from os.path import abspath, dirname

import io_capture

PROJECTS_DIRECTORY = "example_projects"
OUTPUTS_DIRECTORY = "outputs"


def record_output(module_name, outputs_path):
    """
    Records IO from call stack to 'module_name' in 'outputs_path'; the directory must be pre-created
    """
    output = ""
    for i, call in enumerate(io_capture.calls):
        output += f"Call {i+1}:\n"
        output += f"Function: {call['function']}\n"
        output += f"Inputs:   {call['inputs']}\n"
        output += f"Output:   {call['output']}\n"
        output += "\n"

    # resetting {the call stack afte}r each proj
    io_capture.calls = []

    # output the recorded calls
    with open(os.path.join(outputs_path, module_name), "w", encoding="utf-8") as file:
        file.write(output)


def main():
    """
    Starts the decorating machinery
    """
    # set the relevant logging level
    logging.basicConfig(level=logging.WARNING)

    # adjusting the path to include sibling directories via the root path
    root_path = abspath(dirname(dirname(__file__)))
    sys.path.append(root_path)

    # preparing the paths for the projects' directory
    projs_path = os.path.join(root_path, PROJECTS_DIRECTORY)
    projs = [
        item
        for item in os.listdir(projs_path)
        if os.path.isdir(os.path.join(projs_path, item))
    ]

    # create outputs DIR if necessary
    outputs_path = os.path.join(root_path, OUTPUTS_DIRECTORY)
    if not os.path.exists(outputs_path):
        os.makedirs(outputs_path)

    # iterating over each project
    for proj in projs:
        # iterating over each file in the project & decorating it
        for mod_name, module in io_capture.decorate_directory_modules(
            f"{PROJECTS_DIRECTORY}/{proj}"
        ).items():
            try:
                # run the driver code function calls
                module.main()

                # module name - record the IO in an output file
                record_output(f"{proj}?{mod_name}.txt", outputs_path)

            except AttributeError as exc:
                logging.info("%s - treating it as a util module", exc)


if __name__ == "__main__":
    main()
