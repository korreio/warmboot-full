"""Falsify the bounded new-project kickoff evidence and authority contract."""

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar

from acceptance.kickoff_oracle import KickoffVerificationError, main, verify

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "acceptance" / "fixtures" / "kickoff-package"
PROMPT = ROOT / "acceptance" / "kickoff-agent-prompt.txt"
MINIMAL_PROMPT = ROOT / "acceptance" / "minimal-agent-prompt.txt"


def _fullwidth_twin(text: str) -> str:
    """Return a Unicode compatibility (fullwidth) twin that NFKC-folds back to ``text``.

    Used to reproduce a confusable identity that raw ``==``/``in`` treats as distinct
    but the shared ``_identity_key`` normalization collapses onto the real role (WB-047).
    """
    mapping = []
    for character in text:
        if "a" <= character <= "z":
            mapping.append(chr(ord(character) - 0x61 + 0xFF41))
        elif "A" <= character <= "Z":
            mapping.append(chr(ord(character) - 0x41 + 0xFF21))
        elif "0" <= character <= "9":
            mapping.append(chr(ord(character) - 0x30 + 0xFF10))
        elif character == "-":
            mapping.append("－")
        else:
            mapping.append(character)
    return "".join(mapping)


class KickoffOracleTests(unittest.TestCase):
    COUPLED_HAZARD_CROSS_CHECKS: ClassVar[list[str]] = [
        "PATH_RESOURCE_ALIASING",
        "SOURCE_PRESERVATION",
        "EXACT_COMMANDS",
        "FAILURE_INJECTION",
        "PLATFORM_PREREQUISITES",
    ]

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.package = Path(self.temporary.name) / "kickoff-package"
        shutil.copytree(FIXTURE, self.package)

    def read(self, relative: str) -> dict:
        return json.loads((self.package / relative).read_text(encoding="utf-8"))

    def write(self, relative: str, value: dict) -> None:
        (self.package / relative).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def make_live(self) -> None:
        """Turn the synthetic copy into a live package citing primary HTTPS sources."""
        coordination = self.read("coordination.json")
        coordination.pop("evidence_mode")
        self.write("coordination.json", coordination)
        for lane in ("language", "stack", "tooling"):
            report = self.read(f"research/{lane}.json")
            urls = {}
            for index, source in enumerate(report["sources"]):
                urls[source["url"]] = f"https://docs.example.org/{lane}/{index}"
                source["source_kind"] = "PRIMARY_OFFICIAL"
                source["url"] = urls[source["url"]]
                source["evidence"] = "Primary documentation page for the recorded claim."
            for option in report["options"]:
                option["evidence_refs"] = [urls[ref] for ref in option["evidence_refs"]]
            self.write(f"research/{lane}.json", report)

    def run_main(self) -> tuple[int, dict]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--package", str(self.package)])
        return code, json.loads(output.getvalue())

    def assign_owner(self, coordination: dict, lane_id: str, owner: str) -> None:
        delegation = next(
            lane for lane in coordination["delegations"] if lane["lane_id"] == lane_id
        )
        delegation["owner"] = owner
        report = self.read(delegation["artifact"])
        report["author"] = owner
        self.write(delegation["artifact"], report)

    def configure_lower_risk_merge(
        self,
        coordination: dict,
        *,
        rationale: str | None,
        cross_checks: list[str],
    ) -> None:
        architecture_owner = next(
            lane["owner"]
            for lane in coordination["delegations"]
            if lane["lane_id"] == "architecture"
        )
        self.assign_owner(coordination, "delivery", architecture_owner)
        coordination["architecture_delivery_assignment"] = {
            "risk_class": "LOWER_RISK",
            "merged": True,
            "safe_merge_rationale": rationale,
            "challenger_cross_checks": cross_checks,
        }
        challenge = self.read("research/challenge.json")
        challenge["coupled_hazard_cross_checks"] = cross_checks
        self.write("research/challenge.json", challenge)

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 paths")
    def test_cli_reports_an_unsearchable_package_parent_as_fail(self) -> None:
        parent = Path(self.temporary.name)
        parent.chmod(0)
        stderr = io.StringIO()
        try:
            with contextlib.redirect_stderr(stderr):
                status = main(["--package", str(self.package)])
        finally:
            parent.chmod(0o755)
        self.assertEqual(status, 1)
        self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 paths")
    def test_directory_it_cannot_list_fails_closed_until_restored(self) -> None:
        hidden = self.package / "research" / "hidden"
        hidden.mkdir()
        (hidden / "extra.txt").write_text("extra\n", encoding="utf-8")
        with self.assertRaisesRegex(KickoffVerificationError, "extra=.*research/hidden/extra"):
            verify(self.package)
        for mode in (0, 0o444):
            with self.subTest(mode=oct(mode)):
                hidden.chmod(mode)
                stderr = io.StringIO()
                try:
                    with self.assertRaisesRegex(KickoffVerificationError, "cannot be listed"):
                        verify(self.package)
                    with (
                        contextlib.redirect_stderr(stderr),
                        contextlib.redirect_stdout(io.StringIO()),
                    ):
                        status = main(["--package", str(self.package)])
                finally:
                    hidden.chmod(0o755)
                self.assertEqual(status, 1)
                self.assertIn("cannot be listed", stderr.getvalue())
        with self.assertRaisesRegex(KickoffVerificationError, "extra=.*research/hidden/extra"):
            verify(self.package)
        shutil.rmtree(hidden)
        verify(self.package)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "needs named pipes")
    def test_rejects_an_entry_that_is_neither_file_nor_directory(self) -> None:
        os.mkfifo(self.package / "extra.fifo")
        with self.assertRaisesRegex(KickoffVerificationError, "only files and directories"):
            verify(self.package)

    def test_synthetic_fixture_reports_schema_only_mode(self) -> None:
        self.assertEqual(
            self.run_main(), (0, {"evidence_mode": "SYNTHETIC_SCHEMA_ONLY", "status": "PASS"})
        )

    def test_live_package_with_primary_sources_reports_live_mode(self) -> None:
        self.make_live()
        verify(self.package)
        self.assertEqual(
            self.run_main(), (0, {"evidence_mode": "LIVE_STRUCTURE_ONLY", "status": "PASS"})
        )

    def test_rejects_unknown_evidence_mode(self) -> None:
        coordination = self.read("coordination.json")
        coordination["evidence_mode"] = "LIVE_RESEARCH"
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(
            KickoffVerificationError, "evidence_mode must be SYNTHETIC_SCHEMA_ONLY or absent"
        ):
            verify(self.package)

    def test_rejects_live_option_citing_unknown_source(self) -> None:
        self.make_live()
        language = self.read("research/language.json")
        language["options"][0]["evidence_refs"] = ["https://docs.example.org/elsewhere"]
        self.write("research/language.json", language)
        with self.assertRaisesRegex(KickoffVerificationError, "option cites unknown source"):
            verify(self.package)

    def test_synthetic_sources_cannot_be_promoted_to_live_evidence(self) -> None:
        coordination = self.read("coordination.json")
        coordination.pop("evidence_mode")
        self.write("coordination.json", coordination)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_synthetic_fixture_cannot_authorize_implementation_or_install(self) -> None:
        for gate in ("implementation_authorized", "install_authorized"):
            with self.subTest(gate=gate):
                coordination = self.read("coordination.json")
                coordination[gate] = True
                self.write("coordination.json", coordination)
                with self.assertRaises(KickoffVerificationError):
                    verify(self.package)
                coordination[gate] = False
                self.write("coordination.json", coordination)

    def test_accepts_complete_structural_evidence_package_offline(self) -> None:
        verify(self.package)

    def test_accepts_proportional_research_owners_with_high_risk_split(self) -> None:
        coordination = self.read("coordination.json")
        owner_by_lane = {
            "context": "research-owner-a",
            "language": "research-owner-a",
            "tooling": "research-owner-a",
            "stack": "research-owner-b",
            "architecture": "research-owner-b",
            "delivery": "research-owner-c",
        }
        for lane_id, owner in owner_by_lane.items():
            self.assign_owner(coordination, lane_id, owner)
        self.write("coordination.json", coordination)
        verify(self.package)

    def test_accepts_lower_risk_merge_with_rationale_and_challenger_cross_checks(self) -> None:
        coordination = self.read("coordination.json")
        self.configure_lower_risk_merge(
            coordination,
            rationale=(
                "This bounded planning-only diagnostic has no mutation, credentials, "
                "external effects, or scarce shared resource."
            ),
            cross_checks=self.COUPLED_HAZARD_CROSS_CHECKS,
        )
        self.write("coordination.json", coordination)
        verify(self.package)

    def test_rejects_high_risk_architecture_delivery_merge(self) -> None:
        coordination = self.read("coordination.json")
        architecture_owner = next(
            lane["owner"]
            for lane in coordination["delegations"]
            if lane["lane_id"] == "architecture"
        )
        self.assign_owner(coordination, "delivery", architecture_owner)
        coordination["architecture_delivery_assignment"]["merged"] = True
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "high-risk or destructive"):
            verify(self.package)

    def test_rejects_lower_risk_merge_without_concrete_rationale(self) -> None:
        coordination = self.read("coordination.json")
        self.configure_lower_risk_merge(
            coordination,
            rationale=None,
            cross_checks=self.COUPLED_HAZARD_CROSS_CHECKS,
        )
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "safe_merge_rationale"):
            verify(self.package)

    def test_rejects_lower_risk_merge_missing_named_cross_check(self) -> None:
        coordination = self.read("coordination.json")
        self.configure_lower_risk_merge(
            coordination,
            rationale=(
                "This bounded planning-only diagnostic has no mutation, credentials, "
                "external effects, or scarce shared resource."
            ),
            cross_checks=self.COUPLED_HAZARD_CROSS_CHECKS[:-1],
        )
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "all named"):
            verify(self.package)

    def test_rejects_lower_risk_merge_when_challenge_omits_assigned_cross_checks(self) -> None:
        coordination = self.read("coordination.json")
        self.configure_lower_risk_merge(
            coordination,
            rationale=(
                "This bounded planning-only diagnostic has no mutation, credentials, "
                "external effects, or scarce shared resource."
            ),
            cross_checks=self.COUPLED_HAZARD_CROSS_CHECKS,
        )
        challenge = self.read("research/challenge.json")
        challenge["coupled_hazard_cross_checks"] = self.COUPLED_HAZARD_CROSS_CHECKS[:-1]
        self.write("research/challenge.json", challenge)
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "must match"):
            verify(self.package)

    def test_rejects_one_research_owner_for_all_six_concerns(self) -> None:
        coordination = self.read("coordination.json")
        for delegation in coordination["delegations"]:
            if delegation["lane_id"] != "challenge":
                delegation["owner"] = "only-research-owner"
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "at least two"):
            verify(self.package)

    def test_rejects_challenger_who_authored_a_research_concern(self) -> None:
        coordination = self.read("coordination.json")
        context_owner = next(
            lane["owner"] for lane in coordination["delegations"] if lane["lane_id"] == "context"
        )
        challenge = next(
            lane for lane in coordination["delegations"] if lane["lane_id"] == "challenge"
        )
        challenge["owner"] = context_owner
        challenge_report = self.read("research/challenge.json")
        challenge_report["author"] = context_owner
        self.write("research/challenge.json", challenge_report)
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "distinct from every research owner"):
            verify(self.package)

    def test_rejects_challenger_confusable_alias_of_research_owner(self) -> None:
        """A challenger spelled as a compatibility twin of a research owner must be
        rejected: the separation check compares normalized identity keys, so a confusable
        alias that is really the same person is not admitted (WB-047)."""
        coordination = self.read("coordination.json")
        context_owner = next(
            lane["owner"] for lane in coordination["delegations"] if lane["lane_id"] == "context"
        )
        self.assign_owner(coordination, "challenge", _fullwidth_twin(context_owner))
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "distinct from every research owner"):
            verify(self.package)

    def test_rejects_coordinator_confusable_alias_as_lane_owner(self) -> None:
        """A lane owner spelled as a compatibility twin of the coordinator must be
        rejected: the non-coordinator check compares normalized identity keys, so a
        confusable alias cannot masquerade as a distinct delegate (WB-047)."""
        coordination = self.read("coordination.json")
        self.assign_owner(coordination, "context", _fullwidth_twin(coordination["coordinator"]))
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(
            KickoffVerificationError, "kickoff owners must be non-coordinator"
        ):
            verify(self.package)

    def test_rejects_confusable_architecture_delivery_merge(self) -> None:
        """Architecture and delivery owned by two aliases of one identity are actually
        merged, so a declared `merged: false` under a high-risk split must be rejected:
        merge detection compares normalized identity keys, not raw text (WB-047)."""
        coordination = self.read("coordination.json")
        self.assign_owner(coordination, "architecture", "shared-arch-delivery-owner")
        self.assign_owner(coordination, "delivery", _fullwidth_twin("shared-arch-delivery-owner"))
        # The fixture keeps merged=false with a HIGH_RISK_OR_DESTRUCTIVE split; the two
        # aliased owners are one identity, so that flag now understates the real merge.
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(
            KickoffVerificationError, "merged flag must match attributed ownership"
        ):
            verify(self.package)

    def test_rejects_synthetic_ignorable_in_separation_identity(self) -> None:
        """A zero-width space inside a separation-critical identity is a synthetic
        Unicode ignorable and must fail closed at the identity key rather than form a
        distinct alias of a real research owner (WB-047)."""
        coordination = self.read("coordination.json")
        context_owner = next(
            lane["owner"] for lane in coordination["delegations"] if lane["lane_id"] == "context"
        )
        head, tail = context_owner[:8], context_owner[8:]
        self.assign_owner(coordination, "challenge", f"{head}\u200b{tail}")
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "synthetic Unicode ignorables"):
            verify(self.package)

    def test_rejects_leading_space_twin_of_research_owner_as_challenger(self) -> None:
        """A challenger spelled as a surrounding-whitespace twin of a research owner must
        be rejected: `_identity_key` applies the sibling canonical-text (strip) gate
        before folding, so an invisible leading-space alias cannot form a distinct key
        that slips the separation checks (WB-047).

        A leading space survives `nfkc_casefold`, so without the strip gate
        `" context-researcher"` would key distinct from `"context-researcher"` and pass the
        challenger-versus-research-owner check; the gate catches the padded owner at the
        per-delegation identity key first, so the whitespace alias fails closed."""
        coordination = self.read("coordination.json")
        context_owner = next(
            lane["owner"] for lane in coordination["delegations"] if lane["lane_id"] == "context"
        )
        self.assign_owner(coordination, "challenge", f" {context_owner}")
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "surrounding whitespace"):
            verify(self.package)

    def test_rejects_trailing_space_twin_in_architecture_delivery_merge(self) -> None:
        """Architecture and delivery owned by a value and its trailing-space twin are one
        identity, so the canonical-text (strip) gate must reject the padded owner before a
        declared `merged: false` high-risk split can hide the real merge: a trailing space
        survives folding, so without the gate the two owners would key distinct and merge
        detection would read `actually_merged = False` for one person (WB-047)."""
        coordination = self.read("coordination.json")
        self.assign_owner(coordination, "architecture", "shared-arch-delivery-owner")
        self.assign_owner(coordination, "delivery", "shared-arch-delivery-owner ")
        self.write("coordination.json", coordination)
        with self.assertRaisesRegex(KickoffVerificationError, "surrounding whitespace"):
            verify(self.package)

    def test_rejects_coordinator_authored_or_non_independent_lane(self) -> None:
        coordination = self.read("coordination.json")
        coordination["delegations"][0]["owner"] = coordination["coordinator"]
        coordination["delegations"][0]["independent"] = False
        self.write("coordination.json", coordination)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_missing_required_exploration_lane(self) -> None:
        coordination = self.read("coordination.json")
        coordination["delegations"] = [
            lane for lane in coordination["delegations"] if lane["lane_id"] != "architecture"
        ]
        self.write("coordination.json", coordination)
        (self.package / "research" / "architecture.json").unlink()
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_wrong_concern_or_challenge_stage(self) -> None:
        coordination = self.read("coordination.json")
        by_lane = {lane["lane_id"]: lane for lane in coordination["delegations"]}
        by_lane["delivery"]["concern"] = "CURRENT_TECHNOLOGY_TOOLING"
        by_lane["challenge"]["stage"] = "EXPLORATION"
        self.write("coordination.json", coordination)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_proved_research_without_official_url_and_date(self) -> None:
        cases = (
            ("url", "notes/local-copy", "must be an absolute HTTPS URL"),
            ("url", "http://docs.example.org/language/0", "must be an absolute HTTPS URL"),
            ("url", "https:notes/local-copy", "must be an absolute HTTPS URL"),
            ("retrieved_on", "2025-01-01", "retrieved_on must match research_as_of"),
            ("source_kind", "SYNTHETIC", "source_kind must be PRIMARY_OFFICIAL"),
        )
        for field, value, message in cases:
            with self.subTest(field=field, value=value):
                shutil.rmtree(self.package)
                shutil.copytree(FIXTURE, self.package)
                self.make_live()
                language = self.read("research/language.json")
                language["sources"][0][field] = value
                self.write("research/language.json", language)
                with self.assertRaisesRegex(KickoffVerificationError, message):
                    verify(self.package)

    def test_accepts_honest_unproved_lane_without_web_access(self) -> None:
        tooling = self.read("research/tooling.json")
        tooling["status"] = "UNPROVED"
        tooling["sources"] = []
        tooling["options"] = []
        tooling["recommendation"] = "No current recommendation."
        tooling["decision_impact"] = "Do not install tooling packages."
        tooling["unproved_boundary"] = "Current official sources were unavailable offline."
        self.write("research/tooling.json", tooling)

        coordination = self.read("coordination.json")
        coordination["status"] = "UNPROVED"
        next(lane for lane in coordination["delegations"] if lane["lane_id"] == "tooling")[
            "status"
        ] = "UNPROVED"
        self.write("coordination.json", coordination)

        brief = self.read("technology-options-research-brief.json")
        brief["status"] = "UNPROVED"
        brief["unproved_boundaries"] = [
            "Current tooling evidence is unavailable; keep package actions blocked."
        ]
        self.write("technology-options-research-brief.json", brief)

        adr = self.read("technology-architecture-adr.json")
        adr["status"] = "PROPOSED_WITH_UNPROVED"
        adr["unproved_boundaries"] = [
            "Tooling currency is unproved; no tooling package may be installed."
        ]
        self.write("technology-architecture-adr.json", adr)
        plan = self.read("kickoff-plan.json")
        plan["status"] = "AWAITING_WITH_UNPROVED"
        plan["phases"][0]["execution_state"] = "REVIEW_UNPROVED_BOUNDARIES"
        plan["authority_gate"]["next_gate"] = "REVIEW_UNPROVED_BOUNDARIES"
        self.write("kickoff-plan.json", plan)
        verify(self.package)

    def test_rejects_unproved_lane_hidden_by_proved_adr(self) -> None:
        tooling = self.read("research/tooling.json")
        tooling["status"] = "BLOCKED"
        tooling["sources"] = []
        tooling["options"] = []
        tooling["unproved_boundary"] = "Official source access is blocked."
        self.write("research/tooling.json", tooling)

        adr = self.read("technology-architecture-adr.json")
        adr["unproved_boundaries"] = ["Tooling evidence blocked."]
        self.write("technology-architecture-adr.json", adr)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_implementation_or_package_authority_inference(self) -> None:
        coordination = self.read("coordination.json")
        coordination["implementation_authorized"] = True
        self.write("coordination.json", coordination)
        plan = self.read("kickoff-plan.json")
        plan["implementation_authorized"] = True
        self.write("kickoff-plan.json", plan)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_duplicate_implementation_authority_before_safe_value(self) -> None:
        """Raw coordination evidence cannot hide authority behind JSON last-key wins."""
        path = self.package / "coordination.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                '  "implementation_authorized": false,',
                '  "implementation_authorized": true,\n  "implementation_authorized": false,',
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            KickoffVerificationError,
            "duplicate JSON object key: implementation_authorized",
        ):
            verify(self.package)

    def test_rejects_missing_concrete_package_install_phase(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan["phases"] = [phase for phase in plan["phases"] if phase["id"] != "package-install"]
        self.write("kickoff-plan.json", plan)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_missing_portfolio_baseline_assessment(self) -> None:
        adr = self.read("technology-architecture-adr.json")
        adr["portfolio_assessments"] = adr["portfolio_assessments"][:2]
        self.write("technology-architecture-adr.json", adr)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_unjustified_new_stack_divergence(self) -> None:
        adr = self.read("technology-architecture-adr.json")
        adr["new_stack_divergence"]["selected"] = True
        self.write("technology-architecture-adr.json", adr)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_accepts_justified_new_stack_without_forcing_reuse(self) -> None:
        stack = self.read("research/stack.json")
        for assessment in stack["portfolio_assessments"]:
            assessment["disposition"] = "DECLINE"
        self.write("research/stack.json", stack)
        adr = self.read("technology-architecture-adr.json")
        for assessment in adr["portfolio_assessments"]:
            assessment["disposition"] = "DECLINE"
        adr["new_stack_divergence"] = {
            "selected": True,
            "objective_specific_justification": "The objective requires a runtime boundary absent from the portfolio.",
            "solo_maintenance_cost": "One additional runtime and its native test/tool update path.",
            "evidence_refs": ["research/language.json", "docs/exploration/stack-portfolio.md"],
        }
        self.write("technology-architecture-adr.json", adr)
        verify(self.package)

    def test_requires_coordinator_technology_options_brief(self) -> None:
        (self.package / "technology-options-research-brief.json").unlink()
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_non_coordinator_technology_options_brief(self) -> None:
        brief = self.read("technology-options-research-brief.json")
        brief["owner"] = "language-researcher"
        self.write("technology-options-research-brief.json", brief)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_portfolio_assessment_absent_from_stack_lane(self) -> None:
        stack = self.read("research/stack.json")
        stack["portfolio_assessments"] = stack["portfolio_assessments"][:2]
        self.write("research/stack.json", stack)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_adr_that_does_not_synthesize_stack_assessments(self) -> None:
        adr = self.read("technology-architecture-adr.json")
        adr["portfolio_assessments"][0]["objective_specific_fit"] = "Coordinator invention."
        self.write("technology-architecture-adr.json", adr)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_boolean_schema_version(self) -> None:
        context = self.read("research/context.json")
        context["schema_version"] = True
        self.write("research/context.json", context)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_unproved_local_input_hidden_by_proved_lane(self) -> None:
        context = self.read("research/context.json")
        context["local_inputs"][0]["state"] = "UNPROVED"
        self.write("research/context.json", context)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_blocked_report_hidden_by_complete_receipt(self) -> None:
        context = self.read("research/context.json")
        context["status"] = "BLOCKED"
        context["local_inputs"][0]["state"] = "BLOCKED"
        context["unproved_boundary"] = "The objective source cannot be read."
        self.write("research/context.json", context)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_accepted_finding_without_concrete_resolution(self) -> None:
        adr = self.read("technology-architecture-adr.json")
        adr["challenge_dispositions"][0]["resolution_path"] = "research/challenge.json#CH-001"
        self.write("technology-architecture-adr.json", adr)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_deferred_finding_requires_blocked_overall_status(self) -> None:
        for relative in ("technology-architecture-adr.json", "kickoff-plan.json"):
            artifact = self.read(relative)
            artifact["challenge_dispositions"][0]["disposition"] = "DEFERRED_BLOCKED"
            self.write(relative, artifact)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_accepts_honest_deferred_finding_as_blocked(self) -> None:
        coordination = self.read("coordination.json")
        coordination["status"] = "BLOCKED"
        self.write("coordination.json", coordination)
        adr = self.read("technology-architecture-adr.json")
        adr["status"] = "BLOCKED"
        adr["unproved_boundaries"] = ["CH-001 remains deferred and blocks authorization."]
        adr["challenge_dispositions"][0]["disposition"] = "DEFERRED_BLOCKED"
        self.write("technology-architecture-adr.json", adr)
        plan = self.read("kickoff-plan.json")
        plan["status"] = "BLOCKED"
        plan["phases"][0]["execution_state"] = "BLOCKED_BY_EVIDENCE"
        plan["authority_gate"]["next_gate"] = "RESOLVE_BLOCKED_EVIDENCE"
        plan["challenge_dispositions"][0]["disposition"] = "DEFERRED_BLOCKED"
        self.write("kickoff-plan.json", plan)
        verify(self.package)

    def test_rejects_noncanonical_declared_local_path(self) -> None:
        context = self.read("research/context.json")
        context["local_inputs"][0]["path"] = "../outside.md"
        self.write("research/context.json", context)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_symlinked_artifact(self) -> None:
        outside = Path(self.temporary.name) / "outside.json"
        outside.write_text("{}\n", encoding="utf-8")
        artifact = self.package / "research" / "context.json"
        artifact.unlink()
        artifact.symlink_to(outside)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_symlinked_package_root(self) -> None:
        linked = Path(self.temporary.name) / "linked-package"
        linked.symlink_to(self.package, target_is_directory=True)
        with self.assertRaises(KickoffVerificationError):
            verify(linked)

    def test_rejects_install_authority_or_unknown_gate_token(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan["install_authorized"] = True
        plan["phases"][1]["entry_condition_tokens"] = ["TRUST_ME"]
        self.write("kickoff-plan.json", plan)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_missing_target_fit_source_comprehension_contract(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan.pop("source_comprehension")
        self.write("kickoff-plan.json", plan)
        with self.assertRaisesRegex(KickoffVerificationError, "plan keys differ"):
            verify(self.package)

    def test_rejects_source_comprehension_without_implementation_or_review_gate(self) -> None:
        for field in ("implementation_gate", "review_gate"):
            for replacement in ("", "x"):
                with self.subTest(field=field, replacement=replacement):
                    plan = self.read("kickoff-plan.json")
                    plan["source_comprehension"][field] = replacement
                    self.write("kickoff-plan.json", plan)
                    with self.assertRaisesRegex(KickoffVerificationError, field):
                        verify(self.package)
                    shutil.copy2(FIXTURE / "kickoff-plan.json", self.package / "kickoff-plan.json")

    def test_rejects_source_rule_not_owned_created_and_verified_by_gated_phases(self) -> None:
        mutations = {
            "mismatched bootstrap owner": lambda plan: plan["phases"][1].update(
                owner="different-owner"
            ),
            "arbitrary unowned target path": lambda plan: plan["source_comprehension"].update(
                target_rule_path="docs/does-not-exist.md"
            ),
            "path absent from bootstrap ownership": lambda plan: plan["phases"][1][
                "exact_paths"
            ].remove(plan["source_comprehension"]["target_rule_path"]),
            "missing bootstrap adoption": lambda plan: plan["phases"][1]["actions"].clear(),
            "missing bootstrap verification": lambda plan: plan["phases"][1]["evidence"].clear(),
            "missing implementation assessment": lambda plan: plan["phases"][3]["actions"].clear(),
            "missing non-author review": lambda plan: plan["phases"][3]["evidence"].clear(),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                plan = self.read("kickoff-plan.json")
                mutate(plan)
                self.write("kickoff-plan.json", plan)
                with self.assertRaises(KickoffVerificationError):
                    verify(self.package)
                shutil.copy2(FIXTURE / "kickoff-plan.json", self.package / "kickoff-plan.json")

    def test_rejects_source_comprehension_without_target_rule_owner_or_debt_disposition(
        self,
    ) -> None:
        for field in ("target_rule_path", "owner", "existing_debt_disposition"):
            with self.subTest(field=field):
                plan = self.read("kickoff-plan.json")
                plan["source_comprehension"][field] = ""
                self.write("kickoff-plan.json", plan)
                with self.assertRaisesRegex(KickoffVerificationError, field):
                    verify(self.package)
                shutil.copy2(FIXTURE / "kickoff-plan.json", self.package / "kickoff-plan.json")

    def test_rejects_missing_quality_control_loop(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan.pop("quality_control")
        self.write("kickoff-plan.json", plan)
        with self.assertRaisesRegex(KickoffVerificationError, "plan keys differ"):
            verify(self.package)

    def test_rejects_quality_control_without_owned_action_or_independent_challenge(self) -> None:
        for field in ("owner", "action_rule", "challenge_rule", "unknown_policy"):
            with self.subTest(field=field):
                plan = self.read("kickoff-plan.json")
                plan["quality_control"][field] = ""
                self.write("kickoff-plan.json", plan)
                with self.assertRaisesRegex(KickoffVerificationError, field):
                    verify(self.package)
                shutil.copy2(FIXTURE / "kickoff-plan.json", self.package / "kickoff-plan.json")

    def test_rejects_permanent_kickoff_lane_topology(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan["steady_state"]["kickoff_research_lanes_end"] = False
        self.write("kickoff-plan.json", plan)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_challenge_finding_missing_from_adr(self) -> None:
        adr = self.read("technology-architecture-adr.json")
        adr["challenge_dispositions"] = []
        self.write("technology-architecture-adr.json", adr)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_challenge_finding_missing_from_plan(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan["challenge_dispositions"] = []
        self.write("kickoff-plan.json", plan)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_disagreement_between_adr_and_plan_disposition(self) -> None:
        plan = self.read("kickoff-plan.json")
        plan["challenge_dispositions"][0]["disposition"] = "REJECTED_WITH_REASON"
        self.write("kickoff-plan.json", plan)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_challenger_as_coordinator(self) -> None:
        coordination = self.read("coordination.json")
        challenge = next(
            lane for lane in coordination["delegations"] if lane["lane_id"] == "challenge"
        )
        challenge["owner"] = coordination["coordinator"]
        self.write("coordination.json", coordination)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_local_lane_without_exact_inputs(self) -> None:
        architecture = self.read("research/architecture.json")
        architecture["local_inputs"] = []
        self.write("research/architecture.json", architecture)
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_rejects_extra_prose_artifact(self) -> None:
        (self.package / "summary.md").write_text("Looks good.\n", encoding="utf-8")
        with self.assertRaises(KickoffVerificationError):
            verify(self.package)

    def test_prompt_preserves_offline_and_authority_boundaries(self) -> None:
        prompt = PROMPT.read_text(encoding="utf-8")
        required = (
            "act only as coordinator",
            "at least two distinct",
            "floor, not a target",
            "objective/context",
            "architecture/risk/privacy",
            "testing/bootstrap/package",
            "current language, stack, and tooling lanes",
            "primary or official",
            "exact local input paths, snapshots, and evidence",
            "do not invent web",
            "reference service baseline",
            "Prefer reuse when it fits, but do not force it",
            "solo-maintenance cost",
            "technology-options-research-brief.json",
            "stack-and-portfolio lane itself",
            "UNPROVED or BLOCKED",
            "independent challenge",
            "authored none of the research or drafts",
            "Dispose every challenge finding",
            "implementation_authorized false",
            "install_authorized false",
            "eleven-file structure",
            "not a permanent multi-agent requirement",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, prompt)

    def test_minimal_prompt_is_only_the_live_entry_contract(self) -> None:
        prompt = MINIMAL_PROMPT.read_text(encoding="utf-8").strip()
        self.assertEqual(
            prompt,
            "Read AGENTS.md or CLAUDE.md, take full ownership of <OBJECTIVE>, "
            "and work only inside <ABSOLUTE_TARGET>; do not publish or make external changes.",
        )

    def test_minimal_prompt_excludes_self_fulfilling_contract_details(self) -> None:
        prompt = MINIMAL_PROMPT.read_text(encoding="utf-8").lower()
        forbidden = (
            "why",
            "bootstrap",
            "lane",
            "portfolio",
            "artifact",
            "schema",
            "oracle",
            "command",
            "research/",
            "docs/",
            ".json",
            "python3",
        )
        for term in forbidden:
            with self.subTest(term=term):
                self.assertNotIn(term, prompt)

    def test_detailed_prompt_disclaims_minimal_discovery_proof(self) -> None:
        prompt = PROMPT.read_text(encoding="utf-8")
        self.assertTrue(prompt.startswith("DIAGNOSTIC ONLY:"))
        self.assertIn("detailed structural/schema diagnostic", prompt)
        self.assertIn("cannot prove minimal-prompt discovery", prompt)
        self.assertIn("primary live cold-start exercise", prompt)


if __name__ == "__main__":
    unittest.main()
