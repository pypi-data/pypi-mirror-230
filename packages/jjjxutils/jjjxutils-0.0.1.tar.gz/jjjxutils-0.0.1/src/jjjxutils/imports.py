import importlib


def import_file(module_path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def import_module(module_name: str):
    return importlib.import_module(module_name)

def import_rel(module_name: str):
    return __import__(module_name)


def import_from_http(module_url: str, module_name: str):
    import requests
    import tempfile
    import os
    import sys
    import importlib.util

    response = requests.get(module_url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(response.content)
            file.close()
            module = import_file(file.name, module_name)
            os.unlink(file.name)
            return module
    else:
        raise RuntimeError("Could not download module from %s" % module_url)
    
def import_from_github(github_repo: str, branch: str, path: str, module_name: str):
    return import_from_http(f"https://raw.githubusercontent.com/{github_repo}/{branch}/{path}", module_name)
