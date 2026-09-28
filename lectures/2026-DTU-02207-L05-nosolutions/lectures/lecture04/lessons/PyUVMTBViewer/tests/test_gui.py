import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication, QGraphicsTextItem

from PyUVMTBViewer.main_window import MainWindow

FIXTURE = Path(__file__).parent / "fixtures" / "top_test.py"
CONFIG_FIXTURE = Path(__file__).parent / "fixtures" / "viewer.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
E07_CONFIG = (
    REPOSITORY_ROOT
    / "exercises"
    / "E07_sat_pyuvm_uvc_integraion"
    / "PyUVMTBViewer.json"
)


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_loads_fixture_into_all_panes(self):
        window = MainWindow()
        self.assertTrue(window.load_file(FIXTURE))
        self.assertEqual(window.component_tree.topLevelItemCount(), 1)
        self.assertTrue(window.source_view.toPlainText())
        self.assertTrue(window.hierarchy_view.scene().items())
        self.assertTrue(window.phase_view.view.scene().items())
        window.close()

    def test_selecting_phase_highlights_source(self):
        window = MainWindow()
        self.assertTrue(window.load_file(FIXTURE))
        root = window.component_tree.topLevelItem(0)
        build_phase = next(
            root.child(index)
            for index in range(root.childCount())
            if root.child(index).text(0) == "build_phase"
        )
        window.component_tree.setCurrentItem(build_phase)
        self.application.processEvents()
        self.assertTrue(window.source_view.extraSelections())
        self.assertIn("def build_phase", window.source_view.toPlainText())
        window.close()

    def test_hierarchy_boxes_show_class_and_derivation_rows(self):
        window = MainWindow()
        self.assertTrue(window.load_file(FIXTURE))
        labels = {
            item.toPlainText()
            for item in window.hierarchy_view.scene().items()
            if isinstance(item, QGraphicsTextItem)
        }
        self.assertIn("DemoTest", labels)
        self.assertIn("Class: DemoTest", labels)
        self.assertIn("derivation list:\n  DemoBaseTest\n  uvm_test", labels)
        window.close()

    def test_loads_json_and_disables_grey_hierarchy(self):
        window = MainWindow()
        self.assertTrue(window.load_input(CONFIG_FIXTURE))
        root = window.component_tree.topLevelItem(0)
        environment = next(
            root.child(index)
            for index in range(root.childCount())
            if root.child(index).text(0) == "environment"
        )
        grey_item = next(
            environment.child(index)
            for index in range(environment.childCount())
            if environment.child(index).text(0) == "consumer"
        )
        self.assertTrue(grey_item.isDisabled())
        self.assertEqual(grey_item.childCount(), 0)
        window.close()

    def test_e07_driver_uses_one_derivation_list_field(self):
        window = MainWindow()
        self.assertTrue(window.load_input(E07_CONFIG))
        labels = {
            item.toPlainText()
            for item in window.hierarchy_view.scene().items()
            if isinstance(item, QGraphicsTextItem)
        }
        self.assertIn(
            "derivation list:\n  uvc_ssdt_base_driver\n  uvm_driver",
            labels,
        )
        window.close()

    def test_graph_panes_support_zoom_controls(self):
        window = MainWindow()
        self.assertTrue(window.load_file(FIXTURE))
        for view in (window.hierarchy_view.view, window.phase_view.view):
            self.assertAlmostEqual(view.transform().m11(), 1.0)
            view.zoom_in()
            self.assertGreater(view.transform().m11(), 1.0)
            view.zoom_out()
            self.assertAlmostEqual(view.transform().m11(), 1.0)
            view.zoom_fit()
            self.assertGreater(view.transform().m11(), 0.0)
            view.zoom_100()
            self.assertAlmostEqual(view.transform().m11(), 1.0)
        window.close()


if __name__ == "__main__":
    unittest.main()
