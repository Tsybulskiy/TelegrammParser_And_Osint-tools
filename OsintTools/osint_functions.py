import importlib
import inspect
import os

import httpx


def get_functions_from_path(module_path):
    try:
        module = importlib.import_module(module_path)
        functions = {name: f"{module_path}.{name}" for name, value in inspect.getmembers(module) if
                     inspect.isfunction(value)}
        return functions
    except Exception as e:
        print(e)
        return {}


def get_all_functions_from_modules():
    try:
        base_module_path = "modules"
        all_functions = {}

        modules_dir = os.path.join(os.getcwd(), base_module_path)

        subdirectories = [d for d in os.listdir(modules_dir) if os.path.isdir(os.path.join(modules_dir, d))]

        for subdirectory in subdirectories:
            current_dir = os.path.join(modules_dir, subdirectory)
            available_modules = [f[:-3] for f in os.listdir(current_dir) if f.endswith('.py')]

            for module_name in available_modules:
                module_path = f"{base_module_path}.{subdirectory}.{module_name}"
                functions = get_functions_from_path(module_path)
                all_functions.update(functions)

        return all_functions
    except Exception as e:
        print(e)


async def osint_func(email, functions, result_list):
    out = []
    client = httpx.AsyncClient()
    iteration_number = 1

    for module_name, module_function_path in functions.items():
        try:
            module, function_name = module_function_path.rsplit('.', 1)
            actual_module = importlib.import_module(module)
            function = getattr(actual_module, function_name)

            await function(email, client, out)

            if out and out[-1].get("exists"):
                result_list.addItem(f"Result {iteration_number}")
                for key, value in out[-1].items():
                    result_list.addItem(f"{key}: {value}")
                result_list.addItem("")
                iteration_number += 1
        except Exception as e:
            print(e)
            pass

    await client.aclose()
