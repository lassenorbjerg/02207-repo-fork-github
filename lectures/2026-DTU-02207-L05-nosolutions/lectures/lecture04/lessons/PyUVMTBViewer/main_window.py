"""Main window for the PyUVM testbench viewer."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QGroupBox,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .analyzer import AnalysisError, MultipleTestsError, PyUVMAnalyzer
from .config import ConfigurationError, load_viewer_config
from .models import ComponentNode, MethodInfo, effective_display_methods
from .widgets import HierarchyView, PhaseView, SourceView

_ITEM_DATA_ROLE = Qt.UserRole


class MainWindow(QMainWindow):
    """Four-pane viewer matching the supplied main-window sketch."""

    def __init__(self, initial_file: str | Path | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyUVM Testbench Viewer")
        self.resize(1450, 900)

        self.analyzer = PyUVMAnalyzer()
        self.result = None
        self._tree_items: dict[tuple[str, str | None], QTreeWidgetItem] = {}
        self._selected_node: ComponentNode | None = None

        self.component_tree = QTreeWidget()
        self.component_tree.setHeaderLabels(["Component / phase", "Type"])
        self.component_tree.setAlternatingRowColors(True)
        self.component_tree.currentItemChanged.connect(self._tree_selection_changed)

        self.source_view = SourceView()
        self.hierarchy_view = HierarchyView()
        self.phase_view = PhaseView()
        self.hierarchy_view.componentSelected.connect(self._select_component)
        self.phase_view.componentSelected.connect(self._select_component)
        self.phase_view.phaseSelected.connect(self._select_phase)

        self.setCentralWidget(self._build_layout())
        self._create_menu()
        self.statusBar().showMessage("Open a top-level PyUVM test file to begin.")

        if initial_file is not None:
            self.load_input(initial_file)

    def _build_layout(self) -> QWidget:
        root_splitter = QSplitter(Qt.Horizontal)
        right_splitter = QSplitter(Qt.Vertical)
        upper_right_splitter = QSplitter(Qt.Horizontal)

        root_splitter.addWidget(self._pane("A – Components and phases", self.component_tree))
        root_splitter.addWidget(right_splitter)
        upper_right_splitter.addWidget(self._pane("B – Source code", self.source_view))
        upper_right_splitter.addWidget(
            self._pane("C – Component hierarchy", self.hierarchy_view)
        )
        right_splitter.addWidget(upper_right_splitter)
        right_splitter.addWidget(self._pane("D – Phase view", self.phase_view))

        root_splitter.setSizes([330, 1120])
        upper_right_splitter.setSizes([620, 500])
        right_splitter.setSizes([570, 330])
        root_splitter.setStretchFactor(0, 0)
        root_splitter.setStretchFactor(1, 1)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(root_splitter)
        return container

    @staticmethod
    def _pane(title: str, widget: QWidget) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 8, 5, 5)
        layout.addWidget(widget)
        return group

    def _create_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        open_action = QAction("&Open viewer input…", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open PyUVM viewer input",
            "",
            "Viewer configurations (*.json);;Python files (*.py);;All files (*)",
        )
        if filename:
            self.load_input(filename)

    def load_input(self, filename: str | Path) -> bool:
        path = Path(filename).expanduser().resolve()
        if path.suffix.lower() != ".json":
            return self.load_file(path)
        try:
            config = load_viewer_config(path)
        except ConfigurationError as error:
            QMessageBox.critical(self, "Invalid viewer configuration", str(error))
            self.statusBar().showMessage(str(error))
            return False
        return self.load_file(
            config.top_level_uvm_test,
            include_dirs=config.include_dirs,
            instance_rendering=config.instance_rendering,
            input_path=config.path,
            experimental=config.experimental,
            openai_api_key=config.openai_api_key,
            openai_model=config.openai_model,
        )

    def load_file(
        self,
        filename: str | Path,
        top_class_name: str | None = None,
        include_dirs: list[str | Path] | None = None,
        instance_rendering: dict[str, str] | None = None,
        input_path: str | Path | None = None,
        experimental: bool = False,
        openai_api_key: str = "",
        openai_model: str = "gpt-5-mini",
    ) -> bool:
        path = Path(filename).expanduser().resolve()
        try:
            self.result = self.analyzer.analyze(
                path,
                top_class_name,
                include_dirs=include_dirs,
                instance_rendering=instance_rendering,
                experimental=experimental,
                openai_api_key=openai_api_key,
                openai_model=openai_model,
            )
        except MultipleTestsError as error:
            selection, accepted = QInputDialog.getItem(
                self,
                "Select PyUVM test",
                "Test class:",
                error.candidates,
                0,
                False,
            )
            if not accepted:
                return False
            return self.load_file(
                path,
                selection,
                include_dirs,
                instance_rendering,
                input_path,
                experimental,
                openai_api_key,
                openai_model,
            )
        except AnalysisError as error:
            QMessageBox.critical(self, "Analysis failed", str(error))
            self.statusBar().showMessage(str(error))
            return False

        self._populate_tree()
        self.hierarchy_view.set_analysis(self.result)
        self.phase_view.set_analysis(self.result)
        self.setWindowTitle(
            f"PyUVM Testbench Viewer – {self.result.top_class.name}"
        )
        warning_text = " | ".join(self.result.warnings)
        loaded_path = Path(input_path).resolve() if input_path else path
        message = f"Loaded {loaded_path}"
        if warning_text:
            message += f" — {warning_text}"
        self.statusBar().showMessage(message)
        self._select_component(self.result.root)
        return True

    def _populate_tree(self):
        self.component_tree.clear()
        self._tree_items.clear()

        def add_node(node: ComponentNode, parent_item: QTreeWidgetItem | None):
            label = node.instance_name + (" (conditional)" if node.conditional else "")
            item = QTreeWidgetItem([label, node.class_name])
            item.setData(0, _ITEM_DATA_ROLE, (node, None))
            if node.render_mode == "grey":
                grey_brush = QBrush(QColor("#8a8a8a"))
                item.setForeground(0, grey_brush)
                item.setForeground(1, grey_brush)
                item.setDisabled(True)
            if parent_item is None:
                self.component_tree.addTopLevelItem(item)
            else:
                parent_item.addChild(item)
            self._tree_items[(node.path, None)] = item

            methods = (
                []
                if node.render_mode == "grey"
                else effective_display_methods(node.class_info, self.result.classes)
            )
            for method in methods:
                child = QTreeWidgetItem([method.name, "phase" if method.name.endswith("_phase") else "method"])
                child.setData(0, _ITEM_DATA_ROLE, (node, method))
                item.addChild(child)
                self._tree_items[(node.path, method.name)] = child

            for component in node.visible_children:
                add_node(component, item)

        add_node(self.result.root, None)
        self.component_tree.expandToDepth(1)
        self.component_tree.resizeColumnToContents(0)

    def _tree_selection_changed(self, current, _previous):
        if current is None:
            return
        data = current.data(0, _ITEM_DATA_ROLE)
        if not data:
            return
        node, method = data
        self._selected_node = node
        self.source_view.show_component(node, method)
        self.hierarchy_view.set_selected(node)
        phase = method.name if isinstance(method, MethodInfo) and method.name.endswith("_phase") else None
        self.phase_view.set_selection(node, phase)

    def _select_component(self, node: ComponentNode):
        item = self._tree_items.get((node.path, None))
        if item is not None:
            self.component_tree.setCurrentItem(item)
            self.component_tree.scrollToItem(item)

    def _select_phase(self, phase: str):
        node = self._selected_node or (self.result.root if self.result else None)
        if node is None:
            return
        item = self._tree_items.get((node.path, phase))
        if item is None and self.result is not None:
            item = self._tree_items.get((self.result.root.path, phase))
        if item is not None:
            self.component_tree.setCurrentItem(item)
            self.component_tree.scrollToItem(item)
