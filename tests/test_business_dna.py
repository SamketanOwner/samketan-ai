import unittest

from samketan_intelligence.business_dna import (
    BusinessProfile, make_profile, pulses_manufacturing, warehouse_leasing,
)


class BusinessDNATests(unittest.TestCase):
    def test_warehouse_profile(self):
        profile = warehouse_leasing()
        self.assertIn("Kalaburagi", profile.target_regions)
        self.assertIn("3PL procurement", profile.buyer_types)
        self.assertTrue(any("warehouse" in q for q in profile.research_queries()))

    def test_pulses_profile(self):
        profile = pulses_manufacturing()
        self.assertIn("commodity buyer", profile.buyer_types)
        self.assertTrue(any("tur dal" in q for q in profile.research_queries()))

    def test_custom_regions(self):
        profile = make_profile("warehouse_leasing", ("Hubballi", "Belagavi"))
        queries = profile.research_queries()
        self.assertTrue(any("Hubballi" in q for q in queries))
        self.assertTrue(any("Belagavi" in q for q in queries))

    def test_query_limit(self):
        self.assertEqual(len(warehouse_leasing().research_queries(2)), 2)
        with self.assertRaises(ValueError):
            warehouse_leasing().research_queries(0)

    def test_unknown_profile(self):
        with self.assertRaises(ValueError):
            make_profile("unknown")

    def test_invalid_profile(self):
        with self.assertRaises(ValueError):
            BusinessProfile("", "something", ("Karnataka",), ("buyer",), ("signal",))
        with self.assertRaises(ValueError):
            warehouse_leasing(())


if __name__ == "__main__":
    unittest.main()
