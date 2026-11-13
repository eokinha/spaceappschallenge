"""Testes do pipeline. Rodar com: python -m unittest discover -s tests"""
import copy
import json
import unittest

from pipeline.export import ExportError, build_document, validate_document
from pipeline.features import ROOT, SiteError, load_config, load_sites, normalize_lon, sun_max_elevation
from pipeline.similarity import build_matrix, illumination_score, interval_overlap, tag_set_score


class TestFormulas(unittest.TestCase):
    def test_interval_overlap(self):
        self.assertAlmostEqual(interval_overlap((-50, 10), (-110, 0)), 50 / 120)
        self.assertEqual(interval_overlap((0, 10), (20, 30)), 0.0)
        self.assertEqual(interval_overlap((0, 10), (0, 10)), 1.0)

    def test_normalize_lon(self):
        self.assertAlmostEqual(normalize_lon(184.3), -175.7)
        self.assertEqual(normalize_lon(-43.2), -43.2)

    def test_sun_max_elevation(self):
        self.assertAlmostEqual(sun_max_elevation(-89.67, 1.54), 1.87)
        self.assertEqual(sun_max_elevation(0, 23.44), 90.0)

    def test_tag_score_symmetric(self):
        m = build_matrix([["basalto", "tefra_vulcanica", 0.8]])
        a, b = ["basalto", "argila"], ["tefra_vulcanica"]
        self.assertAlmostEqual(tag_set_score(a, b, m), tag_set_score(b, a, m))
        self.assertEqual(tag_set_score(["x"], ["x"], m), 1.0)

    def test_illumination_bounds(self):
        self.assertEqual(illumination_score(10, 0.5, 10, 0.5), 1.0)
        self.assertGreaterEqual(illumination_score(0, 0.0, 90, 1.0), 0.0)


class TestExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.targets, cls.analogs = load_sites(cls.config)
        cls.doc = build_document(cls.config, cls.targets, cls.analogs)
        with open(ROOT / cls.config["paths"]["schema"], encoding="utf-8") as f:
            cls.schema = json.load(f)

    def test_document_is_valid(self):
        validate_document(self.doc, self.schema)

    def test_every_link_has_limits_and_scores_in_range(self):
        for link in self.doc["links"]:
            self.assertTrue(link["limits"])
            self.assertTrue(0 <= link["score"] <= 1)

    def test_empty_limits_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["links"][0]["limits"] = []
        with self.assertRaises(ExportError):
            validate_document(doc, self.schema)

    def test_score_above_one_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["links"][0]["score"] = 1.2
        with self.assertRaises(ExportError):
            validate_document(doc, self.schema)

    def test_unknown_id_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["links"][0]["analog"] = "earth-nao-existe"
        with self.assertRaises(ExportError):
            validate_document(doc, self.schema)

    def test_missing_dimension_is_omitted_not_zero(self):
        import tempfile, yaml
        raw = yaml.safe_load((ROOT / self.config["paths"]["sites"]).read_text(encoding="utf-8"))
        for a in raw["analogs"]:
            a.pop("temperatura_c", None)
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.safe_dump(raw, f, allow_unicode=True)
        targets, analogs = load_sites(self.config, f.name)
        doc = build_document(self.config, targets, analogs)
        for link in doc["links"]:
            self.assertNotIn("temperatura", link["dimensions"])

    def test_bad_site_fails(self):
        import tempfile, yaml
        raw = yaml.safe_load((ROOT / self.config["paths"]["sites"]).read_text(encoding="utf-8"))
        raw["analogs"][0]["regolito"] = ["material_inventado"]
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.safe_dump(raw, f, allow_unicode=True)
        with self.assertRaises(SiteError):
            load_sites(self.config, f.name)


if __name__ == "__main__":
    unittest.main()
