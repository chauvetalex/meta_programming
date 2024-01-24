# This module regroups functions to compare function signatures and bodies.
# It aims at preventing accidental code alteration while using llm for code completion/generation.

import inspect, importlib
import logging

local_logger = logging.getLogger(__name__)


class AlteredCodeError(Exception):
    pass


def explore_module(module_name):

    functions_and_methods = []

    # Import the module dynamically
    module = importlib.import_module(module_name)

    # Loop over all items in the module
    for name, item in inspect.getmembers(module):

        # Check if the item is a class
        if inspect.isclass(item):
            print(f"Class: {name}")

            # Loop over methods in the class
            for method_name, method in inspect.getmembers(item):
                if inspect.isfunction(method):
                    functions_and_methods.append(method)
                    print(f"  Method: {method_name}")

        # Check if the item is a function
        elif inspect.isfunction(item):
            functions_and_methods.append(item)
            print(f"Function: {name}")

    return functions_and_methods


def compare_modules(module1, module2):
    pass


def compare_function_signatures(func1, func2):

    # Get the signatures of the functions
    signature1 = inspect.signature(func1)
    signature2 = inspect.signature(func2)

    # Compare the parameters of the signatures
    if signature1.parameters == signature2.parameters:

        # Check type annotations and default values
        for param_name, param1 in signature1.parameters.items():
            param2 = signature2.parameters[param_name]

            # Compare type annotations. Not blocking.
            if param1.annotation != param2.annotation:
                local_logger.info(f"Type annotation mismatch for parameter {param_name}: {param1.annotation} vs {param2.annotation}")
                return False

            # Compare default values.
            if param1.default != param2.default:
                raise AlteredCodeError(f"Default value mismatch for parameter {param_name}: {param1.default} vs {param2.default}")

        # If all checks pass, signatures match
        local_logger.info("Function signatures match!")
        return True

    else:
        local_logger.info("Function signatures do not match.")
        return False


def compare_function_bodies(func1, func2):

    # Define a function to remove comments and blank lines from the code.
    def _preprocess_code(code):
        lines = code.split('\n')
        return '\n'.join([line for line in lines if not line.strip().startswith('#') and len(line.strip())])

    # Get the source code of the functions.
    source1 = inspect.getsource(func1)
    source2 = inspect.getsource(func2)

    # Remove comments and blank lines from the source code.
    source1_lines = _preprocess_code(source1)
    source2_lines = _preprocess_code(source2)

    # Compare the functions bodies.
    if source1_lines == source2_lines:
        local_logger.info("Function bodies match!")
    else:
        raise AlteredCodeError("Function bodies do not match.")



if __name__ == '__main__':
    pass
