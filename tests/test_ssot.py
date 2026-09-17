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

    def test_query_namespace_scopes_keys(self) -> None:
        document = ssot.classify(_load("c2004-query-namespace.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "query_namespace")
        self.assertIn("leak_query_across_modules", decision["forbid"])
        self.assertIn("scope_query_keys", {item["do"] for item in decision["actions"]})

    def test_served_artifact_rebuilds_dist(self) -> None:
        document = ssot.classify(_load("c2004-served-artifact.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "served_artifact")
        self.assertIn("treat_source_as_served", decision["forbid"])
        self.assertIn("rebuild_served_artifact", {item["do"] for item in decision["actions"]})

    def test_inventory_vs_runtime_refuses_dirty_overwrite(self) -> None:
        document = ssot.classify(_load("c2004-inventory-vs-runtime.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "inventory_vs_runtime")
        self.assertIn("overwrite_dirty_working_tree", decision["forbid"])
        self.assertIn("count_lan_scan_as_connected_agent", decision["forbid"])

    def test_capability_surface_splits_roles(self) -> None:
        document = ssot.classify(_load("c2004-capability-surface.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "capability_surface")
        self.assertIn("treat_visible_edit_as_authorized", decision["forbid"])

    def test_locale_catalog_forbids_hardcoded_copy(self) -> None:
        document = ssot.classify(_load("c2004-locale-catalog.interview.json"))
        decision = document["decisions"][0]
        self.assertEqual(decision["kind"], "locale_catalog")
        self.assertIn("hardcode_ui_locale", decision["forbid"])
        self.assertIn("use_locale_catalog", {item["do"] for item in decision["actions"]})

    def test_stated_query_namespace_wins_over_detected_mirror(self) -> None:
        answers = _load("c2004-query-namespace.interview.json")
        answers["same_git_remote"] = True
        answers["same_pin"] = True
        decision = ssot.classify(answers)["decisions"][0]
        self.assertEqual(decision["kind"], "query_namespace")


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

    def test_missing_query_forbid_fails(self) -> None:
        document = _load("invalid/missing-query-forbid.ssot.json")
        codes = {item.code for item in ssot.validate_decision(document)}
        self.assertIn("SSOT-QUERY-001", codes)


class StandardsLockTests(unittest.TestCase):
    def test_pack_standards_lock_passes(self) -> None:
        manifest = json.loads((ROOT / "dsl-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(ssot.validate_standards_lock(manifest["standardsLock"]), [])

    def test_adopter_example_passes(self) -> None:
        document = _load("standards-lock.adopter.json")
        self.assertEqual(ssot.validate_standards_lock(document), [])

    def test_bad_revision_fails(self) -> None:
        document = _load("standards-lock.adopter.json")
        document["entries"][0]["revision"] = "not-a-sha"
        codes = {item.code for item in ssot.validate_standards_lock(document)}
        self.assertIn("SSOT-LOCK-001", codes)

    def test_bad_digest_fails(self) -> None:
        document = _load("standards-lock.adopter.json")
        document["entries"][0]["contracts"][0]["digest"] = "md5:abcd"
        codes = {item.code for item in ssot.validate_standards_lock(document)}
        self.assertIn("SSOT-LOCK-001", codes)

    def test_automatic_merge_is_forbidden(self) -> None:
        document = _load("standards-lock.adopter.json")
        document["updatePolicy"]["merge"] = "automatic"
        codes = {item.code for item in ssot.validate_standards_lock(document)}
        self.assertIn("SSOT-LOCK-001", codes)

    def test_drift_detects_stale_copy(self) -> None:
        manifest = json.loads((ROOT / "dsl-manifest.json").read_text(encoding="utf-8"))
        stale = _load("standards-lock.stale.json")
        self.assertEqual(ssot.validate_standards_lock(stale), [])
        codes = {item.code for item in ssot.detect_standards_drift(stale, manifest)}
        self.assertIn("SSOT-STALE-001", codes)

    def test_drift_is_silent_for_current_pin(self) -> None:
        manifest = json.loads((ROOT / "dsl-manifest.json").read_text(encoding="utf-8"))
        current = _load("standards-lock.adopter.json")
        self.assertEqual(ssot.detect_standards_drift(current, manifest), [])


class ProjectionTests(unittest.TestCase):
    def test_suggest_emits_document_ssot(self) -> None:
        document = _load("c2004.ssot.json")
        text = ssot.render_dsl(document)
        self.assertTrue(text.startswith("DOCUMENT SSOT"))
        self.assertIn("KIND generated_mirror", text)
        self.assertIn("KIND vendored_copy", text)
        self.assertIn("KIND allowed_divergence", text)
        self.assertIn("KIND facade", text)
        self.assertIn("KIND query_namespace", text)
        self.assertIn("KIND served_artifact", text)
        self.assertIn("KIND inventory_vs_runtime", text)
        self.assertIn("KIND capability_surface", text)
        self.assertIn("KIND locale_catalog", text)
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

    def test_standards_cli_ok(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = ssot.main(["standards", str(EXAMPLES / "standards-lock.adopter.json")])
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), "ok")

    def test_standards_cli_detects_stale(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = ssot.main(
                [
                    "standards",
                    str(EXAMPLES / "standards-lock.stale.json"),
                    "--upstream",
                    str(ROOT / "dsl-manifest.json"),
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("SSOT-STALE-001", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
