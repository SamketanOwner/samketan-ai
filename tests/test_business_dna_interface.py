"""Static integration checks; full Streamlit UI testing remains a separate task."""
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[1] / "app.py"


class BusinessDNAInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_profile_selector_and_custom_mode(self):
        self.assertIn('"Custom (existing settings)"', self.source)
        self.assertIn('"Warehouse leasing"', self.source)
        self.assertIn('"Pulses manufacturing"', self.source)

    def test_explicit_apply_required(self):
        self.assertIn('key="dna_apply_profile"', self.source)
        self.assertIn('if st.button("Apply profile to existing search fields"', self.source)

    def test_existing_target_inputs_preserved(self):
        for key in ("target_product_input", "target_region_input", "target_client_input"):
            self.assertIn('key="' + key + '"', self.source)

    def test_existing_pipeline_preserved(self):
        self.assertIn('run_pipeline = st.button("🚀 LAUNCH 5-AGENT PIPELINE"', self.source)
        self.assertIn("agent_gemini_scout_grounded(", self.source)
        self.assertIn("agent_gemini_communicator(", self.source)

    def test_profile_does_not_claim_verified_demand(self):
        self.assertIn("they do not verify that a company needs your offering", self.source)


if __name__ == "__main__":
    unittest.main()
