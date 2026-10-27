"""Verify that synthetic kickoff receipts bind drafts and reject their stale digests."""

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DRAFTS = {
    "docs/reviews/snapshots/technology-options-draft-1.md":
        "222d77f2d961e070ab9a8f07ce714f58cc1c57e3c6d908977b48fbb80ec85b23",
    "docs/reviews/snapshots/technology-architecture-adr-draft-1.md":
        "45e3af35f3e5b678ac6008b4db5dd7dd81ff31db765e7e6090ff69b359bcc613",
    "docs/reviews/snapshots/kickoff-plan-draft-1.md":
        "2852371c0a68e4d6d892a8f59842d2e4035a6c53a4d031ee5a2e1d2e5a0c87b7",
}

CURRENT = {
    "docs/reviews/work/technology-options.md":
        "7cfd01014f3f6439ef1fed8da40836a70f9d7758338c1d8e5be0635d3ad55b47",
    "docs/reviews/work/technology-architecture-adr.md":
        "eec09d573e70062983a4ab7825934d1af69f8cbbe3275bbb3ce37ecd79d181e3",
    "docs/reviews/work/kickoff-plan.md":
        "5b8f44d02084ec1606c082126840d0b0415933687cca2688fab99fe47031e3f8",
}


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


class KickoffRecoveryHistoryTests(unittest.TestCase):
    def test_pre_challenge_receipt_identifies_each_exact_draft(self) -> None:
        receipt = (ROOT / "docs/reviews/kickoff-pre-challenge-receipt.md").read_text()
        index = (
            ROOT / "docs/reviews/snapshots/example-kickoff-draft-1.md"
        ).read_text()
        challenge = (ROOT / "docs/reviews/kickoff-challenge.md").read_text()

        for relative, expected in DRAFTS.items():
            self.assertEqual(digest(relative), expected)
            for artifact in (receipt, index, challenge):
                self.assertIn(Path(relative).name, artifact)
                self.assertIn(expected, artifact)

    def test_recovery_receipt_rejects_old_claims_and_refreshes_digests(self) -> None:
        receipt = (ROOT / "docs/reviews/kickoff-recovery-receipt.md").read_text()

        for relative, expected in CURRENT.items():
            self.assertEqual(digest(relative), expected)
            self.assertIn(Path(relative).name, receipt)
            self.assertIn(expected, receipt)

        for old, current in zip(DRAFTS.values(), CURRENT.values(), strict=True):
            self.assertNotEqual(old, current)
            self.assertIn(old, receipt)

        self.assertEqual(receipt.count("| `STALE` | `RERUN NOW` |"), 3)
        self.assertIn("ADR: `PROPOSED_FOR_AUTHORIZATION`", receipt)
        self.assertIn("Plan: `AWAITING_IMPLEMENTATION_AUTHORIZATION`", receipt)
        self.assertIn("`implementation_authorized`: `false`", receipt)
        self.assertIn("`install_authorized`: `false`", receipt)

    def test_acceptance_and_authorization_follow_the_recovery_receipt(self) -> None:
        plan = (ROOT / "docs/plans/kickoff-plan.md").read_text()
        adr = (ROOT / "docs/adr/0001-python-standard-library-core.md").read_text()

        pre_challenge = plan.index("WB-EX-PRECHALLENGE-001")
        challenge = plan.index("WB-EX-CHALLENGE-001")
        recovery = plan.index("WB-EX-RESUME-001")
        authorization = plan.index("## 5. Separate decision acceptance and authorization")
        implementation = plan.index("## 6. Ordered implementation")
        self.assertLess(pre_challenge, challenge)
        self.assertLess(challenge, recovery)
        self.assertLess(recovery, authorization)
        self.assertLess(authorization, implementation)

        self.assertIn("- Status: `ACCEPTED`", adr)
        self.assertIn("Accepted after evidence refresh", adr)
        self.assertIn("Implementation gate: `AUTHORIZED`", plan)
        self.assertIn("Package-installation gate: `AUTHORIZED`", plan)
        self.assertIn("`implementation_authorized=true`", plan)
        self.assertIn("`install_authorized=true`", plan)


if __name__ == "__main__":
    unittest.main()
