import importlib
import os
import sys
from typing import Dict, Any

from lzy.py_env.py_env_provider import AutomaticPyEnvProvider, PyEnv
from lzy.api.v1 import Env


def get_auto_py_env(main_script_path: str) -> PyEnv:
    # User may not add cwd to PYTHONPATH, in case of running execution through `datasphere`, not `python -m`.
    # Since path to python script can be only relative, this should always work.
    sys.path.append(os.getcwd())

    namespace = get_module_namespace(main_script_path)
    provider = AutomaticPyEnvProvider()
    return provider.provide(namespace)


def get_module_namespace(path: str) -> Dict[str, Any]:
    module_spec = importlib.util.spec_from_file_location('module', path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return vars(module)


def get_conda_yaml(py_env: PyEnv) -> str:
    return Env(python_version=py_env.python_version, libraries=py_env.libraries).get_conda_yaml()
