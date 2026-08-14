from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import ssot


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class ClassifyTests(unittest.TestCase):
    def test_dual_checkout_is_generated_mirror_not_debt(self) -> None:
        document = ssot.classify(_load("c2004-backend-shared-py.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "generated_mirror")
        self.assertIn("delete_either_tree", decision["forbid"])
        self.assertFalse(document["context"]["analyzer"]["treatAsDebtUntilInterview"])
        actions = {item["do"] for item in decision["actions"]}
        self.assertIn("edit_upstream", actions)
        self.assertIn("bump_pin", actions)
        self.assertIn("keep_both_checkouts", actions)

    def test_vendored_copy_gates_drift_instead_of_coupling(self) -> None:
        document = ssot.classify(_load("c2004-frontend-services.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "vendored_copy")
        self.assertEqual(decision["gate"]["kind"], "parity_test")
        self.assertIn("couple_standalone_to_foreign_monorepo", decision["forbid"])
        actions = {item["do"] for item in decision["actions"]}
        self.assertIn("vendor_and_gate_drift", actions)
        self.assertIn("keep_parity_test", actions)

    def test_parent_url_bridge_is_allowed_divergence(self) -> None:
        document = ssot.classify(_load("c2004-parent-url-bridge.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "allowed_divergence")
        self.assertIn("postMessage", decision["knownDivergent"]["reason"])

    def test_hardware_client_is_facade(self) -> None:
        document = ssot.classify(_load("c2004-hardware-client.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "facade")
        self.assertEqual(decision["canonical"]["module"], "oqlos.hardware.client")
        self.assertEqual(decision["facade"]["path"], "packages/hardware-client-py")
        self.assertIn("fork_logic_into_consumer", decision["forbid"])

    def test_analyzer_noise_asks_questions(self) -> None:
        document = ssot.classify(_load("analyzer-noise.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "same_file_noise")
        self.assertTrue(document["questions"])
        self.assertIn("treat_analyzer_as_debt", decision["forbid"])
        self.assertFalse(document["context"]["analyzer"]["treatAsDebtUntilInterview"])


class ValidateTests(unittest.TestCase):
    def test_c2004_example_passes(self) -> None:
        document = _load("c2004.ssot.json")
        self.assertEqual(ssot.validate_decision(document), [])

    def test_missing_reason_fails(self) -> None:
        document = _load("invalid/missing-reason.ssot.json")
        codes = {item.code for item in ssot.validate_decision(document)}
        self.assertIn("SSOT-REASON-001", codes)

    def test_pin_policy_requires_couple_forbid(self) -> None:
        document = _load("c2004.ssot.json")
        document["policy"]["forbid"] = ["delete_generated_mirror"]
        codes = {item.code for item in ssot.validate_decision(document)}
        self.assertIn("SSOT-COUPLE-001", codes)


class ProjectionTests(unittest.TestCase):
    def test_suggest_emits_document_ssot(self) -> None:
        document = _load("c2004.ssot.json")
        text = ssot.render_dsl(document)
        self.assertTrue(text.startswith("DOCUMENT SSOT"))
        self.assertIn("KIND generated_mirror", text)
        self.assertIn("KIND vendored_copy", text)
        self.assertIn("KIND allowed_divergence", text)
        self.assertIn("KIND facade", text)
        self.assertIn("POLICY pin", text)
        parsed = ssot.parse_dsl(text)
        self.assertEqual(parsed["id"], document["id"])
        self.assertEqual(
            [item["kind"] for item in parsed["decisions"]],
            [item["kind"] for item in document["decisions"]],
        )


class CliTests(unittest.TestCase):
    def test_questions_lists_catalog(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = ssot.main(["questions"])
        self.assertEqual(code, 0)
        self.assertIn("subject_id", buffer.getvalue())

    def test_classify_cli_dsl(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = ssot.main(
                [
                    "classify",
                    str(EXAMPLES / "c2004-backend-shared-py.interview.json"),
                    "--format",
                    "dsl",
                ]
            )
        self.assertEqual(code, 0)
        self.assertIn("KIND generated_mirror", buffer.getvalue())

    def test_validate_cli_ok(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = ssot.main(["validate", str(EXAMPLES / "c2004.ssot.json")])
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), "ok")


if __name__ == "__main__":
    unittest.main()
