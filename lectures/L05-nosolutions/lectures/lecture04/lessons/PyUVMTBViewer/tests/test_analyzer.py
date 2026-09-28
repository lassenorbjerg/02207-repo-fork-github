import unittest
from pathlib import Path
from unittest.mock import patch

from PyUVMTBViewer.analyzer import PyUVMAnalyzer
from PyUVMTBViewer.config import load_viewer_config
from PyUVMTBViewer.llm_analyzer import (
    ConditionalResolution,
    LLMAnalysisResult,
)

FIXTURE = Path(__file__).parent / "fixtures" / "top_test.py"
CONFIG_FIXTURE = Path(__file__).parent / "fixtures" / "viewer.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
E07_TOP = (
    REPOSITORY_ROOT
    / "exercises"
    / "E07_sat_pyuvm_uvc_integraion"
    / "tb"
    / "sat_tb_default_test.py"
)
E07_EXPERIMENTAL_CONFIG = (
    REPOSITORY_ROOT
    / "exercises"
    / "E07_sat_pyuvm_uvc_integraion"
    / "PyUVMTBViewer_experimental.json"
)


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.result = PyUVMAnalyzer().analyze(FIXTURE)

    def test_finds_top_test_and_inherited_phases(self):
        self.assertEqual(self.result.top_class.name, "DemoTest")
        self.assertEqual(
            self.result.phases,
            ["build_phase", "connect_phase", "run_phase"],
        )

    def test_builds_component_instance_hierarchy(self):
        root = self.result.root
        self.assertEqual([child.instance_name for child in root.children], ["environment"])
        environment = root.children[0]
        self.assertEqual(
            [child.instance_name for child in environment.children],
            ["producer", "consumer"],
        )
        for agent in environment.children:
            self.assertEqual(
                [child.instance_name for child in agent.children],
                ["driver", "driver", "sequencer", "monitor"],
            )
            self.assertEqual(
                [child.class_name for child in agent.children[:2]],
                ["DemoProducerDriver", "DemoConsumerDriver"],
            )
            self.assertTrue(agent.children[0].conditional)
            self.assertTrue(agent.children[1].conditional)
            self.assertFalse(agent.children[2].conditional)
            self.assertTrue(agent.children[3].conditional)

    def test_records_connect_calls(self):
        environment_class = next(
            item
            for item in self.result.classes.values()
            if item.name == "DemoEnvironment"
        )
        expressions = [item.expression for item in environment_class.connections]
        self.assertIn(
            "self.producer.analysis_port.connect(self.consumer.analysis_export)",
            expressions,
        )

    def test_resolves_e07_agents_from_shared_common_directory(self):
        result = PyUVMAnalyzer().analyze(E07_TOP)
        environment = next(
            node for node in result.root.children if node.class_name == "sat_tb_env"
        )
        self.assertEqual(
            [child.instance_name for child in environment.children],
            ["sat_tb_top_seqr", "uvc_ssdt_producer", "uvc_ssdt_consumer"],
        )
        for agent in environment.children[1:]:
            self.assertEqual(agent.class_name, "uvc_ssdt_agent")
            self.assertEqual(
                {child.instance_name for child in agent.children},
                {"driver", "sequencer", "monitor", "coverage"},
            )

    def test_json_config_resolves_paths_and_rendering_rules(self):
        config = load_viewer_config(CONFIG_FIXTURE)
        result = PyUVMAnalyzer().analyze(
            config.top_level_uvm_test,
            include_dirs=config.include_dirs,
            instance_rendering=config.instance_rendering,
        )
        environment = result.root.children[0]
        producer, consumer = environment.children
        self.assertEqual(
            [child.class_name for child in producer.children],
            ["DemoProducerDriver", "uvm_sequencer"],
        )
        self.assertFalse(producer.children[0].conditional)
        self.assertEqual(consumer.render_mode, "grey")
        self.assertEqual(consumer.visible_children, [])

    def test_experimental_config_accepts_an_empty_key_template(self):
        config = load_viewer_config(E07_EXPERIMENTAL_CONFIG)

        self.assertTrue(config.experimental)
        self.assertEqual(config.openai_api_key, "")
        self.assertEqual(config.openai_model, "gpt-5-mini")
        self.assertNotIn(
            "conditional",
            " ".join(config.instance_rendering.values()),
        )

    @patch("PyUVMTBViewer.llm_analyzer.LLMConditionalAnalyzer")
    def test_experimental_results_resolve_static_conditionals(self, backend_class):
        backend_class.return_value.analyze.return_value = LLMAnalysisResult(
            (
                ConditionalResolution(
                    "DemoTest.environment.producer.driver",
                    True,
                    "DemoProducerDriver",
                    "Producer configuration",
                ),
                ConditionalResolution(
                    "DemoTest.environment.producer.monitor",
                    False,
                    "",
                    "Coverage disabled",
                ),
                ConditionalResolution(
                    "DemoTest.environment.consumer.driver",
                    True,
                    "DemoConsumerDriver",
                    "Consumer configuration",
                ),
                ConditionalResolution(
                    "DemoTest.environment.consumer.monitor",
                    False,
                    "",
                    "Coverage disabled",
                ),
            )
        )

        result = PyUVMAnalyzer().analyze(
            FIXTURE,
            experimental=True,
            openai_api_key="test-key",
        )

        producer, consumer = result.root.children[0].children
        self.assertEqual(
            [child.class_name for child in producer.children],
            ["DemoProducerDriver", "uvm_sequencer"],
        )
        self.assertEqual(
            [child.class_name for child in consumer.children],
            ["DemoConsumerDriver", "uvm_sequencer"],
        )
        self.assertFalse(producer.children[0].conditional)
        backend_class.assert_called_once_with("test-key", "gpt-5-mini")


if __name__ == "__main__":
    unittest.main()
