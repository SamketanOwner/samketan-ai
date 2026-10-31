"""Tests run with: python -m unittest discover -s tests -v"""
import unittest

from samketan_intelligence.gateway import (
    LeadCandidate,
    ResearchEvidence,
    ResearchGateway,
)


class GatewayTests(unittest.TestCase):
    def test_evidence_requires_https_and_title(self):
        self.assertTrue(ResearchEvidence("Source", "https://example.com/notice").is_valid())
        self.assertFalse(ResearchEvidence("Source", "http://example.com").is_valid())
        self.assertFalse(ResearchEvidence("", "https://example.com").is_valid())

    def test_unverified_lead_is_not_evidence_backed(self):
        self.assertFalse(LeadCandidate("Example", "Karnataka").evidence_backed)

    def test_cited_lead_is_evidence_backed_not_automatically_verified(self):
        lead = LeadCandidate("Example", "Karnataka", (ResearchEvidence("Notice", "https://example.com"),))
        self.assertTrue(lead.evidence_backed)
        self.assertEqual(lead.status, "candidate")

    def test_provider_limit_and_unknown_provider(self):
        gateway = ResearchGateway(max_results=3)
        gateway.register("fixture", lambda query, limit: [LeadCandidate(str(i), "KA") for i in range(5)])
        self.assertEqual(len(gateway.discover("fixture", "warehouse", 2)), 2)
        with self.assertRaises(ValueError):
            gateway.discover("unknown", "warehouse")

    def test_no_duplicate_provider_registration(self):
        gateway = ResearchGateway()
        gateway.register("fixture", lambda q, n: [])
        with self.assertRaises(ValueError):
            gateway.register("fixture", lambda q, n: [])


if __name__ == "__main__":
    unittest.main()
