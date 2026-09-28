"""Reusable PyQt5 widgets for the PyUVM testbench viewer."""

from __future__ import annotations

import keyword
import math
from collections import defaultdict

from PyQt5.QtCore import QPointF, QRegularExpression, Qt, pyqtSignal
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPen,
    QPolygonF,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PyQt5.QtWidgets import (
    QComboBox,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .models import (
    AnalysisResult,
    ComponentNode,
    MethodInfo,
    inheritance_chain,
)


class PythonHighlighter(QSyntaxHighlighter):
    """Small dependency-free Python syntax highlighter."""

    def __init__(self, document):
        super().__init__(document)
        self.rules: list[tuple[QRegularExpression, QTextCharFormat]] = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#005cc5"))
        keyword_format.setFontWeight(QFont.Bold)
        for word in keyword.kwlist + ["self"]:
            self.rules.append(
                (QRegularExpression(rf"\b{word}\b"), keyword_format)
            )

        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#6f42c1"))
        class_format.setFontWeight(QFont.Bold)
        self.rules.append(
            (QRegularExpression(r"\b(class|def|async\s+def)\s+(\w+)"), class_format)
        )

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#22863a"))
        self.rules.extend(
            [
                (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format),
                (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
            ]
        )

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a737d"))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r"#[^\n]*"), comment_format))

    def highlightBlock(self, text: str):
        for expression, text_format in self.rules:
            match = expression.globalMatch(text)
            while match.hasNext():
                result = match.next()
                self.setFormat(
                    result.capturedStart(),
                    result.capturedLength(),
                    text_format,
                )


class SourceView(QPlainTextEdit):
    """Read-only source pane with method highlighting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFont(QFont("monospace", 10))
        self.setPlaceholderText("Select a component to view its source code.")
        self.highlighter = PythonHighlighter(self.document())

    def show_component(
        self,
        node: ComponentNode | None,
        method: MethodInfo | None = None,
    ):
        if node is None or node.class_info is None:
            self.clear()
            self.setPlaceholderText("Source is unavailable for this PyUVM base class.")
            return

        class_info = node.class_info
        source_path = (
            method.path
            if method is not None and method.path != class_info.path
            else class_info.path
        )
        try:
            lines = source_path.read_text(encoding="utf-8").splitlines()
        except OSError as error:
            self.setPlainText(str(error))
            return

        if method is not None and method.path != class_info.path:
            class_lines = lines[method.line - 1 : method.end_line]
            first_source_line = method.line
            self.setToolTip(f"{method.path} (inherited by {class_info.name})")
        else:
            class_lines = lines[class_info.line - 1 : class_info.end_line]
            first_source_line = class_info.line
            self.setToolTip(str(class_info.path))
        self.setPlainText("\n".join(class_lines))
        self.setExtraSelections([])

        if method is None:
            self.moveCursor(QTextCursor.Start)
            return

        relative_line = max(0, method.line - first_source_line)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, relative_line)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor("#fff3a3"))
        self.setExtraSelections([selection])
        self.setTextCursor(cursor)
        self.centerCursor()


class _ClickableBox(QGraphicsRectItem):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.callback is not None:
            self.callback()


class ZoomableGraphicsView(QGraphicsView):
    """Graphics view with bounded zoom and Ctrl+wheel support."""

    zoomChanged = pyqtSignal(int)
    _STEP = 1.2
    _MINIMUM = 0.2
    _MAXIMUM = 5.0

    def zoom_in(self):
        self._set_zoom(self.transform().m11() * self._STEP)

    def zoom_out(self):
        self._set_zoom(self.transform().m11() / self._STEP)

    def zoom_fit(self):
        if self.scene() is None or not self.scene().items():
            return
        bounds = self.scene().itemsBoundingRect().adjusted(-15, -15, 15, 15)
        self.fitInView(bounds, Qt.KeepAspectRatio)
        self._emit_zoom()

    def zoom_100(self):
        self.resetTransform()
        self._emit_zoom()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    def _set_zoom(self, target: float):
        target = min(self._MAXIMUM, max(self._MINIMUM, target))
        current = self.transform().m11()
        if current:
            factor = target / current
            self.scale(factor, factor)
        self._emit_zoom()

    def _emit_zoom(self):
        self.zoomChanged.emit(round(self.transform().m11() * 100))


def _add_zoom_controls(layout: QHBoxLayout, view: ZoomableGraphicsView):
    actions = (
        ("Zoom In", view.zoom_in),
        ("Zoom Out", view.zoom_out),
        ("Zoom Fit", view.zoom_fit),
        ("Zoom 100%", view.zoom_100),
    )
    for text, callback in actions:
        button = QToolButton()
        button.setText(text)
        button.setToolTip(text)
        button.clicked.connect(callback)
        layout.addWidget(button)
    percentage = QLabel("100%")
    percentage.setMinimumWidth(42)
    percentage.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    view.zoomChanged.connect(lambda value: percentage.setText(f"{value}%"))
    layout.addWidget(percentage)


def _add_centered_text(
    scene,
    rectangle,
    text,
    bold=False,
    color="#24292e",
    align_left=False,
):
    item = QGraphicsTextItem(text)
    longest_line = max((len(line) for line in text.splitlines()), default=1)
    point_size = max(6, min(9, int(180 / longest_line)))
    font = QFont("Sans Serif", point_size)
    font.setBold(bold)
    item.setFont(font)
    item.setDefaultTextColor(QColor(color))
    item.setAcceptedMouseButtons(Qt.NoButton)
    bounds = item.boundingRect()
    x_position = (
        rectangle.x() + 7
        if align_left
        else rectangle.x() + (rectangle.width() - bounds.width()) / 2
    )
    item.setPos(
        x_position,
        rectangle.y() + (rectangle.height() - bounds.height()) / 2,
    )
    scene.addItem(item)
    return item


def _add_arrow(scene, x1, y1, x2, y2, color="#6a737d"):
    pen = QPen(QColor(color))
    line = scene.addLine(x1, y1, x2, y2, pen)
    line.setZValue(-1)
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_size = 8
    first = QPointF(
        x2 - arrow_size * math.cos(angle - math.pi / 6),
        y2 - arrow_size * math.sin(angle - math.pi / 6),
    )
    second = QPointF(
        x2 - arrow_size * math.cos(angle + math.pi / 6),
        y2 - arrow_size * math.sin(angle + math.pi / 6),
    )
    arrow = scene.addPolygon(
        QPolygonF([QPointF(x2, y2), first, second]),
        pen,
        QBrush(QColor(color)),
    )
    arrow.setZValue(-1)


class HierarchyView(QWidget):
    """Graphics view showing the inferred component hierarchy."""

    componentSelected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self._scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self._result: AnalysisResult | None = None
        self._selected_path: str | None = None

        toolbar = QHBoxLayout()
        toolbar.addStretch(1)
        _add_zoom_controls(toolbar, self.view)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addLayout(toolbar)
        layout.addWidget(self.view)

    def scene(self):
        return self._scene

    def set_analysis(self, result: AnalysisResult | None):
        self._result = result
        self._selected_path = result.root.path if result else None
        self.view.zoom_100()
        self.redraw()

    def set_selected(self, node: ComponentNode | None):
        self._selected_path = node.path if node else None
        self.redraw()

    def redraw(self):
        self._scene.clear()
        if self._result is None:
            return

        levels: dict[int, list[ComponentNode]] = defaultdict(list)

        def collect(node: ComponentNode, depth: int):
            levels[depth].append(node)
            for child in node.visible_children:
                collect(child, depth + 1)

        collect(self._result.root, 0)
        boxes: dict[str, QGraphicsRectItem] = {}
        width = 215

        for depth, nodes in sorted(levels.items()):
            y = 25
            for node in nodes:
                derivations = self._derivation_labels(node)
                derivation_lines = ["derivation list:"]
                derivation_lines.extend(
                    f"  {derivation}" for derivation in derivations
                )
                if not derivations:
                    derivation_lines.append("  (none)")
                derivation_text = "\n".join(derivation_lines)
                derivation_height = 20 + 20 * len(derivation_lines)
                row_heights = [30, 28, derivation_height]
                height = sum(row_heights)
                x = 25 + depth * 265
                box = _ClickableBox(
                    x,
                    y,
                    width,
                    height,
                    callback=lambda selected=node: self.componentSelected.emit(selected),
                )
                if node.render_mode == "grey":
                    fill_color = "#dddddd"
                elif node.path == self._selected_path:
                    fill_color = "#fff3a3"
                else:
                    fill_color = "#eaf2f8"
                box.setBrush(QBrush(QColor(fill_color)))
                box.setPen(
                    QPen(
                        QColor(
                            "#b08800"
                            if node.path == self._selected_path
                            else "#4a6b82"
                        )
                    )
                )
                self._scene.addItem(box)
                boxes[node.path] = box
                suffix = " ?" if node.conditional else ""
                row_top = y
                title_rect = box.rect()
                title_rect.setTop(row_top)
                title_rect.setHeight(row_heights[0])
                _add_centered_text(
                    self._scene,
                    title_rect,
                    node.instance_name + suffix,
                    bold=True,
                    align_left=True,
                )
                row_top += row_heights[0]

                rows = [f"Class: {node.class_name}", derivation_text]
                for row_index, row_text in enumerate(rows):
                    self._scene.addLine(
                        x,
                        row_top,
                        x + width,
                        row_top,
                        QPen(QColor("#9aa0a6")),
                    )
                    row_rect = box.rect()
                    row_rect.setTop(row_top)
                    row_rect.setHeight(row_heights[row_index + 1])
                    _add_centered_text(
                        self._scene,
                        row_rect,
                        row_text,
                        align_left=True,
                    )
                    row_top += row_heights[row_index + 1]
                y += height + 30

        for node in self._result.root.walk():
            if node.parent is None:
                continue
            parent_box = boxes[node.parent.path].rect()
            child_box = boxes[node.path].rect()
            self._scene.addLine(
                parent_box.right(),
                parent_box.center().y(),
                child_box.left(),
                child_box.center().y(),
                QPen(QColor("#6a737d")),
            )

        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))

    def _derivation_labels(self, node: ComponentNode) -> list[str]:
        if node.class_info is None:
            return []

        chain = inheritance_chain(node.class_info, self._result.classes)
        labels = [item.name for item in reversed(chain[:-1])]
        if chain:
            known_names = {item.name for item in self._result.classes.values()}
            for base in chain[0].bases:
                short_name = base.rsplit(".", 1)[-1]
                if short_name not in known_names:
                    labels.append(short_name)
                    break
        return labels


class PhaseView(QWidget):
    """Phase selector and diagrams for all/build/connect views."""

    componentSelected = pyqtSignal(object)
    phaseSelected = pyqtSignal(str)

    ALL_PHASES = "All phases"
    BUILD_PHASE = "build_phase"
    CONNECT_PHASE = "connect_phase"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: AnalysisResult | None = None
        self._selected_node: ComponentNode | None = None
        self._selected_phase: str | None = None

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("View:"))
        self.selector = QComboBox()
        self.selector.addItems(
            [self.ALL_PHASES, self.BUILD_PHASE, self.CONNECT_PHASE]
        )
        toolbar.addWidget(self.selector)
        toolbar.addStretch(1)

        self._scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self._scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        _add_zoom_controls(toolbar, self.view)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addLayout(toolbar)
        layout.addWidget(self.view)
        self.selector.currentTextChanged.connect(self.redraw)

    def set_analysis(self, result: AnalysisResult | None):
        self._result = result
        self._selected_node = result.root if result else None
        self._selected_phase = None
        self.view.zoom_100()
        self.selector.setCurrentText(self.ALL_PHASES)
        self.redraw()

    def set_selection(
        self,
        node: ComponentNode | None,
        phase: str | None,
    ):
        self._selected_node = node
        self._selected_phase = phase
        self.redraw()

    def redraw(self):
        self._scene.clear()
        if self._result is None:
            return
        if self.selector.currentText() == self.ALL_PHASES:
            self._draw_all_phases()
        else:
            self._draw_component_phase(self.selector.currentText())
        if self._scene.items():
            self._scene.setSceneRect(
                self._scene.itemsBoundingRect().adjusted(-25, -25, 25, 25)
            )

    def _draw_all_phases(self):
        width, height, spacing = 155, 55, 55
        previous = None
        for index, phase in enumerate(self._result.phases):
            x = 25 + index * (width + spacing)
            y = 35
            box = _ClickableBox(
                x,
                y,
                width,
                height,
                callback=lambda selected=phase: self._activate_phase(selected),
            )
            selected = phase == self._selected_phase
            box.setBrush(QBrush(QColor("#fff3a3" if selected else "#e8f5e9")))
            box.setPen(QPen(QColor("#b08800" if selected else "#4f7c54")))
            self._scene.addItem(box)
            _add_centered_text(self._scene, box.rect(), phase, bold=True)
            if previous is not None:
                _add_arrow(
                    self._scene,
                    previous.right(),
                    previous.center().y(),
                    box.rect().left(),
                    box.rect().center().y(),
                )
            previous = box.rect()

    def _activate_phase(self, phase: str):
        self._selected_phase = phase
        self.phaseSelected.emit(phase)
        if phase in (self.BUILD_PHASE, self.CONNECT_PHASE):
            self.selector.setCurrentText(phase)
        else:
            self.redraw()

    def _draw_component_phase(self, phase: str):
        levels: dict[int, list[ComponentNode]] = defaultdict(list)

        def collect(node: ComponentNode, depth: int):
            levels[depth].append(node)
            for child in node.visible_children:
                collect(child, depth + 1)

        collect(self._result.root, 0)
        maximum_depth = max(levels, default=0)
        positions: dict[str, tuple[float, float, float, float]] = {}
        level_bounds: dict[int, tuple[float, float, float, float]] = {}

        for depth, nodes in sorted(levels.items()):
            x_depth = maximum_depth - depth if phase == self.CONNECT_PHASE else depth
            x = 45 + x_depth * 235
            y = 55
            left, top, right, bottom = x - 12, y - 12, x + 180, y
            for node in nodes:
                labels = self._inheritance_labels(node)
                box_height = 31 + max(1, len(labels)) * 25
                outer = _ClickableBox(
                    x,
                    y,
                    170,
                    box_height,
                    callback=lambda selected=node: self.componentSelected.emit(selected),
                )
                selected = (
                    self._selected_node is not None
                    and node.path == self._selected_node.path
                    and (self._selected_phase in (None, phase))
                )
                if node.render_mode == "grey":
                    fill_color = "#dddddd"
                else:
                    fill_color = "#fff3a3" if selected else "#f6f8fa"
                outer.setBrush(QBrush(QColor(fill_color)))
                outer.setPen(QPen(QColor("#b08800" if selected else "#586069")))
                self._scene.addItem(outer)
                title_rect = outer.rect()
                title_rect.setHeight(28)
                _add_centered_text(
                    self._scene,
                    title_rect,
                    node.instance_name + (" ?" if node.conditional else ""),
                    bold=True,
                )

                for label_index, label in enumerate(labels):
                    label_rect = outer.rect()
                    label_rect.setTop(y + 29 + label_index * 25)
                    label_rect.setHeight(24)
                    self._scene.addLine(
                        x,
                        label_rect.top(),
                        x + 170,
                        label_rect.top(),
                        QPen(QColor("#d1d5da")),
                    )
                    _add_centered_text(self._scene, label_rect, label)

                positions[node.path] = (x, y, 170, box_height)
                right = max(right, x + 182)
                bottom = max(bottom, y + box_height + 12)
                y += box_height + 28
            level_bounds[depth] = (left, top, right - left, bottom - top)

        dashed_pen = QPen(QColor("#9aa0a6"), 1, Qt.DashLine)
        for depth, (x, y, width, height) in level_bounds.items():
            group = self._scene.addRect(x, y, width, height, dashed_pen)
            group.setZValue(-2)
            label = self._scene.addText(f"Hierarchy level {depth}")
            label.setDefaultTextColor(QColor("#6a737d"))
            label.setPos(x + 5, y - 23)

        for node in self._result.root.walk():
            if node.parent is None:
                continue
            parent = positions[node.parent.path]
            child = positions[node.path]
            if phase == self.CONNECT_PHASE:
                start = (child[0] + child[2], child[1] + child[3] / 2)
                end = (parent[0], parent[1] + parent[3] / 2)
            else:
                start = (parent[0] + parent[2], parent[1] + parent[3] / 2)
                end = (child[0], child[1] + child[3] / 2)
            _add_arrow(self._scene, *start, *end)

    def _inheritance_labels(self, node: ComponentNode) -> list[str]:
        if node.class_info is None:
            return [node.class_name]
        chain = inheritance_chain(node.class_info, self._result.classes)
        labels = [item.name for item in chain]
        if chain:
            known_names = {item.name for item in self._result.classes.values()}
            for base in chain[0].bases:
                short_name = base.rsplit(".", 1)[-1]
                if short_name not in known_names:
                    labels.insert(0, short_name)
                    break
        return labels or [node.class_name]
