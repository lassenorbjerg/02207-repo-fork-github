"""Data models shared by the analyzer and user interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PHASE_ORDER = (
    "build_phase",
    "connect_phase",
    "end_of_elaboration_phase",
    "start_of_simulation_phase",
    "run_phase",
    "extract_phase",
    "check_phase",
    "report_phase",
    "final_phase",
)

DISPLAY_METHODS = ("__init__",) + PHASE_ORDER

UVM_COMPONENT_BASES = {
    "uvm_component",
    "uvm_test",
    "uvm_env",
    "uvm_agent",
    "uvm_driver",
    "uvm_monitor",
    "uvm_scoreboard",
    "uvm_subscriber",
    "uvm_sequencer",
}


@dataclass
class MethodInfo:
    """A method and its source location."""

    name: str
    path: Path
    line: int
    end_line: int
    calls_super: bool = False


@dataclass
class CreationInfo:
    """A component creation found in a phase method."""

    attribute: str
    class_name: str
    instance_name: str
    path: Path
    line: int
    conditional: bool = False


@dataclass
class ConnectionInfo:
    """A connect call found in connect_phase."""

    expression: str
    path: Path
    line: int


@dataclass
class ClassInfo:
    """A Python class relevant to the analyzed testbench."""

    name: str
    bases: list[str]
    path: Path
    line: int
    end_line: int
    methods: dict[str, MethodInfo] = field(default_factory=dict)
    creations: dict[str, list[CreationInfo]] = field(default_factory=dict)
    connections: list[ConnectionInfo] = field(default_factory=list)
    decorated_test: bool = False
    is_component: bool = False

    @property
    def key(self) -> str:
        return f"{self.path}:{self.name}"


@dataclass
class ComponentNode:
    """An inferred PyUVM component instance."""

    instance_name: str
    class_name: str
    class_info: ClassInfo | None
    parent: ComponentNode | None = field(default=None, repr=False)
    children: list[ComponentNode] = field(default_factory=list)
    conditional: bool = False
    render_mode: str = "normal"

    @property
    def path(self) -> str:
        segment = f"{self.instance_name}<{self.class_name}>"
        if self.parent is None:
            return segment
        return f"{self.parent.path}.{segment}"

    @property
    def instance_path(self) -> str:
        if self.parent is None:
            return self.instance_name
        return f"{self.parent.instance_path}.{self.instance_name}"

    @property
    def visible_children(self) -> list[ComponentNode]:
        if self.render_mode == "grey":
            return []
        return self.children

    def walk(self):
        yield self
        for child in self.visible_children:
            yield from child.walk()


@dataclass
class AnalysisResult:
    """Complete result returned by the static analyzer."""

    selected_file: Path
    top_class: ClassInfo
    root: ComponentNode
    classes: dict[str, ClassInfo]
    warnings: list[str] = field(default_factory=list)

    @property
    def phases(self) -> list[str]:
        present = {
            method.name
            for node in self.root.walk()
            for method in effective_display_methods(node.class_info, self.classes)
            if method.name in PHASE_ORDER
        }
        return [phase for phase in PHASE_ORDER if phase in present]


def effective_display_methods(
    class_info: ClassInfo | None,
    classes: dict[str, ClassInfo],
) -> list[MethodInfo]:
    """Return the visible initialization/phase methods for a class instance."""

    if class_info is None:
        return []

    visible: dict[str, MethodInfo] = {}
    for current in inheritance_chain(class_info, classes):
        for name, method in current.methods.items():
            if name in DISPLAY_METHODS:
                visible[name] = method
    return [visible[name] for name in DISPLAY_METHODS if name in visible]


def inheritance_chain(
    class_info: ClassInfo | None,
    classes: dict[str, ClassInfo],
) -> list[ClassInfo]:
    """Return known ancestors followed by the supplied class."""

    if class_info is None:
        return []

    by_name = {item.name: item for item in classes.values()}
    chain: list[ClassInfo] = []
    visited: set[str] = set()

    def visit(current: ClassInfo):
        if current.key in visited:
            return
        visited.add(current.key)
        for base in current.bases:
            parent = by_name.get(base.rsplit(".", 1)[-1])
            if parent is not None:
                visit(parent)
                break
        chain.append(current)

    visit(class_info)
    return chain
