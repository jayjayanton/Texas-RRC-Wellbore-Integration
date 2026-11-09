import unittest
from src.copybook_parser import zoned_to_number
from src.wellbore_integration import completion_identifiers, enrich_records
from src.validation import validate_records

class IntegrationTests(unittest.TestCase):
    def test_zoned_decimal(self):
        self.assertEqual(zoned_to_number("123A"), 1231)
        self.assertEqual(zoned_to_number("123J", 2), -12.31)

    def test_oil_provenance(self):
        row = {"WB-OIL-CODE":"O","WB-OIL-DIST":"01",
               "WB-OIL-LSE-NBR":"00123","WB-OIL-WELL-NBR":"2A"}
        result = completion_identifiers(row)
        self.assertEqual(result["DISTRICT_NO_SOURCE"], "WB-OIL-DIST")
        self.assertEqual(result["LEASE_NO"], "00123")

    def test_gas_provenance(self):
        row = {"WB-OIL-CODE":"G","WB-GAS-DIST":"02",
               "WB-GAS-RRC-ID":"123456","WB-GAS-WELL-NO":"7"}
        result = completion_identifiers(row)
        self.assertEqual(result["LEASE_NO_SOURCE"], "WB-GAS-RRC-ID")

    def test_boundary_prevents_leakage(self):
        records = [
            (1,"01",{}),
            (2,"02",{"WB-OIL-CODE":"O","WB-OIL-DIST":"01",
                      "WB-OIL-LSE-NBR":"12345","WB-OIL-WELL-NBR":"1"}),
            (3,"06",{"CASING":100}),
            (4,"01",{}),
            (5,"13",{"WB-WGS84-LONGITUDE":-97.5}),
        ]
        result = enrich_records(records)
        self.assertEqual(result[1][2]["DISTRICT_NO"], "01")
        self.assertNotIn("DISTRICT_NO", result[2][2])
        self.assertEqual(result[2][2]["WB-WGS84-LONGITUDE"], -97.5)

    def test_validation(self):
        self.assertEqual(validate_records([(1,"13",{"WB-WGS84-LONGITUDE":-97.5})]), [])

if __name__ == "__main__":
    unittest.main()
