"""
Module computing and checking high level dependencies in the coe (based on pydeps)
"""
from pathlib import Path
from subprocess import run
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple
from typing import Union

from core_devoops.logger import logger_get
from core_devoops.read_write import load_json_file

CONF_FILE = 'dependencies.json'
Dependency = Dict[str, List[str]]
log = logger_get(__name__)


def check_dependencies(conf_rel_path: str,
                       raw_folder: Union[Path, None] = None,
                       code: Union[str, None] = None):
    """
    hook for preserving the pre established solution dependencies.
    See https://think.cothinking.org/coth-team/vedct/-/issues/718 for more info
    """
    ref_folder = raw_folder or Path.cwd().resolve()
    ok_deps = True
    code_folder = code or conf_rel_path.split('/')[0]
    for code_base, config_path, rel_path in _get_dependencies_to_check(ref_folder, conf_rel_path,
                                                                       code_folder):
        allowed_dependencies, dependencies = _get_dependencies(code_base, config_path, rel_path,
                                                               code_folder)
        ok_deps = ok_deps and _test_dependency(allowed_dependencies, dependencies, rel_path)
    if not ok_deps:
        log.error('you changed high level solution dependencies. Intended?')
    return ok_deps


def compute_dependencies(code_base: Path, output_folder: Path, code_folder: str, plot: bool = True):
    """
    Given a code base, compute the dependencies between its high level modules.
     Store in output_folder the dependency matrix in txt format and the png of the dependencies
    """
    modules = _valid_modules(code_base)

    deps: Dependency = _get_current_dependencies(modules, code_base, '', code_folder)
    for mod, mod_deps in deps.items():
        with open(output_folder / f'{mod}.py', 'w') as f_stream:
            f_stream.writelines([f'from .{other_module} import to\n' for other_module in mod_deps])
    with open(output_folder / '__init__.py', 'w') as f_stream:
        f_stream.writelines([])
    if plot:
        run(['pydeps', '.', '-T', 'png', '--no-show'], cwd=output_folder)
    with open(output_folder / f'dependencies_{code_folder}.txt', 'w') as f_stream:
        f_stream.writelines([f'{dependency}\n' for dependency in _get_dep_matrix(modules, deps)])


def _get_dependencies_to_check(ref_folder: Path,
                               conf_rel_path: str,
                               code_folder: str) -> Iterator[Tuple[Path, Path, str]]:
    """
    given a reference_folder for the code,

    Returns:
        The code base folder to inspect
        The stored dependencies of the code base folder
        The relative path of the code base folder to inspect with respect to code_folder.
    """
    for dep_to_check in load_json_file(ref_folder / conf_rel_path / CONF_FILE):
        code_base = ref_folder / dep_to_check[1]
        config_path = ref_folder / conf_rel_path / dep_to_check[0]
        relative_path = dep_to_check[1].replace(f'{code_folder}/', '').replace('/', '.')
        yield code_base, config_path, relative_path


def _test_dependency(allowed_deps: Dependency, dependencies: Dependency, rel_path: str) -> bool:
    """
    For each modules stored in a dependencies.json file, check whether the current
    module dependencies are the same as the config ones.
    """
    rel_path = f'{rel_path}.' if rel_path != '' else ''
    for module in dependencies:
        for dep in allowed_deps[module]:
            if dep not in dependencies[module]:
                log.error(f'{rel_path}{module} no longer imported in {rel_path}{dep}. Intended ?')
        for dep in dependencies[module]:
            if dep not in allowed_deps[module]:
                log.error(f'{rel_path}{dep} now imported in {rel_path}{module}. Intended ?')
        for dep in dependencies[module]:
            if module in dependencies[dep] and dep != module:
                log.error(f'Circular ref created between {rel_path}{module} and {rel_path}{dep}.')
    return dependencies == allowed_deps


