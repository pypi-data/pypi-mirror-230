import ast
import importlib
import inspect
import json
import os
import sys
import tempfile
from types import ModuleType
from typing import Any, Dict, List, Optional, Set, TextIO

import astor

from beam import App

BEAM_MODULE_NAME = "beam"


class AppExtractor(ast.NodeVisitor):
    def __init__(self):
        self.beam_imports: Set[str] = set(BEAM_MODULE_NAME)
        self.output_module_source: List[str] = []
        self.dependencies: Set[str] = set()
        self.nodes_to_keep: Set[ast.AST] = set()
        self.unresolved_nodes: Set[ast.AST] = set()
        self.name_parents: Dict[str, ast.AST] = dict()
        self.current_node: Any = None
        self.imports: Dict[str, ast.Import] = dict()

    def get_base_value(self, node):
        """
        Given an ast.Attribute node, return the base ast.Name node.
        Example: for the attribute expression "a.b.c", this method will return
        the ast.Name node for "a".
        """
        if isinstance(node, ast.Name):
            return node
        elif isinstance(node, ast.Attribute):
            return self.get_base_value(node.value)
        else:
            raise ValueError(f"Unexpected node type: {type(node).__name__}")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._is_nested_inside_function_or_class(node):
            return

        # Handle type annotations in function arguments
        for arg in node.args.args:
            annotation = arg.annotation
            if annotation is not None:
                self._add_dependencies_from_annotation(annotation)

        # Handle return type annotation
        return_annotation = node.returns
        if return_annotation is not None:
            self._add_dependencies_from_annotation(return_annotation)

        self.nodes_to_keep.add(node)
        self.generic_visit(node)

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                base_value = self.get_base_value(decorator.func.value)
                if base_value.id in self.imports:
                    self.nodes_to_keep.add(node)
                    self.nodes_to_keep.add(self.imports[base_value.id])

    def _add_dependencies_from_annotation(self, annotation: ast.AST):
        if isinstance(annotation, ast.Name):
            self.dependencies.add(annotation.id)
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                self.dependencies.add(annotation.value.id)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self.imports[alias.name] = node

        if node.module == BEAM_MODULE_NAME:
            self.beam_imports.update(alias.name for alias in node.names)
            self.nodes_to_keep.add(node)
            return

        # Store the import as a dependency to check later if it's used by Beam
        self.unresolved_nodes.add(node)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports[alias.name] = node

        for alias in node.names:
            if alias.name == BEAM_MODULE_NAME:
                self.beam_imports.add(alias.name)
                self.nodes_to_keep.add(node)
                self.generic_visit(node)
                return

        self.unresolved_nodes.add(node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            if node.value.id in self.dependencies:
                self.nodes_to_keep.add(node)

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.dependencies and node.id in self.name_parents:
            self.nodes_to_keep.add(self.name_parents[node.id])

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.name_parents[target.id] = node

        if any(self._beam_depends_on_node(name) for name in ast.walk(node)):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.dependencies.add(target.id)
                elif isinstance(target, ast.Subscript):
                    if isinstance(target.value, ast.Name):
                        self.dependencies.add(target.value.id)
                elif isinstance(target, ast.Tuple):
                    for element in target.elts:
                        if isinstance(element, ast.Name):
                            self.dependencies.add(element.id)
        else:
            self.unresolved_nodes.add(node)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.parent in self.nodes_to_keep:
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    self.dependencies.add(arg.id)

            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Name):
                    self.dependencies.add(keyword.value.id)

        elif self._beam_depends_on_node(node.func):
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    self.dependencies.add(arg.id)

            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Name):
                    self.dependencies.add(keyword.value.id)

        self.generic_visit(node)

    def _beam_depends_on_node(self, node: ast.AST) -> bool:
        if self._is_nested_inside_function_or_class(node):
            return False

        if isinstance(node, ast.Name):
            return node.id in self.beam_imports or node.id in self.dependencies

        elif isinstance(node, ast.Attribute):
            return (
                node.attr in self.beam_imports
                or node.attr in self.dependencies
                or (isinstance(node.value, ast.Name) and node.value.id in self.dependencies)
                or self._beam_depends_on_node(node.value)
            )

        elif isinstance(node, ast.FunctionDef):
            return node.name in self.dependencies

        elif isinstance(node, ast.Call):
            return self._beam_depends_on_node(node.func)

        elif isinstance(node, ast.Import):
            return any(
                alias.name in self.beam_imports or alias.name in self.dependencies
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            return (
                node.module in self.beam_imports
                or node.module in self.dependencies
                or any(
                    alias.name in self.beam_imports or alias.name in self.dependencies
                    for alias in node.names
                )
            )

        elif isinstance(node, ast.Assign):
            return any(
                self._beam_depends_on_node(target) for target in node.targets
            ) or self._beam_depends_on_node(node.value)

        return False

    def _is_nested_inside_function_or_class(self, node: ast.AST) -> bool:
        """
        Check whether the node is nested inside a function or class definition.
        """
        while hasattr(node, "parent"):
            if isinstance(node.parent, (ast.FunctionDef, ast.ClassDef)):
                return True

            node = node.parent

        return False

    def _add_subdependencies(self, node: ast.AST) -> None:
        if self._is_nested_inside_function_or_class(node):
            return

        if isinstance(node, ast.Call):
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    self.dependencies.add(arg.id)

            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Name):
                    self.dependencies.add(keyword.value.id)

        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                self.dependencies.add(node.value.id)

        # Recursively check for subdependencies in child nodes
        for child_node in ast.iter_child_nodes(node):
            self._add_subdependencies(child_node)

    def _append_source(self, node: ast.AST, end: str = "\n") -> None:
        source = astor.to_source(node).strip() + end
        self.output_module_source.append(source)

    def visit(self, node: ast.AST) -> None:
        if not hasattr(node, "parent"):
            node.parent = self.current_node

        self.current_node = node
        super().visit(node)
        self.current_node = node.parent

    def _remove_child_nodes(self, nodes_to_keep: List[ast.AST]) -> List[ast.AST]:
        nodes_to_remove = set()

        for node in nodes_to_keep:
            parent = getattr(node, "parent", None)

            while parent is not None:
                if parent in nodes_to_keep and parent is not node:
                    nodes_to_remove.add(node)
                    break

                parent = getattr(parent, "parent", None)

        return [node for node in nodes_to_keep if node not in nodes_to_remove]

    def dump_source(self) -> str:
        for node in list(self.nodes_to_keep):
            parent = getattr(node, "parent", None)

            while parent is not None:
                if (
                    parent not in self.nodes_to_keep
                    and not isinstance(parent, ast.FunctionDef)
                    and not isinstance(parent, ast.Module)
                ):
                    self.nodes_to_keep.add(parent)

                parent = getattr(parent, "parent", None)

        # Now handle the dependencies of nodes_to_keep
        for node in list(self.nodes_to_keep):
            self._add_subdependencies(node)

        for node in self.unresolved_nodes:
            if self._beam_depends_on_node(node):
                self.nodes_to_keep.add(node)

        nodes_to_keep = list(self.nodes_to_keep)
        nodes_to_keep = self._remove_child_nodes(nodes_to_keep)
        nodes_to_keep.sort(key=lambda node: node.lineno)

        for node in nodes_to_keep:
            self._append_source(node)

        return "\n".join(self.output_module_source)


