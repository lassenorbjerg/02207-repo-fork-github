import json
import unittest
from types import SimpleNamespace

from PyUVMTBViewer.llm_analyzer import (
    ConditionalCandidate,
    LLMAnalysisError,
    LLMConditionalAnalyzer,
)


class _FakeResponses:
    def __init__(self, payload):
        self.payload = payload
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_text=json.dumps(self.payload))


class LLMAnalyzerTests(unittest.TestCase):
    def test_returns_validated_stable_resolutions(self):
        responses = _FakeResponses(
            {
                "resolutions": [
                    {
                        "instance_path": "DemoTest.env.agent.driver",
                        "include": True,
                        "selected_class": "ProducerDriver",
                        "rationale": "The agent configuration selects PRODUCER.",
                    },
                    {
                        "instance_path": "DemoTest.env.agent.monitor",
                        "include": False,
                        "selected_class": "",
                        "rationale": "Coverage is disabled.",
                    },
                ]
            }
        )
        client = SimpleNamespace(responses=responses)
        candidates = [
            ConditionalCandidate(
                "DemoTest.env.agent.driver",
                ("ProducerDriver", "ConsumerDriver"),
            ),
            ConditionalCandidate(
                "DemoTest.env.agent.monitor",
                ("DemoMonitor",),
            ),
        ]

        result = LLMConditionalAnalyzer("test-key", client=client).analyze(
            {"top_test.py": "class DemoTest: pass"},
            candidates,
        )

        self.assertEqual(
            result.rendering_rules(),
            {
                "DemoTest.env.agent.driver": "conditional:ProducerDriver",
                "DemoTest.env.agent.monitor": "hide",
            },
        )
        output_format = responses.request["text"]["format"]
        self.assertEqual(output_format["type"], "json_schema")
        self.assertTrue(output_format["strict"])

    def test_rejects_a_class_outside_the_candidate_list(self):
        responses = _FakeResponses(
            {
                "resolutions": [
                    {
                        "instance_path": "DemoTest.env.agent.driver",
                        "include": True,
                        "selected_class": "InventedDriver",
                        "rationale": "Invalid result",
                    }
                ]
            }
        )
        analyzer = LLMConditionalAnalyzer(
            "test-key",
            client=SimpleNamespace(responses=responses),
        )

        with self.assertRaisesRegex(LLMAnalysisError, "Invalid selected class"):
            analyzer.analyze(
                {"top_test.py": "pass"},
                [
                    ConditionalCandidate(
                        "DemoTest.env.agent.driver",
                        ("ProducerDriver", "ConsumerDriver"),
                    )
                ],
            )


if __name__ == "__main__":
    unittest.main()
