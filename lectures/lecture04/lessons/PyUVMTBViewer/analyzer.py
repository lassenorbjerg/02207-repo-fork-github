"""Static analyzer for PyUVM component hierarchies."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from .models import (
    UVM_COMPONENT_BASES,
    AnalysisResult,
    ClassInfo,
    ComponentNode,
    ConnectionInfo,
    CreationInfo,
    MethodInfo,
    inheritance_chain,
)


class AnalysisError(RuntimeError):
    """Raised when a source tree cannot be analyzed."""


class MultipleTestsError(AnalysisError):
    """Raised when a selected file contains more than one PyUVM test."""

    def __init__(self, candidates: list[str]):
        super().__init__("The selected file contains multiple PyUVM tests")
        self.candidates = candidates


@dataclass
class _ParsedModule:
    path: Path
    tree: ast.Module
    imports: dict[str, str] = field(default_factory=dict)


class _MethodVisitor(ast.NodeVisitor):
    """Collect component creations and connections within one method."""

    def __init__(self, path: Path, component_names: set[str]):
        self.path = path
        self.component_names = component_names
        self.creations: list[CreationInfo] = []
        self.connections: list[ConnectionInfo] = []
        self._conditional_depth = 0

    def visit_If(self, node: ast.If):
        self._conditional_depth += 1
        self.generic_visit(node)
        self._conditional_depth -= 1

    def visit_Match(self, node: ast.Match):
        self._conditional_depth += 1
        self.generic_visit(node)
        self._conditional_depth -= 1

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1:
            self._handle_assignment(node.targets[0], node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if node.value is not None:
            self._handle_assignment(node.target, node.value, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "connect":
            try:
                expression = ast.unparse(node)
            except (RecursionError, ValueError):
                expression = "connect(...)"
            self.connections.append(ConnectionInfo(expression, self.path, node.lineno))
        self.generic_visit(node)

    def _handle_assignment(self, target: ast.AST, value: ast.AST, line: int):
        if not isinstance(value, ast.Call):
            return

        attribute = _self_attribute(target)
        if attribute is None:
            return

        class_name = ""
        if isinstance(value.func, ast.Attribute) and value.func.attr == "create":
            class_name = _expression_name(value.func.value)
        elif isinstance(value.func, (ast.Name, ast.Attribute)):
            class_name = _expression_name(value.func)

        short_name = class_name.rsplit(".", 1)[-1]
        if short_name not in self.component_names:
            return

        instance_name = attribute
        if (
            value.args
            and isinstance(value.args[0], ast.Constant)
            and isinstance(value.args[0].value, str)
        ):
            instance_name = value.args[0].value
        else:
            name_keyword = next(
                (keyword.value for keyword in value.keywords if keyword.arg == "name"),
                None,
            )
            if (
                isinstance(name_keyword, ast.Constant)
                and isinstance(name_keyword.value, str)
            ):
                instance_name = name_keyword.value

        self.creations.append(
            CreationInfo(
                attribute=attribute,
                class_name=short_name,
                instance_name=instance_name,
                path=self.path,
                line=line,
                conditional=self._conditional_depth > 0,
            )
        )


class PyUVMAnalyzer:
    """Analyze a testbench without importing or executing it."""

    def __init__(self):
        self._modules: dict[Path, _ParsedModule] = {}
        self._warnings: list[str] = []
        self._include_dirs: list[Path] = []

    def find_tests(self, selected_file: str | Path) -> list[str]:
        """Return decorated PyUVM test classes in a file."""

        path = Path(selected_file).expanduser().resolve()
        module = self._parse_module(path)
        return [
            node.name
            for node in module.tree.body
            if isinstance(node, ast.ClassDef) and _is_test_decorated(node)
        ]

    def analyze(
        self,
        selected_file: str | Path,
        top_class_name: str | None = None,
        include_dirs: list[str | Path] | None = None,
        instance_rendering: dict[str, str] | None = None,
        experimental: bool = False,
        openai_api_key: str = "",
        openai_model: str = "gpt-5-mini",
    ) -> AnalysisResult:
        """Analyze a selected top-level PyUVM test file."""

        self._modules = {}
        self._warnings = []
        self._include_dirs = [
            Path(directory).expanduser().resolve()
            for directory in (include_dirs or [])
        ]
        selected_path = Path(selected_file).expanduser().resolve()
        if not selected_path.is_file():
            raise AnalysisError(f"Test file does not exist: {selected_path}")

        self._load_import_graph(selected_path)
        classes = self._collect_classes()
        self._mark_components(classes)
        self._collect_method_details(classes)

        candidates = [
            item
            for item in classes.values()
            if item.path == selected_path and item.decorated_test
        ]
        if top_class_name is not None:
            candidates = [item for item in candidates if item.name == top_class_name]
            if not candidates:
                raise AnalysisError(
                    f"PyUVM test '{top_class_name}' was not found in {selected_path}"
                )
        elif len(candidates) > 1:
            raise MultipleTestsError([item.name for item in candidates])

        if not candidates:
            candidates = [
                item
                for item in classes.values()
                if item.path == selected_path and self._inherits_from_test(item, classes)
            ]
        if len(candidates) > 1 and top_class_name is None:
            raise MultipleTestsError([item.name for item in candidates])
        if not candidates:
            raise AnalysisError(f"No PyUVM test class found in {selected_path}")

        top_class = candidates[0]
        root = ComponentNode(top_class.name, top_class.name, top_class)
        self._build_instance_tree(root, classes, set())
        rendering = {}
        if experimental:
            rendering.update(
                self._resolve_conditionals_with_llm(
                    root,
                    selected_path,
                    openai_api_key,
                    openai_model,
                )
            )
        rendering.update(instance_rendering or {})
        self._apply_instance_rendering(root, rendering)
        return AnalysisResult(
            selected_file=selected_path,
            top_class=top_class,
            root=root,
            classes=classes,
            warnings=list(dict.fromkeys(self._warnings)),
        )

    def _resolve_conditionals_with_llm(
        self,
        root: ComponentNode,
        selected_path: Path,
        api_key: str,
        model: str,
    ) -> dict[str, str]:
        from .llm_analyzer import (
            ConditionalCandidate,
            LLMAnalysisError,
            LLMConditionalAnalyzer,
        )

        grouped: dict[str, list[ComponentNode]] = {}
        for parent in root.walk():
            children_by_path: dict[str, list[ComponentNode]] = {}
            for child in parent.children:
                children_by_path.setdefault(child.instance_path, []).append(child)
            for instance_path, choices in children_by_path.items():
                if any(item.conditional for item in choices):
                    grouped[instance_path] = choices

        candidates = [
            ConditionalCandidate(
                instance_path=instance_path,
                candidate_classes=tuple(
                    dict.fromkeys(item.class_name for item in choices)
                ),
            )
            for instance_path, choices in grouped.items()
        ]
        source_files: dict[str, str] = {}
        for index, path in enumerate(sorted(self._modules), start=1):
            display_path = self._llm_source_name(path, selected_path, index)
            try:
                source_files[display_path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                raise AnalysisError(
                    f"Unable to prepare source for experimental analysis: {error}"
                ) from error

        try:
            result = LLMConditionalAnalyzer(api_key, model).analyze(
                source_files,
                candidates,
            )
        except LLMAnalysisError as error:
            raise AnalysisError(f"Experimental LLM analysis failed: {error}") from error

        self._warnings.append(
            f"Experimental LLM analysis resolved {len(result.resolutions)} "
            "conditional instance(s)"
        )
        return result.rendering_rules()

    @staticmethod
    def _llm_source_name(path: Path, selected_path: Path, index: int) -> str:
        try:
            return path.relative_to(selected_path.parent).as_posix()
        except ValueError:
            tail = "/".join(path.parts[-4:])
            return f"include-{index}/{tail}"

    def _parse_module(self, path: Path) -> _ParsedModule:
        path = path.resolve()
        existing = self._modules.get(path)
        if existing is not None:
            return existing
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as error:
            raise AnalysisError(f"Unable to parse {path}: {error}") from error
        module = _ParsedModule(path, tree)
        self._modules[path] = module
        return module

    def _load_import_graph(self, initial_path: Path):
        queue = [initial_path.resolve()]
        visited: set[Path] = set()
        while queue:
            path = queue.pop(0)
            if path in visited:
                continue
            visited.add(path)
            module = self._parse_module(path)
            for node in ast.walk(module.tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        resolved = self._resolve_module(path, alias.name, 0)
                        module.imports[alias.asname or alias.name] = alias.name
                        if resolved is not None and resolved not in visited:
                            queue.append(resolved)
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module or ""
                    resolved = self._resolve_module(path, module_name, node.level)
                    for alias in node.names:
                        module.imports[alias.asname or alias.name] = alias.name
                        child_name = ".".join(filter(None, (module_name, alias.name)))
                        child = self._resolve_module(path, child_name, node.level)
                        if child is not None and child not in visited:
                            queue.append(child)
                    if resolved is not None and resolved not in visited:
                        queue.append(resolved)

    def _resolve_module(self, importer: Path, module: str, level: int) -> Path | None:
        parts = [part for part in module.split(".") if part]
        if level:
            base = importer.parent
            for _ in range(max(0, level - 1)):
                base = base.parent
            search_roots = [base]
        else:
            search_roots = [importer.parent, *self._include_dirs]
            for parent in importer.parents:
                if parent not in search_roots:
                    search_roots.append(parent)
            for parent in importer.parents:
                for shared_directory in ("common", "src", "tb"):
                    shared_root = parent / shared_directory
                    if shared_root.is_dir() and shared_root not in search_roots:
                        search_roots.append(shared_root)

        for root in search_roots:
            candidate = root.joinpath(*parts) if parts else root
            file_candidate = candidate.with_suffix(".py")
            package_candidate = candidate / "__init__.py"
            if file_candidate.is_file():
                return file_candidate.resolve()
            if package_candidate.is_file():
                return package_candidate.resolve()
        return None

    def _collect_classes(self) -> dict[str, ClassInfo]:
        classes: dict[str, ClassInfo] = {}
        for module in self._modules.values():
            for node in module.tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                methods: dict[str, MethodInfo] = {}
                creations: dict[str, list[CreationInfo]] = {}
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods[child.name] = MethodInfo(
                            child.name,
                            module.path,
                            child.lineno,
                            child.end_lineno or child.lineno,
                            calls_super=_calls_super_method(child, child.name),
                        )
                        creations[child.name] = []
                info = ClassInfo(
                    name=node.name,
                    bases=[_expression_name(base) for base in node.bases],
                    path=module.path,
                    line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    methods=methods,
                    creations=creations,
                    decorated_test=_is_test_decorated(node),
                )
                key = info.key
                classes[key] = info
        return classes

    def _mark_components(self, classes: dict[str, ClassInfo]):
        by_name = {item.name: item for item in classes.values()}

        def is_component(item: ClassInfo, visiting: set[str]) -> bool:
            if item.key in visiting:
                return False
            if item.is_component:
                return True
            visiting.add(item.key)
            for base in item.bases:
                short_name = base.rsplit(".", 1)[-1]
                if short_name in UVM_COMPONENT_BASES:
                    item.is_component = True
                    return True
                parent = by_name.get(short_name)
                if parent is not None and is_component(parent, visiting):
                    item.is_component = True
                    return True
            return item.decorated_test

        for class_info in classes.values():
            class_info.is_component = is_component(class_info, set())

    def _collect_method_details(self, classes: dict[str, ClassInfo]):
        component_names = {
            item.name for item in classes.values() if item.is_component
        } | UVM_COMPONENT_BASES
        by_location = {
            (item.path, item.name): item for item in classes.values()
        }
        for module in self._modules.values():
            for class_node in module.tree.body:
                if not isinstance(class_node, ast.ClassDef):
                    continue
                class_info = by_location.get((module.path, class_node.name))
                if class_info is None:
                    continue
                for method_node in class_node.body:
                    if not isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    visitor = _MethodVisitor(module.path, component_names)
                    visitor.visit(method_node)
                    class_info.creations[method_node.name] = visitor.creations
                    if method_node.name == "connect_phase":
                        class_info.connections.extend(visitor.connections)

    def _inherits_from_test(
        self,
        class_info: ClassInfo,
        classes: dict[str, ClassInfo],
    ) -> bool:
        return any(
            base.rsplit(".", 1)[-1] == "uvm_test"
            for item in inheritance_chain(class_info, classes)
            for base in item.bases
        )

    def _build_instance_tree(
        self,
        node: ComponentNode,
        classes: dict[str, ClassInfo],
        ancestry: set[str],
    ):
        class_info = node.class_info
        if class_info is None or class_info.key in ancestry:
            return
        ancestry = ancestry | {class_info.key}
        by_name = {item.name: item for item in classes.values()}
        creations: list[CreationInfo] = []

        for current in self._phase_implementation_chain(class_info, "build_phase", classes):
            for creation in current.creations.get("build_phase", []):
                matching_index = next(
                    (
                        index
                        for index, existing in enumerate(creations)
                        if existing.attribute == creation.attribute
                        and existing.class_name == creation.class_name
                    ),
                    None,
                )
                if matching_index is None:
                    creations.append(creation)
                else:
                    creations[matching_index] = creation

        for creation in creations:
            child_info = by_name.get(creation.class_name)
            child = ComponentNode(
                instance_name=creation.instance_name,
                class_name=creation.class_name,
                class_info=child_info,
                parent=node,
                conditional=creation.conditional,
            )
            node.children.append(child)
            if child_info is None and creation.class_name not in UVM_COMPONENT_BASES:
                self._warnings.append(
                    f"Could not resolve component class {creation.class_name} "
                    f"created at {creation.path}:{creation.line}"
                )
            self._build_instance_tree(child, classes, ancestry)

    def _apply_instance_rendering(
        self,
        root: ComponentNode,
        rendering: dict[str, str],
    ):
        used_rules: set[str] = set()

        root_rule = rendering.get(root.instance_path)
        if root_rule is not None:
            used_rules.add(root.instance_path)
            if root_rule == "grey":
                root.render_mode = "grey"
            elif root_rule == "hide":
                self._warnings.append("The top-level test cannot be hidden")
            elif root_rule.startswith("conditional:"):
                expected_type = root_rule.removeprefix("conditional:")
                if expected_type != root.class_name:
                    self._warnings.append(
                        f"Conditional type {expected_type} does not match "
                        f"{root.instance_path}"
                    )

        def apply_children(parent: ComponentNode):
            grouped: dict[str, list[ComponentNode]] = {}
            order: list[str] = []
            for child in parent.children:
                if child.instance_name not in grouped:
                    grouped[child.instance_name] = []
                    order.append(child.instance_name)
                grouped[child.instance_name].append(child)

            visible: list[ComponentNode] = []
            for instance_name in order:
                candidates = grouped[instance_name]
                instance_path = candidates[0].instance_path
                rule = rendering.get(instance_path)
                if rule is not None:
                    used_rules.add(instance_path)

                if rule == "hide":
                    continue
                if rule is not None and rule.startswith("conditional:"):
                    expected_type = rule.removeprefix("conditional:")
                    matching = [
                        candidate
                        for candidate in candidates
                        if candidate.class_name == expected_type
                    ]
                    if matching:
                        candidates = matching
                        for candidate in candidates:
                            candidate.conditional = False
                    else:
                        self._warnings.append(
                            f"Conditional type {expected_type} was not found at "
                            f"{instance_path}"
                        )
                elif rule == "grey":
                    for candidate in candidates:
                        candidate.render_mode = "grey"

                visible.extend(candidates)
                for candidate in candidates:
                    if candidate.render_mode != "grey":
                        apply_children(candidate)

            parent.children = visible

        if root.render_mode != "grey":
            apply_children(root)

        for instance_path in rendering.keys() - used_rules:
            self._warnings.append(
                f"Instance rendering path was not found: {instance_path}"
            )

    def _phase_implementation_chain(
        self,
        class_info: ClassInfo,
        phase: str,
        classes: dict[str, ClassInfo],
    ) -> list[ClassInfo]:
        chain = inheritance_chain(class_info, classes)
        implementations = [item for item in chain if phase in item.methods]
        if not implementations:
            return []

        active = [implementations[-1]]
        current = implementations[-1]
        for parent in reversed(implementations[:-1]):
            if not current.methods[phase].calls_super:
                break
            active.append(parent)
            current = parent
        active.reverse()
        return active


def _expression_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _expression_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    if isinstance(node, ast.Subscript):
        return _expression_name(node.value)
    try:
        return ast.unparse(node)
    except (RecursionError, ValueError):
        return ""


def _self_attribute(node: ast.AST) -> str | None:
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return node.attr
    return None


def _is_test_decorated(node: ast.ClassDef) -> bool:
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        name = _expression_name(target)
        if name == "test" or name.endswith(".test"):
            return True
    return False


def _calls_super_method(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    for call in ast.walk(node):
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
            continue
        if call.func.attr != name:
            continue
        value = call.func.value
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "super"
        ):
            return True
    return False