def _get_dependencies(code_base: Path,
                      config_path: Path,
                      relative_path: str,
                      code_folder: str) -> Tuple[Dependency, Dependency]:
    """
    Given a reference folder, a config_path and a relative path wrt to code_folder,
    fetch the base dir of the code solution and the pre established dependency
    file path to compute pre established and current dependencies,
    computed as adjacency dicts. All the values of a given key are its dependencies.
    the keys and the values of the dictionary take their labels in the pre established module list.
    """

    modules, allowed_dependencies = _get_allowed_dependencies(config_path)
    current_dependencies = _get_current_dependencies(modules, code_base, relative_path, code_folder)

    return allowed_dependencies, current_dependencies


def _get_allowed_dependencies(config_path: Path) -> Tuple[List[str], Dependency]:
    """
    Given the pre established dependency file path, compute
    the pre established modules and their dependencies seen as an adjacency dict.
    All the values of a given key are its dependencies.
    The keys and the values of the dictionary take their labels in
    the pre established module list.
    """
    raw_lines = list(_safe_read_lines(config_path))
    raw_matrix = [raw_dependency.split(',') for raw_dependency in raw_lines][1:]
    modules = [raw_dependency[0] for raw_dependency in raw_matrix]
    module_dependencies: Dict[str, List[str]] = {
        module: [modules[idx_other_module] for idx_other_module in range(len(modules))
                 if raw_matrix[idx_module][idx_other_module + 1] == 'Yes']
        for idx_module, module in enumerate(modules)
    }

    return modules, module_dependencies


def _get_current_dependencies(modules: List[str],
                              code_base: Path,
                              rel_path: str,
                              code_folder: str) -> Dependency:
    """
    Given the pre established modules, the code_base directory and the relative path of the code
    directory wrt code_folder, compute the pre current dependencies as an adjacency dict.
    All the values of a given key are its dependencies. The keys and the values of
    the dictionary take their labels in the pre established module list.
    """
    module_dependencies: Dependency = {}
    for module in modules:
        module_dependencies[module] = []
        module_dir = code_base / module
        for other_module in modules:
            if other_module in module_dependencies[module]:
                break
            for py_file in _get_recursively_all_files_in_dir(module_dir, 'py'):
                if _depends_on_module(module_dir / py_file, other_module, rel_path, code_folder):
                    module_dependencies[module].append(other_module)
                    break

    return module_dependencies


def _depends_on_module(file: Path, module: str, raw_path: str, code_folder: str) -> bool:
    """
     check if a reference to module is in the imports of python_file
    """
    rel_path = raw_path if raw_path.endswith('.') or not raw_path else f'{raw_path}.'

    return any(
        (f'from {code_folder}.{rel_path}{module}' in line and 'import' in line)
        or (line.startswith(f'import {code_folder}.{rel_path}.{module}.'))
        for line in _safe_read_lines(file)
    )


def _safe_read_lines(filename: Path) -> Iterator[str]:
    """
    read all lines in file, erase the final special \n character
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    yield from [line.strip() for line in lines]


def _get_recursively_all_files_in_dir(code_folder: Path, extension: str) -> Iterator[Path]:
    """
    Given a folder, recursively return all files of the given extension in the folder
    """
    yield from code_folder.glob(f'**/*.{extension}')


def _valid_folder(folder: Path):
    """
    Return True if folder is a python regroupment of module to be considered for dependency analysis
    """
    return (
        folder.is_dir()
        and not folder.name.startswith('.')
        and not folder.name.startswith('_')
        and folder.name != 'data'
    )


def _valid_modules(root_folder: Path):
    """
    Retrieve valid solution module (found at the base level of root_folder)
    """
    return sorted([folder.name for folder in root_folder.iterdir() if _valid_folder(folder)])


def _get_dep_matrix(modules: List[str], deps: Dependency) -> List[str]:
    """
    Retrieve the dependency matrix of the inspected solution in txt format
    """
    dependencies = [f'module x depends on,{",".join(modules)}']
    dependencies.extend(f'{module},' + ','.join([_depends_on(module, other_module, deps)
                                                 for other_module in modules])for module in modules)

    return dependencies


def _depends_on(module, other_module, deps):
    """
    Write correct input in the dependency matrix ("Yes" if other_module is in deps of module key)
    """
    return 'Yes' if other_module in deps[module] else 'No'