class AppBuilder:
    @staticmethod
    def _find_app_in_module(app_module: ModuleType) -> str:
        app = None
        for member in inspect.getmembers(app_module):
            member_value = member[1]
            if isinstance(member_value, App):
                app = member_value
                break

        if app is not None:
            return json.dumps(app())

        raise RuntimeError("Beam app not found")

    @staticmethod
    def build(*, module_path: str, func_or_app_name: Optional[str]) -> str:
        if not os.path.exists(module_path):
            raise FileNotFoundError

        module_source = ""
        with open(module_path, "r") as f:
            module_source = f.read()

        # Extract app from module source
        tree = ast.parse(module_source)
        extractor = AppExtractor()
        extractor.visit(tree)
        processed_module_source = extractor.dump_source()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write(processed_module_source)
            tmp_module_path = tmp.name

        # Override stdout
        stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

        # Load module
        spec = importlib.util.spec_from_file_location(module_path, tmp_module_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        # Restore stdout
        sys.stdout = stdout
        if func_or_app_name is None:
            config = AppBuilder._find_app_in_module(app_module)
            return AppBuilder._print_config(module_path, tmp_module_path, stdout, config)

        try:
            _callable = getattr(app_module, func_or_app_name)
            config = json.dumps(_callable())
            return AppBuilder._print_config(module_path, tmp_module_path, stdout, config)
        except AttributeError:
            raise

    @staticmethod
    def _print_config(module_path: str, tmp_module_path: str, stdout: TextIO, config: str) -> None:
        try:
            config = str(config)
            config = config.replace(tmp_module_path.lstrip("/"), module_path)
            stdout.write(config)
            stdout.flush()
            sys.stdout = stdout
        finally:
            os.unlink(tmp_module_path)


if __name__ == "__main__":
    """
    Usage:
        python3 -m beam.utils.build <module_name.py>:<func_name>
            or
        python3 -m beam.utils.build <module_name.py:<app_name>
    """

    app_handler = sys.argv[1]
    module_path = app_handler
    func_or_app_name = None
    try:
        module_path, func_or_app_name = app_handler.split(":")
    except ValueError:
        pass

    AppBuilder.build(module_path=module_path, func_or_app_name=func_or_app_name)
